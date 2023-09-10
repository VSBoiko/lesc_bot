import os

from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=dotenv_path)

TOKEN = os.getenv("TOKEN")
HOST = os.getenv("HOST")
ADMIN_CHANEL_ID = os.getenv("ADMIN_CHANEL_ID")

db_datetime_format = "%d.%m.%Y %H:%M:%S"            # Для базы SQLite - поле с датой имеет тип TEXT
