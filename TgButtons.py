from typing import Any

from aiogram.utils.keyboard import InlineKeyboardBuilder


class TgButtons:
    @staticmethod
    def add(builder: InlineKeyboardBuilder, text: str, callback_data: Any) -> InlineKeyboardBuilder:
        builder.button(
            text=text,
            callback_data=callback_data,
        )
        return builder

    @staticmethod
    def get_empty_builder() -> InlineKeyboardBuilder:
        return InlineKeyboardBuilder()
