from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


# TODO Make used field so that the code expires after being used
class Code(Base):
    __tablename__ = "codes"

    id: Mapped[int] = mapped_column(
        primary_key=True)
    value: Mapped[str] = mapped_column(
        nullable=False)
    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    redirect_uri: Mapped[str] = mapped_column(
        nullable=False)
    valid_until: Mapped[datetime] = mapped_column(
        nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now)

    client: Mapped["Client"] = relationship(
        back_populates="codes")
