from Place import Place
from api.base.ApiBase import ApiBase, T_HOST


class ApiPlaces(ApiBase):
    def __init__(self, base_url: T_HOST):
        super().__init__(base_url)

    async def get_places(self) -> list[Place]:
        places = await self._api_get_places()
        return [Place(**json_place) for json_place in places]

