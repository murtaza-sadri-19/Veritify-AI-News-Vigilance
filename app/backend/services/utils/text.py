import re
import html

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
