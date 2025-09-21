from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ExecutionBase(BaseModel):
    agent_id: int
    input: str


class ExecutionCreateSchema(ExecutionBase):
    """
    Schema de entrada para criar/rodar uma execução.
    """
    pass


class ExecutionResponseSchema(BaseModel):
    """
    Schema de resposta ao consultar ou criar uma execução.
    """
    id: int
    agent_id: int
    input: str
    output: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True