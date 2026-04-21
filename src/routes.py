import os
from fastapi import APIRouter, Depends, HTTPException

from src.auth import verify_api_key
from src.schemas import DocumentRequest, DocumentResponse
from src.file_handler import save_base64_file
from src.detector import extract_document_text, analyze_document_content

router = APIRouter()


def detect_file_type(file_name: str, provided_type: str = "") -> str:
    """
    Detect file type safely from filename and/or provided fileType.
    """
    ext = os.path.splitext(file_name)[1].lower().replace(".", "")

    supported = ["pdf", "docx", "png", "jpg", "jpeg", "webp", "bmp", "jfif"]

    if ext in supported:
        return ext

    if provided_type:
        ft = provided_type.lower().strip()

        if ft in supported:
            return ft
        elif ft == "image":
            return "image"
        elif "pdf" in ft:
            return "pdf"
        elif "docx" in ft:
            return "docx"

    return "unknown"


@router.post(
    "/document-analyze",
    response_model=DocumentResponse,
    
)
def analyze_document(request: DocumentRequest):
    file_path = None

    try:
        # Save uploaded file
        file_path = save_base64_file(request.fileName, request.fileBase64)

        # Detect safe file type
        safe_file_type = detect_file_type(request.fileName, request.fileType)

        if safe_file_type == "unknown":
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Please upload PDF, DOCX, PNG, JPG, JPEG, WEBP, BMP, or JFIF."
            )

        # Extract text
        extracted_text = extract_document_text(file_path, safe_file_type)

        if not extracted_text or not extracted_text.strip():
            raise HTTPException(
                status_code=400,
                detail="No readable text found in the document."
            )

        # Analyze content
        analysis = analyze_document_content(extracted_text)

        return {
            "status": "success",
            "fileName": request.fileName,
            "documentType": analysis["document_type"],
            "summary": analysis["summary"],
            "entities": analysis["entities"],
            "sentiment": analysis["sentiment"],
            "tone": analysis["tone"],
            "riskLevel": analysis["risk_level"]
        }

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Clean up temp file after processing
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass