from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.prompt import Prompt
from app.db.session import get_db
from app.schemas.prompt import PromptSchema
from typing import List
from app.models.agent import Agent
from app.core.logging import get_logger

router = APIRouter(prefix="/prompts", tags=["prompts"])
logger = get_logger(__name__)

@router.post("/", response_model=PromptSchema)
def create_prompt(prompt: PromptSchema, db: Session = Depends(get_db), user_id: int | None = None):
    logger.info(f"Criando prompt '{prompt.name}'")
    db_prompt = Prompt(
        name=prompt.name,
        description=prompt.description,
        content=prompt.content,
        version=prompt.version,
    )
    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)
    logger.info(f"Prompt criado com sucesso: ID {db_prompt.id}")
    return db_prompt

@router.get("/", response_model=List[PromptSchema])
def list_prompts(db: Session = Depends(get_db)):
    prompts = db.query(Prompt).all()
    logger.info(f"Listando {len(prompts)} prompts cadastrados")
    return prompts

@router.post("/test/{agent_id}/{prompt_id}")
def test_prompt(agent_id: int, prompt_id: int, db: Session = Depends(get_db)):
    logger.info(f"Testando prompt {prompt_id} com agente {agent_id}")
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()

    if not agent or not prompt:
        logger.warning(f"Agente {agent_id} ou Prompt {prompt_id} não encontrado")
        raise HTTPException(status_code=404, detail="Agente ou Prompt não foi encontrado.")
    
    output = f"Agente: {agent.name} processando: {prompt.content}"
    logger.info(f"Test prompt concluído: {output}")

    return {
        "agent_id": agent.id,
        "agent_name": agent.name,
        "prompt_id": prompt.id,
        "prompt_name": prompt.name,
        "output": output
    }
