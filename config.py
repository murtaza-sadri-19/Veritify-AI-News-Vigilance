# Add to app.py or create a config.py file
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def validate_config():
    """Validate that all required environment variables are set"""
    required_vars = [
        'SECRET_KEY',
        'RAPIDAPI_KEY',
        'FACT_CHECKER_HOST',
        'MEDIA_BIAS_HOST',
        'REAL_TIME_NEWS_HOST',
        'GOOGLE_NEWS_HOST'
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}. "
            f"Please check your .env file."
        )

# Call this function early in your application startup
validate_config()