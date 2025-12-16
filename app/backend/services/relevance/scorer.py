import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline
import Levenshtein
import logging
import os

logger = logging.getLogger(__name__)

class NewsRelevanceCalculator:
    _instance = None
    _bert_model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Load BERT similarity pipeline only once (singleton pattern)
        if NewsRelevanceCalculator._bert_model is None:
            try:
                logger.info("Loading BERT model for relevance scoring...")
                NewsRelevanceCalculator._bert_model = pipeline(
                    "feature-extraction", 
                    model="bert-base-uncased", 
                    tokenizer="bert-base-uncased"
                )
                logger.info("BERT model loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load BERT model: {e}. Will use fallback scoring.")
                NewsRelevanceCalculator._bert_model = None

    def calculate_relevance_score(self, claim: str, title: str, snippet: str = "", source_credibility: float = 0.5) -> float:
        """
        Calculate relevance score between claim and news article with credibility weighting.
        Uses Levenshtein distance, TF-IDF cosine similarity, and BERT embeddings.
        Returns score between 0.0 and 1.0.
        
        Args:
            claim: The claim text
            title: Article title
            snippet: Article snippet/summary
            source_credibility: Credibility score of the news source (0.0 - 1.0), default 0.5 for unknown sources
        """
        try:
            if not claim or not title:
                return 0.0
            
            # Combine title and snippet for comparison
            news_text = f"{title}. {snippet}" if snippet else title

            # 1. Levenshtein Distance (string similarity)
            try:
                max_len = max(len(claim), len(news_text))
                if max_len > 0:
                    levenshtein_score = 1 - (Levenshtein.distance(claim, news_text) / max_len)
                else:
                    levenshtein_score = 0.0
            except Exception as e:
                logger.debug(f"Levenshtein scoring failed: {e}")
                levenshtein_score = 0.0

            # 2. Cosine Similarity (TF-IDF)
            try:
                vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
                tfidf_matrix = vectorizer.fit_transform([claim, news_text])
                cosine_score = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0])
            except Exception as e:
                logger.debug(f"TF-IDF cosine similarity failed: {e}")
                cosine_score = 0.0

            # 3. BERT Similarity (semantic embeddings)
            bert_score = 0.0
            if NewsRelevanceCalculator._bert_model is not None:
                try:
                    # Truncate to avoid BERT input length issues
                    claim_truncated = claim[:512]
                    news_truncated = news_text[:512]
                    
                    claim_embedding = np.mean(
                        NewsRelevanceCalculator._bert_model(claim_truncated)[0], 
                        axis=0
                    )
                    news_embedding = np.mean(
                        NewsRelevanceCalculator._bert_model(news_truncated)[0], 
                        axis=0
                    )
                    
                    norm_a = np.linalg.norm(claim_embedding)
                    norm_b = np.linalg.norm(news_embedding)
                    
                    if norm_a > 0 and norm_b > 0:
                        bert_score = float(np.dot(claim_embedding, news_embedding) / (norm_a * norm_b))
                        # Normalize from [-1, 1] to [0, 1]
                        bert_score = (bert_score + 1.0) / 2.0
                except Exception as e:
                    logger.debug(f"BERT similarity failed: {e}")
                    bert_score = 0.0

            # Combine scores (weighted average)
            # Weights: Levenshtein 0.2, TF-IDF 0.3, BERT 0.5
            # These weights can be overridden via environment variables
            try:
                w_lev = float(os.getenv("RELEVANCE_WEIGHT_LEVENSHTEIN", "0.2"))
                w_tfidf = float(os.getenv("RELEVANCE_WEIGHT_TFIDF", "0.3"))
                w_bert = float(os.getenv("RELEVANCE_WEIGHT_BERT", "0.5"))
                # Normalize weights
                total_weight = w_lev + w_tfidf + w_bert
                if total_weight > 0:
                    w_lev /= total_weight
                    w_tfidf /= total_weight
                    w_bert /= total_weight
            except ValueError:
                w_lev, w_tfidf, w_bert = 0.2, 0.3, 0.5
            
            combined_score = (w_lev * levenshtein_score) + (w_tfidf * cosine_score) + (w_bert * bert_score)
            
            # Apply credibility weighting to the combined semantic relevance score
            # This ensures credible sources are prioritized in fact-checking context
            try:
                weight_relevance = float(os.getenv("SCORE_WEIGHT_RELEVANCE", "0.4"))
                weight_credibility = float(os.getenv("SCORE_WEIGHT_CREDIBILITY", "0.6"))
                # Normalize weights
                total_weight = weight_relevance + weight_credibility
                if total_weight > 0:
                    weight_relevance /= total_weight
                    weight_credibility /= total_weight
            except ValueError:
                weight_relevance = 0.4
                weight_credibility = 0.6
            
            # Final score: semantic relevance + credibility weighting
            # For fact-checking, credible sources are more important
            credibility_adjusted_score = (weight_relevance * combined_score) + (weight_credibility * source_credibility)
            
            # Ensure score is in valid range
            credibility_adjusted_score = float(np.clip(credibility_adjusted_score, 0.0, 1.0))
            
            logger.debug(
                f"Relevance scores - Lev:{levenshtein_score:.3f} TF-IDF:{cosine_score:.3f} "
                f"BERT:{bert_score:.3f} Semantic:{combined_score:.3f} Credibility:{source_credibility:.3f} "
                f"Final:{credibility_adjusted_score:.3f}"
            )
            
            return credibility_adjusted_score
            
        except Exception as e:
            logger.error(f"Unexpected error in relevance calculation: {e}")
            return 0.0
