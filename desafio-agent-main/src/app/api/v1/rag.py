from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from app.services import rag, rag_index

router = APIRouter(prefix="/api/v1/rag", tags=["rag"])


# ---------------------------
# MODELS
# ---------------------------
class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str


class UploadResponse(BaseModel):
    status: str
    indexed_file: str | None = None
    detail: str | None = None


# ---------------------------
# ENDPOINTS
# ---------------------------

@router.post("/query", response_model=QueryResponse)
def rag_query(payload: QueryRequest):
    """
    Consulta documentos já indexados no ChromaDB usando RAG.
    """
    try:
        result = rag.query_rag(payload.question)
        return {"answer": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar a query: {e}")


@router.post("/upload", response_model=UploadResponse)
async def rag_upload(file: UploadFile = File(...)):
    """
    Envia um documento (PDF, TXT, MD) para ser indexado no ChromaDB.
    """
    try:
        result = rag_index.index_document(file)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))