from datetime import datetime

from api.base.Base import Base


class Booking(Base):
    def __init__(
            self, date_time: str, is_paid: bool, user_confirm_paid: bool, pk: int | None = None, **kwargs
    ):
        super().__init__(pk=pk, **kwargs)

        self._date_time: datetime | None = None
        self._member_pk: int | None = None
        self._subscribe_pk: int | None = None

        self._is_paid: bool = is_paid
        self._user_confirm_paid: bool = user_confirm_paid

        self._set_date_time(datetime.strptime(date_time, self._date_time_format_db))
        member: dict = kwargs.get("member", {})
        if member:
            self._set_member_pk(member.get("id", None))

        subscribe: dict = kwargs.get("subscribe", {})
        if subscribe:
            self._set_subscribe_pk(subscribe.get("pk", None))

    def get_date_time(self) -> datetime:
        return self._date_time

    def get_member_pk(self) -> int | None:
        return self._member_pk

    def get_subscribe_pk(self) -> int | None:
        return self._subscribe_pk

    def is_paid(self) -> bool:
        return self._is_paid

    def is_user_confirm_paid(self) -> bool:
        return self._user_confirm_paid

    def set_is_paid(self, value: bool):
        self._is_paid: bool = value

    def set_user_confirm_paid(self, value: bool):
        self._user_confirm_paid: bool = value

    def _set_date_time(self, value: datetime):
        self._date_time: datetime = value

    def _set_member_pk(self, value: int | None):
        self._member_pk: int | None = value

    def _set_subscribe_pk(self, value: int | None):
        self._subscribe_pk: int | None = value
