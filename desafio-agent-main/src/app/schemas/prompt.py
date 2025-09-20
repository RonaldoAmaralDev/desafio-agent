from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PromptBase(BaseModel):
    name: str
    description: Optional[str] = None
    content: str
    version: Optional[str] = "1.0"
    agent_id: Optional[int] = None

class PromptCreate(PromptBase):
    pass

class PromptSchema(PromptBase):
    id: int
    user_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True