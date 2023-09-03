from enum import Enum

from settings import HOST
from api.meetings.ApiMeetings import ApiMeetings

api_meetings = ApiMeetings(HOST)


class ClbPrefix(Enum):
    meeting = "meeting"
    booking = "booking"


# todo сделать типзацию и проверить чтобы все передавали str
def get_clb_data(prefix, postfix):
    return "_".join((str(prefix), str(postfix)))


def get_postfix(clb_data: str):
    return clb_data.split("_")[-1]


def get_clb_meetings() -> list:
    return [get_clb_data(ClbPrefix.meeting.value, meeting.get_pk()) for meeting in api_meetings.get_meetings()]


def get_clb_booking() -> list:
    return [get_clb_data(ClbPrefix.booking.value, meeting.get_pk()) for meeting in api_meetings.get_meetings()]
