from typing import List

from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from api.auth.domain.entities import UserOut

from api.shared.domain.services import SharedServices
from api.auth.application.auth_flow import AuthUseCases
from api.auth.domain.repositories import IUserRepository
from api.auth.infrastructure.auth_repo import UserRepository
from api.auth.domain.services import AuthService, UserService
from api.auth.application.abstract_auth_flow import IAuthUseCases
from api.shared.domain.exceptions import (
    AuthenticationFailedException,
    ForbiddenException,
)


bearer_scheme = HTTPBearer()

auth_router = APIRouter(prefix="/auth", tags=["Auth"])
user_router = APIRouter(prefix="/user", tags=["User"])


def get_auth_use_cases() -> IAuthUseCases:
    user_repo: IUserRepository = UserRepository()
    auth_service = AuthService(user_repo=user_repo)
    user_service = UserService(user_repo=user_repo)
    return AuthUseCases(
        auth_service=auth_service,
        user_repo=user_repo,
        user_service=user_service,
        shared_service=SharedServices,
    )


async def get_user_from_token(token: str, auth_use_cases: IAuthUseCases) -> UserOut:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = auth_use_cases.auth_service.verify_token(token, credentials_exception)
    user = auth_use_cases.user_repo.get_user_by_email(payload["sub"])

    return UserOut(**user.model_dump())


def get_current_user(*required_role: List[str]):
    async def _get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        auth_use_cases: IAuthUseCases = Depends(get_auth_use_cases),
    ) -> UserOut:
        user = await get_user_from_token(credentials.credentials, auth_use_cases)
        if not user:
            raise AuthenticationFailedException("Invalid email or password!")
        user_roles = [role for role in user.roles]
        if not set(required_role) & set(user_roles):
            raise ForbiddenException("Access denied!")
        return user

    return Depends(_get_current_user)


def get_user():
    async def _get_user(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        auth_use_cases: IAuthUseCases = Depends(get_auth_use_cases),
    ) -> UserOut:
        user = await get_user_from_token(credentials.credentials, auth_use_cases)
        return user

    return Depends(_get_user)
