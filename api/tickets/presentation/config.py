from fastapi import APIRouter

from api.tickets.infrastructure.ticket_repo import TicketRepo
from api.tickets.application.ticket_use_cases import TicketUseCases

tickets_route = APIRouter(
    prefix="/tickets",
    tags=["Tickets"],
)


def get_ticket_use_cases() -> TicketUseCases:
    return TicketUseCases(repo=TicketRepo())
