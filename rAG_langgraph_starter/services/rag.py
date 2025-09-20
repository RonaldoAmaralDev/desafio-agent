"""Simple RAG service: query against Chroma + OpenAI LLM.
Replace OPENAI_API_KEY in env before running.
"""
from typing import List
import os

def query_rag(query: str, top_k: int = 4, persist_dir: str = './chroma_db') -> str:
    try:
        from langchain.embeddings import OpenAIEmbeddings
        from langchain.vectorstores import Chroma
        from langchain.llms import OpenAI
        from langchain.chains import ConversationalRetrievalChain
    except Exception as e:
        raise RuntimeError('Missing langchain/OpenAI/chromadb libraries. Install them.') from e

    embeddings = OpenAIEmbeddings()
    db = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
    retriever = db.as_retriever(search_kwargs={'k': top_k})
    llm = OpenAI(temperature=0)

    chain = ConversationalRetrievalChain.from_llm(llm, retriever)
    # no conversation memory in this simple example
    res = chain.run(query)
    return res