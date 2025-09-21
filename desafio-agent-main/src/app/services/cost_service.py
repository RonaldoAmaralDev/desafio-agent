from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.execution_cost import ExecutionCost
from app.models.agent import Agent
from app.core.logging import get_logger

logger = get_logger(__name__)


class CostService:
    def register_execution_cost(self, db: Session, execution_id: int, agent_id: int, cost: float):
        execution_cost = ExecutionCost(
            execution_id=execution_id,
            agent_id=agent_id,
            cost=cost
        )
        db.add(execution_cost)
        db.commit()
        logger.info(f"Custo registrado: agent_id={agent_id}, execution_id={execution_id}, cost={cost}")

    def list_agent_costs(self, db: Session, agent_id: int):
        return db.query(ExecutionCost).filter(ExecutionCost.agent_id == agent_id).all()

    def summarize_agent_costs(self, db: Session, agent_id: int):
        total, avg, count = db.query(
            func.sum(ExecutionCost.cost),
            func.avg(ExecutionCost.cost),
            func.count(ExecutionCost.id)
        ).filter(ExecutionCost.agent_id == agent_id).first()

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
