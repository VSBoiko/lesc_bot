import asyncio
from datetime import date, datetime

from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from aiogram.utils import executor

from db.Db import Db
from db.DbQuery import DbQuery
from settings import TOKEN, DB_NAME

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
db = Db(DB_NAME)
queries = DbQuery(DB_NAME)


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
        text=f"LESC - Local English speaking club BOT\nВсем хай!",
        reply_markup=get_start_menu(),
        parse_mode=ParseMode.MARKDOWN
    )


@dp.callback_query_handler(text=['dates'])
async def clb_dates(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await asyncio.sleep(0.2)
    await callback_query.message.delete()
    await asyncio.sleep(0.2)

    dates = {
        date(year=2023, month=8, day=3): "3 августа",
        date(year=2023, month=8, day=4): "4 августа",
        date(year=2023, month=8, day=5): "5 августа",
    }
    buttons = []
    for k, d in dates.items():
        btn = InlineKeyboardButton(d, callback_data=k.strftime("%d_%m_%Y"))
        buttons.append(btn)

    show_buttons = InlineKeyboardMarkup()
    for button in buttons:
        show_buttons.add(button)
        show_buttons.row()

    await bot.send_message(
        callback_query.from_user.id,
        text=f"На какие даты будет клуб",
        reply_markup=show_buttons,
        parse_mode=ParseMode.MARKDOWN
    )


@dp.callback_query_handler(text=['03_08_2023', '04_08_2023', '05_08_2023'])
async def clb_scheduler(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await asyncio.sleep(0.2)
    await callback_query.message.delete()
    await asyncio.sleep(0.2)

    d = datetime.strptime(callback_query.data, "%d_%m_%Y")
    btn = InlineKeyboardButton("Записаться", callback_data=f"add_{d.strftime('%d_%m_%Y')}")

    buttons = [btn]

    show_buttons = InlineKeyboardMarkup()
    for button in buttons:
        show_buttons.add(button)
        show_buttons.row()

    await bot.send_message(
        callback_query.from_user.id,
        text=f"ну что давай запишемся на {d.strftime('%d.%m')}",
        reply_markup=show_buttons,
        parse_mode=ParseMode.MARKDOWN
    )


@dp.callback_query_handler(text=['add_03_08_2023', 'add_04_08_2023', 'add_05_08_2023'])
async def clb_booking(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await asyncio.sleep(0.2)
    await callback_query.message.delete()
    await asyncio.sleep(0.2)

    await bot.send_message(
        callback_query.from_user.id,
        text=f"записали приходи не забывай",
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