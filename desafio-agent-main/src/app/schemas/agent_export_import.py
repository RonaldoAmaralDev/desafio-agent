from pydantic import BaseModel
from typing import Optional, List

class PromptExportSchema(BaseModel):
    id: int
    content: str

    class Config:
        orm_mode = True

class AgentExportSchema(BaseModel):
    id: int
    name: str
    model: str
    temperature: float
    owner_id: int
    prompt_id: Optional[str]
    prompts: List[PromptExportSchema] = []

class AgentImportSchema(BaseModel):
    name: str
    model: str
    temperature: float
    owner_id: int
    prompt_id: Optional[str]
    prompts: List[PromptExportSchema] = []