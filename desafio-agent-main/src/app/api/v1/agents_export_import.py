from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from src.app.db.session import get_db
from src.app.models.agent import Agent
from src.app.models.prompt import Prompt
from src.app.schemas.agent_export_import import AgentExportSchema, AgentImportSchema
from src.app.core.logging import get_logger
import json

router = APIRouter(prefix="/agents", tags=["Agents Export/Import"])
logger = get_logger(__name__)
# -----------------------------
# Export endpoint
# -----------------------------
@router.get("/export/{agent_id}", response_model=AgentExportSchema)
def export_agent(agent_id: int, db: Session = Depends(get_db)):
    logger.info(f"Solicitação de exportação do agente {agent_id}")
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        logger.warning(f"Agente {agent_id} não encontrado")
        raise HTTPException(status_code=404, detail="Agente não foi encontrado.")
    
    # Inclui prompts relacionados
    prompts = agent.prompts if hasattr(agent, "prompts") else []
    logger.info(f"Exportando agente {agent_id} com {len(prompts)} prompts")

    return {
        "id": agent.id,
        "name": agent.name,
        "model": agent.model,
        "temperature": agent.temperature,
        "owner_id": agent.owner_id,
        "prompt_id": agent.prompt_id,
        "prompts": prompts
    }

# -----------------------------
# Import endpoint
# -----------------------------
@router.post("/import")
def import_agent(file: UploadFile = File(...), db: Session = Depends(get_db)):
    logger.info(f"Solicitação de importação de agente via arquivo: {file.filename}")
    try:
        data = json.load(file.file)
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar JSON: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON file")

    agent = Agent(
        name=data["name"],
        model=data["model"],
        temperature=data["temperature"],
        owner_id=data["owner_id"],
        prompt_id=data.get("prompt_id")
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    logger.info(f"Agente '{agent.name}' importado com sucesso com ID {agent.id}")

    # Cria prompts associados
    prompts_imported = 0
    for p in data.get("prompts", []):
        prompt = Prompt(
            agent_id=agent.id,
            content=p["content"]
        )
        db.add(prompt)
        prompts_imported += 1
    db.commit()
    logger.info(f"{prompts_imported} prompts associados importados para o agente {agent.id}")

    return {"message": "Agente importado com sucesso!", "agent_id": agent.id}