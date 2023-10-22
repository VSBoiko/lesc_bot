

from api.base.Base import Base


class Place(Base):
    def __init__(
            self, name: str, address: str, link: str,
            description: str, pk: int | None = None, **kwargs
    ):
        super().__init__(pk=pk, **kwargs)

        self._name: str = name
        self._address: str = address
        self._link: str = link
        self._description: str = description

    def get_address(self) -> str:
        return self._address

    def get_description(self) -> str:
        return self._description

    def get_name(self) -> str:
        return self._name

    def get_link(self) -> str:
        return self._link
