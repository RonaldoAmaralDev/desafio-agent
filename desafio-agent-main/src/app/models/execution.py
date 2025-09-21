from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base


class Execution(Base):
    __tablename__ = "executions"

    id = Column(Integer, primary_key=True, autoincrement=True)

    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False, index=True)
    agent = relationship("Agent", back_populates="executions")

    input = Column(String, nullable=False)
    output = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    costs = relationship(
        "ExecutionCost",
        back_populates="execution",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Execution(id={self.id}, agent_id={self.agent_id}, input={self.input[:20]}...)>"