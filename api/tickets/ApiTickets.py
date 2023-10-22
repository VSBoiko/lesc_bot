from .Ticket import Ticket
from api.base.ApiBase import ApiBase, T_HOST
from ..bookings.Booking import Booking
from ..members.Member import Member


class ApiTickets(ApiBase):
    def __init__(self, base_url: T_HOST):
        super().__init__(base_url)

    async def get_tickets(self) -> list[Ticket]:
        tickets = await self._api_get_tickets()
        return [Ticket(**ticket) for ticket in tickets]

    async def get_ticket_booking(self, ticket: Ticket) -> Booking | None:
        bookings = await self._api_get_bookings(ticket_id=ticket.get_pk())
        return Booking(**bookings[0]) if bookings else None
