import http.client
import json
from typing import Dict, Optional, Any
import os
import urllib.parse
from datetime import datetime, timedelta, timezone
from .utils.text import sanitize_text, truncate_text
from .relevance.features import get_keywords, extract_entities
from .relevance.scorer import NewsRelevanceCalculator
import logging

logger = logging.getLogger(__name__)

class NewsFetcher:
    def __init__(self):
        """Initialize NewsFetcher with relevance calculator"""
        self.relevance_calculator = NewsRelevanceCalculator()
    def _search_fact_checker_api(self, claim: str, debug_info: Dict) -> Optional[Dict[str, Any]]:
        """Search the fact-checker API for existing fact-checks"""
        conn = None
        try:
            search_query = urllib.parse.quote(claim[:100])
            conn = http.client.HTTPSConnection("fact-checker.p.rapidapi.com")
            headers = {
                'x-rapidapi-key': self.rapidapi_key,
                'x-rapidapi-host': "fact-checker.p.rapidapi.com"
            }
            endpoint = f"/search?query={search_query}&limit=20&offset=0&language=en"
            logger.debug(f"Querying fact-checker API with: {claim[:50]}...")
            conn.request("GET", endpoint, headers=headers)
            res = conn.getresponse()
            data = res.read()
            debug_info['fact_checker_api'] = {
                'status_code': res.status,
                'query': claim[:100],
                'endpoint': endpoint
            }
            if res.status != 200:
                logger.error(f"Fact-checker API returned status {res.status}")
                return None
            response_data = json.loads(data.decode("utf-8"))
            debug_info['fact_checker_api']['results_found'] = len(response_data.get('results', []))
            return response_data
        except Exception as e:
            logger.error(f"Error querying fact-checker API: {str(e)}")
            debug_info['fact_checker_api_error'] = str(e)
            return None
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def _search_realtime_news_api(self, claim: str, debug_info: Dict) -> Optional[Dict[str, Any]]:
        """Search real-time news API for recent articles related to the claim, with advanced analysis

        Enhancements:
        - Build focused search query from claim keywords and entities
        - Optional date range and source filters via environment variables
        - Early source whitelist/blacklist filtering
        - Sort results by relevance before returning
        - Add constructed query and params to debug_info for auditing
        """
        conn = None
        try:
            logger.info(f"Starting news fetch for claim: '{claim}'")

            # Build focused query terms from claim keywords and entities
            keywords = get_keywords(claim, max_keywords=6)
            entities = extract_entities(claim)
            # Prioritize entities (exact phrases) then keywords
            query_terms = []
            for ent in entities:
                if len(ent.split()) > 1:
                    query_terms.append(f'"{ent}"')
            for kw in keywords:
                if kw not in " ".join(query_terms):
                    query_terms.append(kw)

            # Fallback to full claim if no keywords/entities extracted
            if not query_terms:
                query_terms = [claim]

            constructed_query = " ".join(query_terms)

            # Date range filter (optional)
            days_back = int(os.getenv('NEWS_API_DAYS_BACK', '7'))
            to_date = datetime.now(timezone.utc).date()
            from_date = to_date - timedelta(days=days_back)

            # Source whitelist/blacklist (optional)
            source_whitelist = os.getenv('NEWS_SOURCE_WHITELIST', '')
            source_blacklist = os.getenv('NEWS_SOURCE_BLACKLIST', '')
            whitelist = [s.strip().lower() for s in source_whitelist.split(',') if s.strip()]
            blacklist = [s.strip().lower() for s in source_blacklist.split(',') if s.strip()]

            # Prepare connection and headers
            conn = http.client.HTTPSConnection(self.news_api_host)
            headers = {
                'x-rapidapi-key': self.rapidapi_key,
                'x-rapidapi-host': self.news_api_host
            }

            # Decide endpoint: section-based or search-based
            if self.news_api_section:
                endpoint = (
                    f"/topic-news-by-section?topic={urllib.parse.quote(self.news_api_section)}"
                    f"&limit={self.news_api_limit}&country={self.news_api_country}&lang={self.news_api_lang}"
                )
            else:
                # Use constructed query and add date filters if supported
                q = urllib.parse.quote(constructed_query)
                endpoint = (
                    f"/search?query={q}&limit={self.news_api_limit}&country={self.news_api_country}&lang={self.news_api_lang}"
                    f"&from={from_date.isoformat()}&to={to_date.isoformat()}"
                )

            # Record the query metadata for debug
            debug_info['realtime_news_api'] = debug_info.get('realtime_news_api', {})
            debug_info['realtime_news_api'].update({
                'status_code': None,
                'endpoint': endpoint,
                'constructed_query': constructed_query,
                'query_terms': query_terms,
                'from_date': from_date.isoformat(),
                'to_date': to_date.isoformat(),
                'whitelist': whitelist,
                'blacklist': blacklist
            })

            logger.debug(f"Querying real-time news API at endpoint: {endpoint}")
            conn.request("GET", endpoint, headers=headers)
            res = conn.getresponse()
            data = res.read()

            # Update status
            debug_info['realtime_news_api']['status_code'] = res.status
            logger.info(f"News API response status: {res.status}")
            if res.status != 200:
                logger.error(f"Real-time news API returned status {res.status} for claim: '{claim}'")
                return None

            response_data = json.loads(data.decode("utf-8"))
            # Support both 'data' and 'articles' keys
            articles = response_data.get('data') or response_data.get('articles') or []
            logger.info(f"Total articles fetched: {len(articles)} for claim: '{claim}'")
            debug_info['realtime_news_api']['articles_found'] = len(articles)

            # Track sources and sample article references for debugging / audit
            article_sources = set()
            sample_articles = []
            relevant_articles = []
            for idx, article in enumerate(articles):
                # Normalize different possible field names
                title = article.get('title') or article.get('headline') or ''
                snippet = article.get('snippet') or article.get('summary') or article.get('description') or ''
                source_name = (article.get('source_name') or article.get('source') or article.get('sourceName') or '').strip()
                url = article.get('url') or article.get('link') or ''
                published = (article.get('published_datetime_utc') or article.get('published_at') or article.get('published') or '')

                # Basic source filtering (whitelist/blacklist) before computing relevance
                sname_lower = source_name.lower() if source_name else ''
                if whitelist and sname_lower and sname_lower not in whitelist:
                    # skip sources not in whitelist
                    logger.debug(f"Skipping article from non-whitelisted source: {source_name}")
                    continue
                if blacklist and sname_lower and sname_lower in blacklist:
                    logger.debug(f"Skipping article from blacklisted source: {source_name}")
                    continue

                # Collect source names for reference
                if source_name:
                    article_sources.add(source_name)

                relevance = self.relevance_calculator.calculate_relevance_score(claim, title, snippet)

                # Log each article search result (index, source, url, relevance) for traceability
                logger.debug(
                    f"Article[{idx}] searched: title='{title[:80]}' source='{source_name}' url='{url}' published='{published}' relevance={relevance:.3f}"
                )

                # Save a small sample for debug_info (limit configurable)
                if len(sample_articles) < self.sample_article_limit:
                    sample_articles.append({
                        'index': idx,
                        'title': title,
                        'source': source_name,
                        'url': url,
                        'published': published,
                        'relevance': round(relevance, 3)
                    })

                if relevance >= self.relevance_threshold:
                    try:
                        # Advanced analysis using NewsArticleAnalyzer
                        full_text = f"{title}. {snippet}"
                        
                        # Perform NLP analysis with error handling
                        try:
                            preprocessed = self.article_analyzer.preprocess_text(full_text)
                        except Exception as e:
                            logger.warning(f"Preprocessing failed for article '{title[:50]}': {str(e)}")
                            preprocessed = full_text
                        
                        try:
                            location = self.article_analyzer.extract_location(full_text)
                        except Exception as e:
                            logger.warning(f"Location extraction failed for article '{title[:50]}': {str(e)}")
                            location = ""
                        
                        try:
                            genre = self.article_analyzer.classify_genre(full_text)
                        except Exception as e:
                            logger.warning(f"Genre classification failed for article '{title[:50]}': {str(e)}")
                            genre = ""
                        
                        article['preprocessed'] = preprocessed
                        article['location'] = location
                        article['genre'] = genre
                        
                        relevant_articles.append({
                            'article': article,
                            'relevance': relevance,
                            'published': published,
                            'source': source_name,
                            'url': url
                        })
                        logger.info(f"Article analyzed: title='{title[:60]}' relevance={relevance:.3f} location='{location}' genre='{genre}'")
                    except Exception as e:
                        logger.error(f"Failed to process article '{title[:50]}': {str(e)}")
                        # Still add article even if analysis fails
                        relevant_articles.append({
                            'article': article,
                            'relevance': relevance,
                            'published': published,
                            'source': source_name,
                            'url': url
                        })

            # Sort relevant articles by relevance desc, then by published date (if available)
            def _parsed_date(a):
                try:
                    return datetime.fromisoformat(a.get('published'))
                except Exception:
                    return datetime.min

            relevant_articles.sort(key=lambda x: (x['relevance'], _parsed_date(x)), reverse=True)

            # Add collected source and sample info to debug_info
            debug_info['realtime_news_api']['article_sources'] = list(article_sources)
            debug_info['realtime_news_api']['sample_articles'] = sample_articles

            # Log sources and a few sample article references for easier traceability
            if article_sources:
                sample_sources = list(article_sources)[:10]
                logger.info(f"News sources searched (sample): {', '.join(sample_sources)}")
            else:
                logger.info("No source metadata returned by news API")

            if sample_articles:
                for s in sample_articles:
                    logger.info(
                        f"SampleArticle[{s['index']}]: source={s['source']} title='{s['title'][:80]}' url={s['url']} published={s['published']} relevance={s['relevance']}"
                    )
            else:
                logger.info("No sample articles available from news API")

            logger.info(f"Relevant articles found: {len(relevant_articles)} for claim: '{claim}'")
            debug_info['realtime_news_api']['relevant_articles'] = len(relevant_articles)
            logger.info(f"Finished news fetch for claim: '{claim}'")

            return {
                'articles': relevant_articles[:10],  # Limit to top 10
                'total_found': len(articles),
                'query': constructed_query
            }
        except Exception as e:
            logger.error(f"Error querying real-time news API for claim '{claim}': {str(e)}")
            debug_info['realtime_news_api_error'] = str(e)
            return None
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass