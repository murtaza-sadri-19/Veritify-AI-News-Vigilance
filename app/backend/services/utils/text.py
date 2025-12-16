import re
import html
from typing import List


def sanitize_text(text: str) -> str:
    """
    Sanitize input text to prevent security issues and improve matching quality.
    """
    if not text:
        return ""

    # Remove HTML tags if any
    text = re.sub(r"<[^>]+>", "", text)

    # Unescape HTML entities
    text = html.unescape(text)

    # Normalize quotes
    text = normalize_quotes(text)

    # Remove extra whitespace and normalize
    text = re.sub(r"\s+", " ", text).strip()

    # Limit length for generic API calls (not for models with token-based limits)
    if len(text) > 2000:
        text = text[:1997] + "..."

    return text


def normalize_quotes(text: str) -> str:
    """
    Normalize curly quotes and other variants to straight quotes.
    """
    if not text:
        return ""
    replacements = {
        "“": '"',
        "”": '"',
        "„": '"',
        "‟": '"',
        "«": '"',
        "»": '"',
        "‘": "'",
        "’": "'",
        "‚": "'",
        "‛": "'",
    }
    for src, tgt in replacements.items():
        text = text.replace(src, tgt)
    return text


def whitespace_cleanup(text: str) -> str:
    """
    Normalize whitespace: collapse multiple spaces, trim ends.
    """
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def safe_truncate(text: str, max_length: int = 512) -> str:
    """
    Sentence-aware truncation: tries to cut at sentence boundary before max_length.
    Fallbacks to word boundary, then hard cut.
    """
    if not text or len(text) <= max_length:
        return text

    # First attempt: last period before max_length
    snippet = text[:max_length]
    last_period = snippet.rfind(".")
    if last_period > max_length * 0.6:
        return snippet[: last_period + 1]

    # Second attempt: last space before max_length
    last_space = snippet.rfind(" ")
    if last_space > max_length * 0.6:
        return snippet[:last_space] + "..."

    # Hard cut
    return snippet + "..."


def sentence_aware_truncate_for_mnli(
    text: str,
    max_tokens: int = 256,
    tokenizer=None,
) -> str:
    """
    Ensure text fits within MNLI model's token budget.
    If a tokenizer is provided, use it to count tokens; otherwise approximate by length.
    """
    if not text:
        return ""

    if tokenizer is None:
        # Rough heuristic: ~4 characters per token
        approx_tokens = len(text) / 4.0
        if approx_tokens <= max_tokens:
            return text
        target_chars = int(max_tokens * 4)
        return safe_truncate(text, target_chars)

    # Tokenizer-based truncation
    encoded = tokenizer(
        text,
        truncation=True,
        max_length=max_tokens,
        return_overflowing_tokens=False,
    )
    # Decode back to text; this might slightly differ but is safe for the model
    if isinstance(encoded["input_ids"], list):
        ids: List[int] = encoded["input_ids"]
    else:
        ids = encoded["input_ids"].tolist()
    return tokenizer.decode(ids, skip_special_tokens=True)