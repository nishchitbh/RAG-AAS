from abc import ABC, abstractmethod
from fastapi.responses import StreamingResponse
from api.auth.domain.repositories import IUserRepository
from api.auth.domain.services import AuthService, UserService
from api.auth.domain.entities import (
    UserCreate,
    UserOut,
    AddPassword,
    UserUpdate,
    UserLogin,
)


class IAuthUseCases(ABC):
    def __init__(
        self,
        user_repo: IUserRepository,
        auth_service: AuthService,
        user_service: UserService,
    ):
        self.user_repo = user_repo
        self.auth_service = auth_service
        self.user_service = user_service

    @abstractmethod
    def signup_user(user: UserCreate, current_user: UserOut) -> StreamingResponse: ...

    @abstractmethod
    def login_user(user_login: UserLogin) -> dict: ...

    @abstractmethod
    def change_password(
        current_user: UserOut, add_password: AddPassword
    ) -> UserOut: ...

    @abstractmethod
    def update_user(
        user_update: UserUpdate, email: str, current_user: UserOut
    ) -> UserOut: ...

    @abstractmethod
    def get_all_users(page, limit) -> list[UserOut]: ...

    @abstractmethod
    def get_user(email: str) -> UserOut: ...

    @abstractmethod
    def delete_user(email: str, current_user: UserOut) -> str: ...

    @abstractmethod
    def reset_password(email: str, current_user: UserOut) -> StreamingResponse: ...

    @abstractmethod
    def soft_delete_user(email: str, current_user: UserOut) -> UserOut: ...

    @abstractmethod
    def reactivate_user(email: str, current_user: UserOut) -> UserOut: ...
