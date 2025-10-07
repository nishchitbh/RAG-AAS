from typing import List

from api.shared.domain.repositories.data_repo import IDataRepo
from api.shared.infrastructure.data_repo_impl import MongoRepo
from api.end_users.domain.entities import (
    EndUserBase,
    EndUserChat,
    EndUserUpdate,
    LatestChat,
    EndUserList,
    Pagination,
)


class EndUserRepo:
    def __init__(self):
        self.repo: IDataRepo = MongoRepo(collection="end_users")

    def create_user(self, end_user: EndUserChat) -> EndUserBase:
        created_user = self.repo.create(data=end_user.model_dump())
        return EndUserBase(**created_user)

    def get_all(
        self, company_id: str, page: int = 1, limit: int = 10
    ) -> List[EndUserBase]:
        data = self.repo.read_all(
            metadata={"company_id": company_id}, page=page, limit=limit
        )
        if not data:
            return EndUserList(
                end_users=[], pagination=Pagination(page=page, items=limit)
            )
        return EndUserList(
            end_users=[EndUserBase(**user) for user in data],
            pagination=Pagination(page=page, items=limit),
        )

    def get_user_by_id(self, generated_id: str) -> EndUserChat:
        data = self.repo.read(identifier={"generated_id": generated_id})
        return EndUserChat(**data) if data else None

    def push_to_history(
        self, generated_id: str, user_update: LatestChat
    ) -> EndUserChat:
        data = self.repo.push_to_list(
            identifier={"generated_id": generated_id},
            to_push_list_name="chat_history",
            update_data=user_update.model_dump(),
        )
        return EndUserChat(**data)

    def update_user(self, generated_id: str, user_update: EndUserUpdate):
        data = self.repo.update(
            identifier={"generated_id": generated_id},
            update_data=user_update.model_dump(),
        )
        return EndUserChat(**data)

    def delete_user(self, generated_id: str):
        return self.repo.delete(identifier={"generated_id": generated_id})
