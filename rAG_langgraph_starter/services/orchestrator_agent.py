from langgraph.graph import Graph
from langchain_openai import ChatOpenAI

from services.echo_agent import echo_agent
from services.rag_agent import rag_agent

def orchestrator_agent(use_rag: bool = False):
    llm = ChatOpenAI(model="gpt-4o-mini")
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