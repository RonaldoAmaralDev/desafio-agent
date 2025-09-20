from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import engine
from app.models.base import Base
from app.api.v1 import users, prompts, agents, executions, health, costs, agents_export_import, rag
from app.models import execution_cost, user, agent, execution, prompt
from app.core.error_handler import ErrorHandlerMiddleware
from app.core.logging import configure_logging, get_logger

# Configuração de logging
configure_logging()
logger = get_logger(__name__)
logger.info(f"Starting {__name__} - application initializing")

# Cria tabelas (se ainda não existirem)
Base.metadata.create_all(bind=engine)

# Inicialização da API
app = FastAPI(title=settings.APP_NAME)

# CORS (para o frontend Vue)
origins = [
    "http://localhost:5173",
    "http://localhost"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- ROTAS --------
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(prompts.router, prefix="/api/v1", tags=["prompts"])
app.include_router(agents.router, prefix="/api/v1", tags=["agents"])
app.include_router(executions.router, prefix="/api/v1", tags=["executions"])
app.include_router(health.router)
app.include_router(costs.router, prefix="/api/v1", tags=["costs"])
app.include_router(agents_export_import.router, prefix="/api/v1", tags=["agents export/import"])
app.include_router(rag.router, prefix="/api/v1", tags=["rag"])  # <<< Novo: RAG integrado

# Middleware de erros customizado
app.add_middleware(ErrorHandlerMiddleware)


@app.get("/")
def root():
    return {
        "message": f"API {settings.APP_NAME} rodando 🚀",
        "environment": settings.APP_ENV,
        "debug": settings.APP_DEBUG,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(settings.APP_PORT),
        reload=settings.APP_DEBUG
    )
