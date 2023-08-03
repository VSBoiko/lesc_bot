from datetime import datetime

from services.Ticket import Ticket
from services.Meeting import Meeting
from services.MeetingService import MeetingService
from services.User import User
from services.UserService import UserService
from services.Utils import Utils


class TicketService:
    def __init__(self, queries):
        self.queries = queries

    @staticmethod
    def create(meeting: Meeting | None, user: User, booking_date_time: datetime, paid: bool) -> Ticket:
        return Ticket(
            id=None,
            meeting=meeting,
            user=user,
            booking_date_time=booking_date_time,
            paid=paid,
        )

    def get_by_id(self, booking_id: int) -> Ticket | None:
        result = self.queries.get_booking_by_id(booking_id=booking_id)
        user_service = UserService(self.queries)
        user = user_service.get_by_id(user_id=result.get("user_id"))
        if not user:
            raise f"Can`t find user with ID {result.get('user_id')}"

        meeting_service = MeetingService(queries=self.queries)
        meeting = meeting_service.get_by_id(meeting_id=result.get("meeting_id"))
        return Ticket(
            id=booking_id,
            meeting=meeting,
            user=user,
            booking_date_time=Utils.get_date_from_str(result.get("booking_date_time")),
            paid=bool(result.get("paid")),
        )
