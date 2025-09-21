from sqlalchemy import (
    Column, Integer, Float, ForeignKey, DateTime, func, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base


class ExecutionCost(Base):
    __tablename__ = "execution_costs"

    id = Column(Integer, primary_key=True, autoincrement=True)

    execution_id = Column(Integer, ForeignKey("executions.id"), nullable=False, index=True)
    execution = relationship("Execution", back_populates="costs")

    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False, index=True)
    agent = relationship("Agent")

    cost = Column(Float, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<ExecutionCost(id={self.id}, execution_id={self.execution_id}, cost={self.cost})>"


UniqueConstraint("execution_id", "agent_id", name="uq_execution_agent")

Index("idx_executioncost_execution", ExecutionCost.execution_id)
Index("idx_executioncost_agent", ExecutionCost.agent_id)