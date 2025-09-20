import os
from langgraph.graph import Graph

from services.echo_agent import echo_agent
from services.rag_agent import rag_agent

# Lê do .env ou default "openai"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()

if LLM_PROVIDER == "ollama":
    from langchain_ollama import ChatOllama as ChatLLM
else:
    from langchain_openai import ChatOpenAI as ChatLLM


def orchestrator_agent(use_rag: bool = False):
    # Instancia LLM de acordo com provider
    if LLM_PROVIDER == "ollama":
        llm = ChatLLM(model="llama3", temperature=0)
    else:
        llm = ChatLLM(model="gpt-4o-mini", temperature=0)

    graph = Graph()

    @graph.node
    def decide(question: str):
        if use_rag:
            return {"route": "rag", "question": question}
        else:
            return {"route": "echo", "question": question}

    # Importa os sub-agentes
    echo = echo_agent()
    rag = rag_agent()

    # Define entrada e roteamento
    graph.set_entry_point("decide")
    graph.add_conditional_edges(
        "decide",
        lambda x: x["route"],
        {
            "echo": echo.entry_point,
            "rag": rag.entry_point,
        }
    )
    return graph