import json
import redis.asyncio as redis
from app.config.config import settings

redis_client = redis.Redis.from_url(settings.redis_cache_url)

async def get_cached_metadata(key: str):
    try:
        data = await redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        print(f"Redis GET error: {e}")
        return None


async def cache_metadata(key: str, value: dict, expire: int = 3600):
    try:
        await redis_client.set(key, json.dumps(value), ex=expire)
    except Exception as e:
        print(f"Redis SET error: {e}")

