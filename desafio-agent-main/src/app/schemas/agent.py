from pydantic import BaseModel
from typing import Optional

class AgentSchema(BaseModel):
    id: int
    name: str
    model: str
    temperature: float
    owner_id: int
    prompt_id: Optional[str] = None

    class Config:
        orm_mode = True

class AgentCreate(BaseModel):
    name: str
    model: str
    temperature: float
    owner_id: int
    prompt_id: Optional[str] = None