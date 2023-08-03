from datetime import datetime

from db.DbQuery import DbQuery
from services.Booking import Booking
from services.User import User
from services.UserService import UserService


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
        user = user_service.get_by_id(user_id=result.get("user_id"))
        if not user:
            raise f"Can`t find user with ID {result.get('user_id')}"

        booking = BookingService.create(
            user=user,
            booking_date_time=result.get("booking_date_time"),
            paid=bool(result.get("paid")),
        )
        booking.id = result.get("id")
        return booking
