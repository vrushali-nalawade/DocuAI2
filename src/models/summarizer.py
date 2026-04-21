from transformers import pipeline

# Load once at startup
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


def chunk_text_for_summary(text: str, max_words: int = 350):
    """
    Split long text into chunks for transformer summarization.
    """
    words = text.split()
    return [
        " ".join(words[i:i + max_words])
        for i in range(0, len(words), max_words)
    ]


def summarize_chunk(text: str) -> str:
    """
    Summarize a single chunk with adaptive summary lengths.
    """
    if not text or len(text.strip()) < 40:
        return text.strip()

    try:
        text = " ".join(text.split())
        word_count = len(text.split())

        # For short text, avoid forcing weird summarization
        if word_count < 60:
            return text.strip()

        max_len = min(120, max(40, int(word_count * 0.45)))
        min_len = min(60, max(20, int(word_count * 0.20)))

        result = summarizer(
            text,
            max_length=max_len,
            min_length=min_len,
            do_sample=False
        )

        return result[0]["summary_text"].strip()

    except Exception as e:
        print("HF summarization failed:", e)
        return ""


def generate_hf_summary(text: str) -> str:
    """
    Generate summary using Hugging Face model.
    Handles both short and long text safely.
    """
    if not text or len(text.strip()) < 40:
        return text.strip()

    try:
        text = " ".join(text.split())

        # Short/moderate docs
        if len(text.split()) <= 400:
            return summarize_chunk(text)

        # Long docs → summarize in chunks, then summarize summaries
        chunks = chunk_text_for_summary(text, max_words=350)
        chunk_summaries = [summarize_chunk(chunk) for chunk in chunks]
        combined_summary = " ".join([s for s in chunk_summaries if s.strip()])

        if len(combined_summary.split()) > 400:
            return summarize_chunk(combined_summary)

        return combined_summary.strip()

    except Exception as e:
        print("HF summary generation failed:", e)
        return ""