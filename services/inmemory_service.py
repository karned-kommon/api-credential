import redis
from config.config import REDIS_DB, REDIS_HOST, REDIS_PASSWORD, REDIS_PORT


def get_redis_api_db():
    return redis.Redis(
        host=REDIS_HOST,
        db=REDIS_DB,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        decode_responses=True
    )

r = get_redis_api_db()