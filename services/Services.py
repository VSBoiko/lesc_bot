from datetime import datetime

from settings import db_datetime_format, str_datetime_format


class Services:
    @staticmethod
    def get_date_from_str(date_str: str, date_str_format: str = db_datetime_format) -> datetime:
        return datetime.strptime(date_str, date_str_format)

    @staticmethod
    def get_str_from_datetime(date_: datetime, date_str_format: str = str_datetime_format) -> str:
        return date_.strftime(date_str_format)