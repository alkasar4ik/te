
from datetime import datetime, timezone

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TicketStatus:
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    description: Mapped[str] = mapped_column(
        Text, nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(25),
        default=TicketStatus.OPEN,
        nullable=False
    )

    priority: Mapped[str] = mapped_column(
        String(25),
        default=TicketPriority.MEDIUM,
        nullable=False
    )

    client_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    master_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    client = relationship(
        "User",
        foreign_keys=[client_id]
    )

    master = relationship(
        "User",
        foreign_keys=[master_id]
    )
