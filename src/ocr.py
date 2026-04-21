from PIL import Image, ImageOps, ImageFilter
import pytesseract

import os
from src.config import TESSERACT_CMD
import pytesseract

if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


def extract_text_with_ocr(image_path: str) -> str:
    """
    OCR helper used for image files and scanned PDFs.
    """
    try:
        image = Image.open(image_path).convert("RGB")

        # Preprocess for better OCR
        gray = image.convert("L")
        gray = ImageOps.autocontrast(gray)
        gray = gray.filter(ImageFilter.SHARPEN)

        text = pytesseract.image_to_string(gray)

        if not text.strip():
            raise Exception("No readable text found in image.")

        return text.strip()

    except Exception as e:
        raise Exception(f"OCR extraction failed: {str(e)}")