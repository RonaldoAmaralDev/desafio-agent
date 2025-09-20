from langgraph.graph import Graph

def echo_agent():
    graph = Graph()

    @graph.node
    def responder(question: str) -> str:
        return f"Você perguntou: {question}"

    graph.set_entry_point("responder")
    return graph