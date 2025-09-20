"""Simple RAG service: query against Chroma + OpenAI LLM.
Replace OPENAI_API_KEY in env before running.
"""
from langchain_community.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import OpenAIEmbeddings, ChatOpenAI


def query_rag(query: str, top_k: int = 4, persist_dir: str = './chroma_db') -> str:
    # Inicializa embeddings (usa OPENAI_API_KEY do env)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # Banco vetorial persistido (Chroma)
    db = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
    retriever = db.as_retriever(search_kwargs={'k': top_k})

    # Modelo LLM via OpenAI
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Cadeia de RAG (pergunta + contexto recuperado)
    chain = ConversationalRetrievalChain.from_llm(llm, retriever)

    # Executa query (sem memória de conversa neste exemplo)
    res = chain.invoke({"question": query})
    return res["answer"]