from api.base.ApiBase import ApiBase, T_HOST
from .Booking import Booking
from ..settings import datetime_format_str_api


class ApiBookings(ApiBase):
    def __init__(self, base_url: T_HOST):
        super().__init__(base_url)

    async def get_bookings(self) -> list[Booking]:
        bookings = await self._api_get_bookings()
        return [Booking(**booking) for booking in bookings]

    async def get_booking_by_pk(self, pk: int) -> Booking | None:
        booking = await self._api_get_bookings(pk=pk)
        return Booking(**booking[0]) if booking else None

    async def add_booking(self, new_booking: Booking, member_id, ticket_id,) -> Booking:
        result: dict = await self._api_add_booking(
            date_time=new_booking.get_date_time().strftime(datetime_format_str_api),
            is_paid=new_booking.is_paid(),
            member_id=member_id,
            ticket_id=ticket_id,
        )
        if result:
            return Booking(**result)
        else:
            raise

    async def delete_booking(self, pk: int) -> bool:
        return await self._api_delete_booking(pk=pk)

    async def update_booking(self, booking: Booking) -> Booking:
        result: dict = await self._api_patch_booking(
            pk=booking.get_pk(),
            date_time=booking.get_date_time().strftime(datetime_format_str_api),
            is_paid=booking.is_paid()
        )
        if result:
            return Booking(**result)
        else:
            raise
