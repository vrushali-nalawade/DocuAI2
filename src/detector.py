import re
from textblob import TextBlob

from src.extractor_pdf import extract_text_from_pdf
from src.extractor_docx import extract_text_from_docx
from src.extractor_image import extract_text_from_image
from src.models.classifier_zero_shot import (
    detect_sentiment_zero_shot,
    detect_tone_zero_shot
)
from src.utils import (
    clean_text,
    extract_amounts_regex,
    generate_summary,
    normalize_entity_list
)

from src.classifier import detect_document_type


def extract_document_text(file_path: str, file_type: str) -> str:
    """
    Route file to the correct extractor.
    Supports PDF, DOCX, and image formats.
    """
    file_type = file_type.lower().strip()

    if file_type == "pdf":
        return extract_text_from_pdf(file_path)

    elif file_type == "docx":
        return extract_text_from_docx(file_path)

    elif file_type in ["png", "jpg", "jpeg", "webp", "bmp", "jfif", "image"]:
        return extract_text_from_image(file_path)

    else:
        raise ValueError(f"Unsupported file type: {file_type}")


def extract_entities(text: str, document_type: str) -> dict:
    """
    Hybrid entity extraction:
    - Hugging Face NER first
    - regex for dates/amounts
    - domain fallback for organizations
    """
    names = set()
    dates = set()
    organizations = set()
    amounts = set()

    # -----------------------
    # HUGGING FACE NER
    # -----------------------
    try:
        from src.models.ner import extract_hf_entities
        hf_entities = extract_hf_entities(text)
    except Exception as e:
        print("HF entity extraction failed:", e)
        hf_entities = []

    for ent in hf_entities:
        word = ent.get("word", "").strip()
        label = ent.get("entity_group", "").strip()

        # Clean BERT subword tokens
        word = word.replace("##", "").strip()

        if not word or len(word) < 3:
            continue

        if not word[0].isalnum():
            continue

        if label == "PER":
            names.add(word)
        elif label == "ORG":
            organizations.add(word)

    # -----------------------
    # DATES
    # -----------------------
    date_patterns = [
        # 12 March 2024
        r"\b\d{1,2}\s(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{4}\b",

        # March 12, 2024
        r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{1,2},\s\d{4}\b",

        # 12/03/2024 or 12-03-2024
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",

        # March 2024
        r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{4}\b",

        # 2023-2024 or 2023–2024
        r"\b\d{4}\s?[–-]\s?\d{4}\b",

        # Standalone year
        r"\b(?:19|20)\d{2}\b"
    ]

    for pattern in date_patterns:
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        dates.update(matches)

    # -----------------------
    # AMOUNTS
    # -----------------------
    regex_amounts = extract_amounts_regex(text)
    amounts.update(regex_amounts)

    # -----------------------
    # ORG FALLBACK
    # -----------------------
    fallback_org_patterns = [
        r"\b[A-Z][A-Za-z&., ]+(?:Pvt Ltd|Private Limited|Ltd|Limited|Inc|LLP|Corporation|Corp|Bank|University|Institute|Nasscom|Council)\b"
    ]

    for pattern in fallback_org_patterns:
        matches = re.findall(pattern, text)
        organizations.update(m.strip() for m in matches if len(m.strip()) < 80)

    # -----------------------
    # NAME FALLBACK
    # -----------------------
    name_patterns = [
        r"\b(?:Mr|Ms|Mrs|Dr)\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b",
        r"\b[A-Z][a-z]+\s[A-Z][a-z]+\b"
    ]

    for pattern in name_patterns:
        matches = re.findall(pattern, text)
        names.update(m.strip() for m in matches if len(m.strip().split()) <= 3)

    # -----------------------
    # CLEANUP
    # -----------------------
    generic_org_words = {
        "Bank", "Banks", "Institution", "Institutions", "Organizations",
        "Companies", "Institute", "Universities", "Company", "Industry And Government"
    }

    organizations = {
        o for o in organizations
        if o not in generic_org_words and len(o.strip()) > 2 and not o.startswith("#")
    }

    generic_bad = {
        "Technical Requirements", "Key Features", "API Request",
        "API Endpoint", "Cybersecurity Incident Report",
        "Major Data Breach", "Response Field", "Final Score",
        "Track", "Problem Statement"
    }

    names = {n for n in names if n not in generic_bad}
    organizations = {o for o in organizations if o not in generic_bad}

    names = normalize_entity_list(list(names))
    organizations = normalize_entity_list(list(organizations))
    dates = normalize_entity_list(list(dates), min_length=2)
    amounts = normalize_entity_list(list(amounts), min_length=1)

    return {
        "names": names[:10],
        "dates": dates[:10],
        "organizations": organizations[:10],
        "amounts": amounts[:10]
    }


def analyze_sentiment(text: str, document_type: str) -> str:
    """
    Zero-shot sentiment detection with safe fallback.
    """
    if not text.strip():
        return "Neutral"

    # Structured docs are usually neutral
    if document_type in ["invoice", "form", "certificate", "resume"]:
        return "Neutral"

    try:
        sentiment = detect_sentiment_zero_shot(text)

        if sentiment in ["Positive", "Neutral", "Negative"]:
            return sentiment

    except Exception as e:
        print("Zero-shot sentiment failed:", e)

    # Fallback
    polarity = TextBlob(text).sentiment.polarity

    if polarity > 0.15:
        return "Positive"
    elif polarity < -0.15:
        return "Negative"
    else:
        return "Neutral"

def detect_tone(text: str) -> str:
    """
    Zero-shot tone detection with keyword fallback.
    """
    if not text.strip():
        return "Neutral"

    try:
        tone = detect_tone_zero_shot(text)

        allowed_tones = [
            "Formal / Analytical",
            "Professional",
            "Urgent",
            "Concerned / Negative",
            "Positive",
            "Informative"
        ]

        if tone in allowed_tones:
            return tone

    except Exception as e:
        print("Zero-shot tone failed:", e)

    # Fallback keyword logic
    lower = text.lower()

    if "certificate" in lower or "completion" in lower:
        return "Professional"

    if any(word in lower for word in ["recommend", "analysis", "reported", "investigation", "experts"]):
        return "Formal / Analytical"
    elif any(word in lower for word in ["urgent", "critical", "warning", "immediately"]):
        return "Urgent"
    elif any(word in lower for word in ["happy", "great", "excellent", "pleased"]):
        return "Positive"
    elif any(word in lower for word in ["complaint", "issue", "problem", "concern"]):
        return "Concerned / Negative"
    else:
        return "Informative"


def detect_risk_level(text: str, document_type: str) -> str:
    """
    Lightweight risk/severity detection.
    """
    lower = text.lower()

    if document_type in ["invoice", "resume", "form", "certificate"]:
        return "Low"

    high_risk_keywords = [
        "breach", "attack", "fraud", "unauthorized access",
        "data leak", "cybersecurity", "threat", "vulnerability",
        "compromise", "malware", "fraudulent", "suspicious"
    ]

    medium_risk_keywords = [
        "issue", "delay", "concern", "error", "warning",
        "review", "incident", "problem"
    ]

    if any(word in lower for word in high_risk_keywords):
        return "High"
    elif any(word in lower for word in medium_risk_keywords):
        return "Medium"
    else:
        return "Low"


def analyze_document_content(text: str) -> dict:
    """
    Full document analysis pipeline.
    """
    cleaned = clean_text(text)

    # Detect document type
    document_type = detect_document_type(cleaned)

    # Generate summary
    summary = generate_summary(cleaned, document_type=document_type)

    # Extract entities
    entities = extract_entities(cleaned, document_type)

    # Sentiment
    sentiment = analyze_sentiment(cleaned, document_type)

    # Tone
    tone = detect_tone(cleaned)

    # Risk
    risk_level = detect_risk_level(cleaned, document_type)

    return {
        "document_type": document_type,
        "summary": summary,
        "entities": entities,
        "sentiment": sentiment,
        "tone": tone,
        "risk_level": risk_level
    }