import redis
import json

redis = redis.Redis(host="localhost", port=6379, db=0)

def cache_metadata(key: str, data: dict, ttl: int = 3600):
    redis.set(key, json.dumps(data), ex=ttl)

def get_cached_metadata(key: str):
    value = redis.get(key)
    return json.loads(value) if value else None
