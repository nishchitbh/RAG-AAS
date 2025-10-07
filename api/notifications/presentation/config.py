from fastapi import APIRouter
from api.notifications.application.notification_use_cases import NotificationUseCases
from api.notifications.application.abstract_notification_use_cases import (
    INotificationUseCases,
)
from api.notifications.infrastructure.notification_repo import NotificationRepo


notification_router = APIRouter(prefix="/notification", tags=["Notification"])


def get_notification_use_cases() -> INotificationUseCases:
    return NotificationUseCases(repo=NotificationRepo())
