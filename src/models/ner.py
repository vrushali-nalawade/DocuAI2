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
    if not text or len(text.strip()) < 20:
        return []

    try:
        model = get_ner_pipeline()

        cleaned_text = " ".join(text.split())[:2000]

        entities = model(cleaned_text)
        return entities

    except Exception as e:
        print("NER failed:", e)
        return []