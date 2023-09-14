import asyncio
import json
from datetime import datetime

from aiogram import Bot, Dispatcher, types, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import User
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.markdown import bold
from magic_filter import F

from TgButtons import get_meetings_btn_builder
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
        try:
            login = from_user.mention
        except AttributeError:
            login = f"@{from_user.username}"
        except Exception as e:
            login = None

        new_member = Member(
            tg_id=from_user.id,
            login=login,
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
    meetings: list[Meeting] = await api_meetings.get_future_meetings()
    if not meetings:
        await callback_query.answer(
            text="Мы готовим ближайшие встречи и скоро вы сможете записаться на них",
            show_alert=True,
        )
        await after_(callback_query.id)
        return

    btn_builder = get_meetings_btn_builder(meetings=meetings)

    await bot.send_message(
        chat_id=callback_query.from_user.id,
        text=msg_text.get_club_dates(),
        reply_markup=btn_builder.as_markup(),
    )
    await after_(callback_query.id)


@router.callback_query(ClbShowDetail.filter(F.postfix == ClbPostfix.meeting))
async def show_meeting_detail(callback_query: types.CallbackQuery, callback_data: ClbShowDetail):
    meeting: Meeting = await api_meetings.get_meeting_by_pk(pk=callback_data.pk)
    if not meeting:
        await callback_query.answer(
            text="Похоже, что то сломалось, "
                 "я не смог найти встречу, на которую вы хотите записаться( Напишите моим разработчикам",
            show_alert=True,
        )
        await after_(callback_query.id)
        return

    elif not meeting.get_tickets() or not meeting.get_can_be_booked():
        await callback_query.answer(
            text="Бронирований на эту встречу пока что не доступны, мы откроем запись чуть позже",
            show_alert=True,
        )
        await after_(callback_query.id)
        return

    member: Member = await api_members.get_member_by_tg_id(tg_id=callback_query.from_user.id)
    if not member:
        await callback_query.answer(
            text="Похоже, что то сломалось, я не смог вас узнать, напишите, пожалуйста, моим разработчикам",
            show_alert=True,
        )
        await after_(callback_query.id)
        return

    free_tickets: list[Ticket] = meeting.get_free_tickets()
    member_ticket: Ticket | None = meeting.get_ticket_by_tg_id(tg_id=member.get_tg_id())
    btn_builder = InlineKeyboardBuilder()
    tickets_info: str = ""
    if member_ticket:
        if not member_ticket:
            await callback_query.answer(
                text="Похоже, что то сломалось, я не смог найти ваш билет, напишите, пожалуйста, моим разработчикам",
                show_alert=True,
            )
            await after_(callback_query.id)
            return

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
        f"\nСтоимость - {bold(int(free_tickets[0].get_price()))} {bold('₽')}"
        "\n" + tickets_info,
    ))

    btn_builder.adjust(1)

    await bot.send_message(
        chat_id=callback_query.from_user.id,
        text=text,
        reply_markup=btn_builder.as_markup(),
        reply_to_message_id=callback_query.message.message_id,
    )

    await after_(callback_query.id)


@router.callback_query(ClbAdd.filter(F.postfix == ClbPostfix.booking))
async def add_booking(callback_query: types.CallbackQuery, callback_data: ClbAdd):
    member: Member = await api_members.get_member_by_tg_id(tg_id=callback_query.from_user.id)
    if not member:
        await callback_query.answer(
            text="Похоже, что то сломалось, я не смог вас узнать, напишите, пожалуйста, моим разработчикам",
            show_alert=True,
        )
        await after_(callback_query.id)
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
            await callback_query.answer(
                text="Вы подтвердили оплату на встречу и мы увидели оплату, все супер!",
                show_alert=True,
            )
            await after_(callback_query.id)
            return

        elif redis_booking:
            await callback_query.answer(
                text="Вы подтвердили оплату на встречу, мы проверяем вашу оплату и подтвердим бронирование",
                show_alert=True,
            )
            await after_(callback_query.id)
            return

        else:
            await callback_query.answer(
                text=msg_text.get_booking_already(),
                show_alert=True,
            )
            await after_(callback_query.id)
            return

    free_tickets = meeting.get_free_tickets()
    if not free_tickets:
        await callback_query.answer(
            text=msg_text.get_no_tickets(),
            show_alert=True,
        )
        await after_(callback_query.id)
        return

    try:
        _ = await api_bookings.add_booking(
            new_booking=Booking(
                date_time=datetime.now().strftime(datetime_format_str_api),
                is_paid=False,
                user_confirm_paid=False,
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

    await after_(callback_query.id)


@router.callback_query(ClbDelete.filter(F.postfix == ClbPostfix.booking))
async def delete_booking(callback_query: types.CallbackQuery, callback_data: ClbDelete):
    meeting = await api_meetings.get_meeting_by_pk(pk=callback_data.pk)
    member_ticket = meeting.get_ticket_by_tg_id(tg_id=callback_query.from_user.id)
    if not member_ticket:
        await callback_query.answer(
            text="Похоже, что то вы уже отменили бронирование на эту встречу",
            show_alert=True,
        )
    else:
        booking = member_ticket.get_booking()
        redis_key = db_redis.generate_key(key_parts=[
            ClbPostfix.booking,
            booking.get_pk()
        ])
        redis_info = db_redis.get(redis_key)
        if redis_info:
            await callback_query.answer(
                text="Бронирование отменено, сейчас вернем деньги, посмотри встречи на другую дату",
                show_alert=True
            )
        elif booking.is_paid():
            # todo доавить что деньги нельзя вернуть в день встречи
            msg_to_user: types.Message = await bot.send_message(
                chat_id=callback_query.from_user.id,
                text="Бронирование отменено, сейчас вернем деньги, посмотри встречи на другую дату",
                reply_to_message_id=callback_query.message.message_id
            )

            booking_pk = booking.get_pk()
            btn_builder_adm = InlineKeyboardBuilder()
            btn_clb_data = ClbDelete(
                postfix=ClbPostfix.booking_adm,
                pk=booking_pk,
            )
            btn_builder_adm.button(
                text="Подтвердить возврат оплаты",
                callback_data=btn_clb_data
            )

            member: Member = member_ticket.get_booking_member()
            db_redis.set(
                key=redis_key,
                value=json.dumps({
                    "booking_pk": booking_pk,
                    "member_tg_id": member.get_tg_id(),
                    "user_chat_id": callback_query.from_user.id,
                    "msg_to_user_id": msg_to_user.message_id,
                })
            )

            member = member_ticket.get_booking_member()
            if member.get_login():
                notif_text = f"какой то хмырь с именем [{member.get_full_name()}]({member.get_link()}) " \
                             f"отменил бронирование на встречу {meeting.get_name()}\n\nнадо вернуть ему бабосы"
            else:
                notif_text = f"какой то хмырь с именем {member.get_full_name()} " \
                             f"отменил бронирование на встречу {meeting.get_name()}\n\nнадо вернуть ему бабосы"

            await bot.send_message(
                chat_id=ADMIN_CHANEL_ID,
                text=notif_text,
                reply_markup=btn_builder_adm.as_markup(),
            )
        else:
            meetings: list[Meeting] = await api_meetings.get_future_meetings()
            if not meetings:
                text: str = "Бронирование отменено, готовим ближайшие встречи и скоро вы сможете записаться на них"
            else:
                text: str = "Бронирование отменено, посмотри встречи на другую дату"

            btn_builder: InlineKeyboardBuilder = get_meetings_btn_builder(meetings=meetings)
            await bot.send_message(
                chat_id=callback_query.from_user.id,
                text=text,
                reply_markup=btn_builder.as_markup(),
                reply_to_message_id=callback_query.message.message_id
            )

    await after_(callback_query_id=callback_query.id)


@router.callback_query(ClbConfirm.filter(F.postfix == ClbPostfix.confirm_booking))
async def confirm_booking(callback_query: types.CallbackQuery, callback_data: ClbConfirm):
    meeting: Meeting = await api_meetings.get_meeting_by_pk(callback_data.pk)
    ticket: Ticket = meeting.get_ticket_by_tg_id(tg_id=callback_query.from_user.id)
    booking: Booking = ticket.get_booking()
    member: Member = ticket.get_booking_member()

    redis_key = db_redis.generate_key(key_parts=[
        ClbPostfix.confirm_booking,
        booking.get_pk()
    ])
    redis_info = db_redis.get(redis_key)
    if redis_info:
        await callback_query.answer(
            text="Мы проверяем оплату, если сейчас ночь, то мы подтвердим бронирование утром, не волнуйтесь, мы вас ждем",
            show_alert=True
        )
    elif booking.is_paid():
        await callback_query.answer(
            text="Мы подтвердили вашу оплату, спасибо, ждем вас на встрече!",
            show_alert=True,
        )
    else:
        booking.set_user_confirm_paid(True)
        _ = await api_bookings.update_booking(booking)

        msg_to_user = await bot.send_message(
            chat_id=callback_query.from_user.id,
            text="Мы проверяем оплату, если сейчас ночь, то мы подтвердим бронирование утром, не волнуйтесь, мы вас ждем",
        )

        db_redis.set(
            key=redis_key,
            value=json.dumps({
                "booking_pk": booking.get_pk(),
                "member_tg_id": member.get_tg_id(),
                "user_chat_id": callback_query.from_user.id,
                "msg_to_user_id": msg_to_user.message_id,
            })
        )

        btn_builder_adm = InlineKeyboardBuilder()
        btn_builder_adm.button(
            text="Подтвердить бронирование",
            callback_data=ClbConfirm(postfix=ClbPostfix.confirm_booking_adm, pk=booking.get_pk())
        )
        btn_builder_adm.button(
            text="Отменить бронирование",
            callback_data=ClbDelete(postfix=ClbPostfix.booking_adm, pk=booking.get_pk())
        )

        btn_builder_adm.adjust(1)

        if member.get_login():
            notif_text = f"[{member.get_full_name()}]({member.get_link()}) говорит, что оплатил " \
                         f"встречу '{meeting.get_name()}', подтвердите оплату"
        else:
            notif_text = f"{member.get_full_name()} говорит, что оплатил " \
                         f"встречу '{meeting.get_name()}', подтвердите оплату"

        await bot.send_message(
            chat_id=ADMIN_CHANEL_ID,
            text=notif_text,
            reply_markup=btn_builder_adm.as_markup(),
        )

    await after_(callback_query.id)


@router.callback_query(ClbDelete.filter(F.postfix == ClbPostfix.booking_adm))
async def delete_booking_admin(callback_query: types.CallbackQuery, callback_data: ClbDelete):
    # todo добавить кнопку в меню мои бронирования
    chat_id: int = callback_query.message.chat.id

    redis_key: str = db_redis.generate_key([
        ClbPostfix.booking,
        callback_data.pk,
    ])
    redis_info_json: str = db_redis.get(redis_key)
    if not redis_info_json:
        redis_key: str = db_redis.generate_key([
            ClbPostfix.confirm_booking,
            callback_data.pk,
        ])
        redis_info_json: str = db_redis.get(redis_key)

    if not redis_info_json:
        await bot.send_message(
            chat_id=chat_id,
            text="похоже, что пользователь хз как отменил то ли записался то ли хер его, кароч в redis нет инфы про отмену",
        )
        await bot.edit_message_reply_markup(chat_id=chat_id, message_id=callback_query.message.message_id)
        await bot.edit_message_text(
            text=callback_query.message.md_text +
                 "\n\nпохоже, что пользователь хз как отменил то ли записался то ли хер его, кароч в redis нет инфы про отмену",
            chat_id=chat_id,
            message_id=callback_query.message.message_id
        )

        await after_(callback_query.id)
        return

    redis_info: dict = json.loads(redis_info_json)
    booking_pk: int | None = redis_info.get("booking_pk", None)
    member_tg_id: int | None = redis_info.get("member_tg_id", None)
    if not booking_pk or not member_tg_id:
        await bot.send_message(
            chat_id=chat_id,
            text="что по пошло не так и поломалось я хз, не нашел PK брони или tg id юзера, может позже",
        )

        await after_(callback_query.id)
        return

    booking: Booking = await api_bookings.get_booking_by_pk(pk=booking_pk)
    if not booking:
        await bot.send_message(
            chat_id=chat_id,
            text="что по пошло не так и поломалось я хз, не нашел бронь, может позже",
        )
        await after_(callback_query.id)
        return

    db_redis.delete(redis_key)
    await api_bookings.delete_booking(booking)

    user_chat_id = redis_info.get("user_chat_id", None)
    msg_to_user_id = redis_info.get("msg_to_user_id", None)
    if not user_chat_id or not msg_to_user_id:
        # todo дописать отправку текста с ошибкой (подумать куда)
        pass
    else:
        await bot.delete_message(
            chat_id=user_chat_id,
            message_id=msg_to_user_id
        )

    if booking.is_paid():
        text = "Бронь отменили, участника оповестил, что бабки вернули и все ок"
        usr_text = "Мы отменили вашу бронь и вернули деньги, увидимся на другой встрече, выберите для себя подходящую"
    else:
        text = "Бронь отменили, участника оповестил, бабок он не платил"
        usr_text = "Мы не подтвердили ваше бронирование, увидимся на другой встрече"

    meetings = await api_meetings.get_future_meetings()
    btn_builder = get_meetings_btn_builder(meetings)
    await bot.send_message(
        chat_id=member_tg_id,
        text=usr_text,
        reply_markup=btn_builder.as_markup()
    )

    await bot.edit_message_reply_markup(chat_id=chat_id, message_id=callback_query.message.message_id)
    await bot.edit_message_text(
        text=callback_query.message.md_text + f"\n\n{text}",
        chat_id=chat_id,
        message_id=callback_query.message.message_id
    )

    await after_(callback_query.id)


@router.callback_query(ClbConfirm.filter(F.postfix == ClbPostfix.confirm_booking_adm))
async def confirm_booking_admin(callback_query: types.CallbackQuery, callback_data: ClbConfirm):
    redis_key: str = db_redis.generate_key([
        ClbPostfix.confirm_booking,
        callback_data.pk,
    ])

    chat_id: int = callback_query.message.chat.id
    redis_info_json: str = db_redis.get(redis_key)
    if not redis_info_json:
        await bot.send_message(
            chat_id=chat_id,
            text="похоже, что пользователь отменил бронирование на встречу, ну и ладно",
        )
        await bot.edit_message_reply_markup(chat_id=chat_id, message_id=callback_query.message.message_id)
        await bot.edit_message_text(
            text=callback_query.message.md_text + "\n\nпохоже, что пользователь отменил бронирование на встречу, ну и ладно",
            chat_id=chat_id,
            message_id=callback_query.message.message_id
        )

        await after_(callback_query.id)
        return

    redis_info: dict = json.loads(redis_info_json)
    booking_pk: int | None = redis_info.get("booking_pk", None)
    member_tg_id: int | None = redis_info.get("member_tg_id", None)
    if not booking_pk or not member_tg_id:
        await bot.send_message(
            chat_id=chat_id,
            text="что по пошло не так и поломалось я хз, не нашел PK брони или tg id юзера, может позже",
        )

        await after_(callback_query.id)
        return

    booking: Booking = await api_bookings.get_booking_by_pk(pk=booking_pk)
    if not booking:
        await bot.send_message(
            chat_id=chat_id,
            text="что по пошло не так и поломалось я хз, не нашел бронь, может позже",
        )
        await after_(callback_query.id)
        return

    booking.set_is_paid(True)
    _ = await api_bookings.update_booking(booking)
    db_redis.delete(redis_key)

    user_chat_id = redis_info.get("user_chat_id", None)
    msg_to_user_id = redis_info.get("msg_to_user_id", None)
    if not user_chat_id or not msg_to_user_id:
        # todo дописать отправку текста с ошибкой (подумать куда)
        pass
    else:
        await bot.delete_message(
            chat_id=user_chat_id,
            message_id=msg_to_user_id
        )

    await bot.send_message(
        chat_id=member_tg_id,
        text="Мы подтвердили вашу оплату, спасибо, ждем вас на встрече!",
    )

    await bot.edit_message_reply_markup(chat_id=chat_id, message_id=callback_query.message.message_id)
    await bot.edit_message_text(
        text=callback_query.message.md_text + "\n\nБронь подтвердил, участника оповестил, что все оплачено и все ок",
        chat_id=chat_id,
        message_id=callback_query.message.message_id
    )

    await after_(callback_query.id)


async def after_(callback_query_id: str) -> None:
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
