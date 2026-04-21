from docx import Document


def extract_text_from_docx(file_path: str) -> str:
    try:
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        return text.strip()
    except Exception as e:
        raise Exception(f"DOCX extraction failed: {str(e)}")