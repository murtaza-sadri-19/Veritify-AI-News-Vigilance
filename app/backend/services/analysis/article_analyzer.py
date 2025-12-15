#!/usr/bin/env python3
"""
Advanced News Article Analysis and Niche Categorization Pipeline

This script provides a comprehensive NLP pipeline for analyzing news articles,
extracting contextual information (location and genre), and categorizing them
into niche topics. Optimized for Indian Subcontinent news content.

Author: Expert Python Developer
Date: 2025
"""

import argparse
import json
import logging
import re
import sys
from typing import Dict, List, Optional, Tuple
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from transformers import pipeline
import warnings
warnings.filterwarnings("ignore")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class NewsArticleAnalyzer:
    """
    Advanced news article analyzer with NLP preprocessing, location extraction,
    genre classification, and niche topic inference.
    """

    def __init__(self):
        """Initialize the analyzer with required models and data."""
        self.nlp = self._load_spacy_model()
        self.classifier = self._load_zero_shot_classifier()
        self.indian_locations = self._load_indian_locations()
        self.genres = self._load_genres()
        self.news_stopwords = self._load_news_stopwords()

    def _load_spacy_model(self):
        """Load and configure spaCy model."""
        try:
            nlp = spacy.load("en_core_web_lg")
            logger.info("Loaded spaCy large model successfully")
            return nlp
        except OSError:
            try:
                nlp = spacy.load("en_core_web_sm")
                logger.warning("Large model not found, using small model")
                return nlp
            except OSError:
                logger.error("No spaCy English model found. Please install with: python -m spacy download en_core_web_sm")
                sys.exit(1)

    def _load_zero_shot_classifier(self):
        """Load zero-shot classification model."""
        try:
            classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=-1  # Use CPU
            )
            logger.info("Loaded zero-shot classifier successfully")
            return classifier
        except Exception as e:
            logger.error(f"Failed to load zero-shot classifier: {e}")
            sys.exit(1)

    def _load_indian_locations(self) -> Dict[str, int]:
        """Load Indian states, cities, and regions with priority weights."""
        return {
            # Major cities (highest priority)
            "mumbai": 10, "delhi": 10, "bangalore": 10, "kolkata": 10,
            "chennai": 10, "hyderabad": 10, "pune": 10, "ahmedabad": 10,
            "jaipur": 9, "lucknow": 9, "kanpur": 9, "nagpur": 9,
            "indore": 9, "bhopal": 9, "visakhapatnam": 9, "patna": 9,
            "vadodara": 8, "ghaziabad": 8, "ludhiana": 8, "agra": 8,
            "nashik": 8, "faridabad": 8, "meerut": 8, "rajkot": 8,

            # States (high priority)
            "maharashtra": 8, "uttar pradesh": 8, "bihar": 8, "west bengal": 8,
            "madhya pradesh": 8, "tamil nadu": 8, "rajasthan": 8, "karnataka": 8,
            "gujarat": 8, "andhra pradesh": 8, "odisha": 8, "telangana": 8,
            "kerala": 8, "jharkhand": 8, "assam": 8, "punjab": 8,
            "chhattisgarh": 8, "haryana": 8, "uttarakhand": 8, "himachal pradesh": 8,
            "tripura": 7, "meghalaya": 7, "manipur": 7, "nagaland": 7,
            "goa": 7, "arunachal pradesh": 7, "mizoram": 7, "sikkim": 7,

            # Union territories
            "delhi": 10, "puducherry": 7, "chandigarh": 7, "daman and diu": 6,
            "dadra and nagar haveli": 6, "lakshadweep": 6, "andaman and nicobar": 6,
            "ladakh": 7, "jammu and kashmir": 8,

            # Regions and general terms
            "north india": 6, "south india": 6, "east india": 6, "west india": 6,
            "northeast india": 6, "central india": 6, "kashmir": 7,

            # Country level
            "india": 5, "indian subcontinent": 4, "bharat": 5
        }

    def _load_genres(self) -> List[str]:
        """Load predefined genre categories."""
        return [
            "Politics",
            "Business & Finance",
            "Technology",
            "Sports",
            "Crime & Justice",
            "Health & Wellness",
            "Environment",
            "Entertainment",
            "Education",
            "National News",
            "World News"
        ]

    def _load_news_stopwords(self) -> set:
        """Load additional stopwords common in news articles."""
        news_specific = {
            "reportedly", "sources", "said", "according", "officials",
            "spokesperson", "statement", "press", "media", "news",
            "report", "reports", "reported", "citing", "quoted",
            "unnamed", "senior", "government", "ministry", "department"
        }
        return STOP_WORDS.union(news_specific)

    def preprocess_text(self, text: str) -> str:
        """
        Perform comprehensive NLP preprocessing on the input text.

        Args:
            text: Raw news article text

        Returns:
            Preprocessed text string
        """
        if not text or not text.strip():
            return ""

        # Process with spaCy
        doc = self.nlp(text)

        # Extract tokens with preprocessing
        processed_tokens = []
        for token in doc:
            # Skip punctuation, spaces, and stopwords
            if (token.is_punct or token.is_space or
                    token.text.lower() in self.news_stopwords or
                    len(token.text) < 2):
                continue

            # Use lemmatized form
            lemma = token.lemma_.lower()

            # Additional cleaning
            if lemma.isalpha() and lemma not in self.news_stopwords:
                processed_tokens.append(lemma)

        return " ".join(processed_tokens)

    def extract_location(self, text: str) -> str:
        """
        Extract primary geographical location from text using NER and heuristics.

        Args:
            text: News article text

        Returns:
            Primary location string
        """
        doc = self.nlp(text)

        # Extract all location entities
        location_entities = []
        for ent in doc.ents:
            if ent.label_ in ["GPE", "LOC", "PERSON"]:  # Include PERSON for place names
                location_entities.append(ent.text.lower().strip())

        # Score locations based on our Indian locations dictionary
        location_scores = {}

        for entity in location_entities:
            # Direct match
            if entity in self.indian_locations:
                location_scores[entity] = location_scores.get(entity, 0) + self.indian_locations[entity]

            # Partial match for compound names
            for indian_loc, score in self.indian_locations.items():
                if (indian_loc in entity or entity in indian_loc) and len(entity) > 3:
                    location_scores[entity] = location_scores.get(entity, 0) + score * 0.8

        # Additional scoring based on frequency and position
        text_lower = text.lower()
        first_paragraph = text_lower.split('\n')[0] if '\n' in text_lower else text_lower[:200]

        for location in location_scores:
            # Frequency bonus
            frequency = text_lower.count(location)
            location_scores[location] += frequency * 2

            # Position bonus (first paragraph gets higher weight)
            if location in first_paragraph:
                location_scores[location] += 5

        # Select best location
        if location_scores:
            best_location = max(location_scores, key=location_scores.get)

            # Normalize the location name
            for indian_loc in self.indian_locations:
                if indian_loc in best_location.lower() or best_location.lower() in indian_loc:
                    return indian_loc.title()

            return best_location.title()

        # Fallback strategy
        if any(term in text_lower for term in ["india", "indian", "delhi", "mumbai", "bangalore"]):
            return "India"

        return "Global"

    def classify_genre(self, text: str) -> str:
        """
        Classify article genre using zero-shot classification.

        Args:
            text: News article text

        Returns:
            Genre category string
        """
        try:
            # Truncate text if too long for the model
            max_length = 512
            if len(text) > max_length:
                text = text[:max_length]

            result = self.classifier(text, self.genres)

            # Return the highest scoring genre
            return result['labels'][0]

        except Exception as e:
            logger.warning(f"Genre classification failed: {e}")

            # Fallback to keyword-based classification
            return self._classify_genre_fallback(text)

    def _classify_genre_fallback(self, text: str) -> str:
        """
        Fallback genre classification using keyword matching.

        Args:
            text: News article text

        Returns:
            Genre category string
        """
        text_lower = text.lower()

        # Define keyword patterns for each genre
        genre_keywords = {
            "Politics": ["parliament", "election", "minister", "government", "bill", "mp", "mla",
                         "political", "party", "vote", "campaign", "policy", "cabinet"],
            "Business & Finance": ["stock", "market", "bse", "nse", "rbi", "gdp", "economy",
                                   "finance", "investment", "revenue", "profit", "rupee", "inflation"],
            "Technology": ["technology", "tech", "software", "app", "digital", "internet",
                           "ai", "startup", "innovation", "computer", "mobile", "data"],
            "Sports": ["cricket", "bcci", "ipl", "match", "player", "team", "game", "sport",
                       "score", "tournament", "olympics", "medal", "coach"],
            "Crime & Justice": ["police", "crime", "arrest", "court", "judge", "trial", "law",
                                "justice", "investigation", "accused", "victim", "case"],
            "Health & Wellness": ["health", "medical", "doctor", "hospital", "disease", "treatment",
                                  "medicine", "patient", "healthcare", "wellness", "covid"],
            "Environment": ["environment", "climate", "pollution", "green", "forest", "wildlife",
                            "conservation", "nature", "sustainability", "carbon", "emissions"],
            "Entertainment": ["film", "movie", "actor", "actress", "bollywood", "music", "song",
                              "entertainment", "celebrity", "show", "television", "artist"],
            "Education": ["education", "school", "college", "university", "student", "teacher",
                          "exam", "academic", "learning", "study", "degree", "admission"]
        }

        # Score each genre based on keyword presence
        genre_scores = {}
        for genre, keywords in genre_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                genre_scores[genre] = score

        if genre_scores:
            return max(genre_scores, key=genre_scores.get)

        # Default classification
        if any(term in text_lower for term in ["india", "indian", "national"]):
            return "National News"

        return "World News"

    def infer_niche_topic(self, genre: str, location: str) -> str:
        """
        Generate niche topic by combining genre and location.

        Args:
            genre: Article genre
            location: Article location

        Returns:
            Niche topic string
        """
        return f"{genre} - {location}"

    def analyze_article(self, article_text: str) -> Dict:
        """
        Perform complete analysis of a news article.

        Args:
            article_text: Raw news article text

        Returns:
            Dictionary with analysis results
        """
        if not article_text or not article_text.strip():
            logger.warning("Empty article provided")
            return {
                "original_article_text": article_text,
                "inferred_location": "Global",
                "inferred_genre": "World News",
                "niche_topic": "World News - Global"
            }

        try:
            # Extract location
            location = self.extract_location(article_text)
            logger.info(f"Extracted location: {location}")

            # Classify genre
            genre = self.classify_genre(article_text)
            logger.info(f"Classified genre: {genre}")

            # Generate niche topic
            niche_topic = self.infer_niche_topic(genre, location)

            return {
                "original_article_text": article_text,
                "inferred_location": location,
                "inferred_genre": genre,
                "niche_topic": niche_topic
            }

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {
                "original_article_text": article_text,
                "inferred_location": "Global",
                "inferred_genre": "World News",
                "niche_topic": "World News - Global"
            }


def main():
    """Main function to handle command-line execution."""
    parser = argparse.ArgumentParser(
        description="Advanced News Article Analysis and Niche Categorization Pipeline"
    )
    parser.add_argument(
        "article_text",
        help="News article text to analyze"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize analyzer
    logger.info("Initializing News Article Analyzer...")
    analyzer = NewsArticleAnalyzer()

    # Analyze article
    logger.info("Analyzing article...")
    result = analyzer.analyze_article(args.article_text)

    # Output result
    print(json.dumps(result, indent=2, ensure_ascii=False))

    return result


if __name__ == "__main__":
    # Example usage demonstration
    if len(sys.argv) == 1:
        # Demo mode with example article
        example_article = """
        The Reserve Bank of India, headquartered in Mumbai, today announced a surprise hike 
        in the repo rate by 25 basis points to curb inflation. This move is expected to 
        impact loan rates across the country. Financial experts in Mumbai and Delhi have 
        expressed mixed reactions to this monetary policy decision. The RBI Governor stated 
        that this measure is necessary to maintain price stability and support sustainable 
        economic growth in the current inflationary environment.
        """

        print("Demo Mode - Analyzing example article...")
        print("=" * 60)

        analyzer = NewsArticleAnalyzer()
        result = analyzer.analyze_article(example_article.strip())

        print(json.dumps(result, indent=2, ensure_ascii=False))

        print("\n" + "=" * 60)
        print("To analyze your own article, run:")
        print('python process_news.py "Your article text here"')
    else:
        main()