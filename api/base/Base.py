from api.settings import datetime_format_str, datetime_format_str_api


class Base:
    def __init__(
        self, pk: int | None = None, **kwargs
    ):
        if not pk:
            pk: int | None = kwargs.get("id", None)

        self._pk: int | None = pk
        self._datetime_format_str: str = datetime_format_str
        self._date_time_format_db: str = datetime_format_str_api

    def get_pk(self) -> int:
        return self._pk
