from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.services.health_service import HealthService
from app.core.logging import get_logger

router = APIRouter(prefix="/health", tags=["Health"])
logger = get_logger(__name__)

health_service = HealthService()


@router.get("/", summary="Health check da API")
def health_check(db: Session = Depends(get_db)):
    """
    Verifica se a API, o banco de dados, o Redis e a OpenAI estão funcionando corretamente.
    """
    status = health_service.check(db)

    if status["status"] != "ok":
        raise HTTPException(status_code=500, detail=status)

    return status
