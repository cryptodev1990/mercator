import redis as _redis

from app.core.config import get_settings

settings = get_settings()
conn_info = settings.redis_connection

assert conn_info.host
assert conn_info.port
assert conn_info.path

redis = _redis.Redis(
    host=conn_info.host,
    port=int(conn_info.port),
    db=int(conn_info.path[1:]),
    password=conn_info.password,
    decode_responses=True,
)

# Cache TTL is 12 hours
CACHE_TTL = 60 * 60 * 12


def set_cache_value_for_user(user_id: int, key: str, value: str, ttl=CACHE_TTL):
    """Sets a cache value for a user. Deletes the key if value is None.
    Default cache TTL is 12 hours. 
    """
    if value is None:
        redis.delete(f"user:{user_id}:{key}")
    redis.set(f"user:{user_id}:{key}", value, ex=ttl)


def get_cache_value_for_user(user_id, key):
    return redis.get(f"user:{user_id}:{key}")


def check_cache(user_id, key, func, *args, **kwargs) -> str:
    value = get_cache_value_for_user(user_id, key)
    if value is None:
        value = func(*args, **kwargs)
        set_cache_value_for_user(user_id, key, str(value))
    return value


def clear_cache_for_user(user_id, key):
    redis.delete(f"user:{user_id}:{key}")
