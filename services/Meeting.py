from dataclasses import dataclass
from datetime import datetime
from Place import Place
from Booking import Booking


@dataclass(slots=True)
class Meeting:
    id: int | None
    date_time: datetime
    name: str
    place: Place
    booking: list[Booking]
