import redis
from config import DevelopmentConfig


def connect_redis():
    return redis.Redis(**DevelopmentConfig.REDIS_DB_URL)
