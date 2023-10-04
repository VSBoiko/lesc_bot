from enum import StrEnum, auto

from aiogram.filters.callback_data import CallbackData


class StartMenu(StrEnum):
    dates: str = "Даты"
    subscription: str = "Купить абонемент"
    member_bookings: str = "Мои бронирования"


class Postfix(StrEnum):
    start: str = auto()
    meeting: str = auto()
    booking: str = auto()
    booking_adm: str = auto()
    confirm_booking: str = auto()
    confirm_booking_adm: str = auto()
    dates: str = auto()


class Action(StrEnum):
    add: str = auto()
    delete: str = auto()
    show: str = auto()
    confirm: str = auto()


class ClbShowList(CallbackData, prefix="show_list"):
    action: str = Action.show
    postfix: str


class ClbShowDetail(CallbackData, prefix="show_detail"):
    action: str = Action.show
    postfix: str
    pk: int


class ClbAdd(CallbackData, prefix="add"):
    action: str = Action.add
    postfix: str
    pk: int


class ClbDelete(CallbackData, prefix="delete"):
    action: str = Action.delete
    postfix: str
    pk: int


class ClbConfirm(CallbackData, prefix="confirm"):
    action: str = Action.confirm
    postfix: str
    pk: int
