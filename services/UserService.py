from db.DbQuery import DbQuery
from services.User import User

new_user_id = int


class UserService:
    def __init__(self, queries: DbQuery):
        self.queries = queries

    @staticmethod
    def create(tg_id: int, login: str, name: str, surname: str) -> User:
        return User(
            id=None,
            tg_id=tg_id,
            login=login,
            name=name,
            surname=surname,
        )

    def add_to_db(self, user: User) -> new_user_id | None:
        return self.queries.add_user(
            data=[
                user.tg_id,
                user.login,
                user.name,
                user.surname,
            ]
        )

    def get_by_tg_id(self, tg_id: int) -> User | None:
        result = self.queries.get_user_by_tg_id(tg_id)
        if not result:
            return None

        user = UserService.create(
            tg_id=result.get("tg_id"),
            login=result.get("login"),
            name=result.get("name"),
            surname=result.get("surname"),
        )
        user.id = result.get("id")
        return user

    def get_by_id(self, user_id: int) -> User | None:
        result = self.queries.get_user_by_id(user_id)
        if not result:
            return None

        user = UserService.create(
            tg_id=result.get("tg_id"),
            login=result.get("login"),
            name=result.get("name"),
            surname=result.get("surname"),
        )
        user.id = result.get("id")
        return user

    def is_exists_in_db(self, tg_id: int) -> bool:
        return bool(self.queries.get_user_by_tg_id(tg_id))
