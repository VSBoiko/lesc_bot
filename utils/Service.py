from aiogram.types import User
from aiogram.utils.markdown import bold, underline

from api.bookings.ApiBookings import ApiBookings
from api.meetings.ApiMeetings import ApiMeetings
from api.meetings.Meeting import Meeting
from api.members.ApiMembers import ApiMember
from api.members.Member import Member
from api.places.Place import Place
from api.settings import datetime_format_str
from api.tickets.Ticket import Ticket
from texts.ButtonsText import ButtonsText
from texts.MessagesText import MessagesText
from settings import HOST


api_members = ApiMember(HOST)
api_meetings = ApiMeetings(HOST)
api_bookings = ApiBookings(HOST)

msg_text = MessagesText()
btn_text = ButtonsText()

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
    def get_meeting_text(member: Member, meeting: Meeting, show_cnt_tickets: bool = True, *ext_text) -> str:
        free_tickets: list[Ticket] = meeting.get_free_tickets()
        member_ticket: Ticket | None = meeting.get_ticket_by_tg_id(tg_id=member.get_tg_id())
        if member_ticket:
            booking = member_ticket.get_booking()
            if booking.is_paid():
                tickets_info: str = "Мы подтвердили вашу оплату, спасибо, ждем вас на встрече!"
            elif booking.is_user_confirm_paid():
                tickets_info: str = "Вы забронировали место на эту встречу! Мы проверяем оплату, если сейчас ночь, то мы подтвердим бронирование утром, не волнуйтесь, мы вас ждем"
            else:
                tickets_info: str = "\nМы создали бронирование!\nОплатите его по номер +7 (800) 555-35-35 (Соня Батьковна А.) на Сбербанк / Тинькофф и подтвердите перевод по кнопке 'Подтвердить'"

        elif free_tickets:
            tickets_info: str = msg_text.cnt_free_tickets(len(free_tickets))
        else:
            tickets_info: str = msg_text.no_free_tickets()

        meeting_date: str = meeting.get_date_time().strftime(datetime_format_str)
        place: Place = meeting.get_place()
        place_text: str = f"[{place.get_name()}]({place.get_link()})"
        price = int(free_tickets[0].get_price())
        price_str = str(price) + CURRENCY

        text_parts = [
            underline(meeting_date),
            msg_text.meeting_place(place_text),
            f"\nСтоимость - {bold(price_str)}",
        ]

        if show_cnt_tickets:
            text_parts.append("\n" + tickets_info)

        if ext_text:
            text_parts.extend(ext_text)

        return "\n".join(text_parts)
