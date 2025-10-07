from bson import ObjectId

from api.shared.domain.entities import Pagination
from api.shared.domain.repositories.data_repo import IDataRepo
from api.shared.infrastructure.data_repo_impl import MongoRepo
from api.notifications.infrastructure.abstract_notification_repo import (
    INotificationRepo,
)
from api.notifications.domain.entities import (
    Notification,
    NotificationOut,
    NotificationsOut,
    NotificationUpdate,
)


class NotificationRepo(INotificationRepo):
    def __init__(self):
        self.repo: IDataRepo = MongoRepo(collection="notifications")

    def create_notification(self, notification: Notification) -> NotificationOut:
        created_notification = self.repo.create(data=notification.model_dump())
        return Notification(**created_notification)

    def get_all(
        self, company_id: str, page: int = 1, limit: int = 10
    ) -> NotificationsOut:
        data = self.repo.read_all(
            page=page, limit=limit, metadata={"company_id": company_id}
        )
        return NotificationsOut(
            notifications=[NotificationOut(**notification) for notification in data],
            pagination=Pagination(page=page, items=limit),
        )

    def get_notification_by_notification_id(
        self, notification_id: str
    ) -> NotificationOut:
        data = self.repo.read(identifier={"_id": notification_id})
        return NotificationOut(**data)

    def update_notification(
        self, notification_id: str, notification: NotificationUpdate
    ) -> NotificationOut:
        data = self.repo.update(
            identifier={"_id": ObjectId(notification_id)},
            update_data=notification.model_dump(),
        )
        return NotificationOut(**data)
