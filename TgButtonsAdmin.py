from aiogram.utils.keyboard import InlineKeyboardBuilder

from clb_queries import Postfix, ClbConfirm, ClbDelete


class TgButtonsAdmin:
    booking_cancel = "Отменить запись"
    confirm_payment = "Подтвердить оплату"
    confirm_refund = "Подтвердить возврат оплаты"

    @staticmethod
    def add_confirm_payment(builder: InlineKeyboardBuilder, postfix: str, pk: int, **kwargs) -> InlineKeyboardBuilder:
        text = kwargs.get("text") if "text" in kwargs else TgButtonsAdmin.confirm_payment
        builder.button(
            text=text,
            callback_data=ClbConfirm(
                postfix=postfix,
                pk=pk
            ),
        )
        return builder

    @staticmethod
    def add_confirm_refund(builder: InlineKeyboardBuilder, postfix: str, pk: int, **kwargs) -> InlineKeyboardBuilder:
        text = kwargs.get("text") if "text" in kwargs else TgButtonsAdmin.confirm_refund
        builder.button(
            text=text,
            callback_data=ClbDelete(
                postfix=postfix,
                pk=pk,
            ),
        )
        return builder

    @staticmethod
    def add_cancel(builder: InlineKeyboardBuilder, postfix: str, pk: int, **kwargs) -> InlineKeyboardBuilder:
        text = kwargs.get("text") if "text" in kwargs else TgButtonsAdmin.booking_cancel
        builder.button(
            text=text,
            callback_data=ClbDelete(
                postfix=postfix,
                pk=pk
            )
        )
        return builder
