import openai
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.execution import Execution
from app.models.execution_cost import ExecutionCost
from app.models.agent import Agent
from app.schemas.execution import ExecutionCreateSchema
from app.core.logging import get_logger

logger = get_logger(__name__)


class ExecutionService:
    """
    Regras de negócio para Execuções de Agentes.
    """

    def create_execution(
        self, db: Session, agent: Agent, input_text: str, output_text: str, cost: float
    ) -> Execution:
        """
        Cria uma nova execução associada a um agente e salva o custo.
        """
        logger.info(f"Criando execução para agente {agent.id} - {agent.name}")

        execution = Execution(
            agent_id=agent.id,
            input=input_text,
            output=output_text,
            created_at=datetime.utcnow(),
        )
        db.add(execution)
        db.flush()

        execution_cost = ExecutionCost(
            execution_id=execution.id,
            agent_id=agent.id,
            cost=cost,
        )
        db.add(execution_cost)

        db.commit()
        db.refresh(execution)

        logger.info(
            f"Execução {execution.id} criada para agente {agent.id} com custo {cost}"
        )

        return execution

    def run(self, db: Session, exec: ExecutionCreateSchema) -> Execution:
        """
        Executa uma entrada usando o agente configurado (via OpenAI)
        e salva a execução com custo estimado.
        """
        agent = db.query(Agent).filter(Agent.id == exec.agent_id).first()
        if not agent:
            logger.warning(f"Agente {exec.agent_id} não encontrado")
            raise ValueError("Agente não foi encontrado.")

        logger.info(
            f"Executando agente {agent.id} ({agent.name}) "
            f"modelo={agent.model}, temp={agent.temperature}"
        )

        # chamada ao OpenAI
        response = openai.ChatCompletion.create(
            model=agent.model,
            messages=[{"role": "user", "content": exec.input}],
            temperature=agent.temperature,
        )
        output = response.choices[0].message.content

        # custo simplificado (pode ser melhorado com token_usage)
        cost = 0.001 * len(output)

        return self.create_execution(db, agent, exec.input, output, cost)

    def get_execution(self, db: Session, execution_id: int) -> Execution | None:
        """
        Recupera uma execução pelo ID.
        """
        return db.query(Execution).filter(Execution.id == execution_id).first()

    def list_executions(self, db: Session, agent_id: int | None = None) -> list[Execution]:
        """
        Lista execuções, opcionalmente filtradas por agente.
        """
        query = db.query(Execution)
        if agent_id:
            query = query.filter(Execution.agent_id == agent_id)
        return query.order_by(Execution.created_at.desc()).all()

    def delete_execution(self, db: Session, execution_id: int) -> bool:
        """
        Remove uma execução e seus custos associados.
        """
        execution = db.query(Execution).filter(Execution.id == execution_id).first()
        if not execution:
            logger.warning(f"Tentativa de deletar execução inexistente id={execution_id}")
            return False

        db.delete(execution)
        db.commit()

        logger.info(f"Execução {execution_id} removida com sucesso")
        return True
