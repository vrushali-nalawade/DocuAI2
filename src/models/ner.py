from transformers import pipeline

ner_pipeline = None


def get_ner_pipeline():
    global ner_pipeline
    if ner_pipeline is None:
        ner_pipeline = pipeline(
            "ner",
            model="dslim/bert-base-NER",
            aggregation_strategy="simple"
        )
    return ner_pipeline


def extract_hf_entities(text: str):
    """
    Extract entities using Hugging Face NER model.
    Returns raw HF output.
    """
    if not text or len(text.strip()) < 20:
        return []

    try:
        model = get_ner_pipeline()

        # Keep inference manageable
        cleaned_text = " ".join(text.split())

        # Limit to first 2500 chars to reduce noise / speed issues
        cleaned_text = cleaned_text[:2500]

        entities = model(cleaned_text)
        return entities

    except Exception as e:
        print("HF NER failed:", e)
        return []