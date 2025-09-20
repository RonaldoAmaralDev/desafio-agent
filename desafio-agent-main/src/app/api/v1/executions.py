from app.schemas.execution import ExecutionCreateSchema, ExecutionResponseSchema
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.models.execution import Execution
from src.app.models.agent import Agent
import openai
from src.app.core.logging import get_logger

router = APIRouter(prefix="/executions", tags=["executions"])
logger = get_logger(__name__)

@router.post("/", response_model=ExecutionResponseSchema)
def run_execution(exec: ExecutionCreateSchema, db: Session = Depends(get_db)):
    logger.info(f"Solicitação de execução para agente {exec.agent_id} com input: {exec.input}")
    agent = db.query(Agent).filter(Agent.id == exec.agent_id).first()
    if not agent:
        logger.warning(f"Agente {exec.agent_id} não encontrado para execução")
        raise HTTPException(status_code=404, detail="Agente não foi encontrado.")

    logger.info(f"Executando task usando modelo '{agent.model}' com temperatura {agent.temperature}")
    response = openai.ChatCompletion.create(
        model=agent.model,
        messages=[{"role": "user", "content": exec.input}],
        temperature=agent.temperature
    )
    output = response.choices[0].message.content
    logger.info(f"Execução concluída para agente {agent.id}. Output: {output}")

    db_exec = Execution(
        agent_id=agent.id,
        input=exec.input,
        output=output
    )
    db.add(db_exec)
    db.commit()
    db.refresh(db_exec)
    logger.info(f"Execução registrada no banco com ID {db_exec.id} para agente {agent.id}")
    return db_exec

@router.get("/", response_model=List[ExecutionResponseSchema])
def list_executions(db: Session = Depends(get_db)):
    executions = db.query(Execution).all()
    logger.info(f"Listando {len(executions)} execuções registradas")
    return executions