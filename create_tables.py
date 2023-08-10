from db.PgTables import PgTables
from db.PgDatabase import PgDatabase
from settings import DB_NAME, DB_USER, DB_USER_PASS


if __name__ == "__main__":
    db = PgDatabase(
        DB_NAME,
        DB_USER,
        DB_USER_PASS
    )

    tables = PgTables(db)
    tables.create()
