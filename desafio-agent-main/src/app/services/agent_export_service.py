from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from app.models.agent import Agent
from app.models.prompt import Prompt
from app.schemas.agent_export import (
    AgentsExportPackage,
    AgentExportSchema,
    AgentImportSchema,
)
from app.core.logging import get_logger

logger = get_logger(__name__)

EXPORT_VERSION = 1

class AgentExportService:
    @staticmethod
    def export_all(db: Session) -> AgentsExportPackage:
        agents = db.query(Agent).options(joinedload(Agent.prompts)).all()
        logger.info(f"Exportando {len(agents)} agentes")
        return AgentsExportPackage(
            version=EXPORT_VERSION,
            exported_at=datetime.utcnow(),
            agents=[AgentExportSchema.from_orm(a) for a in agents],
        )

    @staticmethod
    def export_one(db: Session, agent_id: int) -> AgentsExportPackage:
        agent = (
            db.query(Agent)
            .options(joinedload(Agent.prompts))
            .filter(Agent.id == agent_id)
            .first()
        )
        if not agent:
            logger.warning(f"Tentativa de exportar agente inexistente id={agent_id}")
            raise ValueError("Agente não encontrado")

        logger.info(f"Exportando agente {agent.id} - {agent.name}")
        return AgentsExportPackage(
            version=EXPORT_VERSION,
            exported_at=datetime.utcnow(),
            agents=[AgentExportSchema.from_orm(agent)],
        )

    @staticmethod
    def import_agents(db: Session, agents: list[AgentImportSchema]) -> dict:
        created, updated = 0, 0
        try:
            for incoming in agents:
                agent = (
                    db.query(Agent)
                    .filter(Agent.name == incoming.name, Agent.owner_id == incoming.owner_id)
                    .first()
                )

                if agent:
                    logger.info(f"Atualizando agente existente: {agent.name}")
                    AgentExportService._update_agent(agent, incoming)
                    updated += 1
                else:
                    logger.info(f"Criando novo agente: {incoming.name}")
                    agent = AgentExportService._create_agent(db, incoming)
                    created += 1

                AgentExportService._sync_prompts(db, agent, incoming.prompts)

            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao importar agentes: {str(e)}")
            raise

        return {"created": created, "updated": updated}

    @staticmethod
    def _update_agent(agent: Agent, data: AgentImportSchema):
        agent.description = data.description
        agent.model = data.model
        agent.temperature = data.temperature
        agent.provider = data.provider
        agent.base_url = data.base_url
        agent.active = data.active

    @staticmethod
    def _create_agent(db: Session, data: AgentImportSchema) -> Agent:
        agent = Agent(
            name=data.name,
            description=data.description,
            model=data.model,
            temperature=data.temperature,
            owner_id=data.owner_id,
            provider=data.provider,
            base_url=data.base_url,
            active=data.active,
        )
        db.add(agent)
        db.flush()
        return agent

    @staticmethod
    def _sync_prompts(db: Session, agent: Agent, prompts: list):
        for pr in prompts:
            prompt = (
                db.query(Prompt)
                .filter(Prompt.agent_id == agent.id, Prompt.name == pr.name)
                .first()
            )
            if prompt:
                logger.info(f"Atualizando prompt {pr.name} do agente {agent.id}")
                prompt.description = pr.description
                prompt.content = pr.content
            else:
                logger.info(f"Criando prompt {pr.name} para agente {agent.id}")
                db.add(
                    Prompt(
                        agent_id=agent.id,
                        name=pr.name,
                        description=pr.description,
                        content=pr.content,
                    )
                )
