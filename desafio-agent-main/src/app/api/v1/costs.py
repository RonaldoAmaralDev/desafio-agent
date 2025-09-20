from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.app.db.session import get_db
from src.app.models.execution_cost import ExecutionCost
from src.app.schemas.execution_cost import ExecutionCostSchema, AgentCostResponse
from src.app.core.logging import get_logger

router = APIRouter(prefix="/costs", tags=["Costs"])
logger = get_logger(__name__)

@router.get("/agent/{agent_id}", response_model=AgentCostResponse)
def get_agent_costs(agent_id: int, db: Session = Depends(get_db)):
    logger.info(f"Consultando custos do agente {agent_id}")
    costs = db.query(ExecutionCost).filter(ExecutionCost.agent_id == agent_id).all()
    total_cost = sum(c.cost for c in costs)
    logger.info(f"Agente {agent_id} possui {len(costs)} execuções, custo total: {total_cost}")
    return {"agent_id": agent_id, "total_cost": total_cost, "executions": costs}