from pydantic import BaseModel
from typing import List

class ExecutionCostSchema(BaseModel):
    id: int
    execution_id: int
    agent_id: int
    cost: float
    created_at: str

    class Config:
        orm_mode = True

class AgentCostResponse(BaseModel):
    agent_id: int
    total_cost: float
    executions: List[ExecutionCostSchema]