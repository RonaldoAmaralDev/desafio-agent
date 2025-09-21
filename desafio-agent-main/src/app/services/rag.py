import os
from langchain_community.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain_ollama import ChatOllama, OllamaEmbeddings
from app.core.config import settings
from app.core.logging import get_logger
from app.core.memory import AgentMemory

logger = get_logger(__name__)

QA_PROMPT = PromptTemplate.from_template("""
Você é um assistente especializado que **sempre responde em português do Brasil**.

Use o seguinte contexto para formular a resposta:
{context}

Histórico da conversa:
{chat_history}

Pergunta:
{question}

Responda em português de forma clara e objetiva:
""")


class RagService:
    def __init__(self):
        self.ollama_url = settings.OLLAMA_BASE_URL
        self.persist_dir = settings.CHROMA_PERSIST_DIR

        self.embeddings = OllamaEmbeddings(
            model=settings.OLLAMA_EMBED_MODEL,
            base_url=self.ollama_url
        )

        self.db = Chroma(
            persist_directory=self.persist_dir,
            embedding_function=self.embeddings
        )

        self.retriever = self.db.as_retriever(search_kwargs={"k": settings.RAG_TOP_K})

        self.llm = ChatOllama(
            model=settings.OLLAMA_MODEL,
            temperature=settings.OLLAMA_TEMPERATURE,
            base_url=self.ollama_url
        )

    def query_rag(self, query: str, agent_id: int | None = None) -> str:
        """
        Executa uma query RAG e retorna resposta em português.
        """
        chat_history = []
        if agent_id:
            chat_history = AgentMemory.get(agent_id)

        chain = ConversationalRetrievalChain.from_llm(
            self.llm,
            self.retriever,
            combine_docs_chain_kwargs={"prompt": QA_PROMPT}
        )

        try:
            result = chain.invoke({"question": query, "chat_history": chat_history})
            answer = result["answer"]

            logger.info(f"RAG executado (query='{query[:30]}...') → resposta gerada")
            return answer
        except Exception as e:
            logger.error(f"Erro no RAG: {str(e)}")
            raise


__all__ = ["RagService"]