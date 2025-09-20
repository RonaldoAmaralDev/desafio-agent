import os
from langgraph.graph import Graph
from langchain_community.vectorstores import Chroma

# Lê do .env (default OpenAI se não definido)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()

if LLM_PROVIDER == "ollama":
    from langchain_ollama import OllamaEmbeddings, ChatOllama
else:
    from langchain_openai import OpenAIEmbeddings, ChatOpenAI


def rag_agent(chroma_path: str = "/chroma_db"):
    # Embeddings
    if LLM_PROVIDER == "ollama":
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
    else:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    vectordb = Chroma(persist_directory=chroma_path, embedding_function=embeddings)

    # LLM
    if LLM_PROVIDER == "ollama":
        llm = ChatOllama(model="llama3", temperature=0)
    else:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

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