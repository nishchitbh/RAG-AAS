from api.shared.domain.exceptions import ConflictException, PasswordValidationException
from api.auth.domain.repositories import IUserRepository
from api.auth.domain.entities import UserCreate
from datetime import datetime, timedelta
from passlib.context import CryptContext
from api.shared.config import setting
from tzlocal import get_localzone
from jwt import PyJWTError
import logging
import random
import string
import jwt


class AuthService:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.logger = logging.getLogger(__name__)

    def hash_password(self, plain_password: str) -> str:
        return self.pwd_context.hash(plain_password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def __create_token(self, data: dict, expires_delta: timedelta) -> str:
        to_encode = data.copy()
        expire = datetime.now(tz=get_localzone()) + expires_delta
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, setting.auth_secret, algorithm=setting.algorithm)

    def create_access_token(self, data: dict) -> str:
        return self.__create_token(
            data, timedelta(minutes=setting.access_token_expiry_time)
        )

    def create_refresh_token(self, data: dict) -> str:
        payload = data.copy()
        payload.update({"type": "refresh"})
        return self.__create_token(
            payload, timedelta(days=setting.refresh_token_expiry_time)
        )

    def verify_token(
        self, token: str, credentials_exception, *, token_type="access"
    ) -> dict:
        try:
            payload = jwt.decode(
                token, setting.auth_secret, algorithms=[setting.algorithm]
            )
            if token_type == "refresh":
                if payload.get("token_type") != "refresh":
                    raise credentials_exception
            else:
                if payload.get("token_type") == "refresh":
                    raise credentials_exception
            username = payload.get("sub")
            if username is None:
                raise credentials_exception
            return payload
        except PyJWTError as e:
            self.logger.warning(f"JWT verification failed: {e}")
            raise credentials_exception

    def generate_password(self) -> str:
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        symbols = string.punctuation
        password = [
            random.choice(uppercase),
            random.choice(lowercase),
            random.choice(digits),
            random.choice(symbols),
        ]
        remaining_characters = random.choices(
            lowercase + uppercase + digits + symbols, k=4
        )
        password.extend(remaining_characters)
        random.shuffle(password)
        password = "".join(password)
        password = password.replace("\\", "=")
        return password


class UserService:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    def validate_user(self, user: UserCreate):
        self.__check_uniqueness(user)
        self.__check_matching_password(user)

    def __check_uniqueness(self, user: UserCreate):
        existing_user = self.user_repo.get_user_by_email(user.email)
        if existing_user:
            raise ConflictException("User already exists!")

    def __check_matching_password(self, user: UserCreate):
        if user.password != user.confirm_password:
            raise PasswordValidationException("Passwords do not match")
