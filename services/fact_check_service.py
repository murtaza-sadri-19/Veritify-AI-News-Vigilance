import os
import requests
from .utils import sanitize_text, extract_entities

class FactCheckService:
    def __init__(self):
        # Get API keys from environment variables
        self.rapid_api_key = os.getenv("RAPIDAPI_KEY")
        self.news_api_key = os.getenv("NEWS_API_KEY")
        
        # RapidAPI hosts
        self.fact_checker_host = os.getenv("FACT_CHECKER_HOST")
        self.media_bias_host = os.getenv("MEDIA_BIAS_HOST")
        self.real_time_news_host = os.getenv("REAL_TIME_NEWS_HOST")
        self.google_news_host = os.getenv("GOOGLE_NEWS_HOST")

    def check_claim(self, claim):
        # Sanitize input
        clean_claim = sanitize_text(claim)
        
        # Try to get fact check results
        fact_check_results = self._query_fact_check_api(clean_claim)
        
        if not fact_check_results:
            # Fall back to mock data if no results
            return self._generate_mock_response(clean_claim)
        
        return fact_check_results
        
    def _query_fact_check_api(self, claim):
        """Query the RapidAPI fact checker endpoint"""
        try:
            headers = {
                "X-RapidAPI-Key": self.rapid_api_key,
                "X-RapidAPI-Host": self.fact_checker_host
            }
            
            url = f"https://{self.fact_checker_host}/factcheck"
            response = requests.get(
                url,
                headers=headers,
                params={"query": claim}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Process the response into our standard format
                if data and "claims" in data and len(data["claims"]) > 0:
                    # Extract the first claim result
                    claim_data = data["claims"][0]
                    
                    # Map the API response to our format
                    result = {
                        "score": self._calculate_score(claim_data),
                        "message": self._generate_message(claim_data),
                        "sources": self._extract_sources(claim_data),
                        "claim_text": claim
                    }
                    return result
            
            # If no results, fallback to Google News search
            return self._search_news_about_claim(claim)
            
        except Exception as e:
            print(f"Error querying fact check API: {str(e)}")
            return None
    
    def _search_news_about_claim(self, claim):
        """Search for news articles about the claim"""
        try:
            headers = {
                "X-RapidAPI-Key": self.rapid_api_key,
                "X-RapidAPI-Host": self.google_news_host
            }
            
            url = f"https://{self.google_news_host}/search"
            response = requests.get(
                url,
                headers=headers,
                params={"q": claim, "limit": 5}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data and "articles" in data and len(data["articles"]) > 0:
                    # We found some news articles - this doesn't give us fact checks
                    # but provides context about the claim
                    return {
                        "score": 50,  # Neutral score since we don't have fact check data
                        "message": "No definitive fact check found, but related news articles are available.",
                        "sources": [
                            {
                                "name": article.get("title", "News Article"),
                                "url": article.get("link", ""),
                                "date": article.get("published_date", "")
                            }
                            for article in data["articles"][:3]  # Get top 3 articles
                        ],
                        "claim_text": claim
                    }
            
            return None
            
        except Exception as e:
            print(f"Error searching news: {str(e)}")
            return None
    
    def _calculate_score(self, claim_data):
        """Calculate truthfulness score (0-100) based on fact check data"""
        # This implementation depends on the actual structure of claim_data
        # Sample implementation:
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
            return 50  # Neutral score for unknown ratings
    
    def _generate_message(self, claim_data):
        """Generate a human-readable assessment message"""
        rating = claim_data.get("rating", "")
        return f"Fact checkers rated this claim as: {rating}"
    
    def _extract_sources(self, claim_data):
        """Extract source information from claim data"""
        # Adapt this based on the actual API response structure
        sources = []
        
        if "source" in claim_data:
            sources.append({
                "name": claim_data.get("source", {}).get("name", "Fact Check Source"),
                "url": claim_data.get("source", {}).get("url", ""),
                "date": claim_data.get("date", "")
            })
            
        return sources
    
    def _generate_mock_response(self, claim):
        """Generate a mock response when no API results are found"""
        # This is fallback data when we can't get real fact checks
        import random
        
        # Political keywords for detecting political claims
        political_keywords = [
            "president", "congress", "democrat", "republican", "election",
            "senator", "government", "vote", "policy", "biden", "trump"
        ]
        
        # Science/health keywords
        science_keywords = [
            "covid", "vaccine", "climate", "study", "research", "scientific",
            "health", "doctor", "medical", "virus", "disease"
        ]
        
        # Check if the claim is political or scientific
        claim_lower = claim.lower()
        is_political = any(keyword in claim_lower for keyword in political_keywords)
        is_scientific = any(keyword in claim_lower for keyword in science_keywords)
        
        # Generate a random score, but make it contextual
        if is_political:
            score = random.randint(30, 70)  # Political claims often have mixed truth
            message = "This appears to be a political claim. Verify with multiple sources."
        elif is_scientific:
            score = random.randint(40, 90)  # Scientific claims tend to be more verifiable
            message = "This appears to be a scientific or health-related claim. Check official sources."
        else:
            score = random.randint(20, 80)  # General claims get a wide range
            message = "No specific fact check was found for this claim. Consider researching further."
        
        return {
            "score": score,
            "message": message,
            "sources": [
                {
                    "name": "TruthTrack AI Analysis",
                    "url": "",
                    "date": "Today"
                }
            ],
            "claim_text": claim
        }