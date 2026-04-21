import fitz  # PyMuPDF
import os
import tempfile

from PIL import Image
from src.ocr import extract_text_with_ocr


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from PDF using PyMuPDF.
    If PDF has little/no text, fallback to OCR page rendering.
    """
    try:
        doc = fitz.open(file_path)
        extracted_text = []

        # -------- First try: native PDF text extraction --------
        for page in doc:
            page_text = page.get_text().strip()
            if page_text:
                extracted_text.append(page_text)

        combined_text = "\n".join(extracted_text).strip()

        # If enough text found, return it
        if len(combined_text) > 50:
            doc.close()
            return combined_text

        # -------- Fallback: OCR for scanned/image PDFs --------
        ocr_texts = []

        for page_index in range(len(doc)):
            page = doc[page_index]
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # higher resolution OCR

            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
                temp_img_path = tmp_img.name
                pix.save(temp_img_path)

            try:
                page_ocr_text = extract_text_with_ocr(temp_img_path)
                if page_ocr_text.strip():
                    ocr_texts.append(page_ocr_text)
            finally:
                if os.path.exists(temp_img_path):
                    os.remove(temp_img_path)

        doc.close()

        final_ocr_text = "\n".join(ocr_texts).strip()

        if not final_ocr_text:
            raise ValueError("No readable text found in PDF.")

        return final_ocr_text

    except Exception as e:
        raise ValueError(f"PDF extraction failed: {str(e)}")