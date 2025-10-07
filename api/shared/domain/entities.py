from pydantic import BaseModel


class Pagination(BaseModel):
    page: int
    items: int
