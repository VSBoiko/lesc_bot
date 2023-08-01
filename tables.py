from db.Db import Db
from settings import DB_PATH

db = Db(DB_PATH)


# таблица "Пользователи"
db.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        tg_id TEXT,
        login TEXT DEFAULT '',
        name_ TEXT DEFAULT '',
        surname TEXT DEFAULT ''
    );
""")

# таблица "Встречи"
db.execute("""
    CREATE TABLE IF NOT EXISTS meetings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        place_id INTEGER,
        date_time TEXT,
        name_ TEXT DEFAULT ''
    );
""")

# таблица "Места встреч"
db.execute("""
    CREATE TABLE IF NOT EXISTS places(
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        name_ TEXT,
        address TEXT,
        link TEXT DEFAULT '',
        description TEXT DEFAULT '' 
    );
""")


# таблица "Бронирования"
db.execute("""
    CREATE TABLE IF NOT EXISTS booking(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        meeting_id INTEGER,
        user_id INTEGER DEFAULT NULL,
        booking_date_time TEXT DEFAULT datetime('now','localtime'),
        paid INTEGER DEFAULT 0
    );
""")
