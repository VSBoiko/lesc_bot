from datetime import datetime, timedelta


from api.base.ApiBase import ApiBase, T_HOST
from api.meetings.Meeting import Meeting
from api.places.Place import Place
from api.settings import datetime_format_str_api
from api.tickets.Ticket import Ticket


class ApiMeetings(ApiBase):
    def __init__(self, base_url: T_HOST):
        super().__init__(base_url)

    async def get_meetings(self) -> list[Meeting]:
        meetings: list[dict] = await self._api_get_meetings()
        return [Meeting(**meeting) for meeting in meetings]

    async def get_meeting_by_pk(self, pk: int) -> Meeting | None:
        meeting: list[dict] = await self._api_get_meetings(id=pk)
        return Meeting(**meeting[0]) if meeting else None

    async def get_place(self, meeting: Meeting) -> Place | None:
        place = await self._api_get_places(id=meeting.get_place_pk())
        return Place(**place[0]) if place else None

    async def get_tickets(self, meeting: Meeting) -> list[Ticket]:
        tickets = await self._api_get_tickets(id_in=meeting.get_tickets_pk())
        return [Ticket(**t) for t in tickets]

    async def get_free_tickets(self, meeting: Meeting) -> list[Ticket]:
        tickets: list[Ticket] = await self.get_tickets(meeting=meeting)
        return [t for t in tickets if not t.has_booking()]

    async def get_busy_tickets(self, meeting: Meeting) -> list[Ticket]:
        tickets: list[Ticket] = await self.get_tickets(meeting=meeting)
        return [t for t in tickets if t.has_booking()]

    async def get_future_meetings(self) -> list[Meeting]:
        date_time_str: str = (datetime.now() + timedelta(hours=1)).strftime(datetime_format_str_api)
        meetings: list[dict] = await self._api_get_meetings(date_time_gte=date_time_str)
        return [Meeting(**meeting) for meeting in meetings]

    async def get_ticket_by_member_id(self, meeting: Meeting, member_id: int) -> Ticket:
        ticket = await self._api_get_tickets(
            meeting_id=meeting.get_pk(),
            booking_member_id=member_id
        )
        return Ticket(**ticket[0]) if ticket else None
