from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from models.base import Base
from models.utils import generate_uuid


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(
        primary_key=True)
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
