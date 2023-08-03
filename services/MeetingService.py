from datetime import datetime, timedelta

from services.Booking import Booking
from services.BookingService import BookingService
from services.Meeting import Meeting
from services.Place import Place
from services.PlaceService import PlaceService
from services.Utils import Utils


class MeetingService:
    def __init__(self, queries):
        self.queries = queries

    @staticmethod
    def create(name: str, place: Place, booking: list[Booking], date_time: datetime) -> Meeting:
        return Meeting(
            id=None,
            date_time=date_time,
            name=name,
            place=place,
            booking=booking,
        )

    def get_by_id(self, meeting_id: int) -> Meeting :
        result = self.queries.get_meeting_by_id(meeting_id=meeting_id)
        if not result:
            raise f"No meeting with ID {meeting_id}"

        place_service = PlaceService(db_queries=self.queries)
        place = place_service.get_by_id(place_id=result.get("place_id"))
        if not place:
            raise f"No place with ID {result.get('place_id')}"

        meeting_bookings = self.queries.get_bookings_by_meeting_id(meeting_id=result.get("id"))
        book_service = BookingService(self.queries)
        booking_list = [book_service.get_by_id(booking_id=booking.get("id")) for booking in meeting_bookings]

        return Meeting(
            id=result.get("id"),
            date_time=Utils.get_date_from_str(result.get("date_time")),
            name=result.get("name"),
            place=place,
            booking=booking_list,
        )

    def get_actual_meetings(self):
        db_meetings = self.queries.get_meetings()
        actual_meetings = []
        for db_meeting in db_meetings:
            meeting = self.get_by_id(db_meeting.get("id"))
            if meeting.date_time > datetime.now() - timedelta(hours=4):
                actual_meetings.append(meeting)

        return actual_meetings

    def get_free_booking(self, meeting: Meeting):
        bookings = meeting.booking
        return [booking for booking in bookings if booking.user is None]
