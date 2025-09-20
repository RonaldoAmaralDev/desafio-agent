from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.agent_export_service import AgentExportService
from app.schemas.agent_export import AgentsExportPackage, AgentImportSchema

router = APIRouter(prefix="/api/v1/agents", tags=["Agents Export/Import"])

@router.get("/export", response_model=AgentsExportPackage)
def export_all(db: Session = Depends(get_db)):
    return AgentExportService.export_all(db)


@router.get("/{agent_id}/export", response_model=AgentsExportPackage)
def export_one(agent_id: int, db: Session = Depends(get_db)):
    try:
        return AgentExportService.export_one(db, agent_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Agent not found")


@router.post("/import")
def import_agents(agents: list[AgentImportSchema], db: Session = Depends(get_db)):
    stats = AgentExportService.import_agents(db, agents)
    return {"status": "ok", "stats": stats}