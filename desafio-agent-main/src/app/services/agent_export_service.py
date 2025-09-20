from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from app.models.agent import Agent
from app.models.prompt import Prompt
from app.schemas.agent_export import (
    AgentsExportPackage,
    AgentExportSchema,
    AgentImportSchema,
)


class AgentExportService:
    @staticmethod
    def export_all(db: Session) -> AgentsExportPackage:
        agents = db.query(Agent).options(joinedload(Agent.prompts)).all()
        return AgentsExportPackage(
            version=1,
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
            raise ValueError("Agent not found")
        return AgentsExportPackage(
            version=1,
            exported_at=datetime.utcnow(),
            agents=[AgentExportSchema.from_orm(agent)],
        )

    @staticmethod
    def import_agents(db: Session, agents: list[AgentImportSchema]) -> dict:
        created, updated = 0, 0
        for incoming in agents:
            agent = (
                db.query(Agent)
                .filter(Agent.name == incoming.name, Agent.owner_id == incoming.owner_id)
                .first()
            )
            if agent:
                # update
                agent.description = incoming.description
                agent.model = incoming.model
                agent.temperature = incoming.temperature
                agent.provider = incoming.provider
                agent.base_url = incoming.base_url
                agent.active = incoming.active
                updated += 1
            else:
                # create
                agent = Agent(
                    name=incoming.name,
                    description=incoming.description,
                    model=incoming.model,
                    temperature=incoming.temperature,
                    owner_id=incoming.owner_id,
                    provider=incoming.provider,
                    base_url=incoming.base_url,
                    active=incoming.active,
                )
                db.add(agent)
                db.flush()
                created += 1

            # prompts
            for pr in incoming.prompts:
                prompt = (
                    db.query(Prompt)
                    .filter(Prompt.agent_id == agent.id, Prompt.name == pr.name)
                    .first()
                )
                if prompt:
                    prompt.description = pr.description
                    prompt.content = pr.content
                else:
                    db.add(
                        Prompt(
                            agent_id=agent.id,
                            name=pr.name,
                            description=pr.description,
                            content=pr.content,
                        )
                    )
        db.commit()
        return {"created": created, "updated": updated}
