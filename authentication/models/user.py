import re
from datetime import datetime
from typing import Set

from sqlalchemy.orm import validates, mapped_column, Mapped, relationship

from models.base import Base, FieldValidationError

EMAIL_REGEX = r"^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9]" \
              r"(?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$"
PASSWORD_REGEX = r"^[a-zA-Z0-9_]+\$[0-9]+\$[a-zA-Z0-9_\/+=]+=*\$[a-zA-Z0-9\/+=]+=*$"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True)
    email: Mapped[str] = mapped_column(
        unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(
        index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now)

    clients: Mapped[Set["Client"]] = relationship(
        back_populates="user")

    @validates("email")
    def validate_email(self, key, email):
        if not re.match(EMAIL_REGEX, email):
            raise FieldValidationError("Invalid email address format")
        return email

    @validates("password")
    def validate_password(self, key, password):
        if not re.match(PASSWORD_REGEX, password):
            raise FieldValidationError("Invalid password format")
        return password
