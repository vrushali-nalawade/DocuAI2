from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes import router

app = FastAPI(
    title="AI Document Analysis API",
    description="Analyze PDF, DOCX, and image documents using AI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/")
def root():
    return {"message": "AI Document Analysis API is running"}