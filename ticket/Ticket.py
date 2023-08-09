from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Ticket:
    id: int | None
    price: float
