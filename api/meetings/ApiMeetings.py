from datetime import datetime, timedelta


from api.base.ApiBase import ApiBase, T_HOST
from api.meetings.Meeting import Meeting
from api.settings import datetime_format_str_api


class ApiMeetings(ApiBase):
    def __init__(self, base_url: T_HOST):
        super().__init__(base_url)

    def get_meetings(self) -> list[Meeting]:
        return [Meeting(**meeting) for meeting in self._api_get_meetings()]

    def get_meeting_by_pk(self, pk: int) -> Meeting | None:
        result: list[Meeting] = [Meeting(**member) for member in self._api_get_meetings(id=pk)]
        return result[0] if result else None

    def get_future_meetings(self) -> list[Meeting]:
        date_time_str = (datetime.now() + timedelta(hours=1)).strftime(datetime_format_str_api)
        return [Meeting(**meeting) for meeting in self._api_get_meetings(date_time_gte=date_time_str)]
