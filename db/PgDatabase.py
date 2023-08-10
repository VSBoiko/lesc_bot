import psycopg2

from db.base.Db import Db


class PgDatabase(Db):
    """Класс для работы с БД Postgresql."""

    def __init__(self, db_name: str, db_user: str, db_user_pass: str):
        """Инициализировать объект класса Db."""
        super().__init__()
        self._db_name = db_name
        self._db_user = db_user
        self._password = db_user_pass

        self._connection = psycopg2.connect(
            host="127.0.0.1",
            port='5432',
            database=self._db_name,
            user=self._db_user,
            password=self._password,
        )
        self._cursor = self._connection.cursor()

    def commit(self):
        self._connection.commit()

    def rollback(self):
        self._connection.rollback()

    def execute(self, query: str):
        """Запрос к БД.

        :param query: текст запроса.
        """
        self._cursor.execute(query)
        return self._cursor.fetchall(), [column.name for column in self._cursor.description]

    def query(self, query: str) -> list[dict]:
        """Запрос к БД с получением результата этого запроса (через fetchall).

        :param query: текст запроса.

        :return: результат запроса.
        """
        rows, columns = self.execute(query)
        result = []
        for row in rows:
            result.append(
                {columns[i]: val for i, val in enumerate(row)}
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
        try:
            self._cursor.execute(query, *data)
        except Exception as e:
            self.rollback()
        else:
            self.commit()
            return self._cursor.fetchone()

    def update(self, query: str, data: list):
        """Обновить в БД.

        :param query: текст запроса;
        :param data: обновленные данные.
        """
        return self.insert(query, data)
