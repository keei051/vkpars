# cache.py
import redis
import json
import logging
from datetime import timedelta
from config import REDIS_HOST, REDIS_PORT, REDIS_DB

class Cache:
    def __init__(self):
        self.redis = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True
        )
        self.cache_ttl = int(timedelta(hours=24).total_seconds())
        logging.info("Redis подключен")

    def get(self, key: str) -> dict | None:
        """Получение данных из кэша."""
        try:
            data = self.redis.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logging.error(f"Ошибка Redis: {e}. Работа без кэша")
            return None

    def set(self, key: str, value: dict):
        """Сохранение данных в кэш."""
        try:
            self.redis.setex(key, self.cache_ttl, json.dumps(value))
            logging.info(f"Сохранено в кэш: {key}")
        except Exception as e:
            logging.error(f"Ошибка Redis при записи: {e}")

cache = Cache()
