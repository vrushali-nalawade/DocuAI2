# src/models/model_loader.py
from transformers import pipeline

summarizer = None
ner_model = None
sentiment_model = None

def load_models():
    global summarizer, ner_model, sentiment_model

    if summarizer is None:
        summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")  # lighter

    if ner_model is None:
        ner_model = pipeline("ner", model="dslim/bert-base-NER")

    if sentiment_model is None:
        sentiment_model = pipeline("sentiment-analysis")

    return summarizer, ner_model, sentiment_model