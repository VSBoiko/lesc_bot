from Db import Db
from settings import DB_NAME

db = Db(DB_NAME)


# таблица "Ставки пользователя"
db.execute("""
    CREATE TABLE IF NOT EXISTS users(
        tg_id TEXT,
        login TEXT DEFAULT '',
        name TEXT DEFAULT '',
        surname TEXT DEFAULT ''
    );
""")
