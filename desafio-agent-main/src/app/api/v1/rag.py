from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services import rag, rag_index
from app.schemas.rag import QueryRequest, QueryResponse, UploadResponse
from app.core.logging import get_logger

router = APIRouter(prefix="/rag", tags=["RAG"])
logger = get_logger(__name__)


@router.post("/query", response_model=QueryResponse, summary="Consultar documentos indexados (RAG)")
def rag_query(payload: QueryRequest):
    """
    Realiza uma consulta nos documentos indexados no ChromaDB usando RAG (Retrieval-Augmented Generation).
    """
    logger.info(f"Consulta RAG recebida: {payload.question}")
    try:
        result = rag.query_rag(payload.question)
        logger.info("Consulta RAG concluída com sucesso")
        return {"answer": result}
    except Exception as e:
        logger.error(f"Erro no RAG query: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar a query: {str(e)}")


@router.post("/upload", response_model=UploadResponse, summary="Indexar documento no ChromaDB")
async def rag_upload(file: UploadFile = File(...)):
    """
    Envia um documento (PDF, TXT ou Markdown) para ser processado e indexado no ChromaDB.
    """
    logger.info(f"Upload de arquivo para indexação: {file.filename}")
    try:
        result = rag_index.index_document(file)
        logger.info(f"Arquivo indexado com sucesso: {file.filename}")
        return result
    except Exception as e:
        logger.error(f"Erro ao indexar documento {file.filename}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
