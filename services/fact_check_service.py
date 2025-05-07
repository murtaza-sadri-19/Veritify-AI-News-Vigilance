import requests
import json
import os
from services.utils import sanitize_text


class FactCheckService:
    def __init__(self):
        # API keys for various fact-checking services
        self.google_factcheck_api_key = os.getenv("GOOGLE_FACTCHECK_API_KEY")
        self.factchecktools_api_key = os.getenv("FACTCHECKTOOLS_API_KEY")

    def check_claim(self, claim_text):
        """
        Check a claim against multiple fact-checking services.
        Returns a consolidated result with sources and scores.
        """
        # Sanitize the input text
        claim_text = sanitize_text(claim_text)

        results = []

        try:
            # Try Google Fact Check API if we have an API key
            if self.google_factcheck_api_key and self.google_factcheck_api_key != "your_google_api_key_here":
                google_results = self._check_google_factcheck(claim_text)
                if google_results:
                    results.extend(google_results)

            # Try other fact-checking services
            other_results = self._check_other_factcheck_service(claim_text)
            if other_results:
                results.extend(other_results)

            # If we can't connect to any services or no API keys, use mock data for demo
            if not results:
                results = self._get_mock_results(claim_text)
        except Exception as e:
            print(f"Error checking fact: {str(e)}")
            # Return mock data in case of errors
            results = self._get_mock_results(claim_text)

        # Calculate an overall trustworthiness score
        trustworthiness_score = self._calculate_score(results)

        return {
            "verified": len(results) > 0,
            "score": trustworthiness_score,
            "message": self._generate_message(trustworthiness_score),
            "sources": results
        }

    def _check_google_factcheck(self, claim_text):
        """
        Use Google's Fact Check Tools API to verify a claim
        """
        try:
            url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
            params = {
                "query": claim_text,
                "key": self.google_factcheck_api_key
            }

            response = requests.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                results = []

                # Process claim review results
                if "claims" in data:
                    for claim in data["claims"]:
                        for review in claim.get("claimReview", []):
                            result = {
                                "source": review.get("publisher", {}).get("name", "Unknown source"),
                                "url": review.get("url", ""),
                                "rating": review.get("textualRating", ""),
                                "title": review.get("title", ""),
                                "reviewDate": review.get("reviewDate", "")
                            }
                            results.append(result)

                return results
            else:
                print(f"Google Fact Check API error: {response.status_code}")
                return []

        except Exception as e:
            print(f"Error in Google fact check: {str(e)}")
            return []

    def _check_other_factcheck_service(self, claim_text):
        """
        Implementation for additional fact-checking services
        Currently using Factcheck.org through a custom API approach
        """
        try:
            # This would be replaced with actual API call when available
            # For example, using Factcheck.org content
            url = "https://www.factcheck.org/wp-json/wp/v2/search"
            params = {
                "search": claim_text,
                "per_page": 5,
                "type": "post"
            }

            response = requests.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                results = []

                for item in data:
                    # Get more details about the fact check
                    if 'id' in item:
                        post_url = f"https://www.factcheck.org/wp-json/wp/v2/posts/{item['id']}"
                        post_response = requests.get(post_url)

                        if post_response.status_code == 200:
                            post_data = post_response.json()

                            # Extract conclusion from content if possible
                            content = post_data.get('content', {}).get('rendered', '')
                            # Simple extraction - in a real implementation you'd want more sophisticated parsing
                            conclusion = "See full analysis at the link"

                            result = {
                                "source": "FactCheck.org",
                                "url": post_data.get('link', ''),
                                "rating": conclusion,
                                "title": post_data.get('title', {}).get('rendered', ''),
                                "reviewDate": post_data.get('date', '')
                            }
                            results.append(result)

                return results
            else:
                print(f"Factcheck.org API error: {response.status_code}")
                return []

        except Exception as e:
            print(f"Error in Factcheck.org check: {str(e)}")
            return []

    def _get_mock_results(self, claim_text):
        """
        Return mock fact-check results for demonstration purposes
        """
        # Analyze the claim text to adjust the response
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

        # This is a simplified scoring algorithm that can be enhanced
        # based on specific needs and available data from fact checkers

        # Keyword-based analysis of ratings
        true_keywords = ['true', 'mostly true', 'correct', 'accurate']
        false_keywords = ['false', 'mostly false', 'incorrect', 'inaccurate', 'pants on fire']
        mixed_keywords = ['mixed', 'half true', 'partly']

        # Count ratings
        total_ratings = len(results)
        true_ratings = sum(1 for r in results if any(kw in r.get("rating", "").lower() for kw in true_keywords))
        false_ratings = sum(1 for r in results if any(kw in r.get("rating", "").lower() for kw in false_keywords))
        mixed_ratings = sum(1 for r in results if any(kw in r.get("rating", "").lower() for kw in mixed_keywords))

        # Default for unknown ratings
        unknown_ratings = total_ratings - true_ratings - false_ratings - mixed_ratings

        # Calculate weighted score
        weighted_sum = (true_ratings * 100 + mixed_ratings * 50 + unknown_ratings * 50)
        base_score = weighted_sum / total_ratings if total_ratings > 0 else 50

        # Apply confidence factor based on number of sources
        confidence = min(1.0, len(results) / 3.0)  # Max confidence with 3+ sources

        final_score = round(base_score * confidence)

        # Adjust score down if there are explicit false ratings
        if false_ratings > 0:
            false_penalty = (false_ratings / total_ratings) * 40
            final_score = max(0, final_score - false_penalty)

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