import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline
import Levenshtein

class NewsRelevanceCalculator:
    def __init__(self):
        # Load BERT similarity pipeline
        self.bert_similarity = pipeline("feature-extraction", model="bert-base-uncased", tokenizer="bert-base-uncased")

    def calculate_relevance_score(self, claim: str, title: str, snippet: str) -> float:
        # Combine title and snippet for comparison
        news_text = f"{title}. {snippet}"

        # 1. Levenshtein Distance
        levenshtein_score = 1 - (Levenshtein.distance(claim, news_text) / max(len(claim), len(news_text)))

        # 2. Cosine Similarity
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([claim, news_text])
        cosine_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

        # 3. BERT Similarity
        claim_embedding = np.mean(self.bert_similarity(claim)[0], axis=0)
        news_embedding = np.mean(self.bert_similarity(news_text)[0], axis=0)
        bert_score = np.dot(claim_embedding, news_embedding) / (np.linalg.norm(claim_embedding) * np.linalg.norm(news_embedding))

        # Combine scores (weighted average)
        combined_score = (0.33 * levenshtein_score) + (0.33 * cosine_score) + (0.33 * bert_score)
        return combined_score