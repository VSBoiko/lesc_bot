from datetime import datetime
from typing import Any

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, KeyboardBuilder

from api.meetings.Meeting import Meeting
from api.members.Member import Member
from api.settings import datetime_format_str
from api.tickets.Ticket import Ticket
from clb_queries import ClbShowDetail, Postfix, ClbShowList, ClbConfirm, ClbDelete, ClbAdd


class TgButtonsAdmin:
    booking_cancel = "Отменить бронирование"
    confirm_payment = "Подтвердить оплату"
    confirm_refund = "Подтвердить возврат оплаты"

    @staticmethod
    def add_confirm_payment(builder: InlineKeyboardBuilder, pk: int) -> InlineKeyboardBuilder:
        builder.button(
            text=TgButtonsAdmin.confirm_payment,
            callback_data=ClbConfirm(
                postfix=Postfix.confirm_booking_adm,
                pk=pk
            ),
        )
        return builder

    @staticmethod
    def add_confirm_refund(builder: InlineKeyboardBuilder, pk: int) -> InlineKeyboardBuilder:
        builder.button(
            text=TgButtonsAdmin.confirm_refund,
            callback_data=ClbDelete(
                postfix=Postfix.booking_adm,
                pk=pk,
            ),
        )
        return builder

    @staticmethod
    def add_booking_cancel(builder: InlineKeyboardBuilder, pk: int) -> InlineKeyboardBuilder:
        builder.button(
            text=TgButtonsAdmin.booking_cancel,
            callback_data=ClbDelete(
                postfix=Postfix.booking_adm,
                pk=pk
            )
        )
        return builder
