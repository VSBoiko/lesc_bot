import json


import requests

from api.settings import datetime_format_str, datetime_format_str_api


T_HOST = str
HEADERS: dict = {
    "Content-Type": "application/json"
}


def api_get(url: str, data: dict | None = None) -> list[dict]:
    if data is None:
        data: dict = {}

    result: requests.Response = requests.get(url=url, params=data, verify=False)
    if str(result.status_code).startswith("20"):
        return json.loads(result.text)
    else:
        return []


def api_post(url: str, data: dict) -> dict:
    result: requests.Response = requests.post(url=url, data=json.dumps(data), headers=HEADERS, verify=False)
    return json.loads(result.text)


class ApiBase:
    def __init__(self, base_url: T_HOST):
        self.base: T_HOST = base_url
        self._date_time_format: str = datetime_format_str
        self._date_time_format_db: str = datetime_format_str_api

    def _api_add_member(self, **kwargs) -> dict:
        return api_post(url=f"{self.base}/api/members/", data=kwargs)

    def _api_add_booking(self, **kwargs) -> dict:
        return api_post(url=f"{self.base}/api/bookings/", data=kwargs)

    def _api_get_places(self, **kwargs) -> list[dict]:
        params: str = self._get_str_from_kwargs(kwargs)
        return api_get(url=f"{self.base}/api/places?{params}")

    def _api_get_members(self, **kwargs) -> list[dict]:
        params: str = self._get_str_from_kwargs(kwargs)
        return api_get(url=f"{self.base}/api/members?{params}")

    def _api_get_tickets(self, **kwargs) -> list[dict]:
        params: str = self._get_str_from_kwargs(kwargs)
        return api_get(url=f"{self.base}/api/tickets?{params}")

    def _api_get_meetings(self, **kwargs) -> list[dict]:
        params: str = self._get_str_from_kwargs(kwargs)
        return api_get(url=f"{self.base}/api/meetings?{params}")

    def _api_get_bookings(self, **kwargs) -> list[dict]:
        params: str = self._get_str_from_kwargs(kwargs)
        return api_get(url=f"{self.base}/api/bookings?{params}")

    def _get_str_from_kwargs(self, kwargs: dict) -> str:
        params: str = ""
        for key, val in kwargs.items():
            params += f"{key}={val}"
        return params
