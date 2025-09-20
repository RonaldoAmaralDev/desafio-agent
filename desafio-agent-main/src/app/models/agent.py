from sqlalchemy import Column, String, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    model = Column(String, nullable=False, default="gpt-3.5")
    temperature = Column(Float, default=0.7)
    prompt_id = Column(String, ForeignKey("prompts.id"), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="agents")

    async def run_task_async(self, task: str) -> str:
        """
        Simula execução assíncrona da tarefa. 
        Substitua aqui pela chamada real da API do agente.
        """
        await asyncio.sleep(1)
        return f"{self.name} processed: {task}"