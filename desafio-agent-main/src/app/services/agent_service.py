from app.models.agent import Agent
from app.db.openai_client import get_chat_completion
from app.core.logging import get_logger

logger = get_logger(__name__)


class AgentService:
    """
    Regras de negócio relacionadas a agentes.
    """

    def create(self, db, data):
        agent = Agent(
            name=data.name,
            model=data.model,
            temperature=data.temperature,
            owner_id=data.owner_id,
            provider=data.provider or "ollama",
            base_url=data.base_url or "http://ollama:11434"
        )
        db.add(agent)
        db.commit()
        db.refresh(agent)
        logger.info(f"Agente criado: {agent.id}")
        return agent

    def list(self, db):
        return db.query(Agent).all()

    async def run_task_async(self, agent: Agent, task: str) -> str:
        """
        Executa uma tarefa usando o agente.
        Integra com OpenAI (ou outro provider configurado).
        """
        logger.info(f"Executando tarefa com o agente {agent.name} (id={agent.id})")

        messages = [
            {
                "role": "system",
                "content": (
                    f"Você é o agente {agent.name}. "
                    "Responda SEMPRE em português do Brasil, "
                    "de forma clara, natural e objetiva."
                ),
            },
            {"role": "user", "content": task},
        ]

        try:
            response = get_chat_completion(
                messages,
                model=agent.model,
                temperature=agent.temperature
            )
            return response
        except Exception as e:
            logger.error(f"Erro ao executar tarefa no agente {agent.id}: {str(e)}")
            raise