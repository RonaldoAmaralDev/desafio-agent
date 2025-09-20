import asyncio
from sqlalchemy import Column, String, Float, Integer, ForeignKey, Boolean, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="agents")

    model = Column(String(100), nullable=False, default="gpt-3.5")
    temperature = Column(Float, default=0.7)

    provider = Column(String(100), nullable=True)
    base_url = Column(String(255), nullable=True)
    active = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)

    prompts = relationship("Prompt", back_populates="agent")

    async def run_task_async(self, task: str) -> str:
        """
        Simula execução assíncrona da tarefa. 
        Substitua aqui pela chamada real da API do agente.
        """
        await asyncio.sleep(1)
        return f"{self.name} processed: {task}"