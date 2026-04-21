def detect_document_type(text: str) -> str:
    """
    Lightweight document type detection.
    Returns one of:
    invoice, certificate, cybersecurity_report, technical_report, research_paper,
    legal_document, resume, complaint, letter, form, generic
    """

    if not text or len(text.strip()) < 20:
        return "generic"

    lower = text.lower()

    categories = {
        "invoice": [
            "invoice", "bill to", "invoice no", "total amount",
            "gst", "tax invoice", "amount due", "payment due"
        ],

        "certificate": [
            "certificate", "certified", "completion", "issued", "awarded",
            "successfully completed", "sector skills council"
        ],

        "cybersecurity_report": [
            "cybersecurity", "data breach", "security incident",
            "unauthorized access", "threat", "malware",
            "vulnerability", "attack", "fraudulent",
            "security analysts", "encryption", "digital security"
        ],

        "technical_report": [
            "technical requirements", "system design", "architecture",
            "implementation", "api", "endpoint", "module",
            "deployment", "backend", "frontend", "workflow",
            "technology industry analysis", "industry analysis", "market analysis"
        ],

        "research_paper": [
            "abstract", "methodology", "results", "discussion",
            "literature review", "hypothesis", "experiment",
            "dataset", "conclusion", "references"
        ],

        "legal_document": [
            "agreement", "contract", "party", "clause", "hereby",
            "terms and conditions", "witnesseth", "liable", "jurisdiction"
        ],

        "resume": [
            "education", "skills", "experience", "projects",
            "certifications", "objective", "internship", "profile",
            "linkedin", "portfolio", "phone", "email"
        ],

        "complaint": [
            "complaint", "issue", "problem", "concern",
            "grievance", "not satisfied", "poor service"
        ],

        "letter": [
            "dear", "sincerely", "regards", "yours faithfully",
            "to whom it may concern"
        ],

        "form": [
            "application form", "form no", "date of birth",
            "signature", "checkbox", "fill in", "applicant name"
        ],
    }

    def count_matches(keywords):
        return sum(1 for kw in keywords if kw in lower)

    scores = {doc_type: count_matches(keywords) for doc_type, keywords in categories.items()}

    best_type = max(scores, key=scores.get)

    if scores[best_type] == 0:
        return "generic"

    # Prevent weak accidental resume classification
    if best_type == "resume" and scores["resume"] < 2:
        if scores.get("technical_report", 0) > 0:
            return "technical_report"
        return "generic"

    return best_type