from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PromptSchema(BaseModel):
    id: Optional[int] = None
    user_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    content: str
    version: Optional[str] = "1.0"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True