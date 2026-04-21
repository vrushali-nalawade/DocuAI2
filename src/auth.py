from fastapi import Header, HTTPException
from src.config import API_SECRET_KEY


def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid API key")