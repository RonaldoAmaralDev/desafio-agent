from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class PromptSchema(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    content: str

    class Config:
        from_attributes = True

class AgentExportSchema(BaseModel):
    id: int
    name: str
    description: Optional[str]
    model: str
    temperature: float
    owner_id: int
    provider: Optional[str]
    base_url: Optional[str]
    active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    prompts: List[PromptSchema] = Field(default_factory=list)

    class Config:
        from_attributes = True

class AgentImportSchema(BaseModel):
    name: str
    description: Optional[str]
    model: str
    temperature: float
    owner_id: int
    provider: Optional[str] = None
    base_url: Optional[str] = None
    active: bool = True
    prompts: List[PromptSchema] = Field(default_factory=list)


class AgentsExportPackage(BaseModel):
    version: int = 1
    exported_at: datetime
    agents: List[AgentExportSchema]