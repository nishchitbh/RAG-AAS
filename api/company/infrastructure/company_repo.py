from typing import List
from bson import ObjectId

from api.shared.domain.repositories.data_repo import IDataRepo
from api.shared.infrastructure.data_repo_impl import MongoRepo
from api.shared.domain.entities import Pagination
from api.company.infrastructure.abstract_company_repo import ICompanyRepo
from api.company.domain.entities import (
    CompanyOut,
    CompanyStore,
    CompanyUpdate,
    CompanyList,
)


class CompanyRepo(ICompanyRepo):
    def __init__(self):
        self.repo: IDataRepo = MongoRepo(collection="companies")

    def create_company(self, company: CompanyStore) -> CompanyOut:
        created_company = self.repo.create(data=company.model_dump())
        return CompanyOut(**created_company)

    def get_all(self, page: int = 1, limit: int = 10) -> List[CompanyOut]:
        data = self.repo.read_all(page=page, limit=limit)
        return CompanyList(
            companies=[CompanyOut(**company) for company in data],
            pagination=Pagination(page=page, items=limit),
        )

    def get_company_by_id(self, company_id: str) -> CompanyOut:
        data = self.repo.read(identifier={"_id": ObjectId(company_id)})
        return CompanyOut(**data) if data else None

    def update_company(
        self, company_id: str, company_update: CompanyUpdate
    ) -> CompanyOut:
        data = self.repo.update(
            identifier={"_id": company_id}, update_data=company_update.model_dump()
        )
        return CompanyOut(**data)

    def delete_company(self, company_id: str):
        return self.repo.delete(identifier={"_id": company_id})
