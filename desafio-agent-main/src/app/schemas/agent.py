from pydantic import BaseModel
from typing import List, Optional


class AgentBase(BaseModel):
    name: str
    model: str
    temperature: Optional[float] = 0.7
    owner_id: int
    provider: Optional[str] = "ollama"
    base_url: Optional[str] = "http://ollama:11434"


class AgentCreate(AgentBase):
    """
    Schema para criação de agentes.
    """
    pass


class AgentSchema(AgentBase):
    """
    Schema de resposta (com ID).
    """
    id: int

    class Config:
        from_attributes = True


# ------------------------
# Execução de Agentes
# ------------------------
class RunRequest(BaseModel):
    input: str


class RunResponse(BaseModel):
    answer: str
    memory: List[dict] = []
    cost: float = 0.0


# ------------------------
# Colaboração entre agentes
# ------------------------
class CollaborationRequest(BaseModel):
    task: str
    agent_ids: List[int]
