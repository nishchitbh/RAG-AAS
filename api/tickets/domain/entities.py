from pydantic import BaseModel
from api.shared.domain.entities import Pagination
from typing import List


class Ticket(BaseModel):
    company_id: str
    user_id: str
    issue: str
    resolved: bool = False


class TicketList(BaseModel):
    tickets: List[Ticket]
    pagination: Pagination


class TicketOut(Ticket):
    id: str


class ResolveTicket(BaseModel):
    resolved: bool = True
