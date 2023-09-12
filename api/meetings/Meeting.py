from datetime import datetime


from api.base.Base import Base
from api.members.Member import Member
from api.places.Place import Place
from api.tickets.Ticket import Ticket


class Meeting(Base):
    def __init__(
            self, name: str, date_time: str, can_be_booked: bool,
            pk: int | None = None, **kwargs
    ):
        super().__init__(pk=pk)

        self._date_time: datetime | None = None
        self._place: Place | None = None
        self._tickets: list[Ticket] | None = None

        self._name: str = name
        self._can_be_booked: bool = can_be_booked
        self._pk: int | None = pk

        self._set_date_time(datetime.strptime(date_time, self._date_time_format_db))

        place: dict = kwargs.get("place") if "place" in kwargs else {}
        if place:
            self._set_place(place)

        tickets: list[dict] = kwargs.get("tickets") if "tickets" in kwargs else []
        self._set_tickets(tickets)

    def get_place(self) -> Place:
        return self._place

    def get_tickets(self) -> list[Ticket]:
        return self._tickets

    def get_can_be_booked(self) -> bool:
        return self._can_be_booked

    def get_name(self) -> str:
        return self._name

    def get_date_time(self) -> datetime:
        return self._date_time

    def get_free_tickets(self) -> list[Ticket]:
        return list(filter(lambda x: not x.has_booking(), self._tickets))

    def get_busy_tickets(self) -> list[Ticket]:
        return list(filter(lambda x: x.has_booking(), self._tickets))

    def get_ticket_by_td_id(self, tg_id: int) -> Ticket | None:
        busy_tickets: list[Ticket] = self.get_busy_tickets()
        if not busy_tickets:
            return None

        member_ticket: list[Ticket] = list(filter(lambda x: x.get_booking_member() == tg_id, busy_tickets))
        if not member_ticket:
            return None

        return member_ticket[0]

    def check_booking_by_td_id(self, tg_id: int) -> bool:
        return bool(self.get_ticket_by_td_id(tg_id=tg_id))

    def get_ticket_by_tg_id(self, tg_id) -> Ticket | None:
        busy_tickets: list[Ticket] = self.get_busy_tickets()
        if not busy_tickets:
            return None

        check_result: list = list(filter(lambda x: x.get_booking_member().get_tg_id() == tg_id, busy_tickets))
        return check_result[0] if check_result else None

    def add_booking(self):
        pass

    def get_pk(self) -> int:
        return self._pk

    def _set_date_time(self, value: datetime):
        self._date_time: datetime = value

    def _set_tickets(self, value: list[dict]):
        self._tickets: list[Ticket] = [Ticket(**t) for t in value]

    def _set_place(self, value: dict):
        self._place: Place = Place(**value)


