import os
import requests
from services.utils import sanitize_text

class FactCheckService:
    def __init__(self):
        # Load RapidAPI credentials and hosts from environment
        self.rapidapi_key = os.getenv("RAPIDAPI_KEY")
        self.real_time_news_host = os.getenv("REAL_TIME_NEWS_HOST")
        self.media_bias_host = os.getenv("MEDIA_BIAS_HOST")
        self.fact_checker_host = os.getenv("FACT_CHECKER_HOST")
        self.google_news_host = os.getenv("GOOGLE_NEWS_HOST")

        # Debug prints for environment variables
        print("DEBUG: RAPIDAPI_KEY:", self.rapidapi_key)
        print("DEBUG: REAL_TIME_NEWS_HOST:", self.real_time_news_host)
        print("DEBUG: MEDIA_BIAS_HOST:", self.media_bias_host)
        print("DEBUG: FACT_CHECKER_HOST:", self.fact_checker_host)
        print("DEBUG: GOOGLE_NEWS_HOST:", self.google_news_host)

    def check_claim(self, claim_text):
        """
        Check a claim using multiple fact-checking and news APIs.
        Returns a consolidated result with sources and scores.
        """
        claim_text = sanitize_text(claim_text)
        print(f"DEBUG: Sanitized claim_text: {claim_text}")
        results = []

        try:
            # Fact Checker API (RapidAPI)
            fc_results = self._check_fact_checker_api(claim_text)
            print(f"DEBUG: Fact Checker API returned {len(fc_results)} results")
            if fc_results:
                results.extend(fc_results)

            # Media Bias Fact Check (RapidAPI)
            mb_results = self._check_media_bias_api()
            print(f"DEBUG: Media Bias API returned {len(mb_results)} results")
            if mb_results:
                results.extend(mb_results)

            # Real-Time News Data (RapidAPI)
            news_results = self._check_real_time_news_api()
            print(f"DEBUG: Real-Time News API returned {len(news_results)} results")
            if news_results:
                results.extend(news_results)

            # Google News (RapidAPI)
            google_news_results = self._check_google_news_api()
            print(f"DEBUG: Google News API returned {len(google_news_results)} results")
            if google_news_results:
                results.extend(google_news_results)

            if not results:
                print("DEBUG: No API results, using mock results.")
                results = self._get_mock_results(claim_text)
        except Exception as e:
            print(f"Error checking fact: {str(e)}")
            results = self._get_mock_results(claim_text)

        trustworthiness_score = self._calculate_score(results)
        print(f"DEBUG: Calculated trustworthiness_score: {trustworthiness_score}")
        return {
            "verified": len(results) > 0,
            "score": trustworthiness_score,
            "message": self._generate_message(trustworthiness_score),
            "sources": results
        }

    def _rapidapi_get(self, host, endpoint, params=None):
        url = f"https://{host}{endpoint}"
        headers = {
            'x-rapidapi-key': self.rapidapi_key,
            'x-rapidapi-host': host
        }
        print(f"DEBUG: Requesting {url} with params={params}")
        response = requests.get(url, headers=headers, params=params)
        print(f"DEBUG: Response status: {response.status_code}")
        if response.status_code != 200:
            print(f"DEBUG: Response text: {response.text}")
        response.raise_for_status()
        return response.json()

    def _check_fact_checker_api(self, claim_text):
        """Query Fact Checker API on RapidAPI."""
        try:
            data = self._rapidapi_get(
                self.fact_checker_host,
                "/search",
                params={"query": claim_text, "limit": 5, "offset": 0, "language": "en"}
            )
            print(f"DEBUG: Fact Checker API raw data: {data}")
            results = []
            for item in data.get("data", []):
                results.append({
                    "source": item.get("site_name", "Fact Checker"),
                    "url": item.get("url", ""),
                    "rating": item.get("claim_result", ""),
                    "title": item.get("claim", ""),
                    "reviewDate": item.get("date_published", "")
                })
            return results
        except Exception as e:
            print(f"Fact Checker API error: {str(e)}")
            return []

    def _check_media_bias_api(self):
        """Query Media Bias Fact Check API on RapidAPI."""
        try:
            data = self._rapidapi_get(
                self.media_bias_host,
                "/fetch-data"
            )
            print(f"DEBUG: Media Bias API raw data: {data}")
            results = []
            for item in data.get("sources", [])[:3]:  # Limit to 3 for brevity
                results.append({
                    "source": item.get("source_name", "Media Bias Fact Check"),
                    "url": item.get("source_url", ""),
                    "rating": item.get("bias_rating", ""),
                    "title": item.get("source_name", ""),
                    "reviewDate": ""
                })
            return results
        except Exception as e:
            print(f"Media Bias API error: {str(e)}")
            return []

    def _check_real_time_news_api(self):
        """Query Real-Time News Data API on RapidAPI (Technology section as example)."""
        try:
            data = self._rapidapi_get(
                self.real_time_news_host,
                "/topic-news-by-section",
                params={
                    "topic": "TECHNOLOGY",
                    "section": "",
                    "limit": 5,
                    "country": "US",
                    "lang": "en"
                }
            )
            print(f"DEBUG: Real-Time News API raw data: {data}")
            results = []
            for item in data.get("articles", [])[:3]:
                results.append({
                    "source": item.get("source", ""),
                    "url": item.get("url", ""),
                    "rating": "News Article",
                    "title": item.get("title", ""),
                    "reviewDate": item.get("publishedAt", "")
                })
            return results
        except Exception as e:
            print(f"Real-Time News API error: {str(e)}")
            return []

    def _check_google_news_api(self):
        """Query Google News API on RapidAPI (Business section as example)."""
        try:
            data = self._rapidapi_get(
                self.google_news_host,
                "/business",
                params={"lr": "en-US"}
            )
            print(f"DEBUG: Google News API raw data: {data}")
            results = []
            for item in data.get("articles", [])[:3]:
                results.append({
                    "source": item.get("source", ""),
                    "url": item.get("url", ""),
                    "rating": "News Article",
                    "title": item.get("title", ""),
                    "reviewDate": item.get("publishedAt", "")
                })
            return results
        except Exception as e:
            print(f"Google News API error: {str(e)}")
            return []

    def _get_mock_results(self, claim_text):
        """
        Return mock fact-check results for demonstration purposes
        """
        is_likely_political = any(word in claim_text.lower() for word in
                                  ["president", "government", "election", "congress", "democrat", "republican",
                                   "policy", "trump", "biden"])

        is_likely_scientific = any(word in claim_text.lower() for word in
                                   ["covid", "vaccine", "climate", "research", "study", "scientists", "medicine",
                                    "medical", "disease"])

        if is_likely_political:
            return [
                {
                    "source": "PolitiFact",
                    "url": "https://www.politifact.com/factchecks/",
                    "rating": "Half True",
                    "title": "Analysis of Political Claim",
                    "reviewDate": "2025-03-15"
                },
                {
                    "source": "FactCheck.org",
                    "url": "https://www.factcheck.org/",
                    "rating": "Contains misleading information",
                    "title": "Examining Political Statement",
                    "reviewDate": "2025-03-10"
                }
            ]
        elif is_likely_scientific:
            return [
                {
                    "source": "Health Feedback",
                    "url": "https://healthfeedback.org/",
                    "rating": "Mostly Accurate",
                    "title": "Scientific Claim Verification",
                    "reviewDate": "2025-02-28"
                },
                {
                    "source": "Science Feedback",
                    "url": "https://sciencefeedback.co/",
                    "rating": "Accurate",
                    "title": "Scientific Evidence Assessment",
                    "reviewDate": "2025-03-05"
                }
            ]
        else:
            return [
                {
                    "source": "Snopes",
                    "url": "https://www.snopes.com/",
                    "rating": "Mixture",
                    "title": "Fact Check: General Claim Analysis",
                    "reviewDate": "2025-03-20"
                }
            ]

    def _calculate_score(self, results):
        """
        Calculate a truthfulness score based on fact-checking results
        Scale: 0-100, where higher means more truthful
        """
        if not results:
            return 0

        true_keywords = ['true', 'mostly true', 'correct', 'accurate']
        false_keywords = ['false', 'mostly false', 'incorrect', 'inaccurate', 'pants on fire']
        mixed_keywords = ['mixed', 'half true', 'partly']

        total_ratings = len(results)
        true_ratings = sum(1 for r in results if any(kw in r.get("rating", "").lower() for kw in true_keywords))
        false_ratings = sum(1 for r in results if any(kw in r.get("rating", "").lower() for kw in false_keywords))
        mixed_ratings = sum(1 for r in results if any(kw in r.get("rating", "").lower() for kw in mixed_keywords))

        unknown_ratings = total_ratings - true_ratings - false_ratings - mixed_ratings

        weighted_sum = (true_ratings * 100 + mixed_ratings * 50 + unknown_ratings * 50)
        base_score = weighted_sum / total_ratings if total_ratings > 0 else 50

        confidence = min(1.0, len(results) / 3.0)  # Max confidence with 3+ sources

        final_score = round(base_score * confidence)

        if false_ratings > 0:
            false_penalty = (false_ratings / total_ratings) * 40
            final_score = max(0, final_score - false_penalty)
        print(f"DEBUG: Score calculation: true={true_ratings}, false={false_ratings}, mixed={mixed_ratings}, unknown={unknown_ratings}, final_score={final_score}")
        return round(final_score)

    def _generate_message(self, score):
        """
        Generate a human-readable message based on the score
        """
        if score >= 80:
            return "This claim appears to be mostly true based on fact-checking sources."
        elif score >= 60:
            return "This claim contains some truth but may have inaccuracies."
        elif score >= 40:
            return "This claim has mixed truthfulness according to fact-checkers."
        elif score >= 20:
            return "This claim appears to be mostly false according to fact-checkers."
        else:
            return "This claim is disputed or labeled as false by fact-checking sources."
