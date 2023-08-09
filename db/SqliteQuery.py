from db.base.DbQuery import DbQuery


# todo доработать
class SqliteQuery(DbQuery):
    def __init__(self, db):
        super().__init__(db)

    def add_booking(self, data: list):
        query = """
            INSERT INTO booking (meeting_id, user_id, booking_date_time, paid)
            VALUES (?, ?, ?, ?);
        """
        self.insert(
            query,
            [data]
        )
        return self.get_last_insert()

    def add_place(self, data: list):
        query = """
            INSERT INTO places (name_, address, link, description)
            VALUES (?, ?, ?, ?);
        """
        self.insert(
            query,
            [data]
        )
        return self.get_last_insert()

    def add_user(self, data: list):
        query = """
            INSERT INTO users (tg_id, login, name_, surname)
            VALUES (?, ?, ?, ?);
        """
        self.insert(
            query,
            [data]
        )
        return self.get_last_insert()

    def get_last_insert(self) -> int | None:
        result = self.query_fetchone("SELECT last_insert_rowid();")
        return result.get("last_insert_rowid()") if "last_insert_rowid()" in result else None

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

    def get_user_by_id(self, user_id: int) -> dict:
        return self.query_fetchone("""
            SELECT u.id as id,
                   u.tg_id as tg_id,
                   u.login as login,
                   u.name_ as name,
                   u.surname as surname
            FROM users u
            WHERE u.id = {0};
        """.format(user_id))

    def get_booking_by_id(self, booking_id: int) -> dict:
        return self.query_fetchone("""
            SELECT b.id as id,
                   b.meeting_id as meeting_id,
                   b.user_id as user_id,
                   b.booking_date_time as booking_date_time,
                   b.paid as paid
            FROM booking b
            WHERE b.id = {0};
        """.format(booking_id))

    def get_place_by_id(self, place_id: int) -> dict:
        return self.query_fetchone("""
            SELECT p.id as id,
                   p.name_ as name,
                   p.address as address,
                   p.link as link,
                   p.description as description
            FROM places p
            WHERE p.id = {0};
        """.format(place_id))

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
                   p.id as place_id
            FROM meetings m
            JOIN places p ON p.id = m.place_id
            WHERE m.id = {0};
        """.format(meeting_id))

    def get_free_tickets_by_meet_id(self, meeting_id: int) -> dict:
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

    def get_bookings_by_meeting_id(self, meeting_id: int) -> list[dict]:
        return self.query("""
            SELECT b.id as id,
                   b.meeting_id as meeting_id,
                   b.user_id as user_id,
                   b.booking_date_time as booking_date_time,
                   b.paid as paid
            FROM booking b
            WHERE b.meeting_id = {0}
        """.format(meeting_id))

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
