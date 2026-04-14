from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str


class StatusResponse(BaseModel):
    document_id: str
    status: str
    detail: Optional[str] = None


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=2000)
    document_ids: Optional[List[str]] = None
    top_k: int = Field(default=4, ge=1, le=10)


class SourceChunk(BaseModel):
    document_id: str
    chunk_id: str
    score: float
    text_preview: str


class AskResponse(BaseModel):
    answer: str
    sources: List[SourceChunk]
    latency_ms: Dict[str, float]