from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.execution import ExecutionCreateSchema, ExecutionResponseSchema
from app.services.execution_service import ExecutionService
from app.core.logging import get_logger

router = APIRouter(prefix="/executions", tags=["Execuções"])
logger = get_logger(__name__)

execution_service = ExecutionService()


@router.post(
    "/",
    response_model=ExecutionResponseSchema,
    summary="Executar um agente"
)
def run_execution(exec: ExecutionCreateSchema, db: Session = Depends(get_db)):
    """
    Executa um agente com a entrada fornecida e retorna a saída
    registrada no banco de dados.
    """
    try:
        return execution_service.run(db, exec)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao executar agente {exec.agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno ao executar agente")


@router.get(
    "/",
    response_model=List[ExecutionResponseSchema],
    summary="Listar execuções"
)
def list_executions(
    db: Session = Depends(get_db),
    agent_id: Optional[int] = None
):
    """
    Lista todas as execuções registradas.
    Se `agent_id` for fornecido, lista apenas execuções do agente específico.
    """
    return execution_service.list_executions(db, agent_id)


@router.get(
    "/{execution_id}",
    response_model=ExecutionResponseSchema,
    summary="Buscar execução por ID"
)
def get_execution(execution_id: int, db: Session = Depends(get_db)):
    """
    Retorna os detalhes de uma execução pelo seu ID.
    """
    exec = execution_service.get_execution(db, execution_id)
    if not exec:
        raise HTTPException(status_code=404, detail="Execução não encontrada")
    return exec


@router.delete(
    "/{execution_id}",
    summary="Remover execução"
)
def delete_execution(execution_id: int, db: Session = Depends(get_db)):
    """
    Remove uma execução (e seus custos associados) pelo ID.
    """
    success = execution_service.delete_execution(db, execution_id)
    if not success:
        raise HTTPException(status_code=404, detail="Execução não encontrada")
    return {"status": "deleted", "execution_id": execution_id}
