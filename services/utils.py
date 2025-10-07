import re
import html
import os
from typing import List, Optional
from difflib import SequenceMatcher
from datetime import datetime
import math

# Global model cache - initialized once, reused for all calculations
_sem_model = None
_sem_model_type = None
_model_initialized = False


def initialize_semantic_model():
    """Initialize semantic similarity model once at startup"""
    global _sem_model, _sem_model_type, _model_initialized
    
    if _model_initialized:
        return
    
    try:
        # Try sentence-transformers first (fastest and most accurate)
        from sentence_transformers import SentenceTransformer
        _sem_model = SentenceTransformer('all-MiniLM-L6-v2')
        _sem_model_type = 'sbert'
        print("✓ Loaded sentence-transformers model")
    except Exception:
        # Fallback to spaCy
        try:
            import spacy
            try:
                _sem_model = spacy.load('en_core_web_md')  # Medium model is faster
                print("✓ Loaded spaCy medium model")
            except Exception:
                _sem_model = spacy.load('en_core_web_sm')
                print("✓ Loaded spaCy small model")
            _sem_model_type = 'spacy'
        except Exception:
            _sem_model = None
            _sem_model_type = 'none'
            print("⚠ No semantic model available, using keyword matching only")
    
    _model_initialized = True


def sanitize_text(text: str) -> str:
    """Sanitize input text to prevent security issues and improve matching quality"""
    if not text:
        return ""
    
    text = re.sub(r'<[^>]+>', '', text)
    text = html.unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    if len(text) > 500:
        text = text[:497] + '...'
    
    return text


def extract_entities(text: str) -> List[str]:
    """Extract important entities (people, organizations, places) from text"""
    if not text:
        return []
    
    entities = []
    
    # People with titles
    people_pattern = r'(Mr\.|Mrs\.|Ms\.|Dr\.|President|Senator|Governor|Prime Minister)\s+([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)'
    people_matches = re.findall(people_pattern, text)
    entities.extend([f"{title} {name}".strip() for title, name in people_matches])
    
    # Simple names
    name_pattern = r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b'
    name_matches = re.findall(name_pattern, text)
    entities.extend(name_matches)
    
    # Organizations
    org_pattern = r'\b([A-Z][A-Za-z]*(?:\s+[A-Z][A-Za-z]*){1,3})\b'
    org_matches = re.findall(org_pattern, text)
    
    common_words = {'The', 'And', 'Of', 'In', 'On', 'At', 'To', 'For', 'With', 'By'}
    for org in org_matches:
        words = org.split()
        if len(words) >= 2 and not any(word in common_words for word in words):
            entities.append(org)
    
    return list(set(entities))


def get_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract important keywords from the text"""
    if not text:
        return []
    
    stopwords = {
        'the', 'a', 'an', 'and', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
        'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
        'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
    }
    
    text_lower = text.lower()
    text_clean = re.sub(r'[^\w\s-]', ' ', text_lower)
    words = text_clean.split()
    
    filtered_words = []
    for word in words:
        if (len(word) > 3 and word not in stopwords and 
            not word.isdigit() and not re.match(r'^\d+$', word)):
            filtered_words.append(word)
    
    word_counts = {}
    for word in filtered_words:
        word_counts[word] = word_counts.get(word, 0) + 1
    
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    return [word for word, count in sorted_words[:max_keywords]]


def _cosine_similarity(a, b):
    """Fast cosine similarity calculation"""
    try:
        import numpy as np
        a = np.array(a, dtype=float)
        b = np.array(b, dtype=float)
        denom = (np.linalg.norm(a) * np.linalg.norm(b))
        if denom == 0:
            return 0.0
        return float(np.dot(a, b) / denom)
    except Exception:
        return 0.0


def calculate_semantic_similarity(claim_text: str, article_text: str) -> float:
    """
    Calculate semantic similarity using pre-loaded model.
    Returns score between 0.0 and 1.0.
    """
    global _sem_model, _sem_model_type
    
    # Initialize model if not done yet
    if not _model_initialized:
        initialize_semantic_model()
    
    semantic_sim = 0.0
    
    try:
        if _sem_model_type == 'sbert' and _sem_model:
            # Batch encoding is faster
            embeddings = _sem_model.encode([claim_text, article_text], 
                                          convert_to_numpy=True,
                                          show_progress_bar=False)
            semantic_sim = _cosine_similarity(embeddings[0], embeddings[1])
            
        elif _sem_model_type == 'spacy' and _sem_model:
            doc1 = _sem_model(claim_text)
            doc2 = _sem_model(article_text)
            try:
                semantic_sim = float(doc1.similarity(doc2))
            except Exception:
                semantic_sim = _cosine_similarity(doc1.vector, doc2.vector)
        else:
            # Fallback to basic text overlap
            claim_words = set(claim_text.lower().split())
            article_words = set(article_text.lower().split())
            if claim_words:
                overlap = len(claim_words.intersection(article_words))
                semantic_sim = overlap / len(claim_words)
    except Exception as e:
        print(f"Semantic similarity error: {e}")
        semantic_sim = 0.0
    
    return max(0.0, min(1.0, semantic_sim))


def calculate_relevance_score(claim: str, title: str, description: str = "", 
                              published: str = None) -> float:
    """
    Calculate relevance score between a claim and news article.
    Returns score between 0.0 and 1.0.
    
    OPTIMIZED VERSION with:
    - Balanced weights for fact-checking
    - Fast computation
    - Proper bounds checking
    """
    if not claim or not title:
        return 0.0
    
    claim_text = sanitize_text(claim)
    article_text = sanitize_text(f"{title}. {description}")
    
    # 1. KEYWORD MATCHING (Fast and important for fact-checking)
    claim_keywords = set(get_keywords(claim_text, 15))
    article_keywords = set(get_keywords(article_text, 20))
    keyword_score = 0.0
    if claim_keywords:
        common_keywords = claim_keywords.intersection(article_keywords)
        keyword_score = len(common_keywords) / len(claim_keywords)
    
    # 2. ENTITY MATCHING (Critical for fact-checking)
    claim_entities = set(extract_entities(claim))
    article_entities = set(extract_entities(article_text))
    entity_score = 0.0
    if claim_entities:
        common_entities = claim_entities.intersection(article_entities)
        entity_score = len(common_entities) / len(claim_entities)
    
    # 3. SEMANTIC SIMILARITY (Context understanding)
    semantic_sim = calculate_semantic_similarity(claim_text, article_text)
    
    # 4. RECENCY SCORE (Recent articles more relevant for verification)
    recency_score = 0.5  # Default neutral
    if published:
        try:
            # Parse publication date
            pub_dt = None
            try:
                pub_dt = datetime.fromisoformat(published.replace('Z', '+00:00'))
            except Exception:
                formats = [
                    "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S",
                    "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"
                ]
                for fmt in formats:
                    try:
                        pub_dt = datetime.strptime(published, fmt)
                        break
                    except Exception:
                        continue
            
            if pub_dt:
                now = datetime.utcnow()
                delta = abs((now - pub_dt.replace(tzinfo=None)).total_seconds())
                days = delta / 86400.0
                
                # Exponential decay (14-day half-life)
                decay_days = float(os.getenv('NEWS_RECENCY_DECAY_DAYS', '14'))
                recency_score = math.exp(-days / max(1.0, decay_days))
                recency_score = max(0.0, min(1.0, recency_score))
        except Exception:
            recency_score = 0.5
    
    # BALANCED WEIGHTS FOR FACT-CHECKING
    # These weights are optimized for fact verification accuracy
    w_sem = 0.35      # Semantic understanding (moderate weight)
    w_kw = 0.25       # Keyword matching (high - specific terms matter)
    w_ent = 0.25      # Entity matching (high - names/orgs critical)
    w_rec = 0.15      # Recency (moderate - recent is better but not critical)
    
    final_score = (
        w_sem * semantic_sim +
        w_kw * keyword_score +
        w_ent * entity_score +
        w_rec * recency_score
    )
    
    # Ensure score is strictly bounded [0.0, 1.0]
    final_score = max(0.0, min(1.0, final_score))
    
    return final_score


def truncate_text(text: str, max_length: int = 100) -> str:
    """Safely truncate text to specified length"""
    if not text or len(text) <= max_length:
        return text
    
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    
    if last_space > max_length * 0.8:
        return truncated[:last_space] + '...'
    else:
        return truncated + '...'