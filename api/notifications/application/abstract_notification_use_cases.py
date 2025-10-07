from abc import ABC, abstractmethod
from api.auth.domain.entities import UserOut
from api.notifications.domain.entities import (
    Notification,
    NotificationsOut,
)

from api.notifications.infrastructure.abstract_notification_repo import (
    INotificationRepo,
)


class INotificationUseCases(ABC):
    def __init__(self, repo: INotificationRepo): ...
    @abstractmethod
    def read_notification(
        self, current_user: UserOut, notification_id: str
    ) -> Notification: ...

    @abstractmethod
    def read_notifications(
        self, current_user: UserOut, page: int = 1, limit: int = 10
    ) -> NotificationsOut: ...
