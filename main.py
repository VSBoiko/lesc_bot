import asyncio
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from aiogram.utils import executor

from api.bookings.ApiBookings import ApiBookings
from api.bookings.Booking import Booking
from api.meetings.ApiMeetings import ApiMeetings
from api.meetings.Meeting import Meeting
from api.members.ApiMembers import ApiMember
from api.members.Member import Member
import clb_text
from api.places.Place import Place
from api.tickets.Ticket import Ticket
from msg_texts.MessagesText import MessagesText
from msg_texts.ButtonsText import ButtonsText
from settings import TOKEN, HOST
from api.settings import datetime_format_str, datetime_format_str_api

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

msg_text = MessagesText()
btn_text = ButtonsText()

api_members = ApiMember(HOST)
api_meetings = ApiMeetings(HOST)
api_bookings = ApiBookings(HOST)


@dp.message_handler(commands=['start'])
async def start_menu(message: types.Message):
    await sleep_()

    from_user = message.from_user
    if not api_members.get_member_by_tg_id(tg_id=from_user.id):
        new_member = Member(
            tg_id=from_user.id,
            login=from_user.mention,
            name=from_user.first_name,
            surname=from_user.last_name,
        )
        api_members.add_member(new_member=new_member)

    await message.answer(
        text=msg_text.get_hello(),
        reply_markup=get_start_menu(),
        parse_mode=ParseMode.MARKDOWN
    )


@dp.callback_query_handler(text=['dates'])
async def callback_dates(callback_query: types.CallbackQuery):
    await asyncio.gather(before_(callback_query.id), sleep_())

    meetings: list[Meeting] = api_meetings.get_future_meetings()
    if not meetings:
        await bot.send_message(
            callback_query.from_user.id,
            text="Мы готовим ближайшие встречи и скоро вы сможете записаться на них",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    def get_date_time(m: Meeting) -> datetime:
        return m.get_date_time()

    meetings.sort(key=get_date_time)
    buttons = []
    for meeting in meetings:
        meeting_date: str = meeting.get_date_time().strftime(datetime_format_str)
        meeting_name = f"{meeting_date} - {meeting.get_place().get_name()}"
        meeting_clb_data: str = clb_text.get_clb_data(clb_text.ClbPrefix.meeting.value, meeting.get_pk())
        btn = InlineKeyboardButton(
            text=meeting_name,
            callback_data=meeting_clb_data,
        )
        buttons.append(btn)

    show_buttons = InlineKeyboardMarkup()
    for button in buttons:
        show_buttons.add(button)
        show_buttons.row()

    await bot.send_message(
        callback_query.from_user.id,
        text=msg_text.get_club_dates(),
        reply_markup=show_buttons,
        parse_mode=ParseMode.MARKDOWN
    )


@dp.callback_query_handler(text=clb_text.get_clb_meetings())
async def callback_meetings(callback_query: types.CallbackQuery):
    await asyncio.gather(before_(callback_query.id), sleep_())

    meeting: Meeting = api_meetings.get_meeting_by_pk(pk=clb_text.get_postfix(callback_query.data))
    if not meeting:
        await bot.send_message(
            callback_query.from_user.id,
            text="Похоже, что то сломалось, "
                 "я не смог найти встречу, на которую вы хотите записаться( Напишите моим разработчикам",
            parse_mode=ParseMode.MARKDOWN,
            reply_to_message_id=callback_query.message.message_id,
        )
        return

    member: Member = api_members.get_member_by_tg_id(tg_id=callback_query.from_user.id)
    if not member:
        await bot.send_message(
            callback_query.from_user.id,
            text="Похоже, что то сломалось, "
                 "я не смог вас узнать, напишите, пожалуйста, моим разработчикам",
            parse_mode=ParseMode.MARKDOWN,
            reply_to_message_id=callback_query.message.message_id,
        )
        return

    show_buttons = InlineKeyboardMarkup()
    free_tickets: list[Ticket] = meeting.get_free_tickets()
    if meeting.check_booking_by_td_id(tg_id=member.get_tg_id()):
        tickets_info: str = msg_text.get_booking_already()
    elif free_tickets:
        booking_clb_data: str = clb_text.get_clb_data(clb_text.ClbPrefix.booking.value, meeting.get_pk())
        btn = InlineKeyboardButton(
            text=btn_text.get_booking(),
            callback_data=booking_clb_data
        )
        buttons = [btn]

        for button in buttons:
            show_buttons.add(button)
            show_buttons.row()

        tickets_info: str = msg_text.get_cnt_free_tickets(len(free_tickets))
    else:
        tickets_info: str = msg_text.get_no_tickets()

    meeting_date: str = meeting.get_date_time().strftime(datetime_format_str)
    place: Place = meeting.get_place()
    place_text = f"[{place.get_name()}]({place.get_link()})"
    text = "\n".join((
        msg_text.get_date_and_time(meeting_date),
        msg_text.get_place(place_text),
        "\n" + tickets_info
    ))

    await bot.send_message(
        callback_query.from_user.id,
        text=text,
        reply_markup=show_buttons,
        parse_mode=ParseMode.MARKDOWN,
        reply_to_message_id=callback_query.message.message_id,
    )


@dp.callback_query_handler(text=clb_text.get_clb_booking())
async def clb_booking(callback_query: types.CallbackQuery):
    await asyncio.gather(before_(callback_query.id), sleep_())

    # todo добавить оплату
    member: Member = api_members.get_member_by_tg_id(tg_id=callback_query.from_user.id)
    if not member:
        await bot.send_message(
            callback_query.from_user.id,
            text="Похоже, что то сломалось, "
                 "я не смог вас узнать, напишите, пожалуйста, моим разработчикам",
            parse_mode=ParseMode.MARKDOWN,
            reply_to_message_id=callback_query.message.message_id,
        )
        return

    # todo добавить условие что тьюторы могут бронировать места без денег
    # todo система оповещений пользователей что скоро занятие
    meeting = api_meetings.get_meeting_by_pk(pk=clb_text.get_postfix(callback_query.data))
    if meeting.check_booking_by_td_id(tg_id=member.get_tg_id()):
        await bot.send_message(
            callback_query.from_user.id,
            text=msg_text.get_booking_already(),
            parse_mode=ParseMode.MARKDOWN,
            reply_to_message_id=callback_query.message.message_id,
        )
        return

    free_tickets = meeting.get_free_tickets()
    if not free_tickets:
        await bot.send_message(
            callback_query.from_user.id,
            text=msg_text.get_no_tickets(),
            parse_mode=ParseMode.MARKDOWN,
            reply_to_message_id=callback_query.message.message_id,
        )
        return

    try:
        api_bookings.add_booking(
            new_booking=Booking(
                date_time=datetime.now().strftime(datetime_format_str_api),
                is_paid=False,
            ),
            ticket_id=free_tickets[0].get_pk(),
            member_id=member.get_pk(),
        )
    except Exception as e:
        text = msg_text.get_smt_went_wrong()
    else:
        text = msg_text.get_booking_success()

    await bot.send_message(
        callback_query.from_user.id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        reply_to_message_id=callback_query.message.message_id,
    )


def get_start_menu():
    buttons = []
    clb = f"dates"
    btn_tour = InlineKeyboardButton("Даты", callback_data=clb)
    buttons.append(btn_tour)

    show_start_menu = InlineKeyboardMarkup()
    for button in buttons:
        show_start_menu.add(button)
        show_start_menu.row()

    return show_start_menu


async def sleep_(time: int | float = 0.2) -> None:
    await asyncio.sleep(time)


async def before_(callback_query_id: str) -> None:
    await bot.answer_callback_query(callback_query_id)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
