import asyncio
import json
from datetime import datetime
from typing import Any

from aiogram import Bot, Dispatcher, types, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import User
from aiogram.utils.keyboard import InlineKeyboardBuilder
from magic_filter import F

from TgButtons import TgButtons
from TgButtonsAdmin import TgButtonsAdmin
from TgButtonsUser import TgButtonsUser
from api.bookings.ApiBookings import ApiBookings
from api.bookings.Booking import Booking
from api.meetings.ApiMeetings import ApiMeetings
from api.meetings.Meeting import Meeting
from api.members.ApiMembers import ApiMember
from api.members.Member import Member
from api.subscribes.Subscribe import Subscribe
from api.subscribes.ApiSubscribes import ApiSubscribes
from api.tickets.ApiTickets import ApiTickets
from clb_queries import ClbPage, ClbAdd, ClbDelete, Postfix, ClbConfirm
from api.tickets.Ticket import Ticket
from texts.Admins import Admins
from texts.Errors import Errors
from texts.Messages import Messages
from settings import TOKEN, HOST, ADMIN_CHANEL_ID, REDIS_HOST, REDIS_PORT
from api.settings import datetime_format_str_api
from utils.RedisHandler import RedisHandler
from utils.Service import Service

bot = Bot(token=TOKEN, parse_mode=ParseMode.MARKDOWN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

text_msg = Messages()
text_errors = Errors()
text_admins = Admins()

api_members = ApiMember(HOST)
api_meetings = ApiMeetings(HOST)
api_bookings = ApiBookings(HOST)
api_subscribes = ApiSubscribes(HOST)
api_tickets = ApiTickets(HOST)

db_redis = RedisHandler(host=REDIS_HOST, port=REDIS_PORT)

# todo система оповещений пользователей что скоро занятие
# todo добавить кнопку в меню мои бронирования
# todo подумать как сделать оповещения о бронировании и отмене


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        text=text_msg.hello(),
        reply_markup=TgButtonsUser.start_menu().as_markup(),
    )


@router.message()
async def delete_message(message: types.Message):
    await bot.delete_message(
        chat_id=message.chat.id,
        message_id=message.message_id
    )


@router.callback_query(ClbPage.filter(F.postfix == Postfix.start))
async def page_start_menu(callback: types.CallbackQuery):
    await replace_last_msg(
        callback=callback,
        text=text_msg.hello(),
        btn_builder=TgButtonsUser.start_menu()
    )
    await after_(callback=callback)


@router.callback_query(ClbPage.filter(F.postfix == Postfix.meetings))
async def page_meetings(callback: types.CallbackQuery):
    from_user: User = callback.from_user
    member: Member = await api_members.get_member_by_tg_id(tg_id=from_user.id)
    if not member:
        await Service.add_member(tg_user=from_user)

    meetings: list[Meeting] = await api_meetings.get_future_meetings()
    if not meetings:
        return await send_answer(
            callback=callback,
            text=text_msg.no_meetings()
        )

    btn_builder: InlineKeyboardBuilder = await TgButtonsUser.meetings(meetings=meetings)
    btn_builder: InlineKeyboardBuilder = TgButtonsUser.add_back(
        builder=btn_builder,
        callback=ClbPage(postfix=Postfix.start)
    )
    btn_builder.adjust(1)

    await replace_last_msg(
        callback=callback,
        text=text_msg.meetings_dates(),
        btn_builder=btn_builder
    )
    await after_(callback=callback)


@router.callback_query(ClbPage.filter(F.postfix == Postfix.meeting))
async def page_meeting(callback: types.CallbackQuery, callback_data: ClbPage):
    meeting: Meeting = await api_meetings.get_meeting_by_pk(pk=callback_data.pk)
    if not meeting:
        return await send_answer(callback=callback, text=text_errors.cant_find_meeting())

    tickets = await api_meetings.get_tickets(meeting=meeting)
    if not tickets or not meeting.get_can_be_booked():
        return await send_answer(callback=callback, text=text_msg.booking_unavailable())

    member: Member = await api_members.get_member_by_tg_id(tg_id=callback.from_user.id)
    if not member:
        return await send_answer(callback=callback, text=text_errors.strange_member())

    meeting_text: str = await Service.get_meeting_text(member=member, meeting=meeting)

    btn_builder: InlineKeyboardBuilder = await TgButtonsUser.meeting(member=member, meeting=meeting)
    btn_builder: InlineKeyboardBuilder = TgButtonsUser.add_back(
        builder=btn_builder,
        callback=ClbPage(postfix=Postfix.meetings)
    )
    btn_builder.adjust(1)

    await replace_last_msg(
        callback=callback,
        text=meeting_text,
        btn_builder=btn_builder
    )
    await after_(callback=callback)


@router.callback_query(ClbPage.filter(F.postfix == Postfix.subscribe))
async def page_subscribe(callback: types.CallbackQuery):
    member: Member = await api_members.get_member_by_tg_id(tg_id=callback.from_user.id)
    text = await Service.get_subscribe_text(member=member)

    builder: InlineKeyboardBuilder = await TgButtonsUser.subscribe(member=member)
    builder: InlineKeyboardBuilder = TgButtonsUser.add_back(
        builder=builder,
        callback=ClbPage(postfix=Postfix.start)
    )
    builder.adjust(1)

    await replace_last_msg(
        callback=callback,
        btn_builder=builder,
        text=text
    )
    await after_(callback=callback)


@router.callback_query(ClbConfirm.filter(F.postfix == Postfix.subscribe))
async def subscribe_confirm(callback: types.CallbackQuery):
    member = await api_members.get_member_by_tg_id(tg_id=callback.from_user.id)
    subscribe = await api_members.get_active_subscribe(member=member)
    if subscribe:
        if subscribe.is_paid():
            return await send_answer(
                callback=callback,
                text=text_msg.subs_success_pay_success()
            )
        elif subscribe.is_user_confirm_paid():
            return await send_answer(
                callback=callback,
                text=text_msg.subs_success_pay_confirm()
            )

    all_subscribes = await api_members.get_subscribes(member=member)
    new_subscribe = Subscribe(
        date_time=datetime.now().strftime(datetime_format_str_api),
        price=2000,
        user_confirm_paid=True,
        is_paid=False,
        is_active=False,
        is_first=not bool(all_subscribes),
        cnt_meetings=5,
    )
    try:
        added_subscribe = await api_subscribes.add_subscribe(new_subscribe=new_subscribe, member_id=member.get_pk())
    except Exception as e:
        # todo добавить логирование
        return await send_answer(
            callback=callback,
            text=text_errors.subs_error()
        )

    text: str = f"{Messages.about_subscribe()}\n\n{text_msg.subs_success_pay_confirm()}"

    btn_builder: InlineKeyboardBuilder = TgButtons.get_empty_builder()
    btn_builder: InlineKeyboardBuilder = TgButtonsUser.add_back(
        builder=btn_builder,
        callback=ClbPage(postfix=Postfix.start),

    )
    await replace_last_msg(callback=callback, btn_builder=btn_builder, text=text)

    redis_key = db_redis.get_key_confirm(name=Postfix.subscribe, pk=added_subscribe.get_pk())
    db_redis.set(
        key=redis_key,
        value=json.dumps({
            "member_tg_id": member.get_tg_id(),
            "user_chat_id": callback.from_user.id,
            "msg_to_user_id": callback.message.message_id,
        })
    )

    btn_builder_adm = TgButtons.get_empty_builder()
    btn_builder_adm = TgButtonsAdmin.add_confirm_payment(
        builder=btn_builder_adm,
        postfix=Postfix.adm_subscribe,
        pk=added_subscribe.get_pk(),
    )
    btn_builder_adm.adjust(1)

    notif_text: str = text_admins.confirm_pay_subs(
        user_info=member.get_markdown_link(),
    )
    await bot.send_message(
        chat_id=ADMIN_CHANEL_ID,
        text=notif_text,
        reply_markup=btn_builder_adm.as_markup(),
    )

    await after_(callback)


@router.callback_query(ClbAdd.filter(F.postfix == Postfix.booking))
async def booking_add(callback: types.CallbackQuery, callback_data: ClbAdd):
    member: Member = await api_members.get_member_by_tg_id(tg_id=callback.from_user.id)
    if not member:
        return await send_answer(callback=callback, text=text_errors.strange_member())

    meeting: Meeting = await api_meetings.get_meeting_by_pk(pk=callback_data.pk)
    ticket: Ticket = await api_meetings.get_ticket_by_member_id(
        meeting=meeting,
        member_id=member.get_pk()
    )
    if ticket:
        booking: Booking = await api_tickets.get_ticket_booking(ticket=ticket)
        if booking.is_paid():
            return await send_answer(callback=callback, text=text_msg.booking_success_pay_success())

        redis_key: str = db_redis.get_key_confirm(name=Postfix.booking, pk=booking.get_pk())
        redis_booking: str = db_redis.get(redis_key)
        if redis_booking:
            return await send_answer(callback=callback, text=text_msg.booking_success_pay_confirm())
        else:
            return await send_answer(callback=callback, text=text_msg.booking_already())

    free_tickets: list[Ticket] = await api_meetings.get_free_tickets(meeting=meeting)
    if not free_tickets:
        return await send_answer(callback=callback, text=text_msg.no_free_tickets())

    btn_builder: InlineKeyboardBuilder = TgButtons.get_empty_builder()
    try:
        await api_bookings.add_booking(
            new_booking=Booking(
                date_time=datetime.now().strftime(datetime_format_str_api),
                is_paid=False,
                user_confirm_paid=False,
            ),
            ticket_id=free_tickets[0].get_pk(),
            member_id=member.get_pk(),
        )
    except Exception as e:
        text: str = await Service.get_meeting_text(
            member,
            meeting,
            False,
            f"\n{text_errors.smt_went_wrong()}",
            f"\n{text_errors.try_one_more_time()}",
        )
        btn_builder = TgButtonsUser.add_booking(
            builder=btn_builder,
            pk=meeting.get_pk(),
        )
    else:
        text: str = await Service.get_meeting_text(
            member,
            meeting,
            False,
            f"\n{text_msg.booking_success()}",
            f"\n{text_msg.payment_info()}",
        )
        btn_builder = TgButtonsUser.payment_confirm(
            builder=btn_builder,
            pk=meeting.get_pk(),
            postfix=Postfix.booking_confirm,
        )
        btn_builder = TgButtonsUser.booking_cancel(
            builder=btn_builder,
            pk=meeting.get_pk(),
        )

    btn_builder: InlineKeyboardBuilder = TgButtonsUser.add_back(
        builder=btn_builder,
        callback=ClbPage(postfix=Postfix.meetings)
    )
    btn_builder.adjust(1)

    await replace_last_msg(callback, text, btn_builder)
    await after_(callback)


@router.callback_query(ClbConfirm.filter(F.postfix == Postfix.booking_confirm))
async def booking_confirm(callback: types.CallbackQuery, callback_data: ClbConfirm):
    meeting: Meeting = await api_meetings.get_meeting_by_pk(pk=callback_data.pk)
    member: Member = await api_members.get_member_by_tg_id(tg_id=callback.from_user.id)
    ticket: Ticket = await api_meetings.get_ticket_by_member_id(
        meeting=meeting,
        member_id=member.get_pk()
    )
    if not ticket:
        return await send_answer(
            callback=callback,
            text=text_msg.no_member_ticket()
        )

    booking: Booking = await api_tickets.get_ticket_booking(ticket=ticket)
    member: Member = await api_bookings.get_booking_member(booking=booking)

    redis_key: str = db_redis.get_key_confirm(name=Postfix.booking, pk=booking.get_pk())
    redis_info = db_redis.get(redis_key)

    if redis_info:
        return await send_answer(
            callback=callback,
            text=text_msg.booking_success_pay_confirm()
        )
    elif booking.is_paid():
        return await send_answer(
            callback=callback,
            text=text_msg.booking_success_pay_success()
        )

    booking.set_user_confirm_paid(value=True)
    try:
        await api_bookings.update_booking(booking=booking)
    except Exception as e:
        # todo добавить логирование
        return await send_answer(
            callback=callback,
            text=text_errors.booking_error()
        )

    text: str = await Service.get_meeting_text(
        member,
        meeting,
        False,
        f"\n{text_msg.booking_success()}",
        f"\n{text_msg.booking_success_pay_confirm()}",
    )
    btn_builder = await TgButtonsUser.meeting(member=member, meeting=meeting)
    await replace_last_msg(callback=callback, btn_builder=btn_builder, text=text)

    db_redis.set(
        key=redis_key,
        value=json.dumps({
            "meeting_pk": meeting.get_pk(),
            "member_tg_id": member.get_tg_id(),
            "user_chat_id": callback.from_user.id,
            "msg_to_user_id": callback.message.message_id,
        })
    )

    btn_builder_adm = TgButtons.get_empty_builder()
    btn_builder_adm = TgButtonsAdmin.add_confirm_payment(
        builder=btn_builder_adm,
        postfix=Postfix.adm_booking_confirm,
        pk=booking.get_pk(),
    )
    btn_builder_adm = TgButtonsAdmin.add_cancel(
        builder=btn_builder_adm,
        postfix=Postfix.adm_booking,
        pk=booking.get_pk(),
    )
    btn_builder_adm.adjust(1)

    notif_text: str = text_admins.confirm_pay(
        user_info=member.get_markdown_link(),
        meeting_info=meeting.get_name(),
    )
    await bot.send_message(
        chat_id=ADMIN_CHANEL_ID,
        text=notif_text,
        reply_markup=btn_builder_adm.as_markup(),
    )

    await after_(callback)


@router.callback_query(ClbDelete.filter(F.postfix == Postfix.booking))
async def booking_delete(callback: types.CallbackQuery, callback_data: ClbDelete):
    meeting: Meeting = await api_meetings.get_meeting_by_pk(pk=callback_data.pk)
    if not meeting:
        return await send_answer(callback=callback, text=text_errors.cant_find_meeting())

    member: Member = await api_members.get_member_by_tg_id(tg_id=callback.from_user.id)
    member_ticket: Ticket = await api_meetings.get_ticket_by_member_id(
        meeting=meeting,
        member_id=member.get_pk()
    )
    if not member_ticket:
        return await send_answer(
            callback=callback,
            text=text_msg.cancel_already(what="запись на эту встречу")
        )

    booking: Booking = await api_tickets.get_ticket_booking(ticket=member_ticket)
    redis_key: str = db_redis.get_key_delete(name=Postfix.booking, pk=booking.get_pk())
    redis_info: Any = db_redis.get(redis_key)

    if redis_info:
        return await send_answer(
            callback=callback,
            text=text_msg.cancel_with_return_money()
        )

    if not all([booking.is_paid(), booking.is_user_confirm_paid()]):
        await api_bookings.delete_booking(booking)

        meetings: list[Meeting] = await api_meetings.get_future_meetings()
        if not meetings:
            text: str = text_msg.no_meetings_after_cancel()
        else:
            text: str = text_msg.meeting_dates_after_cancel()

        btn_builder: InlineKeyboardBuilder = await TgButtonsUser.meetings(meetings=meetings)
        await replace_last_msg(
            callback=callback,
            text=text,
            btn_builder=btn_builder
        )
        return await after_(callback=callback)

    if meeting.is_meeting_today():
        text = text_msg.cancel_with_return_no_money()
    else:
        text = text_msg.cancel_with_return_money()

    meetings: list[Meeting] = await api_meetings.get_future_meetings()
    user_btn_builder = await TgButtonsUser.meetings(meetings=meetings)
    await replace_last_msg(callback=callback, btn_builder=user_btn_builder, text=text)

    member: Member = await api_bookings.get_booking_member(booking=booking)
    db_redis.set(
        key=redis_key,
        value=json.dumps({
            "booking_pk": booking.get_pk(),
            "member_tg_id": member.get_tg_id(),
            "user_chat_id": callback.from_user.id,
            "msg_to_user_id": callback.message.message_id,
        })
    )

    notif_text: str = text_admins.confirm_cancel(
        user_info=member.get_markdown_link(),
        meeting_info=meeting.get_name(),
    )

    btn_builder_adm: InlineKeyboardBuilder = TgButtons.get_empty_builder()
    btn_builder_adm = TgButtonsAdmin.add_confirm_refund(
        builder=btn_builder_adm,
        postfix=Postfix.adm_booking,
        pk=booking.get_pk()
    )

    btn_builder_adm.adjust(1)

    await bot.send_message(
        chat_id=ADMIN_CHANEL_ID,
        text=notif_text,
        reply_markup=btn_builder_adm.as_markup(),
    )

    await after_(callback=callback)


@router.callback_query(ClbDelete.filter(F.postfix == Postfix.booking_confirm))
async def booking_delete_confirm(callback: types.CallbackQuery, callback_data: ClbDelete):
    member = await api_members.get_member_by_tg_id(tg_id=callback.from_user.id)
    if not member:
        return await send_answer(callback=callback, text=text_errors.strange_member())

    meeting = await api_meetings.get_meeting_by_pk(pk=callback_data.pk)
    if not meeting:
        return await send_answer(callback=callback, text=text_errors.cant_find_meeting())

    btn_builder = TgButtons.get_empty_builder()
    btn_builder = TgButtonsUser.booking_cancel(
        builder=btn_builder,
        pk=callback_data.pk,
        text="Да, отменить запись"
    )
    btn_builder = TgButtonsUser.add_back(
        builder=btn_builder,
        callback=ClbPage(postfix=Postfix.meeting, pk=meeting.get_pk())
    )

    btn_builder.adjust(1)

    await replace_last_msg(
        callback=callback,
        text=text_msg.cancel_in_meeting_day(),
        btn_builder=btn_builder,
    )
    await after_(callback=callback)


@router.callback_query(ClbConfirm.filter(F.postfix == Postfix.adm_booking_confirm))
async def admin_booking_confirm(callback: types.CallbackQuery, callback_data: ClbConfirm):
    redis_key: str = db_redis.get_key_confirm(name=Postfix.booking, pk=callback_data.pk)
    redis_info_json: str = db_redis.get(redis_key)

    if not redis_info_json:
        await replace_last_msg(
            callback=callback,
            text=callback.message.md_text + f"\n\n{text_admins.cancel_already(what='запись на встречу')}",
            btn_builder=TgButtons.get_empty_builder(),
        )
        return await after_(callback)

    redis_info: dict = json.loads(redis_info_json)
    meeting_pk: int | None = redis_info.get("meeting_pk", None)
    member_tg_id: int | None = redis_info.get("member_tg_id", None)
    if not meeting_pk or not member_tg_id:
        await replace_last_msg(
            callback=callback,
            text=callback.message.md_text + f"\n\n{text_admins.error()}, не нашел в редисе PK брони или tg id юзера",
            btn_builder=TgButtons.get_empty_builder(),
        )
        return await after_(callback)

    booking: Booking = await api_bookings.get_booking_by_pk(pk=callback_data.pk)
    if not booking:
        await replace_last_msg(
            callback=callback,
            text=callback.message.md_text + f"\n\n{text_admins.error()}, не нашел бронь, может позже",
            btn_builder=TgButtons.get_empty_builder(),
        )
        return await after_(callback)

    booking.set_is_paid(True)
    _ = await api_bookings.update_booking(booking)
    db_redis.delete(redis_key)

    user_chat_id = redis_info.get("user_chat_id", None)
    msg_to_user_id = redis_info.get("msg_to_user_id", None)
    if not user_chat_id or not msg_to_user_id:
        # todo дописать отправку текста с ошибкой (подумать куда)
        pass
    else:
        member = await api_members.get_member_by_pk(pk=booking.get_member_pk())
        if not member:
            return await send_answer(callback=callback, text=text_errors.strange_member())

        meeting = await api_meetings.get_meeting_by_pk(pk=meeting_pk)
        if not meeting:
            return await send_answer(callback=callback, text=text_errors.cant_find_meeting())

        await bot.delete_message(
            chat_id=user_chat_id,
            message_id=msg_to_user_id
        )
        text = await Service.get_meeting_text(
            member,
            meeting,
            False,
            f"\n{text_msg.booking_success_pay_success()}",
        )
        btn_builder = await TgButtonsUser.meeting(member=member, meeting=meeting)
        btn_builder = TgButtonsUser.add_back(
            builder=btn_builder,
            callback=ClbPage(postfix=Postfix.meetings)
        )
        btn_builder.adjust(1)

        await bot.send_message(
            text=text,
            chat_id=user_chat_id,
            reply_markup=btn_builder.as_markup(),
        )

        await replace_last_msg(
            callback=callback,
            text=callback.message.md_text + f"\n\n{text_admins.booking_success()}",
            btn_builder=TgButtons.get_empty_builder()
        )

    await after_(callback)


@router.callback_query(ClbDelete.filter(F.postfix == Postfix.adm_booking))
async def admin_booking_delete(callback: types.CallbackQuery, callback_data: ClbDelete):
    booking_pk: int = callback_data.pk

    redis_key: str = db_redis.get_key_delete(name=Postfix.booking, pk=booking_pk)
    redis_info_json: str = db_redis.get(redis_key)

    if not redis_info_json:
        redis_key: str = db_redis.get_key_confirm(name=Postfix.booking, pk=booking_pk)
        redis_info_json: str = db_redis.get(redis_key)

    if not redis_info_json:
        await bot.send_message(
            chat_id=ADMIN_CHANEL_ID,
            text=f"{text_admins.error()}, кароч в redis нет инфы про отмену",
        )
        return await after_(callback)

    redis_info: dict = json.loads(redis_info_json)
    member_tg_id: int | None = redis_info.get("member_tg_id", None)
    if not booking_pk or not member_tg_id:
        await bot.send_message(
            chat_id=ADMIN_CHANEL_ID,
            text=f"{text_admins.error()}, не нашел PK брони или tg id юзера, может позже",
        )
        return await after_(callback)

    booking: Booking = await api_bookings.get_booking_by_pk(pk=booking_pk)
    if not booking:
        await bot.send_message(
            chat_id=ADMIN_CHANEL_ID,
            text=f"{text_admins.error()}, не нашел бронь, может позже",
        )
        return await after_(callback)

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
        text = text_admins.booking_cancel_success()
        usr_text = text_msg.cancel_with_return_success()
    else:
        text = text_admins.booking_cancel_success_check_money()
        usr_text = text_msg.cancel_by_admin()

    meetings = await api_meetings.get_future_meetings()
    btn_builder = await TgButtonsUser.meetings(meetings)
    await bot.send_message(
        chat_id=member_tg_id,
        text=usr_text,
        reply_markup=btn_builder.as_markup()
    )

    await replace_last_msg(
        callback=callback,
        btn_builder=TgButtons.get_empty_builder(),
        text=callback.message.md_text + f"\n\n{text}"
    )

    await after_(callback)


@router.callback_query(ClbConfirm.filter(F.postfix == Postfix.adm_subscribe))
async def admin_subscribe_confirm(callback: types.CallbackQuery, callback_data: ClbConfirm):
    redis_key: str = db_redis.get_key_confirm(name=Postfix.subscribe, pk=callback_data.pk)
    redis_info_json: str = db_redis.get(redis_key)
    if not redis_info_json:
        await replace_last_msg(
            callback=callback,
            text=callback.message.md_text + f"\n\n{text_admins.cancel_already(what='покупку абонемента')}",
            btn_builder=TgButtons.get_empty_builder(),
        )
        return await after_(callback)

    redis_info: dict = json.loads(redis_info_json)
    member_tg_id: int | None = redis_info.get("member_tg_id", None)
    if not member_tg_id:
        await replace_last_msg(
            callback=callback,
            text=callback.message.md_text + f"\n\n{text_admins.error()}, не нашел в редисе PK tg id юзера",
            btn_builder=TgButtons.get_empty_builder(),
        )
        return await after_(callback)

    subscribe: Subscribe = await api_subscribes.get_subscribe_by_pk(pk=callback_data.pk)
    if not subscribe:
        await replace_last_msg(
            callback=callback,
            text=callback.message.md_text + f"\n\n{text_admins.error()}, не нашел абонемент, может позже",
            btn_builder=TgButtons.get_empty_builder(),
        )
        return await after_(callback)

    subscribe.set_is_paid(True)
    subscribe.set_is_active(True)
    _ = await api_subscribes.update_subscribe(subscribe)
    db_redis.delete(redis_key)

    user_chat_id = redis_info.get("user_chat_id", None)
    msg_to_user_id = redis_info.get("msg_to_user_id", None)
    if not user_chat_id or not msg_to_user_id:
        # todo дописать отправку текста с ошибкой (подумать куда)
        pass
    else:
        member = await api_members.get_member_by_pk(pk=subscribe.get_member_pk())
        if not member:
            return await send_answer(callback=callback, text=text_errors.strange_member())

        await bot.delete_message(
            chat_id=user_chat_id,
            message_id=msg_to_user_id
        )
        text = await Service.get_subscribe_text(
            member,
            f"\n{text_msg.subs_success_pay_success()}",
        )
        btn_builder = TgButtons.get_empty_builder()
        btn_builder = TgButtonsUser.add_back(
            builder=btn_builder,
            callback=ClbPage(postfix=Postfix.start)
        )
        btn_builder.adjust(1)

        await bot.send_message(
            text=text,
            chat_id=user_chat_id,
            reply_markup=btn_builder.as_markup(),
        )

        await replace_last_msg(
            callback=callback,
            text=callback.message.md_text + f"\n\n{text_admins.subscribe_success()}",
            btn_builder=TgButtons.get_empty_builder()
        )

    await after_(callback)


async def replace_last_msg(callback: types.CallbackQuery, text: str, btn_builder: InlineKeyboardBuilder):
    await bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text=text,
        reply_markup=btn_builder.as_markup(),
        disable_web_page_preview=True,

    )


async def send_answer(callback: types.CallbackQuery, text: str):
    await callback.answer(text=text, show_alert=True)
    await after_(callback=callback)


async def after_(callback: types.CallbackQuery) -> None:
    await bot.answer_callback_query(callback.id)


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
