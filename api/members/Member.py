

from api.base.Base import Base


class Member(Base):
    def __init__(
        self, tg_id: int, login: str, name: str, surname: str, pk: int | None = None, **kwargs
    ):
        if not pk:
            pk = kwargs.get("id")

        super().__init__(pk=pk)

        self._tg_id: int = tg_id
        self._login: str = login
        self._name: str = name
        self._surname: str = surname
        self._pk: int | None = pk

        self._bookings: list[dict] = kwargs.get("bookings") if "bookings" in kwargs else []

    def get_tg_id(self) -> int:
        return self._tg_id

    def get_login(self) -> str:
        return self._login

    def get_name(self) -> str:
        return self._name

    def get_surname(self) -> str:
        return self._surname

    def get_pk(self) -> int:
        return self._pk

    def get_link(self):
        return f"https://t.me/{self.get_login()[1:]}"

    def get_full_name(self):
        full_name_parts = [
            self.get_name(),
            self.get_surname(),
        ]
        return " ".join([x for x in full_name_parts if x])
