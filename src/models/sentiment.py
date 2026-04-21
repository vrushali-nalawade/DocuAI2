from transformers import pipeline

sentiment_pipeline = None


def get_sentiment_pipeline():
    global sentiment_pipeline
    if sentiment_pipeline is None:
        sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )
    return sentiment_pipeline


def detect_sentiment(text: str) -> str:
    if not text or len(text.strip()) < 10:
        return "Neutral"

    try:
        model = get_sentiment_pipeline()

        result = model(text[:512])[0]["label"]

        if result == "POSITIVE":
            return "Positive"
        elif result == "NEGATIVE":
            return "Negative"
        else:
            return "Neutral"

    except Exception as e:
        print("Sentiment failed:", e)
        return "Neutral"