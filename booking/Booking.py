from dataclasses import dataclass
from datetime import datetime

from ticket.Ticket import Ticket
from user.User import User


@dataclass(slots=True)
class Booking:
    id: int | None
    ticket: Ticket
    user: User
    date_time: datetime
    is_paid: bool
