from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import json
from openai import RateLimitError, AuthenticationError

from app.core.db import get_db
from app.models.agent import Agent
from app.schemas.agent import AgentSchema, AgentCreate, RunRequest
from app.core.logging import get_logger
from app.services.agent_service import AgentService
from app.services.agent_execution_service import AgentExecutionService
from app.services.cost_service import CostService
from app.services.memory_service import MemoryService

router = APIRouter(prefix="/agents", tags=["Agentes"])
logger = get_logger(__name__)

agent_service = AgentService()
agent_execution_service = AgentExecutionService()
cost_service = CostService()
memory_service = MemoryService()


# ------------------------
# CRUD
# ------------------------
@router.post("/", response_model=AgentSchema, summary="Criar novo agente")
def create_agent(agent: AgentCreate, db: Session = Depends(get_db)):
    return agent_service.create(db, agent)


@router.get("/", response_model=List[AgentSchema], summary="Listar agentes")
def list_agents(db: Session = Depends(get_db)):
    return agent_service.list(db)


# ------------------------
# EXECUÇÃO STREAMING
# ------------------------
@router.post("/{agent_id}/run/stream", summary="Executar agente em modo streaming")
def run_agent_stream(agent_id: int, payload: RunRequest, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agente não encontrado")

    def generate():
        try:
            for event in agent_execution_service.run_stream(db, agent, payload.input):
                yield json.dumps(event, ensure_ascii=False) + "\n"
        except RateLimitError:
            yield json.dumps(
                {"type": "error", "message": "💳 Sem créditos: a conta OpenAI configurada não possui saldo."},
                ensure_ascii=False,
            ) + "\n"
        except AuthenticationError:
            yield json.dumps(
                {"type": "error", "message": "🔑 Chave de API da OpenAI inválida ou não foi configurada corretamente."},
                ensure_ascii=False,
            ) + "\n"
        except Exception as e:
            logger.error(f"Erro no streaming: {e}")
            yield json.dumps(
                {"type": "error", "message": f"Erro inesperado: {str(e)}"},
                ensure_ascii=False,
            ) + "\n"

    return StreamingResponse(generate(), media_type="application/x-ndjson")


# ------------------------
# CUSTOS
# ------------------------
@router.get("/{agent_id}/costs", summary="Listar custos de execuções")
def list_agent_costs(agent_id: int, db: Session = Depends(get_db)):
    costs = cost_service.list_agent_costs(db, agent_id)
    if not costs:
        raise HTTPException(status_code=404, detail="Nenhum custo encontrado para este agente")
    return costs


@router.get("/{agent_id}/costs/summary", summary="Resumo de custos do agente")
def summarize_agent_costs(agent_id: int, db: Session = Depends(get_db)):
    return cost_service.summarize_agent_costs(db, agent_id)

@router.delete("/{agent_id}/memory")
def clear_memory(agent_id: int, db: Session = Depends(get_db)):
    """
    Limpa a memória de um agente específico.
    """
    try:
        memory_service.clear(agent_id)
        logger.info(f"Memória do agente {agent_id} limpa com sucesso")
        return {"status": "ok", "message": f"Memória do agente {agent_id} foi limpa"}
    except Exception as e:
        logger.error(f"Erro ao limpar memória do agente {agent_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao limpar memória do agente")