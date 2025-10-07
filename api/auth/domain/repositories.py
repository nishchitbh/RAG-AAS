from abc import ABC, abstractmethod

from api.auth.domain.entities import UserCreate, UserOut, UserUpdate, UserStore


class IUserRepository(ABC):
    @abstractmethod
    def create_user(self, user: UserCreate) -> UserStore:
        """Create a new user in the repository."""
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> UserStore | None:
        """Retrieve a user by their email address."""
        pass

    @abstractmethod
    def update_user(self, email: str, user_update: UserUpdate) -> UserStore:
        """Update an existing user."""
        pass

    @abstractmethod
    def delete_user(self, email: str) -> None:
        """Delete a user from the repository."""
        pass

    @abstractmethod
    def get_all(self, page: int = 1, limit: int = 10) -> list[UserOut]:
        """Retrieve all users from the repository."""
        pass
