from api.shared.domain.exception_messages import messages as exception_messages


class AppException(Exception):
    """Base exception class for the application."""

    def __init__(self, message: str | None = None, status_code: int = 500):
        key = type(self).__name__
        message = message or exception_messages[key]
        self.detail = message
        self.status_code = status_code
        super().__init__(message)


class PasswordValidationException(AppException):
    """Exception for password validation errors."""

    def __init__(self, message: str | None = None):
        super().__init__(message=message, status_code=400)


class DatabaseException(AppException):
    """Exception for database errors."""

    def __init__(self, message: str | None = None):
        super().__init__(message=message, status_code=500)


class AuthenticationFailedException(AppException):
    """Exception for authentication errors."""

    def __init__(self, message: str | None = None):
        super().__init__(message=message, status_code=401)


class InvalidUpdateException(AppException):
    """Exception for invalid update operations."""

    def __init__(self, message: str | None = None):
        super().__init__(message=message, status_code=400)  # 400 Bad Request


class ConflictException(AppException):
    """Exception raised when trying to create a user that already exists."""

    def __init__(self, message: str | None = None):
        super().__init__(message=message, status_code=409)  # 409 Conflict


class NotFoundException(AppException):
    """Exception raised when an item is not found."""

    def __init__(self, message: str | None = None):
        super().__init__(message=message, status_code=404)  # 404 Not Found


class UnauthorizedException(AppException):
    def __init__(self, message: str | None = None):
        super().__init__(message=message, status_code=401)


class ForbiddenException(AppException):
    def __init__(self, message: str | None = None):
        super().__init__(message=message, status_code=403)  # 403 Forbidden


class RequestEntityTooLargeException(AppException):
    def __init__(self, message: str | None = None):
        super().__init__(message=message, status_code=413)


class MissingValueException(AppException):
    """Exception raised when a required field is missing."""

    def __init__(self, message: str | None = None):
        # 422 Unprocessable Entity
        super().__init__(message=message, status_code=422)


class InvalidInputException(AppException):
    """Exception raised when a required field is missing."""

    def __init__(self, message: str | None = None):
        super().__init__(message=message, status_code=422)


class Unsupported_Media_Type(AppException):
    def __init__(self, message: str | None = None):
        super().__init__(message=message, status_code=415)
