from api.auth.domain.entities import UserOut
from api.shared.domain.exceptions import NotFoundException
from api.notifications.application.abstract_notification_use_cases import (
    INotificationUseCases,
)
from api.notifications.domain.entities import (
    Notification,
    NotificationsOut,
)

from api.notifications.infrastructure.abstract_notification_repo import (
    INotificationRepo,
)


class NotificationUseCases(INotificationUseCases):
    def __init__(self, repo: INotificationRepo):
        self.repo = repo

    def read_notification(
        self, current_user: UserOut, notification_id: str
    ) -> Notification:
        notification = self.repo.update_notification(notification_id)
        if notification.company_id != current_user.company_id:
            raise NotFoundException("Notification not found")
        return notification

    def read_notifications(
        self, current_user: UserOut, page: int = 1, limit: int = 10
    ) -> NotificationsOut:
        return self.repo.get_all(
            company_id=current_user.company_id, page=page, limit=limit
        )
