from dataclasses import dataclass
from datetime import datetime
from services.Place import Place
from services.Booking import Booking


@dataclass(slots=True)
class Meeting:
    id: int | None
    date_time: datetime
    name: str
    place: Place
    booking: list[Booking]
