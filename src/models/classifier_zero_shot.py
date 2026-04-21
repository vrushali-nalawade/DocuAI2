from transformers import pipeline

zero_shot_pipeline = None


def get_zero_shot_pipeline():
    global zero_shot_pipeline

    if zero_shot_pipeline is None:
        zero_shot_pipeline = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )

    return zero_shot_pipeline


def classify_zero_shot(text: str, labels: list[str]) -> dict:
    """
    Generic zero-shot classification helper.
    Returns top label + scores.
    """
    if not text or len(text.strip()) < 20:
        return {"label": "Unknown", "scores": {}}

    try:
        model = get_zero_shot_pipeline()

        # Keep inference manageable
        cleaned_text = " ".join(text.split())[:2000]

        result = model(cleaned_text, candidate_labels=labels)

        return {
            "label": result["labels"][0],
            "scores": dict(zip(result["labels"], result["scores"]))
        }

    except Exception as e:
        print("Zero-shot classification failed:", e)
        return {"label": "Unknown", "scores": {}}


def detect_sentiment_zero_shot(text: str) -> str:
    labels = ["Positive", "Neutral", "Negative"]
    result = classify_zero_shot(text, labels)
    return result["label"]


def detect_tone_zero_shot(text: str) -> str:
    labels = [
        "Formal / Analytical",
        "Professional",
        "Urgent",
        "Concerned / Negative",
        "Positive",
        "Informative"
    ]
    result = classify_zero_shot(text, labels)
    return result["label"]