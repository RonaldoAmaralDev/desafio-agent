from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import traceback
from app.core.logging import get_logger

logger = get_logger(__name__)

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Unhandled error: {str(e)}\n{traceback.format_exc()}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )