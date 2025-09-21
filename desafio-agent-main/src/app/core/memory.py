import json
from typing import List, Dict
from app.core.redis import redis_client
from app.core.config import settings

# Limite de memória (configurável via .env)
MEMORY_LIMIT = settings.AGENT_MEMORY_LIMIT
MEMORY_TTL = settings.AGENT_MEMORY_TTL  # expiração opcional em segundos

class AgentMemory:
    """
    Gerenciador de memória de curto prazo dos agentes.
    Usa Redis para armazenar interações recentes.
    """

    @staticmethod
    def _key(agent_id: int) -> str:
        return f"{settings.APP_NAME.lower().replace(' ', '-')}:agent:{agent_id}:memory"

    @classmethod
    def save(cls, agent_id: int, user_input: str, agent_output: str):
        entry = json.dumps({"input": user_input, "output": agent_output})
        key = cls._key(agent_id)

        redis_client.lpush(key, entry)
        redis_client.ltrim(key, 0, MEMORY_LIMIT - 1)

        if MEMORY_TTL > 0:
            redis_client.expire(key, MEMORY_TTL)

    @classmethod
    def get(cls, agent_id: int) -> List[Dict]:
        key = cls._key(agent_id)
        raw = redis_client.lrange(key, 0, -1)
        return [json.loads(r) for r in raw] if raw else []

    @classmethod
    def clear(cls, agent_id: int):
        redis_client.delete(cls._key(agent_id))