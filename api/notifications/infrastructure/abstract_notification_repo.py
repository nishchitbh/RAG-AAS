from abc import ABC, abstractmethod
from api.notifications.domain.entities import (
    Notification,
    NotificationOut,
    NotificationsOut,
    NotificationUpdate,
)


class INotificationRepo(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def create_notification(self, notification: Notification) -> NotificationOut: ...

    @abstractmethod
    def get_all(
        self, company_id: str, page: int = 1, limit: int = 10
    ) -> NotificationsOut: ...

    @abstractmethod
    def get_notification_by_notification_id(
        self, notification_id: str
    ) -> NotificationOut: ...

    @abstractmethod
    def update_notification(
        self, notification_id: str, notification: NotificationUpdate
    ) -> NotificationOut: ...
