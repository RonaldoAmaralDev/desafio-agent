import os
import json
from app.models.execution import Execution
from app.services.execution_service import ExecutionService
from app.services.cost_service import CostService
from app.services.memory_service import MemoryService
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

execution_service = ExecutionService()
cost_service = CostService()
memory_service = MemoryService()


class AgentExecutionService:
    """
    Serviço para rodar agentes em modo streaming e registrar execuções/custos.
    """

    def run_stream(self, db, agent, user_input: str):
        full_answer, cost, usage = "", 0.0, {}

        history = memory_service.get(agent.id) or ""
        final_input = f"Histórico da conversa:\n{history}\n\nUsuário: {user_input}\nAgente:"

        if agent.provider == "ollama":
            llm = ChatOllama(
                model=agent.model,
                base_url=agent.base_url,
                temperature=agent.temperature or 0
            )
            for chunk in llm.stream(final_input):
                token = chunk.content or ""
                full_answer += token
                yield {"type": "token", "content": token}

            cost = len(full_answer) * 0.001

        elif agent.provider == "openai":
            llm = ChatOpenAI(
                model=agent.model,
                api_key=os.getenv("OPENAI_API_KEY"),
                temperature=agent.temperature or 0
            )
            for chunk in llm.stream(final_input):
                token = chunk.content or ""
                full_answer += token
                yield {"type": "token", "content": token}

                if hasattr(chunk, "response_metadata"):
                    usage = chunk.response_metadata.get("token_usage", {}) or usage

            cost = self._calculate_openai_cost(agent.model, usage)

        else:
            yield {"type": "error", "message": f"Provider {agent.provider} não suportado"}
            return

        # 🔹 Salva execução e memória
        execution = execution_service.create_execution(db, agent, user_input, full_answer, cost)
        memory_service.add_interaction(agent.id, user_input, full_answer)
        history = memory_service.get(agent.id)

        yield {
            "type": "end",
            "answer": full_answer,
            "memory": history,
            "cost": cost,
            "agent_name": agent.name,
            "provider": agent.provider,
            "model": agent.model,
            "execution_id": execution.id
        }

    def _calculate_openai_cost(self, model: str, usage: dict) -> float:
        OPENAI_PRICING = {
            "gpt-4o": {"prompt": 0.005, "completion": 0.015},
            "gpt-4o-mini": {"prompt": 0.003, "completion": 0.006},
        }
        pricing = OPENAI_PRICING.get(model)
        if not pricing:
            return 0.0
        prompt_cost = (usage.get("prompt_tokens", 0) / 1000) * pricing["prompt"]
        completion_cost = (usage.get("completion_tokens", 0) / 1000) * pricing["completion"]
        return round(prompt_cost + completion_cost, 6)