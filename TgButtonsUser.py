from datetime import datetime
from typing import Any

from aiogram.utils.keyboard import InlineKeyboardBuilder

from api.meetings.ApiMeetings import ApiMeetings
from api.meetings.Meeting import Meeting
from api.members.ApiMembers import ApiMember
from api.members.Member import Member
from api.places.Place import Place
from api.settings import datetime_format_str
from api.tickets.ApiTickets import ApiTickets
from api.tickets.Ticket import Ticket
from clb_queries import Postfix, ClbPage, ClbConfirm, ClbDelete, ClbAdd, StartMenu
from settings import HOST


api_meetings = ApiMeetings(HOST)
api_tickets = ApiTickets(HOST)
api_members = ApiMember(HOST)


class TgButtonsUser:
    back_text = "<< назад"
    booking_text = "Записаться"
    booking_cancel_text = "Отменить запись"
    confirm_payment_text = "Подтвердить оплату"

    start_menu_order = [
        StartMenu.meetings,
        StartMenu.subscribe,
        StartMenu.member_bookings,
    ]

    @staticmethod
    def add_back(builder: InlineKeyboardBuilder, callback: Any, **kwargs) -> InlineKeyboardBuilder:
        text = kwargs.get("text") if "text" in kwargs else TgButtonsUser.back_text
        builder.button(
            text=text,
            callback_data=callback,
        )
        return builder

    @staticmethod
    def add_booking(builder: InlineKeyboardBuilder, pk: int, **kwargs) -> InlineKeyboardBuilder:
        text = kwargs.get("text") if "text" in kwargs else TgButtonsUser.booking_text
        builder.button(
            text=text,
            callback_data=ClbAdd(
                postfix=Postfix.booking,
                pk=pk
            ),
        )
        return builder

    @staticmethod
    def add_subscribe(builder: InlineKeyboardBuilder, pk: int, **kwargs) -> InlineKeyboardBuilder:
        text = kwargs.get("text") if "text" in kwargs else TgButtonsUser.booking_text
        builder.button(
            text=text,
            callback_data=ClbAdd(
                postfix=Postfix.subscribe,
                pk=pk
            ),
        )
        return builder

    @staticmethod
    def booking_cancel(builder: InlineKeyboardBuilder, pk: int, **kwargs) -> InlineKeyboardBuilder:
        text = kwargs.get("text") if "text" in kwargs else TgButtonsUser.booking_cancel_text
        builder.button(
            text=text,
            callback_data=ClbDelete(
                postfix=Postfix.booking,
                pk=pk
            )
        )
        return builder

    @staticmethod
    def booking_cancel_confirm(builder: InlineKeyboardBuilder, pk: int, **kwargs) -> InlineKeyboardBuilder:
        text = kwargs.get("text") if "text" in kwargs else TgButtonsUser.booking_cancel_text
        builder.button(
            text=text,
            callback_data=ClbDelete(
                postfix=Postfix.booking_confirm,
                pk=pk
            ),
        )
        return builder

    @staticmethod
    def payment_confirm(builder: InlineKeyboardBuilder, postfix: str, pk: int | None, **kwargs) -> InlineKeyboardBuilder:
        text = kwargs.get("text") if "text" in kwargs else TgButtonsUser.confirm_payment_text
        builder.button(
            text=text,
            callback_data=ClbConfirm(
                postfix=postfix,
                pk=10
            ),
        )
        return builder

    @staticmethod
    async def meeting(member: Member, meeting: Meeting) -> InlineKeyboardBuilder:
        free_tickets: list[Ticket] = await api_meetings.get_free_tickets(meeting=meeting)
        btn_builder = InlineKeyboardBuilder()
        member_ticket: Ticket | None = await api_meetings.get_ticket_by_member_id(
            meeting=meeting,
            member_id=member.get_pk()
        )
        if member_ticket:
            booking = await api_tickets.get_ticket_booking(ticket=member_ticket)
            if not booking.is_user_confirm_paid():
                btn_builder = TgButtonsUser.payment_confirm(
                    builder=btn_builder,
                    pk=meeting.get_pk(),
                    postfix=Postfix.booking_confirm,
                )

            if booking.is_paid() and meeting.is_meeting_today():
                btn_builder = TgButtonsUser.booking_cancel_confirm(
                    builder=btn_builder,
                    pk=meeting.get_pk()
                )
            else:
                btn_builder = TgButtonsUser.booking_cancel(
                    builder=btn_builder,
                    pk=meeting.get_pk()
                )
        elif free_tickets:
            subscribe = await api_members.get_active_subscribe(member=member)
            if subscribe:
                btn_builder = TgButtonsUser.add_booking(
                    builder=btn_builder,
                    pk=meeting.get_pk(),
                    text="Записаться"
                )
            else:
                btn_builder = TgButtonsUser.add_booking(
                    builder=btn_builder,
                    pk=meeting.get_pk()
                )

        btn_builder.adjust(1)

        return btn_builder

    @staticmethod
    async def subscribe(member: Member) -> InlineKeyboardBuilder:
        subscribe = await api_members.get_active_subscribe(member=member)
        btn_builder = InlineKeyboardBuilder()
        if not subscribe:
            btn_builder = TgButtonsUser.payment_confirm(
                builder=btn_builder,
                pk=-1,
                postfix=Postfix.subscribe,
            )

        btn_builder.adjust(1)

        return btn_builder

    @staticmethod
    async def meetings(meetings: list[Meeting]) -> InlineKeyboardBuilder:
        if not meetings:
            InlineKeyboardBuilder()

        def get_date_time(m: Meeting) -> datetime:
            return m.get_date_time()

        meetings.sort(key=get_date_time)
        btn_builder = InlineKeyboardBuilder()
        for meeting in meetings:
            meeting_date: str = meeting.get_date_time().strftime(datetime_format_str)
            place: Place = await api_meetings.get_place(meeting=meeting)
            place_name: str = place.get_name()
            btn_builder.button(
                text=f"{meeting_date} - {place_name}",
                callback_data=ClbPage(
                    postfix=Postfix.meeting,
                    pk=meeting.get_pk()
                ),
            )

        btn_builder.adjust(1)

        return btn_builder

    @staticmethod
    def start_menu() -> InlineKeyboardBuilder:
        bnt_builder = InlineKeyboardBuilder()
        for button in TgButtonsUser.start_menu_order:
            bnt_builder.button(
                text=button,
                callback_data=ClbPage(postfix=button.name)
            )

        bnt_builder.adjust(1)

        return bnt_builder
