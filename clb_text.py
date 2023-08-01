from enum import Enum

from db.Db import Db
from db.DbQuery import DbQuery
from settings import DB_PATH

db = Db(DB_PATH)
queries = DbQuery(DB_PATH)


class ClbPrefix(Enum):
    meeting = "meeting"
    booking = "booking"


# todo сделать типзацию и проверить чтобы все передавали str
def get_clb_data(prefix, postfix):
    return "_".join((str(prefix), str(postfix)))


def get_postfix(clb_data: str):
    return clb_data.split("_")[-1]


def get_clb_meetings() -> list:
    return [get_clb_data(ClbPrefix.meeting.value, meeting.get("id")) for meeting in queries.get_meetings()]


def get_clb_booking() -> list:
    return [get_clb_data(ClbPrefix.booking.value, meeting.get("id")) for meeting in queries.get_meetings()]
