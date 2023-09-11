from enum import StrEnum, auto

from aiogram.filters.callback_data import CallbackData


class ClbPrefix(StrEnum):
    meeting: str = auto()
    booking: str = auto()
    confirm_booking: str = auto()
    dates: str = auto()


class Action(StrEnum):
    add: str = auto()
    delete: str = auto()
    show: str = auto()


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
    pk: int | None = None


class ClbDelete(CallbackData, prefix="delete"):
    action: str = Action.delete
    postfix: str
    pk: int
