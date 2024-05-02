from enum import Enum
from typing import Set

from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class Scope(Base):
    class Types(str, Enum):
        UNRESTRICTED = "unrestricted"
        PROFILE_READ = "profile-read"
        PROFILE_WRITE = "profile-write"

    __tablename__ = "scopes"

    id: Mapped[int] = mapped_column(
        primary_key=True)
    type: Mapped[str] = mapped_column(
        unique=True, nullable=False)

    clients: Mapped[Set["Client"]] = relationship(
        secondary="client_scope", back_populates="scopes")
