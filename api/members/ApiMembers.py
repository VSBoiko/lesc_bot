

from api.base.ApiBase import ApiBase, T_HOST
from .Member import Member


class ApiMember(ApiBase):
    def __init__(self, base_url: T_HOST):
        super().__init__(base_url)

    def get_members(self) -> list[Member]:
        return [Member(**member) for member in self._api_get_members()]

    def get_member_by_pk(self, pk: int) -> Member | None:
        result: list[Member] = [Member(**member) for member in self._api_get_members(id=pk)]
        return result[0] if result else None

    def get_member_by_tg_id(self, tg_id: int) -> Member | None:
        result: list[Member] = [Member(**member) for member in self._api_get_members(tg_id=tg_id)]
        return result[0] if result else None

    def add_member(self, new_member: Member) -> Member:
        result: dict = self._api_add_member(
            tg_id=new_member.get_tg_id(),
            login=new_member.get_login(),
            name=new_member.get_name(),
            surname=new_member.get_surname(),
        )
        if result:
            return Member(**result)
        else:
            raise
