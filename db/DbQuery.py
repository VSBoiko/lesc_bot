import datetime

from db.Db import Db


class DbQuery(Db):
    def add_user(self, tg_id, login, name, surname):
        query = """
            INSERT INTO users (tg_id, login, name, surname)
            VALUES (?, ?, ?, ?)
        """
        self.insert(
            query,
            [(tg_id, login, name, surname)]
        )

    def get_users(self):
        return self.query("""
            SELECT u.tg_id as tg_id,
                   u.login as login,
                   u.name as name,
                   u.surname as surname,
                   u.enable_notifications as enable_notifications
            FROM users u;
        """)

    def get_user_by_tg_id(self, tg_id):
        return self.query_fetchone("""
            SELECT u.tg_id as tg_id,
                   u.login as login,
                   u.name as name,
                   u.surname as surname,
                   u.enable_notifications as enable_notifications
            FROM users u
            WHERE u.tg_id = {0};
        """.format(tg_id))
