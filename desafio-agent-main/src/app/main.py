from fastapi import FastAPI
from app.core.app_factory import create_app
from app.core.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)
logger.info("Starting application...")

app: FastAPI = create_app()

if __name__ == "__main__":
    import uvicorn
    from app.core.config import settings
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(settings.APP_PORT),
        reload=settings.APP_DEBUG,
    )