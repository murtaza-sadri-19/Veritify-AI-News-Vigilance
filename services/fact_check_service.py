import logging
import http.client
import json
import urllib.parse
from typing import Dict, Optional, Any

from .utils import sanitize_text, calculate_relevance_score

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FactCheckService:
    """Service for fact-checking claims using RapidAPI services"""

    def __init__(self):
        self.rapidapi_key = "6701a4274emsh7a0d625386d78f2p1c5863jsn78f437bc6c76"  # Replace with your actual RapidAPI key
        if not self.rapidapi_key or self.rapidapi_key == "":
            logger.warning("RAPIDAPI_KEY not configured - service will return mock responses")

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
        try:
            # Extract key terms from claim for search
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
            try:
                conn.close()
            except:
                pass

    def _search_realtime_news_api(self, claim: str, debug_info: Dict) -> Optional[Dict[str, Any]]:
        """Search real-time news API for recent articles related to the claim"""
        try:
            conn = http.client.HTTPSConnection("real-time-news-data.p.rapidapi.com")

            headers = {
                'x-rapidapi-key': self.rapidapi_key,
                'x-rapidapi-host': "real-time-news-data.p.rapidapi.com"
            }

            # Use general news search - you may want to customize this based on claim content
            # For now, using technology section as an example
            endpoint = "/topic-news-by-section?topic=TECHNOLOGY&section=CAQiSkNCQVNNUW9JTDIwdk1EZGpNWFlTQldWdUxVZENHZ0pKVENJT0NBUWFDZ29JTDIwdk1ETnliSFFxQ2hJSUwyMHZNRE55YkhRb0FBKi4IACoqCAoiJENCQVNGUW9JTDIwdk1EZGpNWFlTQldWdUxVZENHZ0pKVENnQVABUAE&limit=50&country=US&lang=en"

            logger.debug("Querying real-time news API...")

            conn.request("GET", endpoint, headers=headers)
            res = conn.getresponse()
            data = res.read()

            debug_info['realtime_news_api'] = {
                'status_code': res.status,
                'endpoint': endpoint
            }

            if res.status != 200:
                logger.error(f"Real-time news API returned status {res.status}")
                return None

            response_data = json.loads(data.decode("utf-8"))
            debug_info['realtime_news_api']['articles_found'] = len(response_data.get('data', []))

            # Filter articles by relevance to claim
            articles = response_data.get('data', [])
            relevant_articles = []

            for article in articles:
                title = article.get('title', '')
                snippet = article.get('snippet', '')
                relevance = calculate_relevance_score(claim, title, snippet)

                if relevance > 0.1:  # Only include somewhat relevant articles
                    relevant_articles.append({
                        'article': article,
                        'relevance': relevance
                    })

            debug_info['realtime_news_api']['relevant_articles'] = len(relevant_articles)

            return {
                'articles': relevant_articles[:10],  # Limit to top 10
                'total_found': len(articles)
            }

        except Exception as e:
            logger.error(f"Error querying real-time news API: {str(e)}")
            debug_info['realtime_news_api_error'] = str(e)
            return None
        finally:
            try:
                conn.close()
            except:
                pass

    def _combine_results(self, fact_check_results: Optional[Dict],
                         news_results: Optional[Dict], claim: str) -> Dict[str, Any]:
        """Combine results from both APIs into a unified response"""
        sources = []
        total_articles = 0

        # Process fact-check results
        fact_check_score = None
        if fact_check_results and 'results' in fact_check_results:
            for result in fact_check_results['results'][:5]:  # Limit to top 5
                sources.append({
                    "name": result.get('title', 'Fact Check Result'),
                    "url": result.get('url', ''),
                    "date": result.get('date', ''),
                    "source": result.get('source', 'fact-checker'),
                    "relevance": result.get('score', 0.8),
                    "type": "fact-check"
                })

            # Calculate fact-check score based on results
            if fact_check_results.get('results'):
                fact_check_score = 80  # High confidence if fact-checks exist

        # Process news results
        news_score = None
        if news_results and news_results.get('articles'):
            total_articles = news_results.get('total_found', 0)

            for item in news_results['articles'][:5]:  # Limit to top 5
                article = item['article']
                sources.append({
                    "name": article.get('title', 'News Article'),
                    "url": article.get('url', ''),
                    "date": article.get('published_datetime_utc', ''),
                    "source": article.get('source_name', 'news'),
                    "relevance": round(item['relevance'], 2),
                    "type": "news"
                })

            # Calculate news-based score
            avg_relevance = sum(item['relevance'] for item in news_results['articles']) / len(news_results['articles'])
            news_score = min(100, max(30, int(avg_relevance * 100)))

        # Determine overall score
        if fact_check_score and news_score:
            overall_score = max(fact_check_score, news_score)
        elif fact_check_score:
            overall_score = fact_check_score
        elif news_score:
            overall_score = news_score
        else:
            overall_score = None

        # Generate message
        message = self._generate_combined_message(
            bool(fact_check_results and fact_check_results.get('results')),
            total_articles,
            overall_score
        )

        return {
            "score": overall_score,
            "message": message,
            "sources": sources,
            "claim_text": claim,
            "total_articles_found": total_articles
        }

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