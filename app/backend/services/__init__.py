from .fact_check_service import FactCheckService
from .news_fetcher import NewsFetcher
from .utils.text import sanitize_text, truncate_text
from .relevance.scorer import NewsRelevanceCalculator
from .relevance.features import get_keywords, extract_entities
from .analysis.article_analyzer import NewsArticleAnalyzer

__all__ = [
    "FactCheckService",
    "NewsFetcher",
    "sanitize_text",
    "truncate_text",
    "NewsRelevanceCalculator",
    "get_keywords",
    "extract_entities",
    "NewsArticleAnalyzer"
]