from pydantic import BaseModel
from typing import Optional, List
from api.shared.domain.entities import Pagination


class CompanyBase(BaseModel):
    name: str


class CompanyCreate(CompanyBase): ...


class CompanyUpdateSuper(BaseModel):
    name: Optional[str] = None


class CompanyUpdate(CompanyUpdateSuper):
    active: bool = False


class CompanyOut(CompanyBase):
    _id: str


class CompanyStore(CompanyBase):
    name: str
    active: bool


class CompanyList(BaseModel):
    companies: List[CompanyOut]
    pagination: Pagination
