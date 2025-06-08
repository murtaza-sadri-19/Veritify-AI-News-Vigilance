import re
import html
from typing import List, Set
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


def calculate_relevance_score(claim: str, title: str, description: str = "") -> float:
    """
    Calculate relevance score between a claim and news article
    Returns score between 0.0 and 1.0
    """
    if not claim or not title:
        return 0.0

    # Normalize texts
    claim_clean = sanitize_text(claim).lower()
    title_clean = sanitize_text(title).lower()
    desc_clean = sanitize_text(description).lower() if description else ""

    # Get keywords from claim
    claim_keywords = set(get_keywords(claim_clean, 15))

    # Combine title and description for matching
    article_text = f"{title_clean} {desc_clean}".strip()
    article_keywords = set(get_keywords(article_text, 20))

    if not claim_keywords or not article_keywords:
        # Fallback to basic string similarity
        return SequenceMatcher(None, claim_clean, title_clean).ratio()

    # Calculate keyword overlap
    common_keywords = claim_keywords.intersection(article_keywords)
    keyword_score = len(common_keywords) / len(claim_keywords) if claim_keywords else 0

    # Calculate string similarity
    title_similarity = SequenceMatcher(None, claim_clean, title_clean).ratio()

    if desc_clean:
        desc_similarity = SequenceMatcher(None, claim_clean, desc_clean).ratio()
        string_similarity = max(title_similarity, desc_similarity)
    else:
        string_similarity = title_similarity

    # Extract and compare entities
    claim_entities = set(extract_entities(claim))
    article_entities = set(extract_entities(f"{title} {description}"))

    entity_score = 0.0
    if claim_entities and article_entities:
        common_entities = claim_entities.intersection(article_entities)
        entity_score = len(common_entities) / len(claim_entities)

    # Weighted combination of scores
    relevance_score = (
            keyword_score * 0.5 +  # Keywords are most important
            string_similarity * 0.3 +  # Overall text similarity
            entity_score * 0.2  # Named entity matching
    )

    return min(1.0, relevance_score)


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