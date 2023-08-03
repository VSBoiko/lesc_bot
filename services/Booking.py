from dataclasses import dataclass
from datetime import datetime

from services.User import User


@dataclass(slots=True)
class Booking:
    id: int | None
    user: User | None
    booking_date_time: datetime
    paid: bool
