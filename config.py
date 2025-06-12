import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""

    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = FLASK_ENV == 'development'

    # API settings
    NEWSDATA_API_KEY = os.getenv('NEWSDATA_API_KEY')
    NEWSDATA_API_URL = 'https://newsdata.io/api/1/news'

    # Ngrok settings
    NGROK_AUTHTOKEN = os.getenv('NGROK_AUTHTOKEN')
    NGROK_REGION = os.getenv('NGROK_REGION', 'us')

    # Application settings
    MAX_CLAIM_LENGTH = 500
    MAX_RESULTS = 3
    RELEVANCE_THRESHOLD = 0.3

    # Rate limiting
    RATE_LIMIT_PER_MINUTE = 10

    # Timeouts
    API_TIMEOUT = 30

    @staticmethod
    def validate_config():
        """Validate required configuration"""
        if not Config.NEWSDATA_API_KEY:
            raise ValueError("NEWSDATA_API_KEY environment variable is required")

        return True