import re
from typing import List

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
