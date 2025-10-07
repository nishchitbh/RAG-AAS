from fastapi import Depends, status

from api.notifications.domain.entities import (
    NotificationOut,
    NotificationsOut,
)

from api.auth.presentation.config import get_current_user, UserOut
from api.notifications.presentation.config import (
    notification_router,
    INotificationUseCases,
    get_notification_use_cases,
)


class NotificationRoutes:
    def __init__(self):
        self.router = notification_router
        self.router.add_api_route(
            path="/",
            endpoint=self.get_all_notifications,
            methods=["GET"],
            status_code=status.HTTP_200_OK,
            response_model=NotificationsOut,
        )
        self.router.add_api_route(
            path="/{id}",
            endpoint=self.get_notification,
            methods=["GET"],
            status_code=status.HTTP_200_OK,
            response_model=NotificationOut,
        )

    def get_all_notifications(
        self,
        page: int = 1,
        limit: int = 10,
        use_cases: INotificationUseCases = Depends(get_notification_use_cases),
        current_user: UserOut = get_current_user("company_admin", "super"),
    ):
        return use_cases.read_notifications(
            current_user=current_user, page=page, limit=limit
        )

    def get_notification(
        self,
        id: str,
        use_cases: INotificationUseCases = Depends(get_notification_use_cases),
        current_user: UserOut = get_current_user("super", "company_admin"),
    ):
        return use_cases.read_notification(
            current_user=current_user, notification_id=id
        )
