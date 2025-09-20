from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.agent import Agent
from app.schemas.agent import AgentSchema, AgentCreate
from pydantic import BaseModel
import asyncio
from app.models.execution_cost import ExecutionCost
from app.core.logging import get_logger

router = APIRouter(prefix="/agents", tags=["agents"])
logger = get_logger(__name__)

class CollaborationRequest(BaseModel):
    task: str
    agent_ids: List[int]


@router.post("/", response_model=AgentSchema)
def create_agent(agent: AgentCreate, db: Session = Depends(get_db)):
    logger.info(f"Criando agente: {agent.name} (modelo: {agent.model})")
    db_agent = Agent(
        name=agent.name,
        model=agent.model,
        temperature=agent.temperature,
        owner_id=agent.owner_id,
        prompt_id=agent.prompt_id
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    logger.info(f"Agente criado com sucesso: ID {db_agent.id}")
    return db_agent

@router.get("/", response_model=List[AgentSchema])
def list_agents(db: Session = Depends(get_db)):
    return db.query(Agent).all()

@router.post("/collaborate")
async def collaborate(request: CollaborationRequest, db: Session = Depends(get_db)):
    agents = db.query(Agent).filter(Agent.id.in_(request.agent_ids)).all()
    logger.info(f"Listando {len(agents)} agentes")
    if not agents:
        logger.warning(f"Nenhum agente encontrado para IDs {request.agent_ids}")
        raise HTTPException(status_code=404, detail="Agents not found")

    async def run_agent(agent: Agent):
        logger.info(f"Executando task '{request.task}' para agente {agent.id} ({agent.name})")
        output = await agent.run_task_async(request.task)
        logger.info(f"Task concluída para agente {agent.id}: output='{output}'")
        return {"agent_id": agent.id, "agent_name": agent.name, "output": output}

    results = await asyncio.gather(*(run_agent(agent) for agent in agents))
    final_output = " | ".join([r["output"] for r in results])
    logger.info(f"Task '{request.task}' finalizada. Resultado final: {final_output}")

    return {"task": request.task, "results": results, "final_output": final_output}

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