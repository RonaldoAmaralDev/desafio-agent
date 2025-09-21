from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.services.agent_export_service import AgentExportService
from app.schemas.agent_export import AgentsExportPackage, AgentImportSchema

router = APIRouter(prefix="/agents", tags=["Agents Export/Import"])


@router.get("/export", response_model=AgentsExportPackage, summary="Exportar todos os agentes")
def export_all(db: Session = Depends(get_db)):
    """
    Exporta todos os agentes com seus respectivos prompts.
    """
    return AgentExportService.export_all(db)


@router.get("/{agent_id}/export", response_model=AgentsExportPackage, summary="Exportar agente específico")
def export_one(agent_id: int, db: Session = Depends(get_db)):
    """
    Exporta um agente específico (incluindo seus prompts).
    """
    try:
        return AgentExportService.export_one(db, agent_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Agente não encontrado")


@router.post("/import", summary="Importar agentes")
def import_agents(agents: list[AgentImportSchema], db: Session = Depends(get_db)):
    """
    Importa agentes e prompts a partir de um pacote exportado.
    Retorna estatísticas de criação/atualização.
    """
    try:
        stats = AgentExportService.import_agents(db, agents)
        return {"status": "ok", "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao importar agentes: {str(e)}")
