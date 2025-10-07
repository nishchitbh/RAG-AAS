from fastapi import Depends, status

from api.end_users.domain.entities import (
    EndUserBase,
    EndUserChat,
    EndUserList,
)

from api.auth.presentation.config import get_current_user, UserOut
from api.end_users.presentation.config import (
    end_user_route,
    get_end_user_use_cases,
    EndUserUseCases,
)


class EndUserRoutes:
    def __init__(self):
        self.router = end_user_route
        self.router.add_api_route(
            path="/register",
            endpoint=self.create_user,
            methods=["POST"],
            status_code=status.HTTP_201_CREATED,
            response_model=EndUserBase,
        )
        self.router.add_api_route(
            path="/all",
            endpoint=self.get_all_users,
            methods=["GET"],
            status_code=status.HTTP_200_OK,
            response_model=EndUserList,
        )
        self.router.add_api_route(
            path="/{id}",
            endpoint=self.get_user_by_id,
            methods=["GET"],
            status_code=status.HTTP_200_OK,
            response_model=EndUserChat,
        )

    def create_user(
        self,
        company_id: str,
        use_cases: EndUserUseCases = Depends(get_end_user_use_cases),
    ):
        return use_cases.create_user(company_id)

    def get_user_by_id(
        self,
        id: str,
        use_cases: EndUserUseCases = Depends(get_end_user_use_cases),
        current_user: UserOut = get_current_user("super", "company_admin"),
    ):
        return use_cases.get_user_by_admin(generated_id=id, current_user=current_user)

    def get_all_users(
        self,
        page: int = 1,
        items: int = 10,
        use_cases: EndUserUseCases = Depends(get_end_user_use_cases),
        current_user: UserOut = get_current_user("super", "company_admin"),
    ):
        return use_cases.get_users(current_user=current_user, skip=page, limit=items)
