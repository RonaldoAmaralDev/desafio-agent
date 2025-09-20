from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, func
from .base import Base

class ExecutionCost(Base):
    __tablename__ = "execution_costs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_id = Column(Integer, ForeignKey("executions.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    cost = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())