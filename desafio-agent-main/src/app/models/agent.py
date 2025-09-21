from sqlalchemy import (
    Column, String, Float, Integer, ForeignKey, Boolean, Text, DateTime, Index
)
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    owner = relationship("User", back_populates="agents")

    model = Column(String(100), nullable=False, default="gpt-3.5")
    temperature = Column(Float, default=0.7)

    provider = Column(String(100), nullable=True)
    base_url = Column(String(255), nullable=True)
    active = Column(Boolean, nullable=False, default=True, index=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    prompts = relationship(
        "Prompt",
        back_populates="agent",
        cascade="all, delete-orphan"
    )

    executions = relationship(
        "Execution",
        back_populates="agent",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<Agent(id={self.id}, name={self.name}, model={self.model}, "
            f"active={self.active})>"
        )

Index("idx_agent_owner_active", Agent.owner_id, Agent.active)