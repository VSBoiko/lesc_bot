import asyncio
import json
from datetime import datetime

from aiogram import Bot, Dispatcher, types, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import User
from aiogram.utils.keyboard import InlineKeyboardBuilder
from magic_filter import F
from api.bookings.ApiBookings import ApiBookings
from api.bookings.Booking import Booking
from api.meetings.ApiMeetings import ApiMeetings
from api.meetings.Meeting import Meeting
from api.members.ApiMembers import ApiMember
from api.members.Member import Member
from clb_queries import ClbShowList, ClbShowDetail, ClbAdd, ClbDelete, ClbPostfix, ClbConfirm
from api.places.Place import Place
from api.tickets.Ticket import Ticket
from msg_texts.MessagesText import MessagesText
from msg_texts.ButtonsText import ButtonsText
from settings import TOKEN, HOST, ADMIN_CHANEL_ID, REDIS_HOST, REDIS_PORT
from api.settings import datetime_format_str, datetime_format_str_api
from utils.RedisHandler import RedisHandler

START_MENU: dict = {
    ClbPostfix.dates: "Даты",
}

bot = Bot(token=TOKEN, parse_mode=ParseMode.MARKDOWN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

msg_text = MessagesText()
btn_text = ButtonsText()

api_members = ApiMember(HOST)
api_meetings = ApiMeetings(HOST)
api_bookings = ApiBookings(HOST)

db_redis = RedisHandler(host=REDIS_HOST, port=REDIS_PORT)


@router.message(Command("start"))
async def start(message: types.Message):
    from_user: User = message.from_user
    member: Member = await api_members.get_member_by_tg_id(tg_id=from_user.id)
    if not member:
        new_member = Member(
            tg_id=from_user.id,
            login=from_user.mention,
            name=from_user.first_name,
            surname=from_user.last_name,
        )
        await api_members.add_member(new_member=new_member)

    bnt_builder = InlineKeyboardBuilder()
    for postfix, text in START_MENU.items():
        bnt_builder.button(
            text=text,
            callback_data=ClbShowList(postfix=postfix).pack()
        )

    await message.answer(
        text=msg_text.get_hello(),
        reply_markup=bnt_builder.as_markup(),
    )


@router.callback_query(ClbShowList.filter(F.postfix == ClbPostfix.dates))
async def show_meetings_list(callback_query: types.CallbackQuery):
    await before_(callback_query.id)

    meetings: list[Meeting] = await api_meetings.get_future_meetings()
    if not meetings:
        await bot.send_message(
            chat_id=callback_query.from_user.id,
            text="Мы готовим ближайшие встречи и скоро вы сможете записаться на них",
        )
        return

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
                postfix=ClbPostfix.meeting,
                pk=meeting.get_pk()
            ),
        )

    btn_builder.adjust(1)

    await bot.send_message(
        chat_id=callback_query.from_user.id,
        text=msg_text.get_club_dates(),
        reply_markup=btn_builder.as_markup(),
    )


@router.callback_query(ClbShowDetail.filter(F.postfix == ClbPostfix.meeting))
async def show_meeting_detail(callback_query: types.CallbackQuery, callback_data: ClbShowDetail):
    await before_(callback_query.id)

    meeting: Meeting = await api_meetings.get_meeting_by_pk(pk=callback_data.pk)
    if not meeting:
        await bot.send_message(
            chat_id=callback_query.from_user.id,
            text="Похоже, что то сломалось, "
                 "я не смог найти встречу, на которую вы хотите записаться( Напишите моим разработчикам",
            reply_to_message_id=callback_query.message.message_id,
        )
        return
    elif not meeting.get_tickets():
        await bot.send_message(
            chat_id=callback_query.from_user.id,
            text="Бронирований на эту встречу пока что не доступны, мы откроем запись чуть позже",
            reply_to_message_id=callback_query.message.message_id,
        )
        return

    member: Member = await api_members.get_member_by_tg_id(tg_id=callback_query.from_user.id)
    if not member:
        await bot.send_message(
            chat_id=callback_query.from_user.id,
            text="Похоже, что то сломалось, "
                 "я не смог вас узнать, напишите, пожалуйста, моим разработчикам",
            reply_to_message_id=callback_query.message.message_id,
        )
        return

    btn_builder = InlineKeyboardBuilder()
    free_tickets: list[Ticket] = meeting.get_free_tickets()
    member_ticket: Ticket | None = meeting.get_ticket_by_tg_id(tg_id=member.get_tg_id())
    tickets_info: str = ""
    if member_ticket:
        if not member_ticket:
            await bot.send_message(
                chat_id=callback_query.from_user.id,
                text="Похоже, что то сломалось, "
                     "я не смог найти ваш билет, напишите, пожалуйста, моим разработчикам",
                reply_to_message_id=callback_query.message.message_id,
            )
        btn_builder.button(
            text="Отменить бронирование",
            callback_data=ClbDelete(postfix=ClbPostfix.booking, pk=meeting.get_pk())
        )
        tickets_info += msg_text.get_booking_already()
    elif free_tickets:
        btn_builder.button(
            text=btn_text.get_booking(),
            callback_data=ClbAdd(postfix=ClbPostfix.booking, pk=meeting.get_pk())
        )
        tickets_info += msg_text.get_cnt_free_tickets(len(free_tickets))
    else:
        tickets_info += msg_text.get_no_tickets()

    meeting_date: str = meeting.get_date_time().strftime(datetime_format_str)
    place: Place = meeting.get_place()
    place_text: str = f"[{place.get_name()}]({place.get_link()})"
    text: str = "\n".join((
        msg_text.get_date_and_time(meeting_date),
        msg_text.get_place(place_text),
        "\n" + tickets_info
    ))

    btn_builder.adjust(1)

    await bot.send_message(
        chat_id=callback_query.from_user.id,
        text=text,
        reply_markup=btn_builder.as_markup(),
        reply_to_message_id=callback_query.message.message_id,
    )


@router.callback_query(ClbAdd.filter(F.postfix == ClbPostfix.booking))
async def add_booking(callback_query: types.CallbackQuery, callback_data: ClbAdd):
    await before_(callback_query.id)

    member: Member = await api_members.get_member_by_tg_id(tg_id=callback_query.from_user.id)
    if not member:
        await bot.send_message(
            chat_id=callback_query.from_user.id,
            text="Похоже, что то сломалось, "
                 "я не смог вас узнать, напишите, пожалуйста, моим разработчикам",
            reply_to_message_id=callback_query.message.message_id,
        )
        return

    # todo добавить условие что тьюторы могут бронировать места без денег
    # todo система оповещений пользователей что скоро занятие
    meeting: Meeting = await api_meetings.get_meeting_by_pk(pk=callback_data.pk)
    ticket = meeting.get_ticket_by_tg_id(member.get_tg_id())
    btn_builder = InlineKeyboardBuilder()
    if ticket:
        booking: Booking = ticket.get_booking()
        redis_key = db_redis.generate_key([
            ClbPostfix.confirm_booking,
            booking.get_pk(),
        ])
        redis_booking: str = db_redis.get(redis_key)
        if booking.is_paid():
            await bot.send_message(
                chat_id=callback_query.from_user.id,
                text="Вы подтвердили оплату на встречу и мы увидели оплату, все супер!",
                reply_to_message_id=callback_query.message.message_id,
            )
            return
        elif redis_booking:
            await bot.send_message(
                chat_id=callback_query.from_user.id,
                text="Вы подтвердили оплату на встречу, мы проверяем вашу оплату и подтвердим бронирование",
                reply_to_message_id=callback_query.message.message_id,
            )
            return
        else:
            btn_builder.button(
                text="Подтвердить оплату",
                callback_data=ClbConfirm(postfix=ClbPostfix.confirm_booking, pk=meeting.get_pk()),
            )
            await bot.send_message(
                chat_id=callback_query.from_user.id,
                text=msg_text.get_booking_already(),
                reply_markup=btn_builder.as_markup(),
                reply_to_message_id=callback_query.message.message_id,
            )
            return

    free_tickets = meeting.get_free_tickets()
    if not free_tickets:
        await bot.send_message(
            chat_id=callback_query.from_user.id,
            text=msg_text.get_no_tickets(),
            reply_to_message_id=callback_query.message.message_id,
        )
        return

    try:
        _ = await api_bookings.add_booking(
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
        btn_builder.button(
            text="Подтвердить оплату",
            callback_data=ClbConfirm(postfix=ClbPostfix.confirm_booking, pk=meeting.get_pk()),
        )

    await bot.send_message(
        chat_id=callback_query.from_user.id,
        text=text,
        reply_markup=btn_builder.as_markup(),
        reply_to_message_id=callback_query.message.message_id,
    )


@router.callback_query(ClbDelete.filter(F.postfix == ClbPostfix.booking))
async def delete_booking(callback_query: types.CallbackQuery, callback_data: ClbDelete):
    await before_(callback_query_id=callback_query.id)

    meeting = await api_meetings.get_meeting_by_pk(pk=callback_data.pk)
    member_ticket = meeting.get_ticket_by_tg_id(tg_id=callback_query.from_user.id)
    if not member_ticket:
        text = "Похоже, что то вы уже отменили бронирование на эту встречу"
    else:
        booking_pk = member_ticket.get_booking().get_pk()
        result = await api_bookings.delete_booking(pk=booking_pk)
        if result:
            # todo доавить оповещение что нужно вернуть деньги юзверю и что деньги нельзя вернуть в день встречи
            if member_ticket.get_booking().is_paid():
                text = "Бронирование отменено, денежки сейчас вернем, посмотри встречи на другую дату"
            else:
                text = "Бронирование отменено, посмотри встречи на другую дату"
            member = member_ticket.get_booking_member()
            notif_text = f"какой то хмырь с именем [{member.get_full_name()}]({member.get_link()}) " \
                         f"отменил бронирование на встречу {meeting.get_name()}"
            btn_builder_adm = InlineKeyboardBuilder()
            btn_clb_data = ClbDelete(
                prefix=ClbPostfix.booking,
                pk=booking_pk,
            )
            btn_builder_adm.button(
                text="Подтвердить возврат оплаты",
                callback_data=btn_clb_data
            )
            await bot.send_message(
                chat_id=ADMIN_CHANEL_ID,
                text=notif_text,
                reply_markup=btn_builder_adm.as_markup(),
            )
        else:
            text = "Похоже, что то сломалось, я не смог отменить бронирование сам, " \
                   "напишите, пожалуйста, моим разработчикам",

    await bot.send_message(
        chat_id=callback_query.from_user.id,
        text=text,
        reply_to_message_id=callback_query.message.message_id
    )


@router.callback_query(ClbConfirm.filter(F.postfix == ClbPostfix.confirm_booking))
async def confirm_booking(callback_query: types.CallbackQuery, callback_data: ClbConfirm):
    await before_(callback_query.id)

    meeting: Meeting = await api_meetings.get_meeting_by_pk(callback_data.pk)
    ticket: Ticket = meeting.get_ticket_by_tg_id(tg_id=callback_query.from_user.id)
    booking: Booking = ticket.get_booking()
    member: Member = ticket.get_booking_member()

    if booking.is_paid():
        await bot.send_message(
            chat_id=callback_query.from_user.id,
            text="Мы подтвердили вашу оплату, спасибо, ждем вас на встрече!",
        )
    else:
        redis_key = db_redis.generate_key(key_parts=[
            ClbPostfix.confirm_booking,
            booking.get_pk()
        ])
        db_redis.set(
            key=redis_key,
            value=json.dumps({
                "booking_pk": booking.get_pk(),
                "member_tg_id": member.get_tg_id(),
            })
        )

        btn_builder_adm = InlineKeyboardBuilder()
        btn_builder_adm.button(
            text="Подтвердить бронирование",
            callback_data=ClbConfirm(postfix=ClbPostfix.confirm_booking_adm, pk=booking.get_pk())
        )

        notif_text = f"[{member.get_full_name()}]({member.get_link()}) говорит, что оплатил " \
                     f"встречу '{meeting.get_name()}', подтвердите оплату"

        await bot.send_message(
            chat_id=ADMIN_CHANEL_ID,
            text=notif_text,
            reply_markup=btn_builder_adm.as_markup(),
        )

        await bot.send_message(
            chat_id=callback_query.from_user.id,
            text="Мы проверяем оплату, если сейчас ночь, то мы подтвердим бронирование утром, не волнуйтесь, мы вас ждем",
        )


@router.callback_query(ClbConfirm.filter(F.postfix == ClbPostfix.confirm_booking_adm))
async def confirm_booking_admin(callback_query: types.CallbackQuery, callback_data: ClbConfirm):
    await before_(callback_query.id)

    redis_key = db_redis.generate_key([
        ClbPostfix.confirm_booking,
        callback_data.pk,
    ])
    redis_info_json: str = db_redis.get(redis_key)
    redis_info = json.loads(redis_info_json)
    booking_pk = redis_info.get("booking_pk")
    member_tg_id = redis_info.get("member_tg_id")
    booking: Booking = await api_bookings.get_booking_by_pk(pk=booking_pk)
    if booking.is_paid():
        admin_text = "Вы уже подтвердили оплату пользователя, все ок"
    else:
        booking.set_is_paid(True)
        _ = await api_bookings.update_booking(booking)
        db_redis.delete(redis_key)
        admin_text = "Бронь подтвердил, участника оповестил, что все оплачено и все ок"
        await bot.send_message(
            chat_id=member_tg_id,
            text="Мы подтвердили вашу оплату, спасибо, ждем вас на встрече!",
        )

    await bot.send_message(
        chat_id=ADMIN_CHANEL_ID,
        text=admin_text,
    )


async def before_(callback_query_id: str) -> None:
    await bot.answer_callback_query(callback_query_id)


async def main() -> None:
    await dp.start_polling(bot)


async def send_msg_to_admin_chanel(msg: str):
    await bot.send_message(
        chat_id=ADMIN_CHANEL_ID,
        text=msg,
    )


if __name__ == "__main__":
    asyncio.run(main())
