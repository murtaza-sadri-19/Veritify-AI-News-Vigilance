import logging
import json
import os
import urllib.parse
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta, timezone
import requests
from requests.exceptions import RequestException, Timeout
from .utils import (sanitize_text, calculate_relevance_score, get_keywords, 
                   extract_entities, initialize_semantic_model)
from services.News_trace import NewsArticleAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FactCheckService:
    """Service for fact-checking claims using RapidAPI services"""

    def __init__(self):
        self.rapidapi_key = os.getenv("NEWS_API_KEY")
        # Lazy initialize heavy analyzer to avoid startup latency
        self.article_analyzer = None

        # HTTP session for connection reuse and timeouts
        self.session = requests.Session()
        try:
            self.news_api_timeout = float(os.getenv("NEWS_API_TIMEOUT", "5.0"))
        except Exception:
            self.news_api_timeout = 5.0

        # Max number of relevant articles to fully analyze (heavy work)
        try:
            self.news_api_process_max = int(os.getenv("NEWS_API_PROCESS_MAX", "25"))
        except Exception:
            self.news_api_process_max = 25

        if not self.rapidapi_key or self.rapidapi_key == "":
            logger.warning("RAPIDAPI_KEY not configured - service will return mock responses")

        # Initialize semantic model once at startup (PERFORMANCE FIX)
        logger.info("🚀 Initializing semantic similarity model...")
        initialize_semantic_model()
        logger.info("✓ Semantic model ready")

        # Configurable parameters
        self.news_api_host = os.getenv("NEWS_API_HOST", "real-time-news-data.p.rapidapi.com")
        # Keep raw value so empty/unspecified limit can be honored (omit param)
        self.news_api_limit = os.getenv("NEWS_API_LIMIT", "")
        self.news_api_country = os.getenv("NEWS_API_COUNTRY", "US")
        self.news_api_lang = os.getenv("NEWS_API_LANG", "en")
        self.news_api_section = os.getenv("NEWS_API_SECTION", "")
        
        try:
            self.relevance_threshold = float(os.getenv("NEWS_RELEVANCE_THRESHOLD", "0.25"))
        except ValueError:
            self.relevance_threshold = 0.25
            
        self.sample_article_limit = int(os.getenv("NEWS_SAMPLE_LIMIT", "100"))

    def check_claim(self, claim: str) -> Dict[str, Any]:
        """Check a claim against news sources and fact-checking databases"""
        from time import perf_counter
        start_time = perf_counter()
        
        clean_claim = sanitize_text(claim)
        debug_info = {}

        logger.info(f"Checking claim: {clean_claim[:100]}...")

        if not self.rapidapi_key or self.rapidapi_key == "your_rapidapi_key_here":
            logger.warning("No API key configured, returning mock response")
            return self._generate_mock_response(clean_claim)

        # Search fact-checker API
        fact_check_results = self._search_fact_checker_api(clean_claim, debug_info)

        # Search real-time news API
        news_results = self._search_realtime_news_api(clean_claim, debug_info)

        # Combine results
        if fact_check_results or news_results:
            logger.info("API returned results")
            combined_results = self._combine_results(fact_check_results, news_results, clean_claim)
            
            # Add timing information
            elapsed_seconds = perf_counter() - start_time
            debug_info['elapsed_seconds'] = round(elapsed_seconds, 2)
            logger.info(f"⏱️ Total processing time: {elapsed_seconds:.2f}s")
            
            combined_results['debug'] = debug_info
            return combined_results

        # No results found
        logger.info("No relevant information found for claim")
        response = self._generate_no_results_response(clean_claim)
        
        elapsed_seconds = perf_counter() - start_time
        debug_info['elapsed_seconds'] = round(elapsed_seconds, 2)
        response['debug'] = debug_info
        return response

    def _search_fact_checker_api(self, claim: str, debug_info: Dict) -> Optional[Dict[str, Any]]:
        """Search the fact-checker API for existing fact-checks"""
        try:
            search_query = urllib.parse.quote(claim[:100])
            endpoint = f"https://fact-checker.p.rapidapi.com/search?query={search_query}&limit=20&offset=0&language=en"
            headers = {
                'x-rapidapi-key': self.rapidapi_key,
                'x-rapidapi-host': "fact-checker.p.rapidapi.com"
            }

            logger.debug(f"Querying fact-checker API: {endpoint}")
            resp = self.session.get(endpoint, headers=headers, timeout=self.news_api_timeout)

            debug_info['fact_checker_api'] = {
                'status_code': resp.status_code,
                'query': claim[:100],
                'endpoint': endpoint
            }

            if resp.status_code != 200:
                logger.error(f"Fact-checker API returned status {resp.status_code}")
                return None

            response_data = resp.json()
            debug_info['fact_checker_api']['results_found'] = len(response_data.get('results', []))
            return response_data
        except (RequestException, Timeout) as e:
            logger.error(f"Error querying fact-checker API: {str(e)}")
            debug_info['fact_checker_api_error'] = str(e)
            return None
        except Exception as e:
            logger.error(f"Unexpected error querying fact-checker API: {str(e)}")
            debug_info['fact_checker_api_error'] = str(e)
            return None

    def _build_boolean_query(self, claim: str, entities: List, keywords: List, 
                            topic_context: List, location_context: Optional[str]) -> str:
        """
        Build a sophisticated Boolean search query with proper operators.
        
        Example output:
        ("India" AND "Asia Cup 2025" AND ("wins" OR "victory" OR "champion")) 
        AND topic:Sports AND subtopic:Cricket
        
        Args:
            claim: Original claim text
            entities: Extracted entities
            keywords: Extracted keywords
            topic_context: Topic/genre keywords
            location_context: Geographic location
            
        Returns:
            Structured Boolean query string
        """
        query_parts = []
        
        # 1. Build entity clauses (exact phrases with quotes)
        entity_clauses = []
        for ent in entities:
            if len(ent.split()) > 1:
                # Multi-word entity with quotes
                entity_clauses.append(f'"{ent}"')
            else:
                # Single word entity
                entity_clauses.append(f'"{ent}"')
        
        # 2. Build keyword variations with OR (synonyms/related terms)
        keyword_groups = self._generate_keyword_variations(keywords, claim)
        
        # 3. Combine entities with AND
        boolean_parts = []
        if entity_clauses:
            if len(entity_clauses) == 1:
                boolean_parts.append(entity_clauses[0])
            else:
                boolean_parts.append(f"({' AND '.join(entity_clauses)})")
        
        # 4. Add keyword groups with OR operators
        if keyword_groups:
            for group_name, variations in keyword_groups.items():
                if variations:
                    if len(variations) == 1:
                        boolean_parts.append(f'"{variations[0]}"')
                    else:
                        or_clause = ' OR '.join([f'"{v}"' for v in variations])
                        boolean_parts.append(f"({or_clause})")
        
        # 5. Combine main query with AND
        if boolean_parts:
            main_query = ' AND '.join(boolean_parts)
            query_parts.append(f"({main_query})")
        
        # 6. Add topic filter
        if topic_context:
            # Primary topic (first one)
            primary_topic = topic_context[0].title()
            query_parts.append(f"topic:{primary_topic}")
            
            # Subtopic (secondary topics if available)
            if len(topic_context) > 1:
                subtopic = topic_context[1].title()
                query_parts.append(f"subtopic:{subtopic}")
        
        # 7. Add location filter
        if location_context:
            query_parts.append(f'location:"{location_context}"')
        
        # Join all parts with AND
        final_query = ' AND '.join(query_parts) if query_parts else claim
        
        return final_query
    
    def _generate_keyword_variations(self, keywords: List[str], claim: str) -> Dict[str, List[str]]:
        """
        Generate semantic variations of keywords for OR clauses.
        
        Args:
            keywords: Base keywords
            claim: Original claim for context
            
        Returns:
            Dictionary mapping concept to variations
        """
        variations = {}
        claim_lower = claim.lower()
        
        # Action verbs - winning/victory synonyms
        action_words = ['win', 'wins', 'won', 'winning', 'victory', 'defeat', 'beat']
        found_actions = [w for w in action_words if w in claim_lower or w in keywords]
        if found_actions:
            variations['action'] = ['win', 'victory', 'champion', 'triumph', 'defeat']
        
        # Competition/event keywords
        event_words = ['cup', 'championship', 'tournament', 'competition', 'final']
        found_events = [w for w in event_words if w in claim_lower or w in keywords]
        if found_events:
            variations['event'] = [w for w in found_events if w in claim_lower]
        
        # Time-related keywords (years, dates)
        import re
        years = re.findall(r'\b(20\d{2})\b', claim)
        if years:
            variations['time'] = years
        
        # Location variations (if multiple locations mentioned)
        location_words = ['india', 'pakistan', 'bangladesh', 'sri lanka', 'asia']
        found_locations = [w for w in location_words if w in claim_lower]
        if len(found_locations) > 1:
            variations['location'] = found_locations
        
        return variations

    def _search_realtime_news_api(self, claim: str, debug_info: Dict) -> Optional[Dict[str, Any]]:
        """Search real-time news API for recent articles related to the claim"""
        try:
            logger.info(f"🔍 STARTING NEWS SEARCH for claim: '{claim[:100]}...'")

            # Extract basic keywords and entities
            keywords = get_keywords(claim, max_keywords=8)
            entities = extract_entities(claim)

            logger.info(f"🔤 EXTRACTED KEYWORDS: {keywords}")
            logger.info(f"🎯 EXTRACTED ENTITIES: {entities}")

            # ENHANCED: Extract topic and location context from claim
            topic_context = []
            location_context = None
            
            try:
                if self.article_analyzer is None:
                    from services.News_trace import NewsArticleAnalyzer
                    self.article_analyzer = NewsArticleAnalyzer()
                
                # Extract genre/topic from claim
                genre = self.article_analyzer.classify_genre(claim)
                if genre and genre not in ["World News", "National News"]:
                    # Extract topic keywords from genre
                    topic_keywords = genre.lower().replace(' & ', ' ').replace('&', ' ').split()
                    topic_context.extend([kw for kw in topic_keywords if kw not in ["news", "and"]])
                    logger.info(f"📂 EXTRACTED TOPIC CONTEXT: {topic_context}")
                
                # Extract location from claim
                location = self.article_analyzer.extract_location(claim)
                if location and location != "Global":
                    location_context = location
                    logger.info(f"📍 EXTRACTED LOCATION CONTEXT: {location_context}")
            except Exception as e:
                logger.debug(f"Topic/location extraction skipped: {e}")

            # Build Boolean search query with operators
            # NOTE: Most RapidAPI news endpoints don't support Boolean operators
            # Use simple query by default unless using advanced search APIs
            use_boolean_query = os.getenv('USE_BOOLEAN_QUERY', 'false').lower() == 'true'
            
            if use_boolean_query:
                constructed_query = self._build_boolean_query(
                    claim, entities, keywords, topic_context, location_context
                )
                logger.info(f"🔎 BOOLEAN QUERY: '{constructed_query}'")
                logger.warning("⚠️ Boolean query enabled - ensure your API supports Boolean operators!")
            else:
                # Simple query (DEFAULT - works with most APIs)
                query_terms = []
                for ent in entities:
                    if len(ent.split()) > 1:
                        query_terms.append(f'"{ent}"')
                    else:
                        query_terms.append(ent)
                for kw in keywords:
                    if kw not in " ".join(query_terms):
                        query_terms.append(kw)
                for topic in topic_context:
                    if topic not in " ".join(query_terms).lower() and len(topic) > 3:
                        query_terms.append(topic)
                if location_context and location_context.lower() not in " ".join(query_terms).lower():
                    query_terms.append(location_context)
                
                if not query_terms:
                    query_terms = [claim]
                
                constructed_query = " ".join(query_terms)
                logger.info(f"🔎 SIMPLE QUERY: '{constructed_query}'")

            # Date range
            days_back = int(os.getenv('NEWS_API_DAYS_BACK', '7'))
            to_date = datetime.now(timezone.utc).date()
            from_date = to_date - timedelta(days=days_back)

            logger.info(f"📅 DATE RANGE: {from_date} to {to_date}")

            # Source filters
            source_whitelist = os.getenv('NEWS_SOURCE_WHITELIST', '')
            source_blacklist = os.getenv('NEWS_SOURCE_BLACKLIST', '')
            whitelist = [s.strip().lower() for s in source_whitelist.split(',') if s.strip()]
            blacklist = [s.strip().lower() for s in source_blacklist.split(',') if s.strip()]

            # Build headers and endpoint (use full URL with optional limit)
            headers = {
                'x-rapidapi-key': self.rapidapi_key,
                'x-rapidapi-host': self.news_api_host
            }

            if self.news_api_section:
                # include limit only if configured
                limit_fragment = f"&limit={self.news_api_limit}" if self.news_api_limit else ""
                endpoint = (
                    f"https://{self.news_api_host}/topic-news-by-section?topic={urllib.parse.quote(self.news_api_section)}"
                    f"{limit_fragment}&country={self.news_api_country}&lang={self.news_api_lang}"
                )
            else:
                q = urllib.parse.quote(constructed_query)
                limit_fragment = f"&limit={self.news_api_limit}" if self.news_api_limit else ""
                endpoint = (
                    f"https://{self.news_api_host}/search?query={q}{limit_fragment}&country={self.news_api_country}&lang={self.news_api_lang}"
                    f"&from={from_date.isoformat()}&to={to_date.isoformat()}"
                )

            debug_info['realtime_news_api'] = {
                'endpoint': endpoint,
                'constructed_query': constructed_query,
                'query_components': {
                    'entities': len(entities),
                    'keywords': len(keywords),
                    'topics': len(topic_context),
                    'location': location_context or 'None',
                },
                'from_date': from_date.isoformat(),
                'to_date': to_date.isoformat()
            }

            logger.info(f"🌐 API ENDPOINT: {endpoint}")

            resp = self.session.get(endpoint, headers=headers, timeout=self.news_api_timeout)

            debug_info['realtime_news_api']['status_code'] = resp.status_code

            if resp.status_code != 200:
                logger.error(f"❌ API returned status {resp.status_code}: {resp.text[:200]}")
                debug_info['realtime_news_api']['error_response'] = resp.text[:500]
                return None

            response_data = resp.json()
            articles = response_data.get('data') or response_data.get('articles') or []

            if not articles:
                logger.warning(f"⚠️ API returned 200 but NO ARTICLES. Response keys: {list(response_data.keys())}")
                logger.warning(f"⚠️ Response sample: {str(response_data)[:300]}")
                debug_info['realtime_news_api']['empty_response'] = True

            logger.info(f"📰 FETCHED {len(articles)} articles")

            debug_info['realtime_news_api']['articles_found'] = len(articles)

            # Process articles
            relevant_articles = []
            filtered_out_count = 0
            articles_analyzed_count = 0

            # First pass: filter and score relevance (fast - no heavy NLP)
            for idx, article in enumerate(articles):
                title = article.get('title') or article.get('headline') or ''
                snippet = article.get('snippet') or article.get('summary') or article.get('description') or ''
                source_name = (article.get('source_name') or article.get('source') or '').strip()
                url = article.get('url') or article.get('link') or ''
                published = (article.get('published_datetime_utc') or article.get('published_at') or '')

                # Source filtering
                sname_lower = source_name.lower() if source_name else ''
                if whitelist and sname_lower and sname_lower not in whitelist:
                    filtered_out_count += 1
                    continue
                if blacklist and sname_lower and sname_lower in blacklist:
                    filtered_out_count += 1
                    continue

                # Calculate relevance (fast - uses cached semantic model)
                relevance = calculate_relevance_score(claim, title, snippet, published)

                if relevance >= self.relevance_threshold:
                    # Skip heavy NLP analysis (preprocess/location/genre) - not used in scoring
                    # Store only what's needed for display and scoring
                    relevant_articles.append({
                        'article': {
                            'title': title,
                            'snippet': snippet,
                            'source_name': source_name,
                            'url': url,
                            'published_datetime_utc': published,
                            'preprocessed': None,
                            'location': None,
                            'genre': None
                        },
                        'relevance': relevance,
                        'published': published,
                        'source': source_name,
                        'url': url
                    })
                    articles_analyzed_count += 1
                    
                    # Apply processing cap to relevant articles only
                    if articles_analyzed_count >= self.news_api_process_max:
                        logger.info(f"⏹️ Processing cap reached: analyzed {self.news_api_process_max} relevant articles (more may exist)")
                        break

            # Sort by relevance
            relevant_articles.sort(key=lambda x: x['relevance'], reverse=True)

            logger.info(f"📊 FILTERING: {len(articles)} raw → {len(relevant_articles)} relevant (analyzed: {articles_analyzed_count})")
            
            if len(relevant_articles) == 0 and len(articles) > 0:
                logger.warning(f"⚠️ NO RELEVANT ARTICLES FOUND! All {len(articles)} articles below threshold {self.relevance_threshold}")
                logger.warning(f"💡 TIP: Lower NEWS_RELEVANCE_THRESHOLD (currently {self.relevance_threshold}) or improve query")
            
            debug_info['realtime_news_api']['filtered_out_count'] = filtered_out_count
            debug_info['realtime_news_api']['relevant_articles_count'] = len(relevant_articles)
            debug_info['realtime_news_api']['articles_analyzed_count'] = articles_analyzed_count

            return {
                'articles': relevant_articles, 
                'total_found': len(articles), 
                'relevant_count': len(relevant_articles)
            }
            
        except (RequestException, Timeout) as e:
            logger.error(f"Network error querying news API: {str(e)}")
            debug_info['realtime_news_api_error'] = str(e)
            return None
        except Exception as e:
            logger.error(f"Error querying news API: {str(e)}")
            debug_info['realtime_news_api_error'] = str(e)
            return None

    def _combine_results(self, fact_check_results: Optional[Dict],
                         news_results: Optional[Dict], claim: str) -> Dict[str, Any]:
        """Combine results with PROPER SCORE BOUNDS (0-100)"""
        sources = []
        total_articles = 0
        fact_check_score = None
        news_score = None

        logger.info("📄 COMBINING RESULTS")

        # Process fact-check results
        if fact_check_results and 'results' in fact_check_results:
            fact_check_count = len(fact_check_results['results'])
            logger.info(f"📋 FACT-CHECK RESULTS: {fact_check_count} checks found")

            for result in fact_check_results['results'][:5]:
                sources.append({
                    "name": result.get('title', 'Fact Check Result'),
                    "url": result.get('url', ''),
                    "date": result.get('date', ''),
                    "source": result.get('source', 'fact-checker'),
                    "relevance": result.get('score', 0.8),
                    "type": "fact-check"
                })
            
            # Fact-checks are highly credible
            fact_check_score = 80
            logger.info(f"✅ FACT-CHECK SCORE: {fact_check_score}%")

        # Process news results with FIXED SCORING
        if news_results and news_results.get('articles'):
            total_articles = news_results.get('total_found', 0)
            relevant_articles = news_results['articles']

            logger.info(f"📰 NEWS: {len(relevant_articles)} relevant from {total_articles} total")

            for item in relevant_articles[:5]:
                article = item['article']
                # Relevance is already bounded [0.0, 1.0] from calculate_relevance_score
                item_relevance = item['relevance']

                sources.append({
                    "name": article.get('title', 'News Article'),
                    "url": article.get('url', ''),
                    "date": article.get('published_datetime_utc', ''),
                    "source": article.get('source_name', 'news'),
                    "relevance": round(item_relevance, 3),
                    "type": "news",
                    "location": article.get('location', ''),
                    "genre": article.get('genre', '')
                })

            # IMPROVED: Credibility scoring based on multiple factors
            if relevant_articles:
                # All relevance scores are already [0.0, 1.0]
                relevance_scores = [item['relevance'] for item in relevant_articles]
                avg_relevance = sum(relevance_scores) / len(relevance_scores)
                article_count = len(relevant_articles)
                
                # Consider top articles more heavily (consensus factor)
                top_5_scores = relevance_scores[:5]
                top_avg = sum(top_5_scores) / len(top_5_scores) if top_5_scores else avg_relevance

                # Analyze source diversity (more diverse sources = higher credibility)
                unique_sources = set()
                for item in relevant_articles:
                    source = item.get('source', '').strip().lower()
                    if source:
                        unique_sources.add(source)
                source_diversity = len(unique_sources)

                logger.info(f"📊 Avg relevance: {avg_relevance:.3f} | Top-5 avg: {top_avg:.3f} | Count: {article_count} | Unique sources: {source_diversity}")

                # Base score from relevance quality (0-60 points)
                # Higher relevance = stronger evidence
                if top_avg >= 0.7:
                    base_score = 45 + (top_avg - 0.7) * 50  # 45-60 range
                elif top_avg >= 0.5:
                    base_score = 35 + (top_avg - 0.5) * 50  # 35-45 range
                elif top_avg >= 0.3:
                    base_score = 20 + (top_avg - 0.3) * 75  # 20-35 range
                else:
                    base_score = 10 + top_avg * 33  # 10-20 range

                # Article count bonus (0-15 points)
                # More articles = stronger consensus (diminishing returns)
                if article_count >= 20:
                    count_bonus = 15
                elif article_count >= 10:
                    count_bonus = 12
                elif article_count >= 5:
                    count_bonus = 8
                elif article_count >= 3:
                    count_bonus = 5
                else:
                    count_bonus = article_count * 1.5

                # Source diversity bonus (0-15 points) - NEW!
                # More unique sources = better cross-verification
                if source_diversity >= 15:
                    diversity_bonus = 15
                elif source_diversity >= 10:
                    diversity_bonus = 12
                elif source_diversity >= 7:
                    diversity_bonus = 9
                elif source_diversity >= 5:
                    diversity_bonus = 6
                elif source_diversity >= 3:
                    diversity_bonus = 3
                else:
                    diversity_bonus = source_diversity * 1

                # Consistency bonus (0-10 points)
                # Low variance in relevance = consistent reporting
                if len(relevance_scores) > 1:
                    import statistics
                    std_dev = statistics.stdev(relevance_scores)
                    # Lower std_dev = more consistent = higher bonus
                    consistency_bonus = max(0, 10 - (std_dev * 15))
                else:
                    consistency_bonus = 5

                # Final credibility score (0-100)
                news_score = int(base_score + count_bonus + diversity_bonus + consistency_bonus)
                news_score = max(0, min(100, news_score))

                logger.info(f"📊 CREDIBILITY: Base={int(base_score)}, Count={int(count_bonus)}, Diversity={int(diversity_bonus)}, Consistency={int(consistency_bonus)} → {news_score}%")

        # Determine overall score
        if fact_check_score is not None and news_score is not None:
            overall_score = max(fact_check_score, news_score)
            logger.info(f"🎯 COMBINED: max({fact_check_score}%, {news_score}%) = {overall_score}%")
        elif fact_check_score is not None:
            overall_score = fact_check_score
            logger.info(f"🎯 FACT-CHECK ONLY: {overall_score}%")
        elif news_score is not None:
            overall_score = news_score
            logger.info(f"🎯 NEWS ONLY: {overall_score}%")
        else:
            overall_score = 0
            logger.warning("⚠️ NO SCORE AVAILABLE")

        # FINAL SAFETY CHECK: Guarantee [0, 100]
        final_score = max(0, min(100, int(overall_score)))

        message = self._generate_combined_message(
            bool(fact_check_results and fact_check_results.get('results')),
            total_articles,
            final_score
        )

        result = {
            "score": final_score,  # GUARANTEED [0, 100]
            "message": message,
            "sources": sources,
            "claim_text": claim,
            "total_articles_found": total_articles
        }

        logger.info(f"✅ FINAL RESULT: Score = {final_score}%, Sources = {len(sources)}")
        return result

    def _generate_combined_message(self, has_fact_checks: bool,
                                   article_count: int, score: int) -> str:
        """Generate message based on available information"""
        if has_fact_checks and article_count > 0:
            return f"Found existing fact-checks and {article_count} related news articles."
        elif has_fact_checks:
            return "Found existing fact-checks for this claim."
        elif article_count > 0:
            if score >= 70:
                return f"Found {article_count} news articles with some relevance."
        else:
            return "Limited information available for this claim."

    def _generate_mock_response(self, claim: str) -> Dict[str, Any]:
        """Generate a mock response when API is not available"""
        return {
            "score": 0,
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
            "score": 0,
            "message": (
                "No relevant fact-checks or news articles found for this claim. "
                "This could mean the claim is very new, highly specific, or not widely reported."
            ),
            "sources": [],
            "claim_text": claim,
            "total_articles_found": 0
        }