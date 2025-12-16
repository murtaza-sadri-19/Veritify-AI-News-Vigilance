import pytest
from unittest.mock import patch, Mock
from services.fact_check_service import FactCheckService
from services.utils.text import sanitize_text
from services.relevance.scorer import NewsRelevanceCalculator


class TestFactCheckService:
    """Test cases for FactCheckService"""

    def setup_method(self):
        """Setup test fixtures"""
        self.service = FactCheckService(api_key="test_key")

    def test_init(self):
        """Test service initialization"""
        assert self.service.api_key == "test_key"
        assert self.service.api_url == "https://newsdata.io/api/1/news"

    def test_init_no_api_key(self):
        """Test initialization without API key raises error"""
        with pytest.raises(ValueError, match="API key is required"):
            FactCheckService(api_key=None)

    @patch('requests.get')
    def test_search_news_success(self, mock_get):
        """Test successful news search"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 'success',
            'totalResults': 2,
            'results': [
                {
                    'title': 'Climate Change Impact on Weather',
                    'link': 'https://example.com/article1',
                    'source_id': 'testnews',
                    'pubDate': '2025-01-15 10:00:00'
                },
                {
                    'title': 'Global Warming Effects Studied',
                    'link': 'https://example.com/article2',
                    'source_id': 'sciencenews',
                    'pubDate': '2025-01-14 15:30:00'
                }
            ]
        }
        mock_get.return_value = mock_response

        results = self.service._search_news("climate change")

        assert len(results) == 2
        assert results[0]['title'] == 'Climate Change Impact on Weather'
        assert results[1]['source_id'] == 'sciencenews'

    @patch('requests.get')
    def test_search_news_api_error(self, mock_get):
        """Test news search with API error"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {'error': 'Invalid API key'}
        mock_get.return_value = mock_response

        results = self.service._search_news("test query")
        assert results == []

    @patch('requests.get')
    def test_search_news_network_error(self, mock_get):
        """Test news search with network error"""
        mock_get.side_effect = Exception("Network error")

        results = self.service._search_news("test query")
        assert results == []

    @patch.object(FactCheckService, '_search_news')
    def test_verify_claim_success(self, mock_search):
        """Test successful claim verification"""
        # Mock news search results
        mock_search.return_value = [
            {
                'title': 'Climate Change is Real Says Scientists',
                'link': 'https://example.com/article1',
                'source_id': 'sciencenews',
                'pubDate': '2025-01-15 10:00:00'
            },
            {
                'title': 'Weather Patterns Show Climate Impact',
                'link': 'https://example.com/article2',
                'source_id': 'weathernews',
                'pubDate': '2025-01-14 15:30:00'
            }
        ]

        result = self.service.verify_claim("Climate change is happening")

        assert isinstance(result['score'], int)
        assert 0 <= result['score'] <= 100
        assert 'message' in result
        assert 'sources' in result
        assert len(result['sources']) <= 3
        assert 'total_articles_found' in result

    @patch.object(FactCheckService, '_search_news')
    def test_verify_claim_no_results(self, mock_search):
        """Test claim verification with no results"""
        mock_search.return_value = []

        result = self.service.verify_claim("Very obscure claim")

        assert result['score'] == 0
        assert 'no relevant news articles' in result['message'].lower()
        assert result['sources'] == []
        assert result['total_articles_found'] == 0

    def test_validate_claim_empty(self):
        """Test claim validation with empty claim"""
        with pytest.raises(ValueError, match="Claim cannot be empty"):
            self.service._validate_claim("")

    def test_validate_claim_too_long(self):
        """Test claim validation with too long claim"""
        long_claim = "x" * 1000
        with pytest.raises(ValueError, match="Claim is too long"):
            self.service._validate_claim(long_claim)

    def test_validate_claim_valid(self):
        """Test claim validation with valid claim"""
        # Should not raise any exception
        self.service._validate_claim("This is a valid claim")


class TestUtils:
    """Test cases for utility functions"""

    def test_sanitize_text_basic(self):
        """Test basic text sanitization"""
        text = "  Hello World!  "
        result = sanitize_text(text)
        assert result == "Hello World!"

    def test_sanitize_text_html(self):
        """Test HTML sanitization"""
        text = "<script>alert('xss')</script>Hello &amp; World"
        result = sanitize_text(text)
        assert "script" not in result
        assert "Hello & World" in result

    def test_sanitize_text_empty(self):
        """Test sanitization of empty text"""
        assert sanitize_text("") == ""
        assert sanitize_text(None) == ""

    def test_calculate_relevance_score_exact_match(self):
        """Test relevance score for exact match"""
        claim = "climate change is real"
        title = "Climate change is real and happening"
        calculator = NewsRelevanceCalculator()
        score = calculator.calculate_relevance_score(claim, title, "")
        assert score > 0.5

    def test_calculate_relevance_score_no_match(self):
        """Test relevance score for no match"""
        claim = "climate change"
        title = "Sports news today"
        calculator = NewsRelevanceCalculator()
        score = calculator.calculate_relevance_score(claim, title, "")
        assert score < 0.5

    def test_calculate_relevance_score_partial_match(self):
        """Test relevance score for partial match"""
        claim = "global warming effects"
        title = "Study shows global impacts of warming"
        calculator = NewsRelevanceCalculator()
        score = calculator.calculate_relevance_score(claim, title, "")
        assert 0.3 < score < 0.8