from aiogram.types import User
from aiogram.utils.markdown import bold, underline

from api.bookings.ApiBookings import ApiBookings
from api.meetings.ApiMeetings import ApiMeetings
from api.meetings.Meeting import Meeting
from api.members.ApiMembers import ApiMember
from api.members.Member import Member
from api.places.Place import Place
from api.settings import datetime_format_str
from api.subscribes.ApiSubscribes import ApiSubscribes
from api.tickets.ApiTickets import ApiTickets
from api.tickets.Ticket import Ticket
from texts.Messages import Messages
from settings import HOST


api_members = ApiMember(HOST)
api_meetings = ApiMeetings(HOST)
api_bookings = ApiBookings(HOST)
api_tickets = ApiTickets(HOST)
api_subscribes = ApiSubscribes(HOST)

msg_text = Messages()

CURRENCY = "₽"


class Service:
    @staticmethod
    async def add_member(tg_user: User):
        try:
            login = tg_user.mention
        except AttributeError:
            login = f"@{tg_user.username}"
        except Exception as e:
            login = None

        new_member = Member(
            tg_id=tg_user.id,
            login=login,
            name=tg_user.first_name,
            surname=tg_user.last_name,
        )
        await api_members.add_member(new_member=new_member)

    @staticmethod
    async def get_meeting_text(member: Member, meeting: Meeting, show_cnt_tickets: bool = True, *ext_text) -> str:
        free_tickets: list[Ticket] = await api_meetings.get_free_tickets(meeting=meeting)
        member_ticket: Ticket | None = await api_meetings.get_ticket_by_member_id(
            meeting=meeting,
            member_id=member.get_pk()
        )
        if member_ticket:
            booking = await api_tickets.get_ticket_booking(ticket=member_ticket)
            if booking.is_paid():
                tickets_info: str = msg_text.booking_success_pay_success()
            elif booking.is_user_confirm_paid():
                tickets_info: str = msg_text.booking_success_pay_confirm()
            else:
                tickets_info: str = msg_text.payment_info()

        elif free_tickets:
            tickets_info: str = msg_text.cnt_free_tickets(len(free_tickets))
        else:
            tickets_info: str = msg_text.no_free_tickets()

        meeting_date: str = meeting.get_date_time().strftime(datetime_format_str)
        place: Place = await api_meetings.get_place(meeting=meeting)
        place_text: str = f"[{place.get_name()}]({place.get_link()})"
        price = int(free_tickets[0].get_price())
        price_str = str(price) + CURRENCY

        text_parts = [
            underline(meeting_date),
            msg_text.meeting_place(place_text),
            f"\n{msg_text.price(bold(price_str))}",
        ]

        if show_cnt_tickets:
            text_parts.append("\n" + tickets_info)

        if ext_text:
            text_parts.extend(ext_text)

        return "\n".join(text_parts)

    @staticmethod
    async def get_subscribe_text(member: Member, *ext_text) -> str:
        subscribe = await api_members.get_active_subscribe(member=member)
        if subscribe:
            bookings = await api_subscribes.get_bookings(subscribe=subscribe)
            cnt = subscribe.get_cnt_meetings() - len(bookings)
            subscribe_info: str = msg_text.subscribe_balance(str(cnt))
        else:
            subscribe_info: str = f"{msg_text.about_subscribe()}\n\n{msg_text.subs_payment_info()}"

        text_parts = [
            underline(subscribe_info)
        ]
        if ext_text:
            text_parts.extend(ext_text)

        return "\n".join(text_parts)

    @staticmethod
    def pluralize_word(word_if_one, word_if_two, word_if_five, count):
        """
        Склоняет слово в зависимости от числа count с учетом разных вариантов склонения.

        :param word_if_one: Слово, которое используется, если число оканчивается на 1 (кроме 11).
        :param word_if_two: Слово, которое используется, если число оканчивается на 2, 3 или 4 (кроме 12, 13, 14).
        :param word_if_five: Слово, которое используется в остальных случаях.
        :param count: Число, от которого зависит склонение.

        :return: Склоненное слово в соответствии с числом count.
        """
        if count % 10 == 1 and count % 100 != 11:
            return word_if_one
        elif count % 10 in [2, 3, 4] and count % 100 not in [12, 13, 14]:
            return word_if_two
        else:
            return word_if_five
