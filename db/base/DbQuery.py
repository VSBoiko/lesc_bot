from abc import ABC, abstractmethod

from db.base.Db import Db


class DbQuery(ABC):
    def __init__(self, db: Db):
        self.db = db

    @abstractmethod
    def add_booking(self, data: list):
        pass

    @abstractmethod
    def add_place(self, data: list):
        pass

    @abstractmethod
    def add_user(self, data: list):
        pass

    @abstractmethod
    def get_users(self) -> list[dict]:
        pass

    @abstractmethod
    def get_user_by_tg_id(self, tg_id: int) -> dict:
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> dict:
        pass

    @abstractmethod
    def get_booking_by_id(self, booking_id: int) -> dict:
        pass

    @abstractmethod
    def get_place_by_id(self, place_id: int) -> dict:
        pass

    @abstractmethod
    def get_meetings(self) -> list[dict]:
        pass

    @abstractmethod
    def get_meeting_by_id(self, meeting_id: int) -> dict:
        pass

    @abstractmethod
    def get_ticket_by_id(self, ticket_id: int) -> dict:
        pass

    @abstractmethod
    def get_tickets_by_meeting_id(self, meeting_id: int) -> list[dict]:
        pass

    @abstractmethod
    def get_tickets_by_meeting_id_free(self, meeting_id: int) -> list[dict]:
        pass

    @abstractmethod
    def get_meeting_bookings_by_user(self, meeting_id: int, user_id: int) -> list[dict]:
        pass

    @abstractmethod
    def get_bookings_by_meeting_id(self, meeting_id: int) -> list[dict]:
        pass

    @abstractmethod
    def update_booking(self, booking_id: int, user_id: int, is_paid: bool):
        pass
