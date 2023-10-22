from api.base.ApiBase import ApiBase, T_HOST
from .Booking import Booking
from ..members.Member import Member
from ..subscribes.Subscribe import Subscribe


class ApiBookings(ApiBase):
    def __init__(self, base_url: T_HOST):
        super().__init__(base_url)

    async def get_bookings(self) -> list[Booking]:
        bookings = await self._api_get_bookings()
        return [Booking(**booking) for booking in bookings]

    async def get_booking_by_pk(self, pk: int) -> Booking | None:
        booking = await self._api_get_bookings(id=pk)
        return Booking(**booking[0]) if booking else None

    async def get_booking_member(self, booking: Booking):
        members = await self._api_get_members(id=booking.get_member_pk())
        return Member(**members[0]) if members else None

    async def get_booking_subscribe(self, booking: Booking):
        subscribe = await self._api_get_subscribes(pk=booking.get_subscribe_pk())
        return Subscribe(**subscribe[0]) if subscribe else None

    async def add_booking(self, new_booking: Booking, member_id, ticket_id,) -> Booking:
        result: dict = await self._api_add_booking(
            date_time=new_booking.get_date_time().strftime(self._date_time_format_db),
            is_paid=new_booking.is_paid(),
            user_confirm_paid=new_booking.is_user_confirm_paid(),
            member_id=member_id,
            ticket_id=ticket_id,
        )
        if result:
            return Booking(**result)
        else:
            raise

    async def delete_booking(self, booking: Booking) -> bool:
        return await self._api_delete_booking(pk=booking.get_pk())

    async def update_booking(self, booking: Booking) -> Booking:
        result: dict = await self._api_patch_booking(
            pk=booking.get_pk(),
            date_time=booking.get_date_time().strftime(self._date_time_format_db),
            is_paid=booking.is_paid(),
            user_confirm_paid=booking.is_user_confirm_paid(),
        )
        if result:
            return Booking(**result)
        else:
            raise
