import re
from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship, validates

from models.base import Base, FieldValidationError
from models.utils import generate_uuid

USERNAME_REGEX = r"^[a-zA-Z0-9_]{10,255}$"


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(
        primary_key=True)
    name: Mapped[str] = mapped_column(
        unique=True, index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    secret: Mapped[str] = mapped_column(
        default=generate_uuid,
        unique=True, index=True, nullable=False)
    last_authenticated: Mapped[datetime] = mapped_column(
        nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now)

    user: Mapped["User"] = relationship(
        back_populates="clients")
    codes: Mapped["Code"] = relationship(
        back_populates="client")

    @validates("name")
    def validate_username(self, key, username):
        if not re.match(USERNAME_REGEX, username):
            raise FieldValidationError("Invalid name")
        return username
