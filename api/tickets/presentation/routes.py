from fastapi import Depends, status

from api.tickets.domain.entities import Ticket, TicketList

from api.auth.presentation.config import get_current_user, UserOut
from api.tickets.presentation.config import (
    tickets_route,
    get_ticket_use_cases,
    TicketUseCases,
)


class TicketRoutes:
    def __init__(self):
        self.router = tickets_route
        self.router.add_api_route(
            path="/all",
            endpoint=self.get_all_tickets,
            methods=["GET"],
            status_code=status.HTTP_200_OK,
            response_model=TicketList,
        )
        self.router.add_api_route(
            path="/{id}",
            endpoint=self.get_ticket,
            methods=["GET"],
            status_code=status.HTTP_200_OK,
            response_model=Ticket,
        )
        self.router.add_api_route(
            path="resolve/{id}",
            endpoint=self.resolve_ticket,
            methods=["PATCH"],
            status_code=status.HTTP_200_OK,
            response_model=Ticket,
        )

    def get_ticket(
        self,
        id: str,
        use_cases: TicketUseCases = Depends(get_ticket_use_cases),
        current_user: UserOut = get_current_user("company_admin"),
    ):
        return use_cases.get_ticket(ticket_id=id, current_user=current_user)

    def get_all_tickets(
        self,
        page: int = 1,
        items: int = 10,
        use_cases: TicketUseCases = Depends(get_ticket_use_cases),
        current_user: UserOut = get_current_user("company_admin"),
    ):
        return use_cases.get_all_tickets(
            current_user=current_user, page=page, limit=items
        )

    def resolve_ticket(
        self,
        id: str,
        use_cases: TicketUseCases = Depends(get_ticket_use_cases),
        current_user: UserOut = get_current_user("company_admin"),
    ):
        return use_cases.resolve_ticket(ticket_id=id, current_user=current_user)
