import uuid

from api.auth.presentation.config import UserOut
from api.shared.domain.exceptions import NotFoundException
from api.end_users.infrastructure.end_user_repo import EndUserRepo
from api.company.infrastructure.company_repo import CompanyRepo
from api.end_users.domain.entities import (
    EndUserBase,
    EndUserChat,
    EndUserUpdate,
    LatestChat,
    EndUserList,
)


class EndUserUseCases:
    def __init__(self, end_user_repo: EndUserRepo):
        self.end_user_repo = end_user_repo

    def create_user(self, company_id: str) -> EndUserBase:
        company = CompanyRepo().get_company_by_id(company_id)
        if not company:
            raise NotFoundException("Company not found")
        generated_id = str(uuid.uuid4())
        end_user = EndUserChat(generated_id=generated_id, company_id=company_id)
        return self.end_user_repo.create_user(end_user)

    def get_user_by_admin(
        self, generated_id: str, current_user: UserOut
    ) -> EndUserChat:
        user = self.end_user_repo.get_user_by_id(generated_id)
        if not user or current_user.company_id != user.company_id:
            raise NotFoundException("User not found")
        return user

    def push_to_history(self, generated_id: str, chat: LatestChat) -> EndUserChat:
        return self.end_user_repo.push_to_history(
            generated_id=generated_id, user_update=chat
        )

    def update_history_summary(
        self, generated_id: str, chat_summary: str
    ) -> EndUserChat:
        return self.end_user_repo.update_user(
            generated_id, EndUserUpdate(chat_summary=chat_summary)
        )

    def get_users(
        self, current_user: UserOut, skip: int = 0, limit: int = 10
    ) -> EndUserList:
        return self.end_user_repo.get_all(
            company_id=current_user.company_id, page=skip, limit=limit
        )
