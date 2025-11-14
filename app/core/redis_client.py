import redis.asyncio as aioredis
from app.core.config import settings

redis_client = aioredis.from_url(settings.REDIS_URL or "redis://localhost:6379", decode_responses=True) 
