from datetime import datetime


from api.base.Base import Base
from api.places.Place import Place
from api.tickets.Ticket import Ticket


class Meeting(Base):
    def __init__(
            self, name: str, date_time: str, can_be_booked: bool,
            pk: int | None = None, **kwargs
    ):
        super().__init__(pk=pk, **kwargs)

        self._date_time: datetime | None = None
        self._place_pk: int | None = None
        self._tickets_pk: list[int] | None = None

        self._name: str = name
        self._can_be_booked: bool = can_be_booked

        self._set_date_time(datetime.strptime(date_time, self._date_time_format_db))

        place: dict = kwargs.get("place", {})
        if place:
            self._set_place_pk(place.get("id", None))

        tickets: list[dict] = kwargs.get("tickets", [])
        if tickets:
            self._set_tickets_pk([t.get("pk", None) for t in tickets])

    def get_place_pk(self) -> int:
        return self._place_pk

    def get_tickets_pk(self) -> list[int]:
        return self._tickets_pk

    def get_can_be_booked(self) -> bool:
        return self._can_be_booked

    def get_name(self) -> str:
        return self._name

    def get_date_time(self) -> datetime:
        return self._date_time

    def is_meeting_today(self):
        return self.get_date_time().date() == datetime.today().date()

    def _set_date_time(self, value: datetime):
        self._date_time: datetime = value

    def _set_tickets_pk(self, value: list[int]):
        self._tickets_pk: list[int] = value

    def _set_place_pk(self, value: int | None):
        self._place_pk: int | None = value


