from abc import ABC, abstractmethod


class Db(ABC):
    """Абстрактный класс для работы с БД."""

    def __init__(self):
        """Инициализировать объект класса Db."""
        pass

    @abstractmethod
    def execute(self, query: str):
        """Запрос к БД.

        :param query: текст запроса.
        """
        pass

    @abstractmethod
    def query(self, query: str) -> list:
        """Запрос к БД с получением результата этого запроса (через fetchall).

        :param query: текст запроса.

        :return: результат запроса.
        """
        pass

    @abstractmethod
    def query_fetchone(self, query: str) -> dict:
        """Запрос к БД с получением результата этого запроса (через fetchall).

        :param query: текст запроса.

        :return: результат запроса.
        """
        pass

    @abstractmethod
    def insert(self, query: str, data: list):
        """Записать в БД.

        :param query: текст запроса;
        :param data: данные, которые требуется записать.
        """
        pass

    @abstractmethod
    def update(self, query: str, data: list):
        """Обновить в БД.

        :param query: текст запроса;
        :param data: обновленные данные.
        """
        pass
