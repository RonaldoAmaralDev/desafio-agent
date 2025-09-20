from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from pydantic import BaseModel
import asyncio

from app.db.session import get_db
from app.models.agent import Agent
from app.models.execution_cost import ExecutionCost
from app.models.execution import Execution
from app.schemas.agent import AgentSchema, AgentCreate
from app.core.logging import get_logger
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
import json
import os

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
    cost: float = 0.0

# Tabela de preços (USD por 1K tokens)
OPENAI_PRICING = {
    "gpt-4o": {"prompt": 0.005, "completion": 0.015},
    "gpt-4o-mini": {"prompt": 0.003, "completion": 0.006},
}

def calculate_openai_cost(model: str, usage: dict) -> float:
    """
    Calcula custo em USD baseado no modelo e uso de tokens.
    """
    pricing = OPENAI_PRICING.get(model)
    if not pricing:
        return 0.0

    prompt_cost = (usage.get("prompt_tokens", 0) / 1000) * pricing["prompt"]
    completion_cost = (usage.get("completion_tokens", 0) / 1000) * pricing["completion"]
    return round(prompt_cost + completion_cost, 6)

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


@router.post("/{agent_id}/run/stream")
def run_agent_stream(agent_id: int, payload: RunRequest, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agente não encontrado")

    try:
        def generate():
            full_answer = ""

            if agent.provider == "ollama":
                # Streaming nativo do Ollama
                llm = ChatOllama(
                    model=agent.model,
                    base_url=agent.base_url,
                    temperature=agent.temperature or 0
                )
                for chunk in llm.stream(payload.input):
                    token = chunk.content or ""
                    full_answer += token
                    yield json.dumps(
                        {"type": "token", "content": token},
                        ensure_ascii=False
                    ) + "\n"

                # custo simbólico
                cost = len(full_answer) * 0.001

            elif agent.provider == "openai":
                llm = ChatOpenAI(
                    model=agent.model,
                    api_key=os.getenv("OPENAI_API_KEY"),
                    temperature=agent.temperature or 0
                )
                response = llm.invoke(payload.input)
                text = response.content if hasattr(response, "content") else str(response)

                for token in text.split(" "):
                    full_answer += token + " "
                    yield json.dumps(
                        {"type": "token", "content": token + " "},
                        ensure_ascii=False
                    ) + "\n"

                # custo real baseado em tokens
                usage = response.response_metadata.get("token_usage", {})
                cost = calculate_openai_cost(agent.model, usage)

            else:
                raise HTTPException(status_code=400, detail=f"Provider {agent.provider} não suportado")

            # -------------------------
            # registrar execução e custo
            execution = Execution(agent_id=agent.id, input=payload.input, output=full_answer)
            db.add(execution)
            db.commit()
            db.refresh(execution)

            register_execution_cost(db, execution.id, agent.id, cost)
            save_agent_memory(agent.id, payload.input, full_answer)
            history = get_agent_memory(agent.id)

            # enviar evento final
            yield json.dumps(
                {
                    "type": "end",
                    "answer": full_answer,
                    "memory": history,
                    "cost": cost,
                    "agent_name": agent.name,
                    "provider": agent.provider,
                    "model": agent.model
                },
                ensure_ascii=False
            ) + "\n"

        return StreamingResponse(generate(), media_type="application/x-ndjson")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no streaming: {e}")


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


@router.get("/{agent_id}/costs")
def list_agent_costs(agent_id: int, db: Session = Depends(get_db)):
    """
    Lista todas as execuções e custos de um agente.
    """
    costs = db.query(ExecutionCost).filter(ExecutionCost.agent_id == agent_id).all()
    if not costs:
        raise HTTPException(status_code=404, detail="Nenhum custo encontrado para este agente")
    
    return [
        {
            "execution_id": c.execution_id,
            "cost": c.cost,
            "created_at": c.created_at
        }
        for c in costs
    ]


@router.get("/{agent_id}/costs/summary")
def summarize_agent_costs(agent_id: int, db: Session = Depends(get_db)):
    """
    Retorna o custo total, estatísticas e breakdown por provider.
    """
    # total geral
    total, avg, count = db.query(
        func.sum(ExecutionCost.cost),
        func.avg(ExecutionCost.cost),
        func.count(ExecutionCost.id)
    ).filter(ExecutionCost.agent_id == agent_id).first()

    # breakdown por provider
    breakdown = (
        db.query(Agent.provider, func.sum(ExecutionCost.cost))
        .join(Agent, Agent.id == ExecutionCost.agent_id)
        .filter(ExecutionCost.agent_id == agent_id)
        .group_by(Agent.provider)
        .all()
    )

    provider_costs = {provider: cost or 0 for provider, cost in breakdown}

    return {
        "total_cost": total or 0,
        "average_cost": avg or 0,
        "executions": count or 0,
        "by_provider": provider_costs
    }

def summarize_memory(agent_id: str, memory: list[dict], llm: ChatOllama) -> str:
    """
    Usa o modelo para resumir a memória em poucas frases.
    """
    if not memory:
        return ""

    recent_memory = memory[-10:]
    joined = "\n".join([f"Usuário: {m['input']}\nAssistente: {m['output']}" for m in recent_memory])

    prompt = f"""
    Resuma de forma clara e objetiva a conversa abaixo em no máximo 5 frases.
    Concentre-se no contexto relevante para continuar o diálogo, sem repetir literalmente:

    {joined}
    """

    try:
        summary = llm.invoke(prompt)
        return summary.content if hasattr(summary, "content") else str(summary)
    except Exception:
        return joined