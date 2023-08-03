from db.DbQuery import DbQuery
from services.Place import Place


class PlaceService:
    def __init__(self, db_queries: DbQuery):
        self.queries = db_queries

    @staticmethod
    def create(name: str, address: str, link: str, description: str = "") -> Place:
        return Place(
            id=None,
            name=name,
            address=address,
            link=link,
            description=description,
        )

    def add_to_db(self, place: Place) -> int | None:
        return self.queries.add_place(
            data=[
                place.name,
                place.address,
                place.link,
                place.description,
            ]
        )

    def get_by_id(self, place_id: int) -> Place | None:
        result = self.queries.get_place_by_id(place_id)
        if not result:
            return None

        return Place(
            id=result.get("id"),
            name=result.get("name"),
            address=result.get("address"),
            link=result.get("link"),
            description=result.get("description"),
        )
