import os
from langchain_community.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain_ollama import ChatOllama, OllamaEmbeddings

def query_rag(query: str, top_k: int = 4, persist_dir: str = './chroma_db') -> str:
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")

    embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=ollama_url)

    db = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
    retriever = db.as_retriever(search_kwargs={'k': top_k})

    llm = ChatOllama(model="llama3", temperature=0, base_url=ollama_url)

    chain = ConversationalRetrievalChain.from_llm(llm, retriever)

    res = chain.invoke({"question": query, "chat_history": []})
    return res["answer"]