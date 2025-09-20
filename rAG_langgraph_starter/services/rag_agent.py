from langgraph.graph import Graph
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.vectorstores import Chroma

def rag_agent(chroma_path: str = "/chroma_db"):
    embeddings = OpenAIEmbeddings()
    vectordb = Chroma(persist_directory=chroma_path, embedding_function=embeddings)
    llm = ChatOpenAI(model="gpt-4o-mini")

    graph = Graph()

    @graph.node
    def retrieve(question: str):
        docs = vectordb.similarity_search(question, k=3)
        return {"question": question, "docs": docs}

    @graph.node
    def generate(context: dict):
        docs_text = "\n".join([d.page_content for d in context["docs"]])
        prompt = f"Contexto:\n{docs_text}\n\nPergunta: {context['question']}"
        response = llm.predict(prompt)
        return response

    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "generate")
    return graph