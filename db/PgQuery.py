from db.base.Db import Db
from db.base.DbQuery import DbQuery


class PgQuery(DbQuery):
    def __init__(self, db: Db):
        super().__init__(db)

    def add_booking(self, data: list):
        query = """
            INSERT INTO bookings (ticket_id, user_id, date_time, is_paid)
            VALUES (%s, %s, current_timestamp, %s) RETURNING id;
        """
        result = self.db.insert(
            query,
            [data]
        )
        return result[0] if result else None

    def add_place(self, data: list):
        query = """
            INSERT INTO places (name_, address, link, description)
            VALUES (%s, %s, %s, %s) RETURNING id;
        """
        result = self.db.insert(
            query,
            [data]
        )
        return result[0] if result else None

    def add_user(self, data: list):
        query = """
            INSERT INTO tg_users (tg_id, login, name_, surname)
            VALUES (%s, %s, %s, %s) RETURNING id;
        """
        result = self.db.insert(
            query,
            [data]
        )
        return result[0] if result else None

    def get_users(self) -> list[dict]:
        return self.db.query("""
            SELECT u.id as id,
                   u.tg_id as tg_id,
                   u.login as login,
                   u.name_ as name,
                   u.surname as surname
            FROM tg_users u;
        """)

    def get_user_by_tg_id(self, tg_id: int) -> dict:
        return self.db.query_fetchone("""
            SELECT u.id as id,
                   u.tg_id as tg_id,
                   u.login as login,
                   u.name_ as name,
                   u.surname as surname
            FROM tg_users u
            WHERE u.tg_id = {0};
        """.format(tg_id))

    def get_user_by_id(self, user_id: int) -> dict:
        return self.db.query_fetchone("""
            SELECT u.id as id,
                   u.tg_id as tg_id,
                   u.login as login,
                   u.name_ as name,
                   u.surname as surname
            FROM tg_users u
            WHERE u.id = {0};
        """.format(user_id))

    def get_booking_by_id(self, booking_id: int) -> dict:
        return self.db.query_fetchone("""
            SELECT b.id as id,
                   b.ticket_id as ticket_id,
                   b.user_id as user_id,
                   b.date_time as date_time,
                   b.is_paid as is_paid
            FROM bookings b
            WHERE b.id = {0};
        """.format(booking_id))

    def get_place_by_id(self, place_id: int) -> dict:
        return self.db.query_fetchone("""
            SELECT p.id as id,
                   p.name_ as name,
                   p.address as address,
                   p.link as link,
                   p.description as description
            FROM places p
            WHERE p.id = {0};
        """.format(place_id))

    def get_meetings(self) -> list[dict]:
        return self.db.query("""
            SELECT m.id as id,
                   m.place_id as place_id,
                   m.date_time as date_time,
                   m.name_ as name
            FROM meetings m;
        """)

    def get_meeting_by_id(self, meeting_id: int) -> dict:
        return self.db.query_fetchone("""
            SELECT m.id as id,
                   m.place_id as place_id,
                   m.date_time as date_time,
                   m.name_ as name
            FROM meetings m
            WHERE m.id = {0};
        """.format(meeting_id))

    def get_ticket_by_id(self, ticket_id: int) -> dict:
        return self.db.query_fetchone("""
            SELECT t.id as id,
                   t.meeting_id as meeting_id,
                   t.price as price 
            FROM tickets t
            WHERE t.id = {0};
        """.format(ticket_id))

    def get_tickets_by_meeting_id(self, meeting_id: int) -> list[dict]:
        return self.db.query("""
            SELECT t.id as id
            FROM tickets t
            WHERE t.meeting_id = {0};
        """.format(meeting_id))

    def get_tickets_by_meeting_id_free(self, meeting_id: int) -> list[dict]:
        return self.db.query("""
            SELECT t.id as id
            FROM tickets t
            WHERE t.meeting_id = {0} AND
                  t.id not in (SELECT id FROM bookings);
        """.format(meeting_id))

    def get_meeting_bookings_by_user(self, meeting_id: int, user_id: int) -> list[dict]:
        return self.db.query("""
            SELECT b.id as id
            FROM bookings b
            JOIN tickets t ON t.id = b.ticket_id
            WHERE t.meeting_id = {0} and b.user_id = {1};
        """.format(meeting_id, user_id))

    def get_bookings_by_meeting_id(self, meeting_id: int) -> list[dict]:
        return self.db.query("""
            SELECT b.id as id
            FROM bookings b
            JOIN tickets t ON t.id = b.ticket_id
            WHERE t.meeting_id = {0}
        """.format(meeting_id))

    def update_booking(self, booking_id: int, user_id: int, is_paid: bool):
        query = """
            UPDATE bookings SET 
                date_time = current_timestamp,
                user_id = %s,
                is_paid = %s
            WHERE id = {0};
        """.format(booking_id)
        self.db.update(
            query=query,
            data=[[user_id, is_paid]])
