from api.auth.domain.repositories import IUserRepository
from api.shared.domain.repositories.data_repo import IDataRepo
from api.shared.infrastructure.data_repo_impl import MongoRepo
from api.auth.domain.entities import FullUpdate, UserOut, UserStore


class UserRepository(IUserRepository):
    def __init__(self):
        self.repo: IDataRepo = MongoRepo(collection="users")

    def create_user(self, user: UserStore) -> UserStore:
        created_user = self.repo.create(user.model_dump())
        return UserStore(**created_user)

    def get_user_by_email(self, email: str) -> UserStore:
        user = self.repo.read({"email": email})
        if not user:
            return None
        return UserStore(**user)

    def update_user(self, email: str, user_update: FullUpdate) -> UserStore:
        data = self.repo.update({"email": email}, user_update.model_dump())
        return UserStore(**data)

    def delete_user(self, email: str) -> dict:
        return self.repo.delete({"email": email})

    def get_all(self, page: int = 1, limit: int = 10) -> list:
        data = self.repo.read_all(page=page, limit=limit)
        return [UserOut(**user) for user in data]
