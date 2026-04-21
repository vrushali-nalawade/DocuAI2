from pydantic import BaseModel, Field
from typing import List


class DocumentRequest(BaseModel):
    fileName: str = Field(..., example="sample1.pdf")
    fileType: str = Field(..., example="pdf")
    fileBase64: str = Field(..., example="JVBERi0xLjQK...")


class EntityResponse(BaseModel):
    names: List[str]
    dates: List[str]
    organizations: List[str]
    amounts: List[str]


class DocumentResponse(BaseModel):
    status: str
    fileName: str
    documentType: str
    summary: str
    entities: EntityResponse
    sentiment: str
    tone: str
    riskLevel: str