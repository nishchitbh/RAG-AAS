from api.auth.domain.entities import UserOut
from api.tickets.domain.entities import Ticket, TicketList
from api.shared.domain.exceptions import NotFoundException
from api.tickets.infrastructure.ticket_repo import TicketRepo


class TicketUseCases:
    def __init__(self, repo: TicketRepo):
        self.repo = repo

    def get_all_tickets(
        self, current_user: UserOut, page: int = 1, limit: int = 10
    ) -> TicketList:
        return self.repo.get_all(
            company_id=current_user.company_id, page=page, limit=limit
        )

    def get_ticket(
        self,
        ticket_id: str,
        current_user: UserOut,
    ) -> Ticket:
        ticket = self.repo.get_ticket_by_id(ticket_id=ticket_id)
        if not ticket or ticket.company_id != current_user.company_id:
            raise NotFoundException("Ticket not found")
        return ticket

    def resolve_ticket(self, ticket_id: str, current_user: UserOut) -> Ticket:
        ticket = self.repo.get_ticket_by_id(ticket_id=ticket_id)
        if not ticket or ticket.company_id != current_user.company_id:
            raise NotFoundException("Ticket not found")
        return self.repo.resolve_ticket(ticket_id=ticket_id)
