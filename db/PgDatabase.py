import psycopg2


class PgDatabase:
    """Класс для работы с БД Postgresql."""

    def __init__(self, db_name: str, db_user: str, db_user_pass: str):
        """Инициализировать объект класса Db."""
        self._db_name = db_name
        self._db_user = db_user
        self._password = db_user_pass

        self._connection = psycopg2.connect(
            host="localhost",
            port='5432',
            database=self._db_name,
            user=self._db_user,
            password=self._password,
        )
        self._cursor = self._connection.cursor()

    def commit(self):
        self._connection.commit()

    def execute(self, query: str):
        """Запрос к БД.

        :param query: текст запроса.
        """
        self._cursor.execute(query)

    def query(self, query: str) -> list[dict]:
        """Запрос к БД с получением результата этого запроса (через fetchall).

        :param query: текст запроса.

        :return: результат запроса.
        """
        rows = self._cursor.execute(query)
        result = []
        for row in rows:
            result.append(
                {rows.description[i][0]: val for i, val in enumerate(row)}
            )
        del rows
        return result

    def query_fetchone(self, query: str) -> dict:
        """Запрос к БД с получением результата этого запроса (через fetchall).

        :param query: текст запроса.

        :return: результат запроса.
        """
        rows = self.query(query)
        if len(rows) > 0:
            return rows.pop(0)
        else:
            return {}

    def get_db_name(self) -> str:
        """Получить название БД."""
        return self._db_name

    def insert(self, query: str, data: list):
        """Записать в БД.

        :param query: текст запроса;
        :param data: данные, которые требуется записать.
        """
        with self._cursor as cur:
            cur.executemany(query, data)

    def update(self, query: str, data: list):
        """Обновить в БД.

        :param query: текст запроса;
        :param data: обновленные данные.
        """
        self.insert(query, data)
