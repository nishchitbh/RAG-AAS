from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from api.shared.domain.entities import Pagination


class EndUserBase(BaseModel):
    generated_id: str
    company_id: str


class EndUserChat(EndUserBase):
    chat_history: List[Optional[Dict[str, Any]]] = []
    chat_summary: Optional[str] = ""


class EndUserUpdate(BaseModel):
    generated_id: Optional[str] = None
    chat_summary: Optional[str] = None


class LatestChat(BaseModel):
    user: str
    bot: str


class EndUserList(BaseModel):
    end_users: List[EndUserBase]
    pagination: Pagination
