from PIL import Image, ImageOps, ImageFilter
import pytesseract

import os
from src.config import TESSERACT_CMD

if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


def extract_text_from_image(file_path: str) -> str:
    """
    Extract text from image using OCR.
    Supports PNG, JPG, JPEG, WEBP, BMP, JFIF.
    """
    try:
        image = Image.open(file_path).convert("RGB")

        # Preprocess for better OCR
        gray = image.convert("L")
        gray = ImageOps.autocontrast(gray)
        gray = gray.filter(ImageFilter.SHARPEN)

        text = pytesseract.image_to_string(gray)

        return text.strip()

    except Exception as e:
        raise ValueError(f"Image OCR failed: {str(e)}")