from pydantic import BaseModel

class AgentSchema(BaseModel):
    id: int
    name: str
    model: str
    temperature: float
    owner_id: int

    class Config:
        orm_mode = True


class AgentCreate(BaseModel):
    name: str
    model: str
    temperature: float
    owner_id: int