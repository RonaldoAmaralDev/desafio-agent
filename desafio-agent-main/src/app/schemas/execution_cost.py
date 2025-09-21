from pydantic import BaseModel
from typing import List
from datetime import datetime


class ExecutionCostSchema(BaseModel):
    id: int
    execution_id: int
    agent_id: int
    cost: float
    created_at: datetime

    class Config:
        from_attributes = True


class AgentCostResponse(BaseModel):
    agent_id: int
    total_cost: float
    executions: List[ExecutionCostSchema]
