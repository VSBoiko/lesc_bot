from datetime import datetime
from typing import Any

from aiogram.utils.keyboard import InlineKeyboardBuilder

from api.meetings.Meeting import Meeting
from api.members.Member import Member
from api.settings import datetime_format_str
from api.tickets.Ticket import Ticket
from clb_queries import ClbShowDetail, Postfix, ClbShowList, ClbConfirm, ClbDelete, ClbAdd, StartMenu


class TgButtonsUser:
    back = "<< назад"
    booking = "Записаться"
    booking_cancel = "Отменить бронирование"
    confirm_payment = "Подтвердить оплату"

    start_menu = [
        StartMenu.dates,
        StartMenu.subscription,
        StartMenu.member_bookings,
    ]

    @staticmethod
    def add_back(builder: InlineKeyboardBuilder, callback: Any, **kwargs) -> InlineKeyboardBuilder:
        text = kwargs.get("text") if "text" in kwargs else TgButtonsUser.back
        builder.button(
            text=text,
            callback_data=callback,
        )
        return builder

    @staticmethod
    def add_booking(builder: InlineKeyboardBuilder, pk: int, **kwargs) -> InlineKeyboardBuilder:
        text = kwargs.get("text") if "text" in kwargs else TgButtonsUser.booking
        builder.button(
            text=text,
            callback_data=ClbAdd(
                postfix=Postfix.booking,
                pk=pk
            ),
        )
        return builder

    @staticmethod
    def add_booking_cancel(builder: InlineKeyboardBuilder, pk: int, **kwargs) -> InlineKeyboardBuilder:
        text = kwargs.get("text") if "text" in kwargs else TgButtonsUser.booking_cancel
        builder.button(
            text=text,
            callback_data=ClbDelete(
                postfix=Postfix.booking,
                pk=pk
            )
        )
        return builder

    @staticmethod
    def add_booking_cancel_confirm(builder: InlineKeyboardBuilder, pk: int, **kwargs) -> InlineKeyboardBuilder:
        text = kwargs.get("text") if "text" in kwargs else TgButtonsUser.booking_cancel
        builder.button(
            text=text,
            callback_data=ClbDelete(
                postfix=Postfix.confirm_booking,
                pk=pk
            ),
        )
        return builder

    @staticmethod
    def add_payment_confirm(builder: InlineKeyboardBuilder, pk: int, **kwargs) -> InlineKeyboardBuilder:
        text = kwargs.get("text") if "text" in kwargs else TgButtonsUser.confirm_payment
        builder.button(
            text=text,
            callback_data=ClbConfirm(
                postfix=Postfix.confirm_booking,
                pk=pk
            ),
        )
        return builder

    @staticmethod
    def get_meeting(member: Member, meeting: Meeting) -> InlineKeyboardBuilder:
        free_tickets: list[Ticket] = meeting.get_free_tickets()
        btn_builder = InlineKeyboardBuilder()
        member_ticket: Ticket | None = meeting.get_ticket_by_tg_id(tg_id=member.get_tg_id())
        if member_ticket:
            booking = member_ticket.get_booking()
            if not booking.is_user_confirm_paid():
                btn_builder = TgButtonsUser.add_payment_confirm(
                    builder=btn_builder,
                    pk=meeting.get_pk()
                )

            if booking.is_paid() and meeting.is_meeting_today():
                btn_builder = TgButtonsUser.add_booking_cancel_confirm(
                    builder=btn_builder,
                    pk=meeting.get_pk()
                )
            else:
                btn_builder = TgButtonsUser.add_booking_cancel(
                    builder=btn_builder,
                    pk=meeting.get_pk()
                )
        elif free_tickets:
            btn_builder = TgButtonsUser.add_booking(
                builder=btn_builder,
                pk=meeting.get_pk()
            )

        btn_builder.adjust(1)

        return btn_builder

    @staticmethod
    def get_meetings(meetings: list[Meeting]) -> InlineKeyboardBuilder:
        if not meetings:
            InlineKeyboardBuilder()

        def get_date_time(m: Meeting) -> datetime:
            return m.get_date_time()

        meetings.sort(key=get_date_time)
        btn_builder = InlineKeyboardBuilder()
        for meeting in meetings:
            meeting_date: str = meeting.get_date_time().strftime(datetime_format_str)
            place_name: str = meeting.get_place().get_name()
            btn_builder.button(
                text=f"{meeting_date} - {place_name}",
                callback_data=ClbShowDetail(
                    postfix=Postfix.meeting,
                    pk=meeting.get_pk()
                ),
            )

        btn_builder.adjust(1)

        return btn_builder

    @staticmethod
    def get_start_menu() -> InlineKeyboardBuilder:
        bnt_builder = InlineKeyboardBuilder()
        for button in TgButtonsUser.start_menu:
            bnt_builder.button(
                text=button,
                callback_data=ClbShowList(postfix=button.name)
            )

        bnt_builder.adjust(1)

        return bnt_builder
