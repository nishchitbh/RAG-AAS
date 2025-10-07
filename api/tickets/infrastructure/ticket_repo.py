from typing import List
from bson import ObjectId

from api.shared.domain.repositories.data_repo import IDataRepo
from api.shared.infrastructure.data_repo_impl import MongoRepo

from api.shared.domain.entities import Pagination
from api.tickets.domain.entities import Ticket, TicketList, ResolveTicket, TicketOut


class TicketRepo:
    def __init__(self):
        self.repo: IDataRepo = MongoRepo(collection="tickets")

    def create_ticket(self, ticket: Ticket) -> TicketOut:
        created_ticket = self.repo.create(data=ticket.model_dump())
        return TicketOut(**created_ticket)

    def get_all(self, company_id: str, page: int = 1, limit: int = 10) -> List[Ticket]:
        data = self.repo.read_all(
            metadata={"company_id": company_id}, page=page, limit=limit
        )
        if not data:
            return TicketList(tickets=[], pagination=Pagination(page=page, items=limit))
        return TicketList(
            tickets=[Ticket(**ticket) for ticket in data],
            pagination=Pagination(page=page, items=limit),
        )

    def get_ticket_by_id(self, ticket_id: str) -> Ticket:
        data = self.repo.read(identifier={"_id": ObjectId(ticket_id)})
        if not data:
            return None
        return Ticket(**data)

    def resolve_ticket(
        self,
        ticket_id: str,
    ):
        resolve = ResolveTicket(resolved=True)
        data = self.repo.update(
            identifier={"_id": ObjectId(ticket_id)},
            update_data=resolve.model_dump(),
        )
        return Ticket(**data)
