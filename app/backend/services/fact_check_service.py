import logging
import http.client
import json
import os
import urllib.parse
from typing import Dict, Optional, Any
from datetime import datetime, timedelta, timezone
from .utils.text import sanitize_text, truncate_text
from .relevance.scorer import NewsRelevanceCalculator
from .relevance.features import get_keywords, extract_entities
from .analysis.article_analyzer import NewsArticleAnalyzer
from .news_fetcher import NewsFetcher

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FactCheckService(NewsFetcher):
    """Service for fact-checking claims using RapidAPI services"""

    def __init__(self):
        # Call parent init
        super().__init__()
        
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

    def _combine_results(self, fact_check_results: Optional[Dict],
                         news_results: Optional[Dict], claim: str) -> Dict[str, Any]:
        """Combine results from both APIs into a unified response, including advanced news analysis"""
        sources = []
        total_articles = 0
        fact_check_score = None
        
        logger.info(f"Combining results for claim: '{claim[:80]}'")
        logger.debug(f"Fact-check results available: {bool(fact_check_results)}")
        logger.debug(f"News results available: {bool(news_results)}")
        
        if fact_check_results and 'results' in fact_check_results:
            logger.info(f"Found {len(fact_check_results['results'])} fact-check results")
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
                fact_check_score = 80
        else:
            logger.debug("No fact-check results found")
            
        news_score = None
        if news_results and news_results.get('articles'):
            total_articles = news_results.get('total_found', 0)
            relevant_count = len(news_results.get('articles', []))
            logger.info(f"Found {relevant_count} relevant news articles out of {total_articles} total")
            
            for idx, item in enumerate(news_results['articles'][:5]):
                article = item.get('article', {})
                relevance = item.get('relevance', 0.0)
                sources.append({
                    "name": article.get('title', 'News Article'),
                    "url": article.get('url', ''),
                    "date": article.get('published_datetime_utc', ''),
                    "source": article.get('source_name', 'news'),
                    "relevance": round(relevance, 2),
                    "type": "news",
                    "location": article.get('location', ''),
                    "genre": article.get('genre', ''),
                    "preprocessed": article.get('preprocessed', '')
                })
                logger.debug(
                    f"Article {idx}: relevance={relevance:.3f} location='{article.get('location', '')}' "
                    f"genre='{article.get('genre', '')}'"
                )
            
            if len(news_results.get('articles', [])) > 0:
                avg_relevance = sum(item['relevance'] for item in news_results['articles']) / len(news_results['articles'])
                news_score = min(100, max(30, int(avg_relevance * 100)))
                logger.info(f"Average news relevance: {avg_relevance:.3f}, Score: {news_score}")
        else:
            logger.debug("No relevant news articles found")
            
        if fact_check_score and news_score:
            overall_score = max(fact_check_score, news_score)
        elif fact_check_score:
            overall_score = fact_check_score
        elif news_score:
            overall_score = news_score
        else:
            overall_score = None
            
        message = self._generate_combined_message(
            bool(fact_check_results and fact_check_results.get('results')),
            total_articles,
            overall_score
        )
        
        logger.info(f"Final score: {overall_score}, Total sources: {len(sources)}")
        
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