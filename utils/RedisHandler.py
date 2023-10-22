from typing import Any

import redis

HOST = str
PORT = int

DELETE = "delete"
CONFIRM = "confirm"


class RedisHandler:
    def __init__(self, host: HOST, port: PORT):
        self.db_redis: redis.Redis = redis.Redis(
            host=host,
            port=port,
            decode_responses=True
        )

    @staticmethod
    def generate_key(key_parts: [] = None):
        if not key_parts:
            key_parts = []

        key_parts_str = list(map(lambda x: str(x), key_parts))
        return "_".join(key_parts_str)

    def get(self, key: str) -> Any:
        return self.db_redis.get(key)

    def get_key_confirm(self, name: str, pk: int | None = None):
        return self.generate_key([
            CONFIRM,
            name,
            str(pk)
        ])

    def get_key_delete(self, name: str, pk: int):
        return self.generate_key([
            DELETE,
            name,
            str(pk)
        ])

    def delete(self, key: str):
        self.db_redis.delete(key)

    def set(self, key: str, value: Any = None):
        self.db_redis.set(key, value)
