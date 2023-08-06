import os

from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=dotenv_path)

TOKEN = os.getenv("TOKEN")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_USER_PASS = os.getenv("DB_USER_PASS")

db_datetime_format = "%d.%m.%Y %H:%M:%S"            # Для базы SQLite - поле с датой имеет тип TEXT
str_datetime_format = "%d %B %H:%M"
