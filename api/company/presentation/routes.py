from typing import List
from fastapi import Depends, status

from api.company.domain.entities import CompanyOut, CompanyCreate, CompanyList

from api.auth.presentation.config import get_current_user, UserOut
from api.company.application.abstract_company_use_caases import ICompanyUseCases
from api.company.presentation.config import (
    company_router,
    get_company_use_cases,
    CompanyUseCases,
)


class CompanyRoutes:
    def __init__(self):
        self.router = company_router
        self.router.add_api_route(
            path="/",
            endpoint=self.create_company,
            methods=["POST"],
            status_code=status.HTTP_201_CREATED,
            response_model=CompanyOut,
        )
        self.router.add_api_route(
            path="/all",
            endpoint=self.get_all_companies,
            methods=["GET"],
            status_code=status.HTTP_200_OK,
            response_model=CompanyList,
        )
        self.router.add_api_route(
            path="/{id}",
            endpoint=self.get_company_by_id,
            methods=["GET"],
            status_code=status.HTTP_200_OK,
            response_model=CompanyOut,
        )

    def create_company(
        self,
        company: CompanyCreate,
        use_cases: ICompanyUseCases = Depends(get_company_use_cases),
        current_user: UserOut = get_current_user("company_admin"),
    ):
        return use_cases.create_company(current_user=current_user, company=company)

    def get_company_by_id(
        self,
        id: str,
        use_cases: CompanyUseCases = Depends(get_company_use_cases),
        current_user: UserOut = get_current_user("super", "company_admin"),
    ):
        return use_cases.get_company_by_id(current_user=current_user, company_id=id)

    def get_all_companies(
        self,
        page: int = 1,
        limit: int = 10,
        use_cases: ICompanyUseCases = Depends(get_company_use_cases),
        current_user: UserOut = get_current_user("super"),
    ):
        return use_cases.get_all(page=page, limit=limit)
