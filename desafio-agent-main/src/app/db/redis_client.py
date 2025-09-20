import os
import redis

REDIS_URL = os.environ.get("REDIS_URL")
redis_client = redis.from_url(REDIS_URL)