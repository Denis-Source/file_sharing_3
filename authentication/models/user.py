import re
from datetime import datetime
from typing import Set

from sqlalchemy.orm import validates, mapped_column, Mapped, relationship

from models.base import Base, FieldValidationError

USERNAME_REGEX = r"^[a-zA-Z0-9_]{3,20}$"
PASSWORD_REGEX = r"^[a-zA-Z0-9_]+\$[0-9]+\$[a-zA-Z0-9_\/+=]+=*\$[a-zA-Z0-9\/+=]+=*$"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True)
    username: Mapped[str] = mapped_column(
        unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(
        index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now)

    clients: Mapped[Set["Client"]] = relationship(
        back_populates="user")

    @validates("username")
    def validate_username(self, key, username):
        if not re.match(USERNAME_REGEX, username):
            raise FieldValidationError("Invalid username")
        return username

    @validates("password")
    def validate_password(self, key, password):
        if not re.match(PASSWORD_REGEX, password):
            raise FieldValidationError("Invalid password format")
        return password
