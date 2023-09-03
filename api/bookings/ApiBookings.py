from api.base.ApiBase import ApiBase, T_HOST
from .Booking import Booking
from ..settings import datetime_format_str_api


class ApiBookings(ApiBase):
    def __init__(self, base_url: T_HOST):
        super().__init__(base_url)

    def get_bookings(self) -> list[Booking]:
        return [Booking(**booking) for booking in self._api_get_bookings()]

    def get_booking_by_pk(self, pk: int) -> Booking | None:
        result: list[Booking] = [Booking(**booking) for booking in self._api_get_bookings(pk=pk)]
        return result[0] if result else None

    def add_booking(self, new_booking: Booking, member_id, ticket_id,) -> Booking:
        result: dict = self._api_add_booking(
            date_time=new_booking.get_date_time().strftime(datetime_format_str_api),
            is_paid=new_booking.is_paid(),
            member_id=member_id,
            ticket_id=ticket_id,
        )
        if result:
            return Booking(**result)
        else:
            raise
