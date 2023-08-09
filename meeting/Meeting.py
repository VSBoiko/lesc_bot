from dataclasses import dataclass
from datetime import datetime
from place.Place import Place
from booking.Booking import Booking
from ticket.Ticket import Ticket


@dataclass(slots=True)
class Meeting:
    id: int | None
    date_time: datetime
    name: str
    place: Place
    tickets: list[Ticket]
    bookings: list[Booking]
