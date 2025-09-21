from sqlalchemy.orm import Session
from app.models.prompt import Prompt
from app.schemas.prompt import PromptCreate
from app.models.agent import Agent
from app.core.logging import get_logger

logger = get_logger(__name__)


class PromptService:
    """
    Regras de negócio para Prompts.
    """

    def create_prompt(self, db: Session, prompt_in: PromptCreate) -> Prompt:
        logger.info(f"Criando prompt '{prompt_in.name}' vinculado ao agente {prompt_in.agent_id}")
        prompt = Prompt(
            name=prompt_in.name,
            description=prompt_in.description,
            content=prompt_in.content,
            version=prompt_in.version,
            agent_id=prompt_in.agent_id,
        )
        db.add(prompt)
        db.commit()
        db.refresh(prompt)
        logger.info(f"Prompt criado com sucesso: {prompt.id}")
        return prompt

    def list_prompts(self, db: Session) -> list[Prompt]:
        prompts = db.query(Prompt).all()
        logger.info(f"Listando {len(prompts)} prompts")
        return prompts

    def test_prompt(self, db: Session, agent_id: int, prompt_id: int) -> dict:
        logger.info(f"Testando prompt {prompt_id} com agente {agent_id}")
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()

        if not agent or not prompt:
            logger.warning(f"Agente {agent_id} ou Prompt {prompt_id} não encontrado")
            return None

        output = f"Agente: {agent.name} processando: {prompt.content}"
        logger.info(f"Test prompt concluído: {output}")

        return {
            "agent_id": agent.id,
            "agent_name": agent.name,
            "prompt_id": prompt.id,
            "prompt_name": prompt.name,
            "output": output,
        }
