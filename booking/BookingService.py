from datetime import datetime

from db.base.DbQuery import DbQuery
from booking.Booking import Booking
from ticket.Ticket import Ticket
from ticket.TicketService import TicketService
from user.User import User
from user.UserService import UserService


class BookingService:
    def __init__(self, db_queries: DbQuery):
        self.queries = db_queries

    @staticmethod
    def create(ticket: Ticket, user: User, date_time: datetime, is_paid: bool) -> Booking:
        return Booking(
            id=None,
            ticket=ticket,
            user=user,
            date_time=date_time,
            is_paid=is_paid,
        )

    def get_by_id(self, booking_id: int) -> Booking | None:
        result = self.queries.get_booking_by_id(booking_id)
        if not result:
            return None

        user_service = UserService(self.queries)
        user = user_service.get_by_id(user_id=result.get("user_id"))
        if not user:
            raise f"Can`t find user with ID {result.get('user_id')}"

        ticket_service = TicketService(self.queries)
        ticket = ticket_service.get_by_id(ticket_id=result.get("ticket_id"))
        if not ticket:
            raise f"Can`t find ticket with ID {result.get('ticket_id')}"

        return Booking(
            id=result.get("id"),
            ticket=ticket,
            user=user,
            date_time=result.get("date_time"),
            is_paid=result.get("paid"),
        )
