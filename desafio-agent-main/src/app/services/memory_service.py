from collections import defaultdict
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class MemoryService:
    """
    Serviço simples de memória de agentes em runtime (in-memory).
    Guarda interações (input/output) de cada agente.
    Opcionalmente respeita limite e TTL.
    """

    def __init__(self):
        self._store = defaultdict(list)

    def add_interaction(self, agent_id: int, user_input: str, agent_output: str):
        """
        Salva uma interação no histórico de memória de um agente.
        """
        logger.debug(f"Memória: adicionando interação para agent_id={agent_id}")
        history = self._store[agent_id]

        history.append({"input": user_input, "output": agent_output})

        if settings.AGENT_MEMORY_LIMIT and len(history) > settings.AGENT_MEMORY_LIMIT:
            self._store[agent_id] = history[-settings.AGENT_MEMORY_LIMIT :]

    def get(self, agent_id: int) -> list[dict]:
        """
        Recupera todo histórico de memória de um agente.
        """
        return self._store.get(agent_id, [])

    def clear(self, agent_id: int):
        """
        Limpa memória de um agente.
        """
        if agent_id in self._store:
            logger.info(f"Memória limpa para agent_id={agent_id}")
            del self._store[agent_id]

    def clear_all(self):
        """
        Limpa memória de todos os agentes.
        """
        logger.info("Memória limpa para todos os agentes")
        self._store.clear()