import json

import aiohttp

from api.settings import datetime_format_str, datetime_format_str_api


T_HOST = str
HEADERS: dict = {
    "Content-Type": "application/json"
}


async def api_get(url: str, data: dict | None = None) -> list[dict]:
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(url=url, params=data) as response:
            if str(response.status).startswith("20"):
                text = await response.text()
                return json.loads(text)
            else:
                return []


async def api_post(url: str, data: dict) -> dict:
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.post(url=url, data=json.dumps(data)) as response:
            if str(response.status).startswith("20"):
                text = await response.text()
                return json.loads(text)
            else:
                return {}
            
            
async def api_delete(url: str, data: dict) -> bool:
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.delete(url=url, data=json.dumps(data)) as response:
            return response.status == 204


async def api_patch(url: str, data: dict) -> dict:
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.patch(url=url, data=json.dumps(data)) as response:
            if str(response.status).startswith("20"):
                text = await response.text()
                return json.loads(text)
            else:
                return {}


class ApiBase:
    def __init__(self, base_url: T_HOST):
        self.base: T_HOST = base_url
        self._date_time_format: str = datetime_format_str
        self._date_time_format_db: str = datetime_format_str_api

    async def _api_add_member(self, **kwargs) -> dict:
        return await api_post(url=f"{self.base}/api/members/", data=kwargs)

    async def _api_add_booking(self, **kwargs) -> dict:
        return await api_post(url=f"{self.base}/api/bookings/", data=kwargs)

    async def _api_delete_booking(self, **kwargs):
        return await api_delete(url=f"{self.base}/api/bookings/", data=kwargs)

    async def _api_patch_booking(self, **kwargs):
        return await api_patch(url=f"{self.base}/api/bookings/", data=kwargs)

    async def _api_get_places(self, **kwargs) -> list[dict]:
        params: str = self._get_str_from_kwargs(kwargs)
        return await api_get(url=f"{self.base}/api/places?{params}")

    async def _api_get_members(self, **kwargs) -> list[dict]:
        params: str = self._get_str_from_kwargs(kwargs)
        return await api_get(url=f"{self.base}/api/members?{params}")

    async def _api_get_tickets(self, **kwargs) -> list[dict]:
        params: str = self._get_str_from_kwargs(kwargs)
        return await api_get(url=f"{self.base}/api/tickets?{params}")

    async def _api_get_meetings(self, **kwargs) -> list[dict]:
        params: str = self._get_str_from_kwargs(kwargs)
        return await api_get(url=f"{self.base}/api/meetings?{params}")

    async def _api_get_bookings(self, **kwargs) -> list[dict]:
        params: str = self._get_str_from_kwargs(kwargs)
        return await api_get(url=f"{self.base}/api/bookings?{params}")

    def _get_str_from_kwargs(self, kwargs: dict) -> str:
        params = []
        for key, val in kwargs.items():
            params.append(f"{key}={val}")
        return "&".join(params)
