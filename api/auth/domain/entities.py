from api.shared.domain.exceptions import PasswordValidationException
from pydantic import BaseModel, EmailStr, Field, field_validator
from api.shared.domain.entities import Pagination
from typing import Optional, List
from datetime import datetime
from enum import Enum
import re


class Role(str, Enum):
    SUPER = "super"
    COMPANY_ADMIN = "company_admin"
    USER = "user"


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    company_registered: bool


class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    company_id: Optional[str] = None


class UnregisteredUser(BaseModel):
    identifier: str
    company_id: str


class UserCreate(UserBase):
    email: EmailStr
    company_id: Optional[str] = None
    password: str = Field(
        ...,
        min_length=8,
        description=(
            "New password must be at least 8 characters long and contain at least one "
            "uppercase letter, one lowercase letter, one digit, and one special character"
        ),
    )
    confirm_password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, pw: str) -> str:
        errors = []
        if not re.search(r"[a-z]", pw):
            errors.append("one lowercase letter")
        if not re.search(r"[A-Z]", pw):
            errors.append("one uppercase letter")
        if not re.search(r"\d", pw):
            errors.append("one digit")
        if not re.search(r"[\W_]", pw):
            errors.append("one special character")
        if errors:
            raise PasswordValidationException(
                f"Password must contain at least {', '.join(errors)}"
            )
        return pw


class UserOut(UserBase):
    roles: List[str]
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None


class UserSignedUp(UserOut):
    message: str = (
        "User registered successfully! Please contact super-admin for activation"
    )
    company_registered: bool


class UsersOut(BaseModel):
    users: List[UserOut]
    pagination: Pagination


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class AddPassword(BaseModel):
    current_password: str
    new_password: str = Field(
        ...,
        min_length=8,
        description=(
            "New password must be at least 8 characters long and contain at least one "
            "uppercase letter, one lowercase letter, one digit, and one special character"
        ),
    )
    confirm_new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, pw: str) -> str:
        errors = []
        if not re.search(r"[a-z]", pw):
            errors.append("one lowercase letter")
        if not re.search(r"[A-Z]", pw):
            errors.append("one uppercase letter")
        if not re.search(r"\d", pw):
            errors.append("one digit")
        if not re.search(r"[\W_]", pw):
            errors.append("one special character")
        if errors:
            raise PasswordValidationException(
                f"Password must contain at least {', '.join(errors)}"
            )
        return pw


class UserStore(UserBase):
    password: str
    roles: List[str] = [Role.COMPANY_ADMIN.value]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    soft_deleted: Optional[bool] = None


class UserUpdateBase(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    roles: Optional[List[str]] = None


class UserUpdate(UserUpdateBase): ...


class LastLoginUpdate(BaseModel):
    last_login_at: datetime


class FullUpdate(UserUpdateBase):
    company_id: Optional[str] = None
    password: Optional[str] = None
    generated_password: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    soft_deleted: Optional[bool] = None
