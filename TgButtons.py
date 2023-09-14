from datetime import datetime

from aiogram.utils.keyboard import InlineKeyboardBuilder

from api.meetings.Meeting import Meeting
from api.settings import datetime_format_str
from clb_queries import ClbShowDetail, ClbPostfix


def get_meetings_btn_builder(meetings: list[Meeting]) -> InlineKeyboardBuilder:
    if not meetings:
        InlineKeyboardBuilder()

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

    return btn_builder
