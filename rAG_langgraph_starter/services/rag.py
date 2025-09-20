"""RAG service with conversation history"""
from langchain_community.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.memory import ConversationBufferMemory

# 🔹 Memória global (guarda o histórico da conversa)
memory = ConversationBufferMemory(
    memory_key="chat_history", 
    return_messages=True
)

def query_rag(query: str, top_k: int = 4, persist_dir: str = './chroma_db') -> str:
    # Inicializa embeddings (usa OPENAI_API_KEY do env)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # Banco vetorial persistido (Chroma)
    db = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
    retriever = db.as_retriever(search_kwargs={'k': top_k})

    # Modelo LLM via OpenAI
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Cadeia de RAG com memória de histórico
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory
    )

    # Executa query (agora com histórico de conversa)
    res = chain.invoke({"question": query})
    return res["answer"] if isinstance(res, dict) else res