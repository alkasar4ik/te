from datetime import datetime, timezone

from sqlalchemy import Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)

    content: Mapped[str] = mapped_column(
        Text, nullable=False
    )

    ticket_id: Mapped[int] = mapped_column(
        ForeignKey("tickets.id"), nullable=False
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User")
    ticket = relationship("Ticket")