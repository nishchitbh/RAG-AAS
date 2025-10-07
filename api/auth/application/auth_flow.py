from tzlocal import get_localzone
from datetime import datetime
from pydantic import EmailStr
from fastapi.responses import StreamingResponse

from api.shared.domain.services import SharedServices
from api.auth.domain.repositories import IUserRepository
from api.auth.domain.services import AuthService, UserService
from api.auth.application.abstract_auth_flow import IAuthUseCases
from api.shared.domain.exceptions import (
    AuthenticationFailedException,
    PasswordValidationException,
    ConflictException,
)
from api.auth.domain.entities import (
    UserCreate,
    UserOut,
    UsersOut,
    UserSignedUp,
    UserUpdate,
    AddPassword,
    UserStore,
    UserLogin,
    LastLoginUpdate,
    FullUpdate,
    LoginResponse,
    Pagination,
)


class AuthUseCases(IAuthUseCases):
    def __init__(
        self,
        user_repo: IUserRepository,
        auth_service: AuthService,
        user_service: UserService,
        shared_service: SharedServices,
    ):
        self.user_repo = user_repo
        self.auth_service = auth_service
        self.user_service = user_service
        self.shared_service = shared_service

    def signup_user(self, user: UserCreate) -> StreamingResponse:
        """
        Register a new user.
        :param user_create: UserCreate object containing user details.
        :return: UserOut object with the created user's details.
        """
        self.user_service.validate_user(user)
        hashed_generated_password = self.auth_service.hash_password(user.password)
        user_store = UserStore(
            **user.model_dump(exclude={"password"}),
            created_at=datetime.now(tz=get_localzone()),
            password=hashed_generated_password,
            generated_password=hashed_generated_password,
        )
        created = self.user_repo.create_user(user_store)
        returnable = UserSignedUp(
            **created.model_dump(),
            company_registered=True if created.company_id else False,
        )
        return returnable

    def login_user(self, user_login: UserLogin) -> dict:
        """
        Log in a user.
        :param user_login: UserLogin object containing login credentials.
        :return: UserOut object with the logged-in user's details.
        """
        user = self.user_repo.get_user_by_email(user_login.email)
        if not user or not self.auth_service.verify_password(
            user_login.password, user.password
        ):
            raise AuthenticationFailedException("Invalid email or password")
        if user.soft_deleted:
            raise AuthenticationFailedException("Invalid email or password")
        token = self.auth_service.create_access_token(data={"sub": user.email})
        last_login = datetime.now(tz=get_localzone())
        self.user_repo.update_user(
            email=user.email, user_update=LastLoginUpdate(last_login_at=last_login)
        )
        return LoginResponse(
            company_registered=True if user.company_id else False,
            access_token=token,
            token_type="bearer",
        )

    def change_password(self, email: EmailStr, add_password: AddPassword) -> UserOut:
        """
        Change the user's password.
        :param user: UserOut object containing the user's details.
        :param add_password: AddPassword object containing the new password.
        :return: UserOut object with the updated user's details.
        """

        current_user = self.user_repo.get_user_by_email(email)
        if not self.auth_service.verify_password(
            add_password.current_password, current_user.password
        ):
            raise AuthenticationFailedException("Invalid current password")
        if add_password.new_password == add_password.current_password:
            raise PasswordValidationException(
                "New password cannot be the same as the current password"
            )
        if add_password.new_password != add_password.confirm_new_password:
            raise PasswordValidationException(
                "New password and confirmation do not match"
            )
        new_hashed_password = self.auth_service.hash_password(add_password.new_password)
        updated = FullUpdate(password=new_hashed_password)
        updated_user = self.user_repo.update_user(
            email=current_user.email, user_update=updated
        )
        return UserOut(**updated_user.model_dump())

    def update_user(self, user_update: UserUpdate, email: str) -> UserOut:
        """
        Update user details by the user themselves.
        :param user_update: UserUpdate object containing the updated user details.
        :param email: Email of the user to be updated.
        :return: UserOut object with the updated user's details.
        """
        updated_user = self.user_repo.update_user(email=email, user_update=user_update)
        return UserOut(**updated_user.model_dump())

    def get_all_users(self, page, limit) -> list[UserOut]:
        """
        Get all users
        Returns:
            list[UserOut]: list of all users
        """
        all_users = [
            UserOut(**user.model_dump())
            for user in self.user_repo.get_all(page=page, limit=limit)
        ]
        pagination = Pagination(page=page, items=limit)
        returnable = UsersOut(users=all_users, pagination=pagination)
        return returnable

    def get_user(self, email: str) -> UserOut:
        """
        Get a user by email.
        :param email: Email of the user to be retrieved.
        :return: UserOut object with the retrieved user's details.
        """
        user = self.user_repo.get_user_by_email(email)
        return UserOut(**user.model_dump())

    def delete_user(self, email: str) -> str:
        """
        Delete a user by email.
        :param email: Email of the user to be deleted.
        :return: UserOut object with the deleted user's details.
        """
        self.user_repo.delete_user(email)
        return f"User with email {email} has been deleted"

    def reset_password(self, email: str) -> StreamingResponse:
        """
        Reset the password of a user.
        :param email: Email of the user to be reset.
        :return: CSV with email and generated password.
        """
        generated_password = self.auth_service.generate_password()
        hashed_generated_password = self.auth_service.hash_password(generated_password)
        updated = FullUpdate(
            password=hashed_generated_password,
            generated_password=hashed_generated_password,
        )
        updated_user = self.user_repo.update_user(email=email, user_update=updated)
        to_send = {"Email": [updated_user.email], "Password": [generated_password]}
        filename = f"{self.shared_service.filename_sanitizer(email)}_creds.csv"
        return self.shared_service.dict_to_streaming_response(
            data=to_send, filename=filename
        )

    def soft_delete_user(self, email: str) -> str:
        """
        Soft delete a user by email.
        :param email: Email of the user to be soft deleted.
        :return: UserOut object with the soft deleted user's details.
        """
        user = self.user_repo.get_user_by_email(email)
        if user.soft_deleted:
            raise ConflictException("User already soft deleted!")
        user_update = FullUpdate(soft_deleted=True)
        self.update_user(user_update=user_update, email=email)
        return "User has been soft deleted"

    def reactivate_user(self, email: str) -> str:
        """
        Reactivate a user by email.
        :param email: Email of the user to be reactivated.
        :return: UserOut object with the reactivated user's details.
        """
        user = self.user_repo.get_user_by_email(email)
        if not user.soft_deleted:
            raise ConflictException("User is not soft deleted!")
        user_update = FullUpdate(soft_deleted=False)
        data = self.update_user(user_update=user_update, email=email)
        return data
