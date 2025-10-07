from api.auth.domain.entities import UserOut, FullUpdate, Role
from api.company.domain.services import CompanyService
from api.auth.domain.repositories import IUserRepository
from api.company.infrastructure.abstract_company_repo import ICompanyRepo
from api.company.application.abstract_company_use_caases import ICompanyUseCases
from vector_store.vector_infra import VectorStoreService
from api.company.domain.entities import (
    CompanyCreate,
    CompanyStore,
    CompanyOut,
    CompanyUpdate,
    CompanyUpdateSuper,
)
from api.shared.domain.exceptions import NotFoundException, ConflictException


class CompanyUseCases(ICompanyUseCases):
    def __init__(
        self,
        company_repo: ICompanyRepo,
        company_service: CompanyService,
        user_repo: IUserRepository,
        vectordb_service: VectorStoreService,
    ):
        self.company_repo = company_repo
        self.company_service = company_service
        self.user_repo = user_repo
        self.vectordb_service = vectordb_service

    def create_company(
        self, current_user: UserOut, company: CompanyCreate
    ) -> CompanyOut:
        if current_user.company_id is not None:
            raise ConflictException("User already has a company")
        company = CompanyStore(**company.model_dump(), active=False)
        created = self.company_repo.create_company(company=company)
        updated_user = FullUpdate(company_id=created.id)
        self.user_repo.update_user(email=current_user.email, user_update=updated_user)
        self.vectordb_service.create_customer_collection(company_id=created.id)
        return CompanyOut(**created.model_dump())

    def get_all(self, page: int = 1, limit: int = 10) -> list[CompanyOut]:
        return self.company_repo.get_all(page=page, limit=limit)

    def get_company_by_id(self, current_user: UserOut, company_id: str) -> CompanyOut:
        if (
            Role.SUPER.value not in current_user.roles
            and current_user.company_id != company_id
        ):
            raise NotFoundException("Company not found")
        return self.company_repo.get_company_by_id(company_id=company_id)

    def update_company(
        self, current_user: UserOut, company_id: str, company_update: CompanyUpdateSuper
    ) -> CompanyOut:
        if (
            Role.SUPER.value not in current_user.roles
            or current_user.company_id != company_id
        ):
            raise NotFoundException("Company not found")
        return self.company_repo.update_company(
            company_id=company_id, company_update=company_update
        )

    def activate_company(self, company_id: str) -> CompanyOut:
        return self.company_repo.update_company(
            company_id=company_id, company_update=CompanyUpdate(active=True)
        )

    def deactivate_company(self, company_id: str) -> CompanyOut:
        return self.company_repo.update_company(
            company_id=company_id, company_update=CompanyUpdate(active=False)
        )

    def delete_company(self, current_user: UserOut, company_id: str):
        if (
            Role.SUPER.value not in current_user.roles
            or current_user.company_id != company_id
        ):
            raise NotFoundException("Company not found")
        return self.company_repo.delete_company(company_id=company_id)
