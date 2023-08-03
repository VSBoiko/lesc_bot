from datetime import datetime

from services.Booking import Booking
from services.BookingService import BookingService
from services.Meeting import Meeting
from services.Place import Place
from services.PlaceService import PlaceService
from Utils import Utils


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

    def get_by_id(self, meeting_id: int):
        result = self.queries.get_meeting_by_id(meeting_id=meeting_id)
        if not result:
            return None

        place_service = PlaceService(db_queries=self.queries)
        place = place_service.get_by_id(place_id=result.get("place_id"))
        if not place:
            return None

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
