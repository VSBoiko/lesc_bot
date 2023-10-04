from Subscribe import Subscribe
from api.base.ApiBase import ApiBase, T_HOST
from api.settings import datetime_format_str_api


class ApiSubscribes(ApiBase):
    def __init__(self, base_url: T_HOST):
        super().__init__(base_url)

    async def get_subscribes(self) -> list[Subscribe]:
        subscribes = await self._api_get_subscribes()
        return [Subscribe(**json_subscribe) for json_subscribe in subscribes]

    async def get_subscribe_by_pk(self, pk: int) -> Subscribe | None:
        subscribe = await self._api_get_subscribes(id=pk)
        return Subscribe(**subscribe[0]) if subscribe else None

    async def add_subscribe(self, new_subscribe: Subscribe, member_id: int) -> Subscribe:
        result: dict = await self._api_add_subscribe(
            date_time=new_subscribe.get_date_time().strftime(datetime_format_str_api),
            is_paid=new_subscribe.is_paid(),
            is_first=new_subscribe.is_first(),
            is_active=new_subscribe.is_active(),
            user_confirm_paid=new_subscribe.is_user_confirm_paid(),
            cnt_meetings=new_subscribe.get_cnt_meetings(),
            price=new_subscribe.get_price(),
            member_id=member_id,
        )
        if result:
            return Subscribe(**result)
        else:
            raise

    async def update_subscribe(self, subscribe: Subscribe) -> Subscribe:
        result: dict = await self._api_patch_subscribe(
            pk=subscribe.get_pk(),
            date_time=subscribe.get_date_time().strftime(datetime_format_str_api),
            is_paid=subscribe.is_paid(),
            is_first=subscribe.is_first(),
            is_active=subscribe.is_active(),
            user_confirm_paid=subscribe.is_user_confirm_paid(),
        )
        if result:
            return Subscribe(**result)
        else:
            raise
