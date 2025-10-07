from pydantic import EmailStr
from fastapi import Depends, status
from fastapi.responses import StreamingResponse

from api.auth.application.abstract_auth_flow import IAuthUseCases
from api.auth.presentation.config import (
    auth_router,
    user_router,
    get_current_user,
    get_auth_use_cases,
)
from api.auth.domain.entities import (
    UserOut,
    UsersOut,
    UserLogin,
    UserCreate,
    UserUpdate,
    AddPassword,
    UserSignedUp,
    LoginResponse,
)


class AuthRoutes:
    def __init__(self):
        self.router = auth_router
        self.router.add_api_route(
            path="/login",
            endpoint=self.login,
            methods=["POST"],
            status_code=status.HTTP_200_OK,
            response_model=LoginResponse,
        )
        self.router.add_api_route(
            path="/signup",
            endpoint=self.signup,
            methods=["POST"],
            status_code=status.HTTP_201_CREATED,
            response_model=UserSignedUp,
        )
        self.router.add_api_route(
            path="/change-password",
            endpoint=self.change_password,
            methods=["PATCH"],
            status_code=status.HTTP_200_OK,
            response_model=UserOut,
        )
        self.router.add_api_route(
            path="/reset-password",
            endpoint=self.reset_password,
            methods=["PATCH"],
            response_class=StreamingResponse,
            status_code=status.HTTP_200_OK,
        )

    def login(
        self,
        user_login: UserLogin,
        auth_use_cases: IAuthUseCases = Depends(get_auth_use_cases),
    ):
        """
        **Log in a user.**\n
        **:param** user_login: UserLogin object containing:\n
        * email : EmailStr\n
        * password: str\n
        **:return:** UserOut object with access_token, token_type and must_change_password
        """
        return auth_use_cases.login_user(user_login)

    def signup(
        self,
        user_create: UserCreate,
        auth_use_cases: IAuthUseCases = Depends(get_auth_use_cases),
    ):
        """
        **Signup a new user.**\n
        **:param** UserCreate: UserCreate object containing:\n
        * full_name : str\n
        * email: EmailStr\n
        * company: str\n
        **:return:** info of created user\n
        """
        return auth_use_cases.signup_user(user_create)

    def change_password(
        self,
        add_password: AddPassword,
        current_user: UserOut = get_current_user("user"),
        auth_use_cases: IAuthUseCases = Depends(get_auth_use_cases),
    ):
        """
        **Change the user's password.**\n
        **:param** add_password: AddPassword object containing:\n
        * current_password: str\n
        * new_password: str\n
        * confirm_new_password: str\n
        **:return:** UserOut object with user's info.
        """
        return auth_use_cases.change_password(
            email=current_user.email, add_password=add_password
        )

    def reset_password(
        self,
        email: str,
        current_user: UserOut = get_current_user("super"),
        auth_use_cases: IAuthUseCases = Depends(get_auth_use_cases),
    ):
        """
        **Reset the user's password.**\n
        **:param** email: EmailStr\n
        **:return:** CSV file with user's email and password.
        """
        return auth_use_cases.reset_password(email)


class UserRoutes:
    def __init__(self):
        self.router = user_router
        self.router.add_api_route(
            path="/me",
            endpoint=self.get_me,
            methods=["GET"],
            response_model=UserOut,
            status_code=status.HTTP_200_OK,
        )
        self.router.add_api_route(
            path="/update-me",
            endpoint=self.self_update_user,
            methods=["PATCH"],
            response_model=UserOut,
            status_code=status.HTTP_200_OK,
        )
        self.router.add_api_route(
            path="/users",
            endpoint=self.get_all_users,
            methods=["GET"],
            status_code=status.HTTP_200_OK,
            response_model=UsersOut,
        )
        self.router.add_api_route(
            path="/users/",
            endpoint=self.get_user_by_id,
            methods=["GET"],
            status_code=status.HTTP_200_OK,
            response_model=UserOut,
        )
        self.router.add_api_route(
            path="/hard-delete/",
            endpoint=self.delete_user,
            methods=["DELETE"],
            status_code=status.HTTP_200_OK,
            response_model=str,
            responses={
                200: {
                    "description": "User has been deleted",
                }
            },
        )
        self.router.add_api_route(
            path="/delete",
            endpoint=self.soft_delete,
            methods=["DELETE"],
            status_code=status.HTTP_200_OK,
            response_model=str,
            responses={
                200: {
                    "description": "User has been deleted",
                }
            },
        )
        self.router.add_api_route(
            path="/update/",
            endpoint=self.update_user,
            methods=["PATCH"],
            status_code=status.HTTP_200_OK,
            response_model=UserOut,
        )
        self.router.add_api_route(
            path="/reactivate-user/",
            endpoint=self.reactivate_user,
            methods=["PATCH"],
            status_code=status.HTTP_200_OK,
            response_model=UserOut,
        )

    def get_me(self, current_user: UserOut = get_current_user("user")):
        """
        **Get the current user.**\n
        **:return:** UserOut object
        """
        return current_user

    def self_update_user(
        self,
        user_update: UserUpdate,
        current_user: UserOut = get_current_user("user"),
        auth_use_cases: IAuthUseCases = Depends(get_auth_use_cases),
    ):
        """
        **Update the current user.**\n
        **:return:** UserOut object
        """
        return auth_use_cases.update_user(
            user_update=user_update, email=current_user.email
        )

    def update_user(
        self,
        email: EmailStr,
        user_update: UserUpdate,
        current_user: UserOut = get_current_user("super", "admin"),
        auth_use_cases: IAuthUseCases = Depends(get_auth_use_cases),
    ):
        """
        **Update a user by email.**\n
        **:param** email: EmailStr\n
        **:param** user_update: SelfUpdate object containing:\n
        **:return:** UserOut object
        """
        return auth_use_cases.update_user(user_update=user_update, email=email)

    def get_all_users(
        self,
        page: int = 1,
        limit: int = 10,
        current_user: UserOut = get_current_user("super", "admin"),
        auth_use_cases: IAuthUseCases = Depends(get_auth_use_cases),
    ):
        """
        **Get all users.**\n
        **:return:** list[UserOut] object
        """
        return auth_use_cases.get_all_users(page=page, limit=limit)

    def get_user_by_id(
        self,
        email: str,
        current_user: UserOut = get_current_user("super", "admin"),
        auth_use_cases: IAuthUseCases = Depends(get_auth_use_cases),
    ):
        """
        **Get a user by email.**\n
        **:return:** UserOut object
        """
        return auth_use_cases.get_user(email)

    def soft_delete(
        self,
        current_user: UserOut = get_current_user("user"),
        auth_use_cases: IAuthUseCases = Depends(get_auth_use_cases),
    ):
        """
        **Soft delete a user by email.**\n
        **:return:** UserOut object
        """
        return auth_use_cases.soft_delete_user(email=current_user.email)

    def delete_user(
        self,
        email: EmailStr,
        current_user: UserOut = get_current_user("super", "admin"),
        auth_use_cases: IAuthUseCases = Depends(get_auth_use_cases),
    ):
        """
        **Hard delete a user by email.**\n
        **:return:** UserOut object
        """
        return auth_use_cases.delete_user(email)

    def reactivate_user(
        self,
        email: EmailStr,
        current_user: UserOut = get_current_user("super", "admin"),
        auth_use_cases: IAuthUseCases = Depends(get_auth_use_cases),
    ):
        """
        **Reactivate a user by email.**\n
        **:return:** UserOut object
        """
        return auth_use_cases.reactivate_user(email)
