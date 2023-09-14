from typing import Any

import redis

HOST = str
PORT = int


class RedisHandler:
    def __init__(self, host: HOST, port: PORT):
        self.db_redis: redis.Redis = redis.Redis(
            host=host,
            port=port,
            decode_responses=True
        )

    def generate_key(self, key_parts: [] = None):
        if not key_parts:
            key_parts = []

        key_parts_str = list(map(lambda x: str(x), key_parts))
        return "_".join(key_parts_str)

    def set(self, key: str, value: Any = None):
        self.db_redis.set(key, value)

    def get(self, key: str) -> Any:
        return self.db_redis.get(key)

    def delete(self, key: str):
        self.db_redis.delete(key)
