from sqlalchemy.orm import DeclarativeBase

from exceptions import ValidationError


class FieldValidationError(ValidationError):
    pass


class Base(DeclarativeBase):
    pass
