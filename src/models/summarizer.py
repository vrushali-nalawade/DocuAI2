from transformers import pipeline

summarizer = None


def get_summarizer():
    global summarizer
    if summarizer is None:
        summarizer = pipeline(
            "summarization",
            model="sshleifer/distilbart-cnn-12-6"
        )
    return summarizer


def chunk_text_for_summary(text: str, max_words: int = 350):
    words = text.split()
    return [
        " ".join(words[i:i + max_words])
        for i in range(0, len(words), max_words)
    ]


def summarize_chunk(text: str) -> str:
    if not text or len(text.strip()) < 40:
        return text.strip()

    try:
        model = get_summarizer()

        text = " ".join(text.split())
        word_count = len(text.split())

        if word_count < 60:
            return text.strip()

        max_len = min(120, max(40, int(word_count * 0.45)))
        min_len = min(60, max(20, int(word_count * 0.20)))

        result = model(
            text,
            max_length=max_len,
            min_length=min_len,
            do_sample=False
        )

        return result[0]["summary_text"].strip()

    except Exception as e:
        print("Summarization failed:", e)
        return ""


def generate_hf_summary(text: str) -> str:
    if not text or len(text.strip()) < 40:
        return text.strip()

    try:
        text = " ".join(text.split())

        if len(text.split()) <= 400:
            return summarize_chunk(text)

        chunks = chunk_text_for_summary(text)
        chunk_summaries = [summarize_chunk(c) for c in chunks]

        combined = " ".join([s for s in chunk_summaries if s.strip()])

        if len(combined.split()) > 400:
            return summarize_chunk(combined)

        return combined.strip()

    except Exception as e:
        print("Summary generation failed:", e)
        return ""