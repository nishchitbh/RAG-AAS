from abc import ABC, abstractmethod

from api.auth.domain.entities import UserOut
from api.company.domain.services import CompanyService
from api.auth.domain.repositories import IUserRepository
from api.company.infrastructure.abstract_company_repo import ICompanyRepo
from api.company.domain.entities import (
    CompanyCreate,
    CompanyOut,
    CompanyUpdateSuper,
)


class ICompanyUseCases(ABC):
    def __init__(
        self,
        company_repo: ICompanyRepo,
        company_service: CompanyService,
        user_repo: IUserRepository,
    ):
        self.company_repo = company_repo
        self.company_service = company_service
        self.user_repo = user_repo

    @abstractmethod
    def create_company(
        self, current_user: UserOut, company: CompanyCreate
    ) -> CompanyOut: ...
    @abstractmethod
    def get_all(self, page: int = 1, limit: int = 10) -> list[CompanyOut]: ...
    @abstractmethod
    def get_company_by_id(
        self, current_user: UserOut, company_id: str
    ) -> CompanyOut: ...
    @abstractmethod
    def update_company(
        self, current_user: UserOut, company_id: str, company_update: CompanyUpdateSuper
    ) -> CompanyOut: ...
    @abstractmethod
    def activate_company(self, company_id: str) -> CompanyOut: ...
    @abstractmethod
    def deactivate_company(self, company_id: str) -> CompanyOut: ...
    @abstractmethod
    def delete_company(self, current_user: UserOut, company_id: str): ...
