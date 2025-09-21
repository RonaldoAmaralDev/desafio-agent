import redis
from redis.exceptions import ConnectionError
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

def init_redis_client():
    if not settings.REDIS_URL:
        logger.warning("⚠️ Redis desativado: nenhuma REDIS_URL configurada")
        return None

    try:
        client = redis.Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5,
            health_check_interval=30,
        )
        client.ping()
        logger.info(f"✅ Conectado ao Redis: {settings.REDIS_URL}")
        return client
    except ConnectionError as e:
        logger.error(f"❌ Falha ao conectar ao Redis: {e}")
        return None

# único cliente global
redis_client = init_redis_client()