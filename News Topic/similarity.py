from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from difflib import SequenceMatcher
from sentence_transformers import SentenceTransformer
import numpy as np

print("Enter the first paragraph:")
para1 = input().strip()

print("Enter the second paragraph:")
para2 = input().strip()

# 1. Preprocessing and Cosine Similarity (TF-IDF)
print("\n=== TF-IDF Cosine Similarity ===")
tfidf = TfidfVectorizer()
tfidf_matrix = tfidf.fit_transform([para1, para2])
cosine_sim = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]
print(f"Cosine Similarity (TF-IDF): {cosine_sim:.4f}")

# 2. Levenshtein Distance
print("\n=== Levenshtein Distance ===")
levenshtein_sim = SequenceMatcher(None, para1, para2).ratio()
print(f"Levenshtein Similarity: {levenshtein_sim:.4f}")

# 3. Semantic Matching with Sentence Transformers
print("\n=== Semantic Similarity with Sentence Transformers ===")
model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight model
emb1 = model.encode(para1, normalize_embeddings=True)
emb2 = model.encode(para2, normalize_embeddings=True)
bert_cosine_sim = cosine_similarity([emb1], [emb2])[0][0]
print(f"Cosine Similarity (Sentence Transformers): {bert_cosine_sim:.4f}")

# 4. Harmonic Mean of All Similarity Measures
hm_all = 3 / (1/cosine_sim + 1/levenshtein_sim + 1/bert_cosine_sim)
print(f"\n=== Harmonic Mean (TF-IDF, Levenshtein, BERT) ===")
print(f"Harmonic Mean: {hm_all:.4f}")
