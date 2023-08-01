from datetime import datetime
from enum import Enum

from settings import db_datetime_format, str_datetime_format


def get_date_from_str(date_str: str, date_str_format: str = db_datetime_format) -> datetime:
    return datetime.strptime(date_str, date_str_format)


def get_str_from_datetime(date_: datetime, date_str_format: str = str_datetime_format) -> str:
    return date_.strftime(date_str_format)


class MessagesText(Enum):
    hello = f"LESC - Local English speaking club BOT\nВсем хай!"
    which_dates = f"На какие даты будет клуб:"
    date_and_time = "Дата и время: {0}"
    place_info = "Место: {0}"
    tickets = "Свободных мест - {0}"
    no_tickets = "Sorry, кажется, уже все места заняты, выбери другой день"
    ok_booking = "Записали! Приходи не забывай плати деньги"
    smt_went_wrong_booking = "Что то пошло не так, извините, попробуйте еще раз или напишите нам"


class ButtonsText(Enum):
    booking = f"Записаться"
