from enum import StrEnum, auto

from aiogram.filters.callback_data import CallbackData


class StartMenu(StrEnum):
    meetings: str = "Встречи"
    subscribe: str = "Мой абонемент"
    member_bookings: str = "Мои записи"


class Postfix(StrEnum):
    start: str = auto()
    meeting: str = auto()
    meetings: str = auto()
    booking: str = auto()
    booking_confirm: str = auto()
    subscribe: str = auto()
    subscribe_confirm: str = auto()

    adm_booking: str = auto()
    adm_booking_confirm: str = auto()
    adm_subscribe: str = auto()
    adm_subscribe_confirm: str = auto()


class Actions(StrEnum):
    add: str = auto()
    delete: str = auto()
    page: str = auto()
    confirm: str = auto()


class ClbPage(CallbackData, prefix=Actions.page):
    postfix: str
    pk: int | None = None


class ClbAdd(CallbackData, prefix=Actions.add):
    postfix: str
    pk: int | None = None


class ClbDelete(CallbackData, prefix=Actions.delete):
    postfix: str
    pk: int | None = None


class ClbConfirm(CallbackData, prefix=Actions.confirm):
    postfix: str
    pk: int | None = None
