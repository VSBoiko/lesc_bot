import datetime

from db.Db import Db


class DbQuery(Db):
    def add_user(self, data: list):
        query = """
            INSERT INTO users (tg_id, login, name_, surname)
            VALUES (?, ?, ?, ?)
        """
        self.insert(
            query,
            [data]
        )

    def get_users(self) -> list[dict]:
        return self.query("""
            SELECT u.id as id,
                   u.tg_id as tg_id,
                   u.login as login,
                   u.name_ as name,
                   u.surname as surname
            FROM users u;
        """)

    def get_user_by_tg_id(self, tg_id: int) -> dict:
        return self.query_fetchone("""
            SELECT u.id as id,
                   u.tg_id as tg_id,
                   u.login as login,
                   u.name_ as name,
                   u.surname as surname
            FROM users u
            WHERE u.tg_id = {0};
        """.format(tg_id))

    def get_meetings(self) -> list[dict]:
        return self.query("""
            SELECT m.id as id,
                   m.date_time as date_time,
                   m.name_ as name,
                   p.name_ as place_name,
                   p.address as place_address,
                   p.link as place_link,
                   (SELECT COUNT(1) FROM booking b where b.meeting_id = m.id AND user_id IS NULL) as cnt_tickets
            FROM meetings m
            JOIN places p ON p.id = m.place_id;
        """)

    def get_meeting_by_id(self, meeting_id: int) -> dict:
        return self.query_fetchone("""
            SELECT m.id as id,
                   m.date_time as date_time,
                   m.name_ as name,
                   p.name_ as place_name,
                   p.address as place_address,
                   p.link as place_link,
                   (SELECT COUNT(1) FROM booking b where b.meeting_id = m.id AND user_id IS NULL) as cnt_tickets
            FROM meetings m
            JOIN places p ON p.id = m.place_id
            WHERE m.id = {0};
        """.format(meeting_id))

    def get_free_booking_one(self, meeting_id: int) -> dict:
        return self.query_fetchone("""
            SELECT b.id as id
            FROM booking b
            WHERE b.meeting_id = {0} and b.user_id is NULL;
        """.format(meeting_id))

    def get_booking_by_user(self, meeting_id: int, user_id: int) -> dict:
        return self.query_fetchone("""
            SELECT b.id as id
            FROM booking b
            WHERE b.meeting_id = {0} and b.user_id = {1};
        """.format(meeting_id, user_id))

    def upd_booking(self, booking_id: int, user_id: int):
        query = """
            UPDATE booking SET 
                user_id = ?,
                booking_date_time = datetime('now','localtime')
            WHERE id = {0};
        """.format(booking_id)
        self.update(
            query=query,
            data=[[user_id]])
