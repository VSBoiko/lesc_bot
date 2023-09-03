

from api.base.Base import Base
from api.bookings.Booking import Booking
from api.members.Member import Member


class Ticket(Base):
    def __init__(
            self, price: float, pk: int | None = None, **kwargs
    ):
        super().__init__(pk=pk)

        self._booking: Booking | None = None

        self._price: float = price
        self._pk: int | None = pk

        booking: list[dict] = kwargs.get("booking") if "booking" in kwargs else []
        if booking:
            self._set_booking(booking.pop())

    def get_booking(self) -> Booking | None:
        return self._booking

    def get_price(self) -> float:
        return self._price

    def get_pk(self) -> int:
        return self._pk

    def has_booking(self) -> bool:
        return bool(self.get_booking())

    def get_booking_member(self) -> Member | None:
        booking: Booking | None = self.get_booking()
        return booking.get_member() if isinstance(booking, Booking) else None

    def _set_booking(self, value: dict):
        self._booking = Booking(**value)
