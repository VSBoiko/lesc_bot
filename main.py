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


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
db = Db(DB_PATH)
queries = DbQuery(DB_PATH)
msg_text = services.MessagesText


@dp.message_handler(commands=['start'])
async def start_menu(message: types.Message):
    await asyncio.sleep(0.2)
    user_info = queries.get_user_by_tg_id(message.from_user.id)
    if not user_info:
        from_user = message.from_user
        queries.add_user(
            tg_id=from_user.id,
            login=from_user.mention,
            name=from_user.first_name,
            surname=from_user.last_name
        )

    await message.answer(
        text=msg_text.hello.value,
        reply_markup=get_start_menu(),
        parse_mode=ParseMode.MARKDOWN
    )


@dp.callback_query_handler(text=['dates'])
async def callback_dates(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await asyncio.sleep(0.2)
    await callback_query.message.delete()
    await asyncio.sleep(0.2)

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
    await bot.answer_callback_query(callback_query.id)
    await asyncio.sleep(0.2)
    await callback_query.message.delete()
    await asyncio.sleep(0.2)

    meeting = queries.get_meeting_by_id(meeting_id=clb_text.get_postfix(callback_query.data))
    booking_clb_data = clb_text.get_clb_data(clb_text.ClbPrefix.booking.value, meeting.get("id"))
    btn = InlineKeyboardButton(services.ButtonsText.booking.value, callback_data=booking_clb_data)

    show_buttons = InlineKeyboardMarkup()
    if int(meeting.get("cnt_tickets")) > 0:
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
        parse_mode=ParseMode.MARKDOWN
    )


@dp.callback_query_handler(text=clb_text.get_clb_booking())
async def clb_booking(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await asyncio.sleep(0.2)
    await callback_query.message.delete()
    await asyncio.sleep(0.2)

    # todo добавить оплату
    meeting_id = clb_text.get_postfix(callback_query.data)
    free_booking = queries.get_free_booking_one(meeting_id=meeting_id)
    user = queries.get_user_by_tg_id(tg_id=callback_query.from_user.id)
    booking_result = False

    # todo добавить проверку что человек еще не бронировал этот урок
    # todo добавить условие что тьюторы могут бронировать места без денег
    # todo система оповещений пользователей что скоро занятие
    text = msg_text.smt_went_wrong_booking.value
    if free_booking and user:
        try:
            queries.upd_booking(
                booking_id=free_booking.get("id"),
                user_id=user.get("id")
            )
        except:
            pass
        else:
            text = msg_text.ok_booking.value

    await bot.send_message(
        callback_query.from_user.id,
        text=text,
        parse_mode=ParseMode.MARKDOWN
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


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)