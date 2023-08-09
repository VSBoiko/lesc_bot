from datetime import datetime, timedelta

from booking.Booking import Booking
from booking.BookingService import BookingService
from meeting.Meeting import Meeting
from place.Place import Place
from place.PlaceService import PlaceService
from ticket.Ticket import Ticket
from ticket.TicketService import TicketService
from user.User import User


class MeetingService:
    def __init__(self, queries):
        self.queries = queries

    @staticmethod
    def create(name: str, place: Place, tickets: list[Ticket], booking: list[Booking], date_time: datetime) -> Meeting:
        return Meeting(
            id=None,
            date_time=date_time,
            name=name,
            place=place,
            tickets=tickets,
            bookings=booking,
        )

    def get_by_id(self, meeting_id: int) -> Meeting:
        result = self.queries.get_meeting_by_id(meeting_id=meeting_id)
        if not result:
            raise f"No meeting with ID {meeting_id}"

        place_service = PlaceService(db_queries=self.queries)
        place = place_service.get_by_id(place_id=result.get("place_id"))
        if not place:
            raise f"No place with ID {result.get('place_id')}"

        meeting_tickets = self.queries.get_tickets_by_meeting_id(meeting_id=result.get("id"))
        tickets_service = TicketService(self.queries)
        tickets_list = [tickets_service.get_by_id(ticket_id=ticket.get("id")) for ticket in meeting_tickets]

        meeting_bookings = self.queries.get_bookings_by_meeting_id(meeting_id=result.get("id"))
        book_service = BookingService(self.queries)
        bookings_list = [book_service.get_by_id(booking_id=booking.get("id")) for booking in meeting_bookings]

        return Meeting(
            id=result.get("id"),
            date_time=result.get("date_time"),
            name=result.get("name"),
            place=place,
            tickets=tickets_list,
            bookings=bookings_list,
        )

    def get_actual_meetings(self):
        db_meetings = self.queries.get_meetings()
        actual_meetings = []
        for db_meeting in db_meetings:
            meeting = self.get_by_id(db_meeting.get("id"))
            if meeting.date_time > datetime.now() - timedelta(hours=4):
                actual_meetings.append(meeting)

        return actual_meetings

    @staticmethod
    def get_free_tickets(meeting: Meeting):
        bookings_tickets = [booking.ticket for booking in meeting.bookings]
        return [ticket for ticket in meeting.tickets if ticket not in bookings_tickets]

    @staticmethod
    def is_user_have_meeting_booking(meeting: Meeting, user: User) -> bool:
        bookings = meeting.bookings
        user_booking = [booking for booking in bookings if booking.user.id == user.id]
        return bool(user_booking)

    def add_meeting_booking(self, user: User, ticket: Ticket, is_paid: bool):
        self.queries.add_booking([
            ticket.id,
            user.id,
            is_paid,
        ])
