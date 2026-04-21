def detect_tone(text: str) -> str:
    text = text.lower()

    if any(word in text for word in ["urgent", "immediately", "asap"]):
        return "Urgent"

    if any(word in text for word in ["regret", "sorry", "concern"]):
        return "Concerned"

    if any(word in text for word in ["happy", "great", "excellent"]):
        return "Positive"

    if any(word in text for word in ["analysis", "report", "data"]):
        return "Analytical"

    return "Informative"