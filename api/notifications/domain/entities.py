from pydantic import BaseModel
from typing import List, Optional
from api.shared.domain.entities import Pagination


class Notification(BaseModel):
    company_id: str
    message: str
    read: bool = False


class NotificationOut(Notification):
    _id: str


class NotificationsOut(BaseModel):
    notifications: List[NotificationOut]
    pagination: Pagination


class NotificationUpdate(BaseModel):
    read: Optional[bool]
