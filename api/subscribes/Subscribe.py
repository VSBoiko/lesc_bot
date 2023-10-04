from datetime import datetime

from api.base.Base import Base
from api.members.Member import Member


class Subscribe(Base):
    def __init__(
            self, date_time: str, price: float, user_confirm_paid: bool, is_paid: bool, is_active: bool,
            is_first: bool, cnt_meetings: int, pk: int | None = None, **kwargs
    ):
        super().__init__(pk=pk)

        self._date_time: datetime | None = None
        self._member: Member | None = None

        self._price: float = price
        self._user_confirm_paid: bool = user_confirm_paid
        self._is_paid: bool = is_paid
        self._is_first: bool = is_first
        self._is_active: bool = is_active
        self._cnt_meetings: int = cnt_meetings
        self._pk: int | None = pk

        self._set_date_time(datetime.strptime(date_time, self._date_time_format_db))

        member: dict = kwargs.get("member") if "member" in kwargs else {}
        if member:
            self._set_member(member)

    def get_date_time(self) -> datetime | None:
        return self._date_time

    def get_price(self) -> float:
        return self._price

    def is_user_confirm_paid(self) -> bool:
        return self._user_confirm_paid

    def is_paid(self) -> bool:
        return self._is_paid

    def is_first(self) -> bool:
        return self._is_first

    def is_active(self) -> bool:
        return self._is_active

    def get_cnt_meetings(self) -> int:
        return self._cnt_meetings

    def get_pk(self) -> int | None:
        return self._pk

    def set_is_paid(self, value: bool):
        self._is_paid = value

    def set_is_active(self, value: bool):
        self._is_active = value

    def set_user_confirm_paid(self, value: bool):
        self._user_confirm_paid = value

    def _set_date_time(self, value: datetime):
        self._date_time: datetime = value

    def _set_member(self, value: dict):
        self._member: Member = Member(**value)
