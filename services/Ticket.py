from dataclasses import dataclass
from datetime import datetime

from services.Meeting import Meeting
from services.User import User


@dataclass(frozen=True, slots=True)
class Ticket:
    id: int | None
    meeting: Meeting | None
    user: User | None
    booking_date_time: datetime
    paid: bool
