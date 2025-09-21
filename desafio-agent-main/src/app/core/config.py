from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List

class Settings(BaseSettings):
    # --------------------
    # App
    # --------------------
    APP_NAME: str = Field("Desafio Agent", description="Nome da aplicação")
    APP_ENV: str = Field("development", description="Ambiente de execução")
    APP_DEBUG: bool = Field(True, description="Debug mode")
    APP_PORT: int = Field(8000, description="Porta da API")

    # --------------------
    # Segurança
    # --------------------
    SECRET_KEY: str = Field(..., description="Chave secreta usada para JWT")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, description="Expiração do token em minutos")

    # --------------------
    # Banco de dados
    # --------------------
    DATABASE_URL: str = Field(..., description="URL de conexão com o banco")
    DATABASE_HOST: str = Field("db", description="Host do banco de dados")
    DATABASE_PORT: int = Field("5432", description="Porta do banco de dados")
    DATABASE_USER: str = Field("postgres", description="Usuário do banco de dados")
    DATABASE_PASSWORD: str = Field("postgres", description="Senha do banco de dados")
    DATABASE_NAME: str = Field("postgres", description="Nome do banco de dados")

    # URL montada automaticamente
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+psycopg2://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"

    # --------------------
    # REDIS
    # --------------------
    REDIS_URL: str | None = Field(None, description="URL do Redis (opcional)")
    REDIS_HOST: str | None = Field("localhost", description="Host do Redis (opcional)")
    redis_port: int | None = Field(6379, description="Porta do Redis (opcional)")

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/0"

    # --------------------
    # Prometheus
    # --------------------
    #  
    prometheus_port: int | None = Field(9090)

    # --------------------
    # CORS
    # --------------------
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost"]

    # --------------------
    # Logging
    # --------------------
    LOG_DIR: str = Field("/tmp/desafio-agent-logs", description="Diretório dos logs")
    LOG_LEVEL: str = Field("INFO", description="Nível de log (DEBUG, INFO, WARNING, ERROR)")
    LOG_MAX_BYTES: int = Field(10 * 1024 * 1024, description="Tamanho máximo do log em bytes")
    LOG_BACKUP_COUNT: int = Field(5, description="Número de arquivos de backup")

    # --------------------
    # AGENT MEMORY
    # --------------------
    AGENT_MEMORY_LIMIT: int = Field(5, description="Número máximo de interações salvas na memória do agente")
    AGENT_MEMORY_TTL: int = Field(0, description="Tempo de expiração da memória em segundos (0 = infinito)")

    # --------------------
    # API
    # --------------------
    API_VERSION: str = Field("v1", description="Versão da API")

    # --------------------
    # OPENAI GPT
    # --------------------
    OPENAI_API_KEY: str | None = Field(None, description="Chave de API do OpenAI")
    OPENAI_MODEL: str = Field("gpt-4o-mini", description="Modelo padrão do OpenAI")

    # --------------------
    # RAG / Ollama / Chroma / LLM
    # --------------------
    OLLAMA_BASE_URL: str = Field("http://ollama:11434", description="URL base do Ollama")
    OLLAMA_EMBED_MODEL: str = Field("nomic-embed-text", description="Modelo de embeddings")
    OLLAMA_MODEL: str = Field("gemma:2b-instruct", description="Modelo do Ollama usado no RAG")
    OLLAMA_TEMPERATURE: float = Field(0.0, description="Temperatura do modelo Ollama")
    RAG_TOP_K: int = Field(4, description="Número de documentos recuperados no RAG")
    CHROMA_PERSIST_DIR: str = Field("./chroma_db", description="Diretório para persistência do Chroma")
    LLM_PROVIDER: str = Field("./llm_provider", description="Qual provider é o padrão")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
