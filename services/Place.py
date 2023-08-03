from dataclasses import dataclass


@dataclass(slots=True)
class Place:
    id: int | None
    name: str
    address: str
    link: str
    description: str
