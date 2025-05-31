import os
import requests
import logging

from .utils import sanitize_text, extract_entities

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class FactCheckService:
    def __init__(self):
        self.rapid_api_key = os.getenv("RAPIDAPI_KEY")
        self.news_api_key = os.getenv("NEWS_API_KEY")
        self.fact_checker_host = os.getenv("FACT_CHECKER_HOST")
        self.media_bias_host = os.getenv("MEDIA_BIAS_HOST")
        self.real_time_news_host = os.getenv("REAL_TIME_NEWS_HOST")
        self.google_news_host = os.getenv("GOOGLE_NEWS_HOST")
        self.newsdata_api_key = os.getenv("NEWSDATA_API_KEY")

    def check_claim(self, claim):
        clean_claim = sanitize_text(claim)
        debug_info = {}

        # 1. Fact-check API
        logging.debug("Querying Fact-Check API...")
        fact_check_results = self._query_fact_check_api(clean_claim, debug_info)
        if fact_check_results:
            logging.info("Fact-Check API replied with results.")
            fact_check_results['debug'] = debug_info
            return fact_check_results

        # 2. NewsData.io fallback
        logging.debug("Querying NewsData.io API...")
        news_results = self._search_newsdata_about_claim(clean_claim, debug_info)
        if news_results:
            logging.info("NewsData.io API replied with results.")
            news_results['debug'] = debug_info
            return news_results

        # 3. Final fallback
        logging.warning("No API replied with results. Using mock response.")
        response = self._generate_mock_response(clean_claim)
        response['debug'] = debug_info
        return response

    def _query_fact_check_api(self, claim, debug_info):
        try:
            headers = {
                "X-RapidAPI-Key": self.rapid_api_key,
                "X-RapidAPI-Host": self.fact_checker_host
            }
            url = f"https://{self.fact_checker_host}/factcheck"
            response = requests.get(url, headers=headers, params={"query": claim})
            debug_info['fact_check_api'] = f"Status {response.status_code}"
            if response.status_code == 200:
                logging.debug("Fact-Check API responded successfully.")
                data = response.json()
                debug_info['fact_check_api_response'] = data
                if data and "claims" in data and len(data["claims"]) > 0:
                    return {
                        "score": self._calculate_score(data["claims"][0]),
                        "message": self._generate_message(data["claims"][0]),
                        "sources": self._extract_sources(data["claims"][0]),
                        "claim_text": claim
                    }
            return None
        except Exception as e:
            logging.error(f"Error querying Fact-Check API: {str(e)}")
            debug_info['fact_check_api_error'] = str(e)
            return None

    def _search_newsdata_about_claim(self, claim, debug_info):
        try:
            truncated_claim = claim[:99]
            url = "https://newsdata.io/api/1/latest"
            params = {
                "apikey": self.newsdata_api_key,
                "q": truncated_claim,
                "language": "en"
            }
            response = requests.get(url, params=params)
            debug_info['newsdata_io'] = f"Status {response.status_code}"
            debug_info['newsdata_io_query'] = truncated_claim
            if response.status_code == 200:
                logging.debug("NewsData.io API responded successfully.")
                data = response.json()
                debug_info['newsdata_io_response'] = data
                articles = data.get("results", [])
                if articles:
                    return {
                        "score": 50,
                        "message": (
                            "No definitive fact check found, but highly relevant news articles are available."
                        ),
                        "sources": [
                            {
                                "name": article.get("title", "News Article"),
                                "url": article.get("link", ""),
                                "date": article.get("pubDate", "")
                            }
                            for article in articles[:3]
                        ],
                        "claim_text": claim
                    }
            return None
        except Exception as e:
            logging.error(f"Error querying NewsData.io API: {str(e)}")
            debug_info['newsdata_io_exception'] = str(e)
            return None

    def _calculate_score(self, claim_data):
        rating = claim_data.get("rating", "").lower()
        if "true" in rating or "correct" in rating:
            return 90
        elif "mostly true" in rating or "mostly correct" in rating:
            return 75
        elif "mixed" in rating or "partly" in rating:
            return 50
        elif "mostly false" in rating:
            return 25
        elif "false" in rating or "incorrect" in rating:
            return 10
        else:
            return 50

    def _generate_message(self, claim_data):
        rating = claim_data.get("rating", "")
        return f"Fact checkers rated this claim as: {rating}"

    def _extract_sources(self, claim_data):
        sources = []
        if "source" in claim_data:
            sources.append({
                "name": claim_data.get("source", {}).get("name", "Fact Check Source"),
                "url": claim_data.get("source", {}).get("url", ""),
                "date": claim_data.get("date", "")
            })
        return sources

    def _generate_mock_response(self, claim):
        return {
            "score": None,
            "message": (
                "No fact check or relevant news coverage was found for this claim. "
                "This does not mean the claim is true or false. Please consult multiple reputable sources."
            ),
            "sources": [],
            "claim_text": claim
        }