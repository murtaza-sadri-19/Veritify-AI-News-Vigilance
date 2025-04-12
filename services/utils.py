import re
import html


def sanitize_text(text):
    """
    Sanitize input text to prevent security issues and improve matching quality
    """
    # Remove HTML tags if any
    text = re.sub(r'<[^>]+>', '', text)

    # Unescape HTML entities
    text = html.unescape(text)

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Limit length for API calls
    if len(text) > 500:
        text = text[:497] + '...'

    return text


def extract_entities(text):
    """
    Extract important entities (people, organizations, places) from text
    For more advanced implementation, consider using NLP libraries
    """
    # This is a simplified implementation
    # In a production system, you would use a named entity recognition system

    # Simple regex patterns to detect potential entities
    # People: Title + Capitalized words
    people = re.findall(r'(Mr\.|Mrs\.|Ms\.|Dr\.|President|Senator|Governor)?\s?([A-Z][a-z]+\s[A-Z][a-z]+)', text)

    # Organizations: Multiple capitalized words
    orgs = re.findall(r'([A-Z][a-z]+(\s[A-Z][a-z]+)+)', text)

    entities = []
    if people:
        entities.extend([' '.join(p).strip() for p in people if p[1]])
    if orgs:
        entities.extend([o[0] for o in orgs])

    # Remove duplicates
    return list(set(entities))


def get_keywords(text, max_keywords=5):
    """
    Extract important keywords from the text
    Basic implementation - for production use NLP libraries
    """
    # Remove common words
    stopwords = ['the', 'a', 'an', 'and', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
    words = text.lower().split()

    # Filter out stopwords and short words
    filtered_words = [w for w in words if w not in stopwords and len(w) > 3]

    # Count frequencies
    word_counts = {}
    for word in filtered_words:
        word_counts[word] = word_counts.get(word, 0) + 1

    # Get top words by frequency
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)

    return [word for word, count in sorted_words[:max_keywords]]