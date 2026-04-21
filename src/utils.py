import re
from collections import Counter

try:
    from src.models.summarizer import generate_hf_summary
except Exception:
    generate_hf_summary = None


def clean_text(text: str) -> str:
    """
    Clean extracted document text for downstream processing.
    """
    if not text:
        return ""

    text = re.sub(r"[■●•▪◦]+", " ", text)
    text = re.sub(r"#+", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def split_sentences(text: str):
    """
    Split text into reasonably clean sentences.
    """
    if not text:
        return []

    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 25]


def extract_amounts_regex(text: str):
    """
    Extract currency/amount-like values using regex.
    """
    if not text:
        return []

    pattern = r"(₹\s?\d[\d,]*(?:\.\d+)?|\$\s?\d[\d,]*(?:\.\d+)?|Rs\.?\s?\d[\d,]*(?:\.\d+)?)"
    matches = re.findall(pattern, text)
    return sorted(list(set(matches)))


def get_word_frequencies(text: str):
    """
    Compute word frequencies for extractive summarization.
    """
    if not text:
        return {}

    stopwords = {
        "the", "is", "a", "an", "and", "or", "of", "to", "in", "for", "on", "with",
        "that", "this", "it", "as", "at", "by", "from", "was", "were", "are", "be",
        "has", "have", "had", "their", "its", "into", "after", "through", "while",
        "also", "been", "than", "but", "not", "they", "them", "he", "she", "his", "her"
    }

    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    words = [w for w in words if w not in stopwords]

    return Counter(words)


def score_sentences(sentences, word_freq):
    """
    Score sentences based on frequency of important words.
    """
    sentence_scores = {}

    for sentence in sentences:
        words = re.findall(r"\b[a-zA-Z]{3,}\b", sentence.lower())
        if not words:
            continue

        score = sum(word_freq.get(word, 0) for word in words)

        # Slight bonus for medium-length informative sentences
        length = len(words)
        if 8 <= length <= 35:
            score += 3

        sentence_scores[sentence] = score

    return sentence_scores


def generate_summary(text: str, document_type: str = "generic", max_sentences: int = 3) -> str:
    """
    Hybrid summary:
    - document-aware summary for structured docs
    - HF summarizer for textual docs
    - extractive fallback
    """
    if not text:
        return "No summary could be generated."

    cleaned = " ".join(text.split())
    word_count = len(cleaned.split())

    # -------------------------------
    # DOCUMENT-AWARE SUMMARIES
    # -------------------------------
    if document_type == "certificate":
        return (
            "This document appears to be a certificate of completion or achievement, "
            "recognizing successful participation or qualification in a specific program, "
            "training, or competency-based activity."
        )

    elif document_type == "resume":
        return (
            "This document appears to be a resume or profile containing personal, academic, "
            "and/or professional details of an individual."
        )

    elif document_type == "invoice":
        return (
            "This document appears to be an invoice containing billing, payment, "
            "and transaction-related information."
        )

    elif document_type == "form":
        return (
            "This document appears to be a form intended for structured information entry, "
            "including fields such as personal or administrative details."
        )

    # -------------------------------
    # HF SUMMARY FOR LONGER DOCS
    # -------------------------------
    if generate_hf_summary and word_count >= 80:
        hf_summary = generate_hf_summary(cleaned)
        if hf_summary and len(hf_summary.strip()) > 40:
            return hf_summary

    # -------------------------------
    # EXTRACTIVE FALLBACK
    # -------------------------------
    sentences = split_sentences(cleaned)

    if not sentences:
        return cleaned[:300]

    word_freq = get_word_frequencies(cleaned)
    sentence_scores = score_sentences(sentences, word_freq)

    ranked = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
    top_sentences = [s[0] for s in ranked[:max_sentences]]
    ordered = [s for s in sentences if s in top_sentences]

    return " ".join(ordered)[:500]


def normalize_entity_list(items, min_length: int = 4):
    """
    Clean and deduplicate extracted entities.
    """
    if not items:
        return []

    cleaned = []
    junk_words = {
        "report", "document", "incident", "summary", "data", "major",
        "breach", "affects", "cybersecurity", "information",
        "certificate", "completion", "industry", "government"
    }

    for item in items:
        if not item:
            continue

        item = item.strip(" ,.-:;")
        item = item.replace("##", "").strip()

        if len(item) < min_length:
            continue

        if item.lower() in junk_words:
            continue

        # Remove obvious broken OCR fragments
        if item.islower() and len(item.split()) == 1:
            continue

        cleaned.append(item)

    return sorted(list(set(cleaned)))