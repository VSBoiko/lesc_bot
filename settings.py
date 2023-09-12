import os

import redis
from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=dotenv_path)

TOKEN = os.getenv("TOKEN")
HOST = os.getenv("HOST")
ADMIN_CHANEL_ID = os.getenv("ADMIN_CHANEL_ID")
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")

DB_REDIS = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
