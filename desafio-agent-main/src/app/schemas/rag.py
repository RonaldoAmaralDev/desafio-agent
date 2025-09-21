from pydantic import BaseModel
from typing import Optional


class QueryRequest(BaseModel):
    """Entrada para consultas no RAG"""
    question: str


class QueryResponse(BaseModel):
    """Resposta de uma consulta RAG"""
    answer: str


class UploadResponse(BaseModel):
    """Resposta ao indexar documento no ChromaDB"""
    status: str
    indexed_file: Optional[str] = None
    detail: Optional[str] = None
