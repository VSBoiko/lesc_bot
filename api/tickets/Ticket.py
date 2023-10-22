from api.base.Base import Base


class Ticket(Base):
    def __init__(
            self, price: float, pk: int | None = None, **kwargs
    ):
        super().__init__(pk=pk, **kwargs)

        self._booking_pk: int | None = None

        self._price: float = price

        bookings: dict = kwargs.get("booking", [])
        if bookings:
            self._set_booking_pk(bookings[0].get("id", None))

    def get_booking_pk(self) -> int | None:
        return self._booking_pk

    def get_price(self) -> float:
        return self._price

    def get_pk(self) -> int:
        return self._pk

    def has_booking(self) -> bool:
        return bool(self.get_booking_pk())

    def _set_booking_pk(self, value: dict):
        self._booking_pk = value
