# services/redis_service.py

import redis.asyncio as redis
from config import settings

# Initialize a singleton Redis client instance
redis_client = redis.from_url(settings.redis_url)
