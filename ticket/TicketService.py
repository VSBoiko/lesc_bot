from ticket.Ticket import Ticket


class TicketService:
    def __init__(self, queries):
        self.queries = queries

    def get_by_id(self, ticket_id: int) -> Ticket:
        result = self.queries.get_ticket_by_id(ticket_id=ticket_id)

        return Ticket(
            id=ticket_id,
            price=result.get("price"),
        )
