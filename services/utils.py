import re
import html
from typing import List
from difflib import SequenceMatcher


def sanitize_text(text: str) -> str:
    """
    Sanitize input text to prevent security issues and improve matching quality
    """
    if not text:
        return ""

    # Remove HTML tags if any
    text = re.sub(r'<[^>]+>', '', text)

    # Unescape HTML entities
    text = html.unescape(text)

    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text).strip()

    # Limit length for API calls
    if len(text) > 500:
        text = text[:497] + '...'

    return text


def extract_entities(text: str) -> List[str]:
    """
    Extract important entities (people, organizations, places) from text
    Simplified implementation - for production use NLP libraries like spaCy
    """
    if not text:
        return []

    entities = []

    # People: Title + Capitalized words
    people_pattern = r'(Mr\.|Mrs\.|Ms\.|Dr\.|President|Senator|Governor|Prime Minister)\s+([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)'
    people_matches = re.findall(people_pattern, text)
    entities.extend([f"{title} {name}".strip() for title, name in people_matches])

    # Simple name patterns (First Last)
    name_pattern = r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b'
    name_matches = re.findall(name_pattern, text)
    entities.extend(name_matches)

    # Organizations (multiple capitalized words)
    org_pattern = r'\b([A-Z][A-Za-z]*(?:\s+[A-Z][A-Za-z]*){1,3})\b'
    org_matches = re.findall(org_pattern, text)

    # Filter organizations (avoid common false positives)
    common_words = {'The', 'And', 'Of', 'In', 'On', 'At', 'To', 'For', 'With', 'By'}
    for org in org_matches:
        words = org.split()
        if len(words) >= 2 and not any(word in common_words for word in words):
            entities.append(org)

    # Remove duplicates and return
    return list(set(entities))


def get_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """
    Extract important keywords from the text
    Enhanced implementation with better filtering
    """
    if not text:
        return []

    # Expanded stopwords list
    stopwords = {
        'the', 'a', 'an', 'and', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
        'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
        'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
    }

    # Clean and tokenize
    text_lower = text.lower()
    # Remove punctuation except hyphens in words
    text_clean = re.sub(r'[^\w\s-]', ' ', text_lower)
    words = text_clean.split()

    # Filter words
    filtered_words = []
    for word in words:
        # Remove stopwords, short words, and numbers
        if (len(word) > 3 and
                word not in stopwords and
                not word.isdigit() and
                not re.match(r'^\d+$', word)):
            filtered_words.append(word)

    # Count frequencies
    word_counts = {}
    for word in filtered_words:
        word_counts[word] = word_counts.get(word, 0) + 1

    # Sort by frequency and return top keywords
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    return [word for word, count in sorted_words[:max_keywords]]


def calculate_relevance_score(claim: str, title: str, description: str = "", published: str = None) -> float:
    """
    Calculate relevance score between a claim and news article using context-aware
    semantic similarity combined with keyword and entity overlap. Returns score between 0.0 and 1.0.
    """
    if not claim or not title:
        return 0.0

    claim_text = sanitize_text(claim)
    article_text = sanitize_text(f"{title}. {description}")

    # Prepare keyword and entity signals (lighter weight)
    claim_keywords = set(get_keywords(claim_text, 15))
    article_keywords = set(get_keywords(article_text, 20))
    keyword_score = 0.0
    if claim_keywords:
        common_keywords = claim_keywords.intersection(article_keywords)
        keyword_score = len(common_keywords) / len(claim_keywords)

    claim_entities = set(extract_entities(claim))
    article_entities = set(extract_entities(article_text))
    entity_score = 0.0
    if claim_entities:
        common_entities = claim_entities.intersection(article_entities)
        entity_score = len(common_entities) / len(claim_entities) if claim_entities else 0.0

    # Semantic similarity (context-aware) - try sentence-transformers first, then spaCy vectors, else fallback
    semantic_sim = 0.0

    # Cached model holders
    global _sem_model, _sem_model_type
    try:
        _sem_model
    except NameError:
        _sem_model = None
        _sem_model_type = None

    def _cosine(a, b):
        try:
            import numpy as _np
            a = _np.array(a, dtype=float)
            b = _np.array(b, dtype=float)
            denom = (_np.linalg.norm(a) * _np.linalg.norm(b))
            if denom == 0:
                return 0.0
            return float(_np.dot(a, b) / denom)
        except Exception:
            return 0.0

    # Try sentence-transformers
    if _sem_model_type is None:
        try:
            from sentence_transformers import SentenceTransformer
            _sem_model = SentenceTransformer('all-MiniLM-L6-v2')
            _sem_model_type = 'sbert'
        except Exception:
            # Try spaCy vectors
            try:
                import spacy
                try:
                    _sem_model = spacy.load('en_core_web_lg')
                except Exception:
                    _sem_model = spacy.load('en_core_web_sm')
                _sem_model_type = 'spacy'
            except Exception:
                _sem_model = None
                _sem_model_type = 'none'

    try:
        if _sem_model_type == 'sbert' and _sem_model:
            emb_claim = _sem_model.encode([claim_text], convert_to_numpy=True)[0]
            emb_article = _sem_model.encode([article_text], convert_to_numpy=True)[0]
            semantic_sim = _cosine(emb_claim, emb_article)
        elif _sem_model_type == 'spacy' and _sem_model:
            doc1 = _sem_model(claim_text)
            doc2 = _sem_model(article_text)
            # spaCy .similarity may rely on word vectors; ensure non-zero
            try:
                semantic_sim = float(doc1.similarity(doc2))
            except Exception:
                semantic_sim = _cosine(doc1.vector, doc2.vector)
        else:
            semantic_sim = 0.0
    except Exception:
        semantic_sim = 0.0

    # Normalize semantic_sim to [0,1]
    if semantic_sim is None:
        semantic_sim = 0.0
    semantic_sim = max(0.0, min(1.0, semantic_sim))

    # Recency signal (respect article dates) - optional, falls back to neutral
    recency_score = 0.5
    if published:
        try:
            from datetime import datetime
            import math
            # Try ISO parse first
            try:
                pub_dt = datetime.fromisoformat(published)
            except Exception:
                # Try common timestamp formats
                formats = [
                    "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%d"
                ]
                pub_dt = None
                for fmt in formats:
                    try:
                        pub_dt = datetime.strptime(published, fmt)
                        break
                    except Exception:
                        continue
            if pub_dt:
                now = datetime.utcnow()
                delta = now - pub_dt if now > pub_dt else pub_dt - now
                days = delta.total_seconds() / 86400.0
                # Exponential decay with configurable half-life-ish behavior
                decay_days = float(os.getenv('NEWS_RECENCY_DECAY_DAYS', '14'))
                recency_score = float(math.exp(-days / max(1.0, decay_days)))
                # normalize to [0,1]
                if recency_score < 0:
                    recency_score = 0.0
                if recency_score > 1:
                    recency_score = 1.0
        except Exception:
            recency_score = 0.5

    # Combine signals with weights; give semantic and recency higher importance
    # Weights sum to 1.0
    w_sem = 0.5
    w_kw = 0.2
    w_ent = 0.1
    w_rec = 0.2
    final_score = (
        w_sem * semantic_sim +
        w_kw * keyword_score +
        w_ent * entity_score +
        w_rec * recency_score
    )

    return min(1.0, max(0.0, final_score))


def truncate_text(text: str, max_length: int = 100) -> str:
    """Safely truncate text to specified length"""
    if not text or len(text) <= max_length:
        return text

    # Try to truncate at word boundary
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')

    if last_space > max_length * 0.8:  # If we can save most of the text
        return truncated[:last_space] + '...'
    else:
        return truncated + '...'