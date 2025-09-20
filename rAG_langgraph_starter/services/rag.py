import os
from langchain_community.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain_ollama import ChatOllama, OllamaEmbeddings


def query_rag(query: str, top_k: int = 4, persist_dir: str = './chroma_db') -> str:
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")

    # Embeddings
    embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=ollama_url)

    # Banco vetorial
    db = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
    retriever = db.as_retriever(search_kwargs={'k': top_k})

    # Modelo LLM
    llm = ChatOllama(model="llama3", temperature=0, base_url=ollama_url)

    # Prompt com 'context'
    QA_PROMPT = PromptTemplate.from_template("""
    Você é um assistente especializado que **sempre responde em português do Brasil**.

    Use o seguinte contexto para formular a resposta:
    {context}

    Histórico da conversa:
    {chat_history}

    Pergunta:
    {question}

    Resposta em português:
    """)

    # Cadeia de RAG com prompt customizado
    chain = ConversationalRetrievalChain.from_llm(
        llm,
        retriever,
        combine_docs_chain_kwargs={"prompt": QA_PROMPT}
    )

    res = chain.invoke({"question": query, "chat_history": []})
    return res["answer"]