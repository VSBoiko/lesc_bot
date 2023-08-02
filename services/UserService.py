from db.DbQuery import DbQuery
from services.User import User
from settings import DB_PATH


class UserService:
    def __init__(self):
        self.queries = DbQuery(db_name=DB_PATH)

    @staticmethod
    def create_user(tg_id: int, login: str, name: str, surname: str) -> User:
        return User(
            id=None,
            tg_id=tg_id,
            login=login,
            name=name,
            surname=surname,
        )

    def add_user_to_db(self, user: User) -> bool:
        self.queries.add_user(
            data=[
                user.tg_id,
                user.login,
                user.name,
                user.surname,
            ]
        )
        return self.is_user_exists(user.tg_id)

    def get_user_by_tg_id(self, tg_id: int) -> User | None:
        result = self.queries.get_user_by_tg_id(tg_id)
        if not result:
            return None

        return UserService.create_user(
            tg_id=result.get("tg_id"),
            login=result.get("login"),
            name=result.get("name"),
            surname=result.get("surname"),
        )

    def is_user_exists(self, tg_id: int) -> bool:
        return bool(self.queries.get_user_by_tg_id(tg_id))
