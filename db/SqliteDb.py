from db.base.Db import Db

import sqlite3


class SqliteDb(Db):
    """Класс для работы с БД SQLite3."""

    def __init__(self, db_name: str):
        """Инициализировать объект класса Db.

        :param db_name: название файла с БД (например, "basedb.db").
        """
        super().__init__()
        self.__db_name = db_name
        self.__connection = sqlite3.connect(self.__db_name, check_same_thread=False)

    def execute(self, query: str):
        """Запрос к БД.

        :param query: текст запроса.
        """
        self.__connection.cursor().execute(query)

    def query(self, query: str) -> list:
        """Запрос к БД с получением результата этого запроса (через fetchall).

        :param query: текст запроса.

        :return: результат запроса.
        """
        rows = self.__connection.execute(query)
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
        return self.__db_name

    def insert(self, query: str, data: list):
        """Записать в БД.

        :param query: текст запроса;
        :param data: данные, которые требуется записать.
        """
        with self.__connection as connection:
            connection.executemany(query, data)

    def update(self, query: str, data: list):
        """Обновить в БД.

        :param query: текст запроса;
        :param data: обновленные данные.
        """
        self.insert(query, data)
