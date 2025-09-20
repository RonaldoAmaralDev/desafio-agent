from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
import openai
import os
from app.core.logging import get_logger

router = APIRouter(prefix="/health", tags=["health"])
logger = get_logger(__name__)

@router.get("/")
def health_check(db: Session = Depends(get_db)):
    logger.info("Iniciando health check da API, banco de dados e OpenAI")
    try:
        db.execute(text("SELECT 1"))
        logger.info("Banco de dados disponível")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Banco de dados indisponível: {str(e)}")

    openai_key = os.environ.get("OPENAI_API_KEY")
    if not openai_key:
        logger.error("OpenAI API Key não configurada")
        raise HTTPException(status_code=500, detail="OpenAI API Key não configurada")
    
    try:
        openai.api_key = openai_key
        openai.models.list()
        logger.info("Conexão com OpenAI OK")
    except Exception as e:
        logger.error(f"Falha ao conectar com OpenAI: {e}")
        raise HTTPException(status_code=500, detail=f"Falha ao conectar com OpenAI: {str(e)}")

    logger.info("Health check concluído com sucesso ✅")
    return {
        "status": "ok",
        "message": "API, banco de dados e OpenAI funcionando ✅"
    }