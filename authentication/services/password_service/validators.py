from env import get_password_min_length, get_password_max_length
from exceptions import ValidationError


class PasswordValidationError(ValidationError):
    pass


def validate_min_length(value: str) -> str:
    if get_password_min_length() > len(value):
        raise PasswordValidationError("Password is too short")
    return value


def validate_max_length(value: str) -> str:
    if get_password_max_length() < len(value):
        raise PasswordValidationError("Password is too long")
    return value
