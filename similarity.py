from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from difflib import SequenceMatcher
from sentence_transformers import SentenceTransformer

def calculate_similarity(para1, para2):
    """
    Calculate various similarity metrics between two paragraphs.

    Args:
        para1 (str): First paragraph.
        para2 (str): Second paragraph.

    Returns:
        dict: A dictionary containing similarity scores.
    """
    results = {}

    # 1. Preprocessing and Cosine Similarity (TF-IDF)
    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform([para1, para2])
    cosine_sim = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]
    results['cosine_similarity_tfidf'] = cosine_sim

    # 2. Levenshtein Distance
    levenshtein_sim = SequenceMatcher(None, para1, para2).ratio()
    results['levenshtein_similarity'] = levenshtein_sim

    # 3. Semantic Matching with Sentence Transformers
    model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight model
    emb1 = model.encode(para1, normalize_embeddings=True)
    emb2 = model.encode(para2, normalize_embeddings=True)
    bert_cosine_sim = cosine_similarity([emb1], [emb2])[0][0]
    results['cosine_similarity_bert'] = bert_cosine_sim

    # 4. Harmonic Mean of All Similarity Measures
    hm_all = 3 / (1/cosine_sim + 1/levenshtein_sim + 1/bert_cosine_sim)
    results['harmonic_mean'] = hm_all

    return results
