from enum import Enum

from db.PgDatabase import PgDatabase
from db.PgQuery import PgQuery
from settings import DB_NAME, DB_USER, DB_USER_PASS

db = PgDatabase(DB_NAME, DB_USER, DB_USER_PASS)
queries = PgQuery(db)


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
