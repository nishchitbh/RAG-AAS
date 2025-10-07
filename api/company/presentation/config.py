from fastapi import APIRouter

from api.company.domain.services import CompanyService
from api.auth.infrastructure.auth_repo import UserRepository
from api.company.infrastructure.company_repo import CompanyRepo
from api.company.application.company_use_cases import CompanyUseCases
from api.company.infrastructure.abstract_company_repo import ICompanyRepo

from vector_store.vector_infra import VectorStoreService, qdrant_client

company_router = APIRouter(prefix="/company", tags=["Company"])


def get_company_use_cases() -> CompanyUseCases:
    company_repo: ICompanyRepo = CompanyRepo()
    company_service = CompanyService()
    user_repo = UserRepository()
    return CompanyUseCases(
        company_repo=company_repo,
        company_service=company_service,
        user_repo=user_repo,
        vectordb_service=VectorStoreService(client=qdrant_client),
    )
