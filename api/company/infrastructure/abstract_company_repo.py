from abc import ABC, abstractmethod
from typing import List

from api.shared.domain.repositories.data_repo import IDataRepo
from api.company.domain.entities import (
    CompanyOut,
    CompanyStore,
    CompanyUpdate,
)


class ICompanyRepo(ABC):
    def __init__(self, repo: IDataRepo):
        self.repo = repo

    @abstractmethod
    def create_company(self, company: CompanyStore) -> CompanyOut: ...

    @abstractmethod
    def get_all(self, page: int = 1, limit: int = 10) -> List[CompanyOut]: ...

    @abstractmethod
    def get_company_by_id(self, company_id: str) -> CompanyOut: ...

    @abstractmethod
    def update_company(
        self, company_id: str, company_update: CompanyUpdate
    ) -> CompanyOut: ...

    @abstractmethod
    def delete_company(self, company_id: str): ...
