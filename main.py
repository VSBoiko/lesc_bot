import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from aiogram.utils import executor

import clb_text
import services
from db.Db import Db
from db.DbQuery import DbQuery
from settings import TOKEN, DB_PATH
from services import get_date_from_str
from services.UserService import UserService

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
db = Db(DB_PATH)
queries = DbQuery(DB_PATH)
msg_text = services.MessagesText
user_service = UserService()


@dp.message_handler(commands=['start'])
async def start_menu(message: types.Message):
    await sleep_()

    from_user = message.from_user
    if not user_service.is_user_exists(tg_id=from_user.id):
        new_user = user_service.create_user(
            tg_id=from_user.id,
            login=from_user.mention,
            name=from_user.first_name,
            surname=from_user.last_name,
        )
        user_service.add_user_to_db(user=new_user)

    await message.answer(
        text=msg_text.hello.value,
        reply_markup=get_start_menu(),
        parse_mode=ParseMode.MARKDOWN
    )


@dp.callback_query_handler(text=['dates'])
async def callback_dates(callback_query: types.CallbackQuery):
    await asyncio.gather(before_(callback_query.id), sleep_())

    meetings = queries.get_meetings()
    buttons = []
    for meeting in meetings:
        meeting_date = get_date_from_str(meeting.get("date_time"))
        meeting_name = f"{services.get_str_from_datetime(meeting_date)} - {meeting.get('place_name')}"
        meeting_clb_data = clb_text.get_clb_data(clb_text.ClbPrefix.meeting.value, meeting.get("id"))
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
        text=msg_text.which_dates.value,
        reply_markup=show_buttons,
        parse_mode=ParseMode.MARKDOWN
    )


@dp.callback_query_handler(text=clb_text.get_clb_meetings())
async def callback_meetings(callback_query: types.CallbackQuery):
    await asyncio.gather(before_(callback_query.id), sleep_())

    meeting = queries.get_meeting_by_id(meeting_id=clb_text.get_postfix(callback_query.data))
    booking_clb_data = clb_text.get_clb_data(clb_text.ClbPrefix.booking.value, meeting.get("id"))
    btn = InlineKeyboardButton(services.ButtonsText.booking.value, callback_data=booking_clb_data)
    user = user_service.get_user_by_tg_id(tg_id=callback_query.from_user.id)

    show_buttons = InlineKeyboardMarkup()
    already_booked = queries.get_booking_by_user(meeting_id=meeting.get("id"), user_id=user.id)
    if already_booked:
        tickets_info = services.MessagesText.already_booked.value
    elif meeting.get("cnt_tickets") > 0:
        buttons = [btn]
        for button in buttons:
            show_buttons.add(button)
            show_buttons.row()

        tickets_info = msg_text.tickets.value.format(meeting.get("cnt_tickets"))
    else:
        tickets_info = msg_text.no_tickets.value

    meeting_date = services.get_date_from_str(meeting.get("date_time"))
    place_text = f"[{meeting.get('place_name')}]({meeting.get('place_link')})"
    text = "\n".join((
        msg_text.date_and_time.value.format(services.get_str_from_datetime(meeting_date)),
        msg_text.place_info.value.format(place_text),
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
    user = user_service.get_user_by_tg_id(tg_id=callback_query.from_user.id)
    if not user:
        await bot.send_message(
            callback_query.from_user.id,
            text=msg_text.smt_went_wrong_booking.value,
            parse_mode=ParseMode.MARKDOWN,
            reply_to_message_id=callback_query.message.message_id,
        )
        return

    # todo добавить условие что тьюторы могут бронировать места без денег
    # todo система оповещений пользователей что скоро занятие
    meeting_id = clb_text.get_postfix(callback_query.data)
    already_booked = queries.get_booking_by_user(meeting_id=meeting_id, user_id=user.id)
    if already_booked:
        await bot.send_message(
            callback_query.from_user.id,
            text=msg_text.already_booked.value,
            parse_mode=ParseMode.MARKDOWN,
            reply_to_message_id=callback_query.message.message_id,
        )
        return

    free_booking = queries.get_free_booking_one(meeting_id=meeting_id)
    if not free_booking:
        await bot.send_message(
            callback_query.from_user.id,
            text=msg_text.no_free_booked.value,
            parse_mode=ParseMode.MARKDOWN,
            reply_to_message_id=callback_query.message.message_id,
        )
        return

    try:
        queries.upd_booking(
            booking_id=free_booking.get("id"),
            user_id=user.id
        )
    except Exception as e:
        text = msg_text.smt_went_wrong_booking.value
    else:
        text = msg_text.ok_booking.value

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