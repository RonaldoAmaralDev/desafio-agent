from fastapi import APIRouter
from app.api.v1 import (
    users, prompts, agents, executions, costs, rag, agent_export, health
)
from app.core.config import settings

# Usa versão configurável
api_router = APIRouter(prefix=f"/api/{settings.API_VERSION}")

# Domínio: Usuários e agentes
api_router.include_router(users.router, tags=["Usuários"])
api_router.include_router(agents.router, tags=["Agentes"])

# Domínio: Prompts e execuções
api_router.include_router(prompts.router, tags=["Prompts"])
api_router.include_router(executions.router, tags=["Execuções"])

# Custos e RAG
api_router.include_router(costs.router, tags=["Custos"])
api_router.include_router(rag.router, tags=["RAG"])

# Exportações
api_router.include_router(agent_export.router, tags=["Agents Export/Import"])

# Healthcheck (sem versão, endpoint raiz)
api_router.include_router(health.router, tags=["Health"])