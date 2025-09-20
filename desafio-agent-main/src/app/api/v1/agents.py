from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
import asyncio

from app.db.session import get_db
from app.models.agent import Agent
from app.models.execution_cost import ExecutionCost
from app.schemas.agent import AgentSchema, AgentCreate
from app.core.logging import get_logger
from langchain_ollama import ChatOllama

from app.core.memory import save_agent_memory, get_agent_memory, clear_agent_memory

router = APIRouter(prefix="/agents", tags=["agents"])
logger = get_logger(__name__)

class CollaborationRequest(BaseModel):
    task: str
    agent_ids: List[str]


class RunRequest(BaseModel):
    input: str


class RunResponse(BaseModel):
    answer: str
    memory: list[dict] = [] 

@router.post("/", response_model=AgentSchema)
def create_agent(agent: AgentCreate, db: Session = Depends(get_db)):
    logger.info(f"Criando agente: {agent.name} (modelo: {agent.model})")
    db_agent = Agent(
        name=agent.name,
        model=agent.model,
        temperature=agent.temperature,
        owner_id=agent.owner_id,
        provider=agent.provider or "ollama",
        base_url=agent.base_url or "http://ollama:11434"
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    logger.info(f"Agente criado com sucesso: ID {db_agent.id}")
    return db_agent


@router.get("/", response_model=List[AgentSchema])
def list_agents(db: Session = Depends(get_db)):
    agents = db.query(Agent).all()
    logger.info(f"Listando {len(agents)} agentes")
    return agents


@router.post("/{agent_id}/run", response_model=RunResponse)
def run_agent(agent_id: str, payload: RunRequest, db: Session = Depends(get_db)):
    """
    Executa um agente Ollama pelo ID com memória de curto prazo.
    """
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agente não encontrado")

    if agent.provider != "ollama":
        raise HTTPException(status_code=400, detail="Somente agentes Ollama suportados nesta versão")

    try:
        memory = get_agent_memory(agent.id)
        context = "\n".join([f"Você: {m['input']}\nAgente: {m['output']}" for m in memory])

        final_input = f"""
        Contexto das últimas interações:
        {context}

        Nova pergunta:
        {payload.input}
        """

        llm = ChatOllama(
            model=agent.model,
            base_url=agent.base_url,
            temperature=agent.temperature or 0
        )

        res = llm.invoke(final_input)
        answer = res.content if hasattr(res, "content") else str(res)

        save_agent_memory(agent.id, payload.input, answer)

        logger.info(f"Agente {agent.id} executado com sucesso com memória")
        return {
            "answer": answer,
            "memory": get_agent_memory(agent.id)
        }

    except Exception as e:
        logger.error(f"Erro ao executar agente {agent.id}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao executar agente: {e}")


@router.delete("/{agent_id}/memory")
def clear_memory(agent_id: str):
    """
    Limpa memória de curto prazo de um agente.
    """
    clear_agent_memory(agent_id)
    logger.info(f"Memória do agente {agent_id} limpa com sucesso")
    return {"status": "ok", "message": f"Memória do agente {agent_id} foi limpa"}


@router.post("/collaborate")
async def collaborate(request: CollaborationRequest, db: Session = Depends(get_db)):
    agents = db.query(Agent).filter(Agent.id.in_(request.agent_ids)).all()
    logger.info(f"Listando {len(agents)} agentes para colaboração")
    if not agents:
        logger.warning(f"Nenhum agente encontrado para IDs {request.agent_ids}")
        raise HTTPException(status_code=404, detail="Agents not found")

    async def run_agent_task(agent: Agent):
        logger.info(f"Executando task '{request.task}' para agente {agent.id} ({agent.name})")
        output = await agent.run_task_async(request.task)
        logger.info(f"Task concluída para agente {agent.id}: output='{output}'")
        return {"agent_id": agent.id, "agent_name": agent.name, "output": output}

    results = await asyncio.gather(*(run_agent_task(agent) for agent in agents))
    final_output = " | ".join([r["output"] for r in results])
    logger.info(f"Task '{request.task}' finalizada. Resultado final: {final_output}")

    return {"task": request.task, "results": results, "final_output": final_output}


# ------------------------
# COST TRACKING
# ------------------------

def register_execution_cost(db: Session, execution_id: int, agent_id: int, cost: float):
    logger.info(f"Registrando custo de execução: execution_id={execution_id}, agent_id={agent_id}, cost={cost}")
    execution_cost = ExecutionCost(
        execution_id=execution_id,
        agent_id=agent_id,
        cost=cost
    )
    db.add(execution_cost)
    db.commit()
    logger.info(f"Custo registrado com sucesso para agent_id={agent_id}")
