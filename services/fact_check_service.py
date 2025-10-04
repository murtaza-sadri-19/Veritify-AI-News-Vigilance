import logging
import http.client
import json
import os
import urllib.parse
from typing import Dict, Optional, Any
from datetime import datetime, timedelta, timezone
from .utils import sanitize_text, calculate_relevance_score, get_keywords, extract_entities
from services.News_trace import NewsArticleAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FactCheckService:
    """Service for fact-checking claims using RapidAPI services"""

    def __init__(self):
        self.rapidapi_key = os.getenv("NEWS_API_KEY")  # Replace with your actual RapidAPI key
        self.article_analyzer = NewsArticleAnalyzer()

        if not self.rapidapi_key or self.rapidapi_key == "":
            logger.warning("RAPIDAPI_KEY not configured - service will return mock responses")

        # Configurable news API parameters (avoid hardcoding)
        self.news_api_host = os.getenv("NEWS_API_HOST", "real-time-news-data.p.rapidapi.com")
        self.news_api_limit = int(os.getenv("NEWS_API_LIMIT", "50"))
        self.news_api_country = os.getenv("NEWS_API_COUNTRY", "US")
        self.news_api_lang = os.getenv("NEWS_API_LANG", "en")
        # Optional section/topic (if provided, will be used instead of free-text search)
        self.news_api_section = os.getenv("NEWS_API_SECTION", "")
        # Minimum relevance threshold to consider an article (0.0 - 1.0)
        try:
            self.relevance_threshold = float(os.getenv("NEWS_RELEVANCE_THRESHOLD", "0.25"))
        except ValueError:
            self.relevance_threshold = 0.25
        # Limit number of sample articles logged
        self.sample_article_limit = int(os.getenv("NEWS_SAMPLE_LIMIT", "5"))

    def check_claim(self, claim: str) -> Dict[str, Any]:
        """
        Check a claim against news sources and fact-checking databases

        Args:
            claim: The claim to verify

        Returns:
            Dictionary containing score, message, sources, and claim_text
        """
        clean_claim = sanitize_text(claim)
        debug_info = {}

        logger.info(f"Checking claim: {clean_claim[:100]}...")

        if not self.rapidapi_key or self.rapidapi_key == "your_rapidapi_key_here":
            logger.warning("No API key configured, returning mock response")
            return self._generate_mock_response(clean_claim)

        # First, try the dedicated fact-checker API
        fact_check_results = self._search_fact_checker_api(clean_claim, debug_info)

        # Then, search real-time news for additional context
        news_results = self._search_realtime_news_api(clean_claim, debug_info)

        # Combine results
        if fact_check_results or news_results:
            logger.info("API returned results")
            combined_results = self._combine_results(fact_check_results, news_results, clean_claim)
            combined_results['debug'] = debug_info
            return combined_results

        # No results found
        logger.info("No relevant information found for claim")
        response = self._generate_no_results_response(clean_claim)
        response['debug'] = debug_info
        return response

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
        - Detailed logging of search categories and strategies
        """
        conn = None
        try:
            logger.info(f"🔍 STARTING NEWS SEARCH for claim: '{claim[:100]}...'")

            # Log initial configuration
            logger.info(f"📊 NEWS SEARCH CONFIG - Limit: {self.news_api_limit}, Country: {self.news_api_country}, Language: {self.news_api_lang}")
            logger.info(f"📊 RELEVANCE THRESHOLD: {self.relevance_threshold}, HOST: {self.news_api_host}")

            # Build focused query terms from claim keywords and entities
            keywords = get_keywords(claim, max_keywords=6)
            entities = extract_entities(claim)

            logger.info(f"🔤 EXTRACTED KEYWORDS: {keywords}")
            logger.info(f"🎯 EXTRACTED ENTITIES: {entities}")

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
                logger.warning("⚠️  NO KEYWORDS/ENTITIES FOUND - Using full claim as search query")

            constructed_query = " ".join(query_terms)
            logger.info(f"🔍 CONSTRUCTED SEARCH QUERY: '{constructed_query}'")

            # Date range filter (optional)
            days_back = int(os.getenv('NEWS_API_DAYS_BACK', '7'))
            to_date = datetime.now(timezone.utc).date()
            from_date = to_date - timedelta(days=days_back)

            logger.info(f"📅 DATE RANGE: {from_date} to {to_date} ({days_back} days back)")

            # Source whitelist/blacklist (optional)
            source_whitelist = os.getenv('NEWS_SOURCE_WHITELIST', '')
            source_blacklist = os.getenv('NEWS_SOURCE_BLACKLIST', '')
            whitelist = [s.strip().lower() for s in source_whitelist.split(',') if s.strip()]
            blacklist = [s.strip().lower() for s in source_blacklist.split(',') if s.strip()]

            if whitelist:
                logger.info(f"✅ SOURCE WHITELIST: {whitelist}")
            if blacklist:
                logger.info(f"❌ SOURCE BLACKLIST: {blacklist}")

            # Prepare connection and headers
            conn = http.client.HTTPSConnection(self.news_api_host)
            headers = {
                'x-rapidapi-key': self.rapidapi_key,
                'x-rapidapi-host': self.news_api_host
            }

            # Decide endpoint: section-based or search-based
            search_strategy = ""
            if self.news_api_section:
                search_strategy = f"SECTION-BASED: {self.news_api_section}"
                endpoint = (
                    f"/topic-news-by-section?topic={urllib.parse.quote(self.news_api_section)}"
                    f"&limit={self.news_api_limit}&country={self.news_api_country}&lang={self.news_api_lang}"
                )
                logger.info(f"📰 NEWS CATEGORY STRATEGY: {search_strategy}")
                logger.info(f"📂 EXPLORING SECTION: '{self.news_api_section}'")
            else:
                search_strategy = "KEYWORD-BASED SEARCH"
                # Use constructed query and add date filters if supported
                q = urllib.parse.quote(constructed_query)
                endpoint = (
                    f"/search?query={q}&limit={self.news_api_limit}&country={self.news_api_country}&lang={self.news_api_lang}"
                    f"&from={from_date.isoformat()}&to={to_date.isoformat()}"
                )
                logger.info(f"🔍 NEWS SEARCH STRATEGY: {search_strategy}")
                logger.info(f"🎯 SEARCH CATEGORIES: General news, breaking news, recent articles")

            # WHY 50 ARTICLES: Log the reason for fetching this many
            logger.info(f"📈 FETCHING {self.news_api_limit} ARTICLES (configured limit)")
            logger.info(f"🎯 REASON: API fetches max articles first, then filters by relevance threshold {self.relevance_threshold}")

            # Record the query metadata for debug
            debug_info['realtime_news_api'] = debug_info.get('realtime_news_api', {})
            debug_info['realtime_news_api'].update({
                'status_code': None,
                'endpoint': endpoint,
                'search_strategy': search_strategy,
                'constructed_query': constructed_query,
                'query_terms': query_terms,
                'from_date': from_date.isoformat(),
                'to_date': to_date.isoformat(),
                'whitelist': whitelist,
                'blacklist': blacklist,
                'configured_limit': self.news_api_limit,
                'relevance_threshold': self.relevance_threshold
            })

            logger.info(f"🌐 API ENDPOINT: {endpoint}")
            logger.debug(f"Querying real-time news API at endpoint: {endpoint}")

            conn.request("GET", endpoint, headers=headers)
            res = conn.getresponse()
            data = res.read()

            # Update status
            debug_info['realtime_news_api']['status_code'] = res.status
            logger.info(f"📊 NEWS API RESPONSE STATUS: {res.status}")

            if res.status != 200:
                logger.error(f"❌ Real-time news API returned status {res.status} for claim: '{claim}'")
                return None

            response_data = json.loads(data.decode("utf-8"))
            # Support both 'data' and 'articles' keys
            articles = response_data.get('data') or response_data.get('articles') or []

            logger.info(f"📰 TOTAL RAW ARTICLES FETCHED: {len(articles)}")
            logger.info(f"🎯 NOW FILTERING BY RELEVANCE THRESHOLD: {self.relevance_threshold}")

            debug_info['realtime_news_api']['articles_found'] = len(articles)

            # Track sources and sample article references for debugging / audit
            article_sources = set()
            sample_articles = []
            relevant_articles = []
            filtered_out_count = 0

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
                    logger.debug(f"⛔ FILTERED OUT (not whitelisted): {source_name}")
                    filtered_out_count += 1
                    continue
                if blacklist and sname_lower and sname_lower in blacklist:
                    logger.debug(f"⛔ FILTERED OUT (blacklisted): {source_name}")
                    filtered_out_count += 1
                    continue

                # Collect source names for reference
                if source_name:
                    article_sources.add(source_name)

                relevance = calculate_relevance_score(claim, title, snippet, published)

                # Log each article search result for traceability
                if relevance >= self.relevance_threshold:
                    logger.info(f"✅ RELEVANT Article[{idx+1}/{len(articles)}]: '{title[:60]}...' | Source: {source_name} | Relevance: {relevance:.3f}")
                else:
                    logger.debug(f"❌ LOW RELEVANCE Article[{idx+1}/{len(articles)}]: '{title[:60]}...' | Source: {source_name} | Relevance: {relevance:.3f}")

                # Save a small sample for debug_info (limit configurable)
                if len(sample_articles) < self.sample_article_limit:
                    sample_articles.append({
                        'index': idx,
                        'title': title,
                        'source': source_name,
                        'url': url,
                        'published': published,
                        'relevance': round(relevance, 3),
                        'is_relevant': relevance >= self.relevance_threshold
                    })

                if relevance >= self.relevance_threshold:
                    # Advanced analysis using NewsArticleAnalyzer
                    full_text = f"{title}. {snippet}"
                    preprocessed = self.article_analyzer.preprocess_text(full_text)
                    location = self.article_analyzer.extract_location(full_text)
                    genre = self.article_analyzer.classify_genre(full_text)

                    logger.debug(f"📍 ARTICLE ANALYSIS - Location: {location}, Genre: {genre}")

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

            # Sort relevant articles by relevance desc, then by published date (if available)
            def _parsed_date(a):
                try:
                    return datetime.fromisoformat(a.get('published'))
                except Exception:
                    return datetime.min

            relevant_articles.sort(key=lambda x: (x['relevance'], _parsed_date(x)), reverse=True)

            # COMPREHENSIVE LOGGING OF RESULTS
            logger.info(f"📊 FILTERING RESULTS:")
            logger.info(f"  • Raw articles fetched: {len(articles)}")
            logger.info(f"  • Filtered out by source rules: {filtered_out_count}")
            logger.info(f"  • Passed relevance threshold ({self.relevance_threshold}): {len(relevant_articles)}")
            logger.info(f"  • Sources explored: {len(article_sources)}")

            # Add collected source and sample info to debug_info
            debug_info['realtime_news_api']['article_sources'] = list(article_sources)
            debug_info['realtime_news_api']['sample_articles'] = sample_articles
            debug_info['realtime_news_api']['filtered_out_count'] = filtered_out_count
            debug_info['realtime_news_api']['relevant_articles_count'] = len(relevant_articles)

            # Log sources and sample articles for traceability
            if article_sources:
                logger.info(f"🗞️  NEWS SOURCES EXPLORED: {', '.join(sorted(list(article_sources)))}")
            else:
                logger.warning("⚠️  NO SOURCE METADATA returned by news API")

            if sample_articles:
                logger.info(f"📄 SAMPLE ARTICLES ANALYZED:")
                for i, s in enumerate(sample_articles):
                    status = "✅ RELEVANT" if s['is_relevant'] else "❌ NOT RELEVANT"
                    logger.info(f"  {i+1}. [{status}] {s['source']} | '{s['title'][:50]}...' | Score: {s['relevance']}")

            logger.info(f"🎯 FINAL RESULT: {len(relevant_articles)} relevant articles found for claim verification")
            logger.info(f"🔍 COMPLETED NEWS SEARCH for claim: '{claim[:50]}...'")

            return {'articles': relevant_articles, 'total_found': len(articles), 'relevant_count': len(relevant_articles)}
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

    def _combine_results(self, fact_check_results: Optional[Dict],
                         news_results: Optional[Dict], claim: str) -> Dict[str, Any]:
        """Combine results from both APIs into a unified response, including advanced news analysis"""
        sources = []
        total_articles = 0
        fact_check_score = None

        logger.info("🔄 COMBINING RESULTS from fact-check and news APIs")

        # Process fact-check results
        if fact_check_results and 'results' in fact_check_results:
            fact_check_count = len(fact_check_results['results'])
            logger.info(f"📋 FACT-CHECK RESULTS: Found {fact_check_count} existing fact-checks")

            for result in fact_check_results['results'][:5]:
                sources.append({
                    "name": result.get('title', 'Fact Check Result'),
                    "url": result.get('url', ''),
                    "date": result.get('date', ''),
                    "source": result.get('source', 'fact-checker'),
                    "relevance": result.get('score', 0.8),
                    "type": "fact-check"
                })
            if fact_check_results.get('results'):
                fact_check_score = 80  # Fixed credibility score for existing fact-checks
                logger.info(f"✅ FACT-CHECK SCORE: {fact_check_score}%")

        # Process news results with CORRECTED SCORING
        news_score = None
        if news_results and news_results.get('articles'):
            total_articles = news_results.get('total_found', 0)
            relevant_articles = news_results['articles']

            logger.info(f"📰 NEWS RESULTS: {len(relevant_articles)} relevant articles from {total_articles} total")

            for item in relevant_articles[:5]:
                article = item['article']
                # Ensure relevance is properly bounded [0.0, 1.0]
                item_relevance = max(0.0, min(1.0, item['relevance']))

                sources.append({
                    "name": article.get('title', 'News Article'),
                    "url": article.get('url', ''),
                    "date": article.get('published_datetime_utc', ''),
                    "source": article.get('source_name', 'news'),
                    "relevance": round(item_relevance, 3),  # Keep as 0.0-1.0 for display
                    "type": "news",
                    "location": article.get('location', ''),
                    "genre": article.get('genre', ''),
                    "preprocessed": article.get('preprocessed', '')
                })

            # FIXED SCORING CALCULATION - Ensure proper percentage conversion
            if relevant_articles:
                # Calculate average relevance (should be between 0.0 and 1.0)
                relevance_scores = [max(0.0, min(1.0, item['relevance'])) for item in relevant_articles]
                avg_relevance = sum(relevance_scores) / len(relevance_scores)

                logger.info(f"📊 RELEVANCE CALCULATION:")
                logger.info(f"  • Individual scores: {[round(r, 3) for r in relevance_scores[:5]]}")
                logger.info(f"  • Average relevance: {avg_relevance:.3f}")

                # Convert to percentage (0-100) with proper bounds
                news_score_raw = avg_relevance * 100  # Convert 0.0-1.0 to 0-100

                # Apply realistic scoring bounds for news credibility
                # High relevance (>0.7) = 70-85% credibility
                # Medium relevance (0.4-0.7) = 50-70% credibility
                # Low relevance (<0.4) = 30-50% credibility
                if avg_relevance >= 0.7:
                    news_score = min(85, max(70, int(70 + (avg_relevance - 0.7) * 50)))
                elif avg_relevance >= 0.4:
                    news_score = min(70, max(50, int(50 + (avg_relevance - 0.4) * 66)))
                else:
                    news_score = min(50, max(30, int(30 + avg_relevance * 50)))

                # Final safety check - ensure score is always 0-100
                news_score = max(0, min(100, news_score))

                logger.info(f"📊 CREDIBILITY SCORING:")
                logger.info(f"  • Raw average relevance: {avg_relevance:.3f}")
                logger.info(f"  • Converted percentage: {news_score_raw:.1f}%")
                logger.info(f"  • Final credibility score: {news_score}%")

        # Determine overall score
        if fact_check_score and news_score:
            overall_score = max(fact_check_score, news_score)
            logger.info(f"🎯 COMBINED SCORE: max(fact-check: {fact_check_score}%, news: {news_score}%) = {overall_score}%")
        elif fact_check_score:
            overall_score = fact_check_score
            logger.info(f"🎯 FACT-CHECK ONLY SCORE: {overall_score}%")
        elif news_score:
            overall_score = news_score
            logger.info(f"🎯 NEWS ONLY SCORE: {overall_score}%")
        else:
            overall_score = None
            logger.warning("⚠️  NO SCORE AVAILABLE: No relevant sources found")

        # Generate message
        message = self._generate_combined_message(
            bool(fact_check_results and fact_check_results.get('results')),
            total_articles,
            overall_score
        )

        # Final result
        result = {
            "score": overall_score,
            "message": message,
            "sources": sources,
            "claim_text": claim,
            "total_articles_found": total_articles
        }

        logger.info(f"✅ FINAL VERIFICATION RESULT: Score = {overall_score}%, Sources = {len(sources)}")
        return result

    def _generate_combined_message(self, has_fact_checks: bool,
                                   article_count: int, score: Optional[int]) -> str:
        """Generate a message based on available information"""
        if has_fact_checks and article_count > 0:
            return f"Found existing fact-checks and {article_count} related news articles for this claim."
        elif has_fact_checks:
            return "Found existing fact-checks for this claim."
        elif article_count > 0:
            if score and score >= 70:
                return f"Found {article_count} highly relevant news articles discussing this topic."
            elif score and score >= 50:
                return f"Found {article_count} moderately relevant news articles related to this claim."
            else:
                return f"Found {article_count} news articles with some relevance to this claim."
        else:
            return "Limited information available for this claim."

    def _generate_mock_response(self, claim: str) -> Dict[str, Any]:
        """Generate a mock response when API is not available"""
        return {
            "score": None,
            "message": (
                "RapidAPI key not configured. This is a demo response. "
                "Configure your RapidAPI key to get real fact-checking results."
            ),
            "sources": [
                {
                    "name": "Demo Source: Configure API Key",
                    "url": "https://rapidapi.com/",
                    "date": "2025-01-01",
                    "source": "demo",
                    "relevance": 0.0,
                    "type": "demo"
                }
            ],
            "claim_text": claim,
            "total_articles_found": 0
        }

    def _generate_no_results_response(self, claim: str) -> Dict[str, Any]:
        """Generate response when no relevant information is found"""
        return {
            "score": None,
            "message": (
                "No relevant fact-checks or news articles found for this claim. "
                "This could mean the claim is very new, highly specific, or not widely reported."
            ),
            "sources": [],
            "claim_text": claim,
            "total_articles_found": 0
        }
