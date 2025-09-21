import openai
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Configura chave da API
if not settings.OPENAI_API_KEY:
    logger.warning("⚠️ Nenhuma OPENAI_API_KEY definida. As chamadas ao OpenAI irão falhar.")

openai.api_key = settings.OPENAI_API_KEY

# Modelo padrão
DEFAULT_MODEL = settings.OPENAI_MODEL or "gpt-4o-mini"

def get_chat_completion(messages, model: str = None, temperature: float = 0.7, max_tokens: int = 500):
    """
    Cria uma resposta do modelo OpenAI com base no histórico de mensagens.
    """
    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY não configurada.")

    response = openai.ChatCompletion.create(
        model=model or DEFAULT_MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response["choices"][0]["message"]["content"]