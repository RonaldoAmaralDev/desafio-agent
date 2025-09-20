from pydantic import BaseModel

class ExecutionCreateSchema(BaseModel):
    agent_id: int
    input: str

class ExecutionResponseSchema(BaseModel):
    id: int
    agent_id: int
    input: str
    output: str | None = None

    class Config:
        orm_mode = True