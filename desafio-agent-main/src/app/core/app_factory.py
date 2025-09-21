from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.error_handler import ErrorHandlerMiddleware
from app.api.router import api_router

def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME)

    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_origins=settings.CORS_ORIGINS or ["*"],
    )

    app.add_middleware(ErrorHandlerMiddleware)

    app.include_router(api_router)

    @app.get("/")
    def root():
        return {
            "message": f"API {settings.APP_NAME} rodando!",
            "environment": settings.APP_ENV,
            "debug": settings.APP_DEBUG,
        }

    return app
