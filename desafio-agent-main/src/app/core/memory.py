import json
from typing import List, Dict
from app.core.redis import redis_client

MEMORY_LIMIT = 5  # últimas 5 interações

def save_agent_memory(agent_id: int, user_input: str, agent_output: str):
    """
    Salva interação no histórico de memória de curto prazo do agente.
    """
    key = f"agent:{agent_id}:memory"
    entry = json.dumps({"input": user_input, "output": agent_output})
    redis_client.lpush(key, entry)
    redis_client.ltrim(key, 0, MEMORY_LIMIT - 1)

def get_agent_memory(agent_id: int) -> List[Dict]:
    """
    Recupera histórico recente do agente (lista de interações).
    """
    key = f"agent:{agent_id}:memory"
    raw = redis_client.lrange(key, 0, -1)
    return [json.loads(r) for r in raw] if raw else []

def clear_agent_memory(agent_id: int):
    """
    Limpa memória do agente (se necessário).
    """
    key = f"agent:{agent_id}:memory"
    redis_client.delete(key)