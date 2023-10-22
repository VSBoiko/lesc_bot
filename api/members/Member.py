from api.base.Base import Base


class Member(Base):
    def __init__(
        self, tg_id: int, login: str, name: str, surname: str, pk: int | None = None, **kwargs
    ):
        super().__init__(pk=pk, **kwargs)

        self._bookings_pk = []
        self._subscribes_pk = []

        self._tg_id: int = tg_id
        self._login: str = login
        self._name: str = name
        self._surname: str = surname

        subscribes: list[dict] = kwargs.get("subscribes", [])
        if subscribes:
            self._set_subscribes_pk(subscribes)

        bookings: list[dict] = kwargs.get("bookings", [])
        if bookings:
            self._set_bookings_pk(bookings)

    def get_tg_id(self) -> int:
        return self._tg_id

    def get_login(self) -> str:
        return self._login

    def get_bookings_pk(self) -> list[int]:
        return self._bookings_pk

    def get_subscribes_pk(self) -> list[int]:
        return self._subscribes_pk

    def get_name(self) -> str:
        return self._name

    def get_surname(self) -> str:
        return self._surname

    def get_markdown_link(self) -> str:
        if self.get_login():
            return f"[{self.get_full_name()}]({self.get_link()})"
        else:
            return self.get_full_name()

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

    def _set_bookings_pk(self, value: list[dict]):
        self._bookings_pk = [b.get("id") for b in value]

    def _set_subscribes_pk(self, value: list[dict]):
        self._subscribes_pk = [s.get("pk") for s in value]
