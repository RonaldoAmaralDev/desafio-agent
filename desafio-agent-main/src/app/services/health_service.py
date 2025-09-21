import os
import openai
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.logging import get_logger
from app.core.redis import redis_client

logger = get_logger(__name__)


class HealthService:
    def check(self, db: Session) -> dict:
        status = {
            "status": "ok",
            "database": "ok",
            "openai": "ok",
            "redis": "ok",
        }

        # -------------------
        # Banco de dados
        # -------------------
        try:
            db.execute(text("SELECT 1"))
            logger.info("Banco de dados disponível")
        except Exception as e:
            logger.error(f"Banco de dados indisponível: {e}")
            status["status"] = "error"
            status["database"] = "Indisponível"

        # -------------------
        # OpenAI
        # -------------------
        openai_key = os.environ.get("OPENAI_API_KEY")
        if not openai_key:
            logger.error("OpenAI API Key não configurada")
            status["status"] = "error"
            status["openai"] = "API KEY não configurado"
        else:
            try:
                openai.api_key = openai_key
                openai.models.list()
                logger.info("Conexão com OpenAI OK")
            except Exception as e:
                logger.error(f"Falha ao conectar com OpenAI: {e}")
                status["status"] = "error"
                status["openai"] = "Indisponível"

        # -------------------
        # Redis
        # -------------------
        try:
            pong = redis_client.ping()
            if pong:
                logger.info("Redis disponível")
            else:
                raise Exception("Resposta inválida do Redis")
        except Exception as e:
            logger.error(f"Redis indisponível: {e}")
            status["status"] = "error"
            status["redis"] = "Indisponível"

        return status
