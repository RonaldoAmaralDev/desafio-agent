from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import ValidationError
import traceback
from app.core.logging import get_logger

logger = get_logger(__name__)

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response

        except HTTPException as e:
            logger.warning(
                f"Erro HTTP {e.status_code} em {request.url.path}: {e.detail}"
            )
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "erro": e.detail,
                    "codigo_status": e.status_code
                },
            )

        except ValidationError as e:
            logger.warning(f"Erro de validação em {request.url.path}: {str(e)}")
            return JSONResponse(
                status_code=422,
                content={
                    "erro": "Erro de validação",
                    "detalhes": e.errors()
                },
            )

        except Exception as e:
            logger.error(
                f"Erro não tratado em {request.url.path}: {str(e)}\n{traceback.format_exc()}"
            )
            return JSONResponse(
                status_code=500,
                content={"erro": "Erro interno do servidor"},
            )