from datetime import datetime, timedelta


from api.base.ApiBase import ApiBase, T_HOST
from api.meetings.Meeting import Meeting
from api.settings import datetime_format_str_api


class ApiMeetings(ApiBase):
    def __init__(self, base_url: T_HOST):
        super().__init__(base_url)

    async def get_meetings(self) -> list[Meeting]:
        meetings: list[dict] = await self._api_get_meetings()
        return [Meeting(**meeting) for meeting in meetings]

    async def get_meeting_by_pk(self, pk: int) -> Meeting | None:
        meeting: list[dict] = await self._api_get_meetings(id=pk)
        return Meeting(**meeting[0]) if meeting else None

    async def get_future_meetings(self) -> list[Meeting]:
        date_time_str: str = (datetime.now() + timedelta(hours=1)).strftime(datetime_format_str_api)
        meetings: list[dict] = await self._api_get_meetings(date_time_gte=date_time_str, can_be_booked=True)
        return [Meeting(**meeting) for meeting in meetings]
