from fastapi import APIRouter

from api.end_users.infrastructure.end_user_repo import EndUserRepo
from api.end_users.application.end_user_use_cases import EndUserUseCases

end_user_route = APIRouter(
    prefix="/end_users",
    tags=["End Users"],
)


def get_end_user_use_cases() -> EndUserUseCases:
    return EndUserUseCases(end_user_repo=EndUserRepo())
