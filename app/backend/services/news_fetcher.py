import http.client
import json
import os
import urllib.parse
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Any, List
import numpy as np
import logging

from .utils.text import sanitize_text, safe_truncate as truncate_text
from .analysis.article_analyzer import NewsArticleAnalyzer
from .relevance.scorer import RelevanceAndEntailmentScorer

logger = logging.getLogger(__name__)


class NewsFetcher:
    """
    Two-stage retrieval:
    - Stage 1: cheap lexical/TF-IDF batch scoring + metadata-only enrichment
    - Stage 2: only selected candidates go to semantic + entailment (handled downstream)
    """

    def __init__(self):
        self.article_analyzer = NewsArticleAnalyzer()
        self.scorer = RelevanceAndEntailmentScorer()

        # Configuration
        self.news_api_host = os.getenv("NEWS_API_HOST", "real-time-news-data.p.rapidapi.com")
        self.news_api_limit = int(os.getenv("NEWS_API_LIMIT", "50"))
        self.news_api_country = os.getenv("NEWS_API_COUNTRY", "US")
        self.news_api_lang = os.getenv("NEWS_API_LANG", "en")
        self.news_api_section = os.getenv("NEWS_API_SECTION", "")

        self.sample_article_limit = int(os.getenv("NEWS_SAMPLE_LIMIT", "5"))
        self.top_k_articles = int(os.getenv("NEWS_TOP_K_ARTICLES", "15"))

    # ── External API calls (unchanged shape, cheaper internals) ────

    def _search_fact_checker_api(self, claim: str, debug_info: Dict) -> Optional[Dict[str, Any]]:
        conn = None
        try:
            search_query = urllib.parse.quote(claim[:100])
            conn = http.client.HTTPSConnection("fact-checker.p.rapidapi.com")
            headers = {
                "x-rapidapi-key": self.rapidapi_key,
                "x-rapidapi-host": "fact-checker.p.rapidapi.com",
            }
            endpoint = f"/search?query={search_query}&limit=20&offset=0&language=en"
            logger.debug(f"Querying fact-checker API with: {claim[:50]}...")
            conn.request("GET", endpoint, headers=headers)
            res = conn.getresponse()
            data = res.read()
            debug_info["fact_checker_api"] = {
                "status_code": res.status,
                "query": claim[:100],
                "endpoint": endpoint,
            }
            if res.status != 200:
                logger.error(f"Fact-checker API returned status {res.status}")
                return None
            response_data = json.loads(data.decode("utf-8"))
            debug_info["fact_checker_api"]["results_found"] = len(
                response_data.get("results", [])
            )
            return response_data
        except Exception as e:
            logger.error(f"Error querying fact-checker API: {str(e)}")
            debug_info["fact_checker_api_error"] = str(e)
            return None
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def _search_realtime_news_api(
        self,
        claim: str,
        context,
        debug_info: Dict,
    ) -> Optional[Dict[str, Any]]:
        """
        Stage 1: cheap retrieval + batch TF-IDF scoring + dynamic candidate selection.
        Stage 2 (semantic + entailment) is handled later via scorer using RequestContext.
        """
        conn = None
        try:
            logger.info(f"Starting news fetch for claim: '{claim}'")

            # Focused query from sanitized claim
            constructed_query = sanitize_text(claim)

            # Date range filter
            days_back = int(os.getenv("NEWS_API_DAYS_BACK", "7"))
            to_date = datetime.now(timezone.utc).date()
            from_date = to_date - timedelta(days=days_back)

            conn = http.client.HTTPSConnection(self.news_api_host)
            headers = {
                "x-rapidapi-key": self.rapidapi_key,
                "x-rapidapi-host": self.news_api_host,
            }

            if self.news_api_section:
                endpoint = (
                    f"/topic-news-by-section?topic={urllib.parse.quote(self.news_api_section)}"
                    f"&limit={self.news_api_limit}&country={self.news_api_country}&lang={self.news_api_lang}"
                )
            else:
                q = urllib.parse.quote(constructed_query)
                endpoint = (
                    f"/search?query={q}&limit={self.news_api_limit}"
                    f"&country={self.news_api_country}&lang={self.news_api_lang}"
                    f"&from={from_date.isoformat()}&to={to_date.isoformat()}"
                )

            debug_info["realtime_news_api"] = {
                "status_code": None,
                "endpoint": endpoint,
                "constructed_query": constructed_query,
                "from_date": from_date.isoformat(),
                "to_date": to_date.isoformat(),
            }

            logger.debug(f"Querying real-time news API at endpoint: {endpoint}")
            conn.request("GET", endpoint, headers=headers)
            res = conn.getresponse()
            data = res.read()

            debug_info["realtime_news_api"]["status_code"] = res.status
            logger.info(f"News API response status: {res.status}")

            if res.status != 200:
                logger.error(f"Real-time news API returned status {res.status}")
                return None

            response_data = json.loads(data.decode("utf-8"))
            articles = response_data.get("data") or response_data.get("articles") or []
            logger.info(f"[NEWS] Fetched {len(articles)} articles from news API")
            debug_info["realtime_news_api"]["articles_found"] = len(articles)
            
            # Log article titles for transparency
            for idx, a in enumerate(articles[:5], 1):
                title = a.get("title") or a.get("headline") or "(untitled)"
                source = a.get("source_name") or a.get("source") or "unknown"
                logger.debug(f"  [{idx}] {source}: {title[:80]}")

            # Metadata-only enrichment (no heavy NLP here)
            meta_articles: List[Dict[str, Any]] = []
            sample_articles: List[Dict[str, Any]] = []

            for idx, a in enumerate(articles):
                title = a.get("title") or a.get("headline") or ""
                snippet = (
                    a.get("snippet")
                    or a.get("summary")
                    or a.get("description")
                    or ""
                )
                source_name = (
                    a.get("source_name") or a.get("source") or a.get("sourceName") or ""
                ).strip()
                url = a.get("url") or a.get("link") or ""
                published = (
                    a.get("published_datetime_utc")
                    or a.get("published_at")
                    or a.get("published")
                    or ""
                )

                snippet = truncate_text(snippet, max_length=300)

                article_meta = {
                    "title": title,
                    "snippet": snippet,
                    "source_name": source_name,
                    "url": url,
                    "published_datetime_utc": published,
                }
                meta_articles.append(article_meta)

                if len(sample_articles) < self.sample_article_limit:
                    sample_articles.append(
                        {
                            "index": idx,
                            "title": title,
                            "source": source_name,
                            "url": url,
                            "published": published,
                        }
                    )

            debug_info["realtime_news_api"]["sample_articles"] = sample_articles

            if not meta_articles:
                logger.info("No articles returned after metadata enrichment")
                return {
                    "articles": [],
                    "total_found": 0,
                    "relevant_count": 0,
                    "query": constructed_query,
                }

            # Stage 1: Batch TF-IDF lexical similarity
            texts_for_tfidf = [
                f"{m['title']}. {m['snippet']}".strip() for m in meta_articles
            ]
            lexical_scores = self.scorer.batch_tfidf_lexical(
                context, claim, texts_for_tfidf
            )

            # Dynamic candidate selection based on semantic distribution
            # (semantic will be computed downstream; here we use lexical as placeholder)
            top_n = max(20, int(0.4 * len(lexical_scores)))
            candidate_indices = list(np.argsort(lexical_scores)[-top_n:])

            context.candidate_indices = candidate_indices
            debug_info["realtime_news_api"]["candidate_indices"] = candidate_indices

            # Only pass candidate articles forward to semantic + entailment
            candidate_articles = [meta_articles[i] for i in candidate_indices]

            logger.info(
                f"Selected {len(candidate_articles)} lexical candidates for semantic analysis"
            )

            return {
                "articles": candidate_articles,
                "total_found": len(articles),
                "relevant_count": len(candidate_articles),
                "query": constructed_query,
            }

        except Exception as e:
            logger.error(f"Error querying real-time news API: {str(e)}")
            debug_info["realtime_news_api_error"] = str(e)
            return None
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass