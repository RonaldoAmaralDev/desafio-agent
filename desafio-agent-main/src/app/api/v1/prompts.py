from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.db import get_db
from app.schemas.prompt import PromptSchema, PromptCreate
from app.services.prompt_service import PromptService

router = APIRouter(prefix="/prompts", tags=["Prompts"])
prompt_service = PromptService()


@router.post("/", response_model=PromptSchema, summary="Criar novo prompt")
def create_prompt(prompt: PromptCreate, db: Session = Depends(get_db)):
    return prompt_service.create_prompt(db, prompt)


@router.get("/", response_model=List[PromptSchema], summary="Listar prompts")
def list_prompts(db: Session = Depends(get_db)):
    return prompt_service.list_prompts(db)


@router.post("/test/{agent_id}/{prompt_id}", summary="Testar execução de um prompt em um agente")
def test_prompt(agent_id: int, prompt_id: int, db: Session = Depends(get_db)):
    result = prompt_service.test_prompt(db, agent_id, prompt_id)
    if not result:
        raise HTTPException(status_code=404, detail="Agente ou Prompt não foi encontrado.")
    return result
