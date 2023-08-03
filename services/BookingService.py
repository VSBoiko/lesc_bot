from datetime import datetime

from db.DbQuery import DbQuery
from services.Booking import Booking
from services.User import User
from services.UserService import UserService
from services.Utils import Utils


class BookingService:
    def __init__(self, db_queries: DbQuery):
        self.queries = db_queries

    @staticmethod
    def create(user: User, booking_date_time: datetime, paid: bool) -> Booking:
        return Booking(
            id=None,
            user=user,
            booking_date_time=booking_date_time,
            paid=paid,
        )

    def get_by_id(self, booking_id: int) -> Booking | None:
        result = self.queries.get_booking_by_id(booking_id)
        if not result:
            return None

        user_service = UserService(self.queries)
        if result.get("user_id"):
            user = user_service.get_by_id(user_id=result.get("user_id"))
        else:
            user = None

        if result.get("booking_date_time"):
            booking_date_time = Utils.get_date_from_str(
                result.get("booking_date_time"),
                date_str_format="%Y-%m-%d %H:%M:%S"
            )
        else:
            booking_date_time = None

        return Booking(
            id=result.get("id"),
            user=user,
            booking_date_time=booking_date_time,
            paid=bool(result.get("paid")),
        )
