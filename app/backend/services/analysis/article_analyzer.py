#!/usr/bin/env python3
"""
Lightweight News Article Analyzer

This module now focuses only on:
- Text normalization
- Optional entity extraction
- Optional topic/genre detection
It must NOT decide truth.
"""

import logging
from typing import Dict, List, Optional

import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from transformers import pipeline

from ..utils.text import sanitize_text, safe_truncate

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# ── Global model loading (once) ─────────────────────────────────────

_SPACY_NLP = None
_ZERO_SHOT = None


def _load_spacy_model() -> Optional[spacy.language.Language]:
    global _SPACY_NLP
    if _SPACY_NLP is not None:
        return _SPACY_NLP
    try:
        _SPACY_NLP = spacy.load("en_core_web_sm")
        logger.info("Loaded spaCy model for article analysis")
    except OSError as e:
        logger.warning(f"spaCy model not available, entity extraction disabled: {e}")
        _SPACY_NLP = None
    return _SPACY_NLP


def _load_zero_shot_classifier():
    global _ZERO_SHOT
    if _ZERO_SHOT is not None:
        return _ZERO_SHOT
    try:
        _ZERO_SHOT = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=-1,  # CPU
        )
        logger.info("Loaded zero-shot classifier for genre explanation")
    except Exception as e:
        logger.warning(f"Failed to load zero-shot classifier; falling back to rules: {e}")
        _ZERO_SHOT = None
    return _ZERO_SHOT


class NewsArticleAnalyzer:
    """
    Reduced, focused analyzer:
    - No truth decision
    - Only light NLP helpers
    """

    def __init__(self) -> None:
        self.nlp = _load_spacy_model()
        self.classifier = _load_zero_shot_classifier()
        self.genres = self._load_genres()
        self.news_stopwords = self._load_news_stopwords()

    @staticmethod
    def _load_genres() -> List[str]:
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
            "World News",
        ]

    @staticmethod
    def _load_news_stopwords() -> set:
        news_specific = {
            "reportedly", "sources", "said", "according", "officials",
            "spokesperson", "statement", "press", "media", "news",
            "report", "reports", "reported", "citing", "quoted",
            "unnamed", "senior", "government", "ministry", "department",
        }
        return STOP_WORDS.union(news_specific)

    # ── Text normalization ─────────────────────────────────────────

    def normalize(self, text: str) -> str:
        text = sanitize_text(text)
        text = safe_truncate(text, max_length=4000)
        return text

    def preprocess_text(self, text: str) -> str:
        """
        Lightweight preprocessing for possible future lexical operations.
        """
        text = self.normalize(text)
        if not text or not self.nlp:
            return text

        doc = self.nlp(text)
        tokens = []
        for token in doc:
            if (
                token.is_punct
                or token.is_space
                or token.text.lower() in self.news_stopwords
                or len(token.text) < 2
            ):
                continue
            lemma = token.lemma_.lower()
            if lemma.isalpha() and lemma not in self.news_stopwords:
                tokens.append(lemma)
        return " ".join(tokens)

    # ── Optional entity extraction ─────────────────────────────────

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Basic entity extraction for UI context; no scoring.
        """
        if not self.nlp or not text:
            return {"PERSON": [], "ORG": [], "GPE": []}

        doc = self.nlp(text)
        entities: Dict[str, List[str]] = {"PERSON": [], "ORG": [], "GPE": []}
        for ent in doc.ents:
            if ent.label_ in entities:
                entities[ent.label_].append(ent.text)
        return entities

    # ── Optional topic/genre detection (for UI) ────────────────────

    def classify_genre(self, text: str) -> str:
        """
        Optional zero-shot genre classification.
        Used for explanation only, not for scoring.
        """
        text = self.normalize(text)
        if not text:
            return "World News"

        classifier = self.classifier
        if classifier is None:
            return self._classify_genre_fallback(text)

        try:
            truncated = safe_truncate(text, max_length=1024)
            result = classifier(truncated, self.genres)
            return result["labels"][0]
        except Exception as e:
            logger.warning(f"Zero-shot genre classification failed: {e}")
            return self._classify_genre_fallback(text)

    @staticmethod
    def _classify_genre_fallback(text: str) -> str:
        text_lower = text.lower()
        genre_keywords = {
            "Politics": ["parliament", "election", "minister", "government", "bill", "policy", "party"],
            "Business & Finance": ["stock", "market", "gdp", "economy", "finance", "investment", "revenue"],
            "Technology": ["technology", "software", "startup", "ai", "data", "digital", "app"],
            "Sports": ["match", "team", "cricket", "tournament", "score", "coach", "league"],
            "Crime & Justice": ["police", "crime", "arrest", "court", "trial", "case", "investigation"],
            "Health & Wellness": ["health", "hospital", "doctor", "vaccine", "covid", "disease", "medical"],
            "Environment": ["climate", "pollution", "forest", "wildlife", "carbon", "emissions", "environment"],
            "Entertainment": ["film", "movie", "actor", "music", "bollywood", "series", "celebrity"],
            "Education": ["school", "college", "university", "student", "exam", "education"],
        }

        scores: Dict[str, int] = {}
        for genre, keywords in genre_keywords.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[genre] = score

        if scores:
            return max(scores, key=scores.get)

        if any(term in text_lower for term in ["india", "indian", "national"]):
            return "National News"
        return "World News"