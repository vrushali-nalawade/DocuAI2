import os
import base64
import uuid

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

MAX_FILE_SIZE_MB = 15
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".bmp",
    ".jfif"
}


def validate_file_extension(file_name: str):
    ext = os.path.splitext(file_name)[1].lower()

    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file format: {ext}. "
            "Supported formats are PDF, DOCX, PNG, JPG, JPEG, WEBP, BMP, JFIF."
        )


def save_base64_file(file_name: str, file_base64: str) -> str:
    """
    Decode base64 and save file safely to temp directory.
    Returns saved file path.
    """
    try:
        validate_file_extension(file_name)

        # Remove data URL prefix if present
        if "," in file_base64:
            file_base64 = file_base64.split(",")[1]

        file_bytes = base64.b64decode(file_base64)

        if len(file_bytes) > MAX_FILE_SIZE_BYTES:
            raise ValueError(
                f"File too large. Maximum allowed size is {MAX_FILE_SIZE_MB} MB."
            )

        ext = os.path.splitext(file_name)[1].lower()
        unique_name = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(TEMP_DIR, unique_name)

        with open(file_path, "wb") as f:
            f.write(file_bytes)

        return file_path

    except Exception as e:
        raise ValueError(f"Failed to save uploaded file: {str(e)}")