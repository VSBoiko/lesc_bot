import os

from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=dotenv_path)

TOKEN = os.getenv("TOKEN")
DB_NAME = os.getenv("DB_NAME")
DB_PATH = os.path.join(os.path.dirname(__file__), DB_NAME)

db_datetime_format = "%d.%m.%Y %H:%M:%S"
str_datetime_format = "%d %B %H:%M"
