import pytest
import json
from unittest.mock import patch, Mock
from app.backend.main import create_app


@pytest.fixture
def app():
    """Create test app instance"""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


class TestAPI:
    """Test cases for the fact-check API"""

    def test_index_page(self, client):
        """Test that index page loads correctly"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Veritify AI Vigilance' in response.data
        assert b'Verify the Truth with AI' in response.data

    def test_about_page(self, client):
        """Test that about page loads correctly"""
        response = client.get('/about')
        assert response.status_code == 200
        assert b'About Veritify AI Vigilance' in response.data
        assert b'Our Mission' in response.data

    def test_verify_endpoint_missing_claim(self, client):
        """Test API with missing claim"""
        response = client.post('/api/verify',
                               data=json.dumps({}),
                               content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'claim is required' in data['error'].lower()

    def test_verify_endpoint_empty_claim(self, client):
        """Test API with empty claim"""
        response = client.post('/api/verify',
                               data=json.dumps({'claim': ''}),
                               content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False

    def test_verify_endpoint_short_claim(self, client):
        """Test API with too short claim"""
        response = client.post('/api/verify',
                               data=json.dumps({'claim': 'short'}),
                               content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False

    @patch('services.fact_check_service.FactCheckService.verify_claim')
    def test_verify_endpoint_success(self, mock_verify, client):
        """Test successful verification"""
        # Mock successful response
        mock_verify.return_value = {
            'score': 75,
            'message': 'Found relevant news articles',
            'sources': [
                {
                    'name': 'Test Article',
                    'url': 'https://example.com/article',
                    'source': 'Test News',
                    'date': '2025-01-15',
                    'relevance': 0.8
                }
            ],
            'total_articles_found': 1,
            'debug': {}
        }

        response = client.post('/api/verify',
                               data=json.dumps({'claim': 'Climate change is real and happening'}),
                               content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'result' in data
        assert data['result']['score'] == 75
        assert len(data['result']['sources']) == 1

    @patch('services.fact_check_service.FactCheckService.verify_claim')
    def test_verify_endpoint_api_error(self, mock_verify, client):
        """Test API error handling"""
        # Mock API error
        mock_verify.side_effect = Exception("API error")

        response = client.post('/api/verify',
                               data=json.dumps({'claim': 'Test claim for error'}),
                               content_type='application/json')

        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data

    def test_verify_endpoint_invalid_json(self, client):
        """Test with invalid JSON"""
        response = client.post('/api/verify',
                               data='invalid json',
                               content_type='application/json')
        assert response.status_code == 400

    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'