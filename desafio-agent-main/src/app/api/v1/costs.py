from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.services.cost_service import CostService
from app.schemas.execution_cost import AgentCostResponse
from app.core.logging import get_logger

router = APIRouter(prefix="/costs", tags=["Custos"])
logger = get_logger(__name__)

cost_service = CostService()


@router.get(
    "/agent/{agent_id}",
    response_model=AgentCostResponse,
    summary="Consultar custos de um agente"
)
def get_agent_costs(agent_id: int, db: Session = Depends(get_db)):
    """
    Retorna os custos totais e execuções detalhadas de um agente específico.
    """
    logger.info(f"Consultando custos do agente {agent_id}")
    costs = cost_service.list_agent_costs(db, agent_id)

    if not costs:
        raise HTTPException(status_code=404, detail="Nenhum custo encontrado para este agente")

    total_cost = sum(c.cost for c in costs)
    logger.info(f"Agente {agent_id} possui {len(costs)} execuções, custo total: {total_cost}")

    return {
        "agent_id": agent_id,
        "total_cost": total_cost,
        "executions": costs
    }