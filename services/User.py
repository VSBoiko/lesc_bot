from dataclasses import dataclass


@dataclass(slots=True)
class User:
    id: int | None
    tg_id: int
    login: str
    name: str
    surname: str
