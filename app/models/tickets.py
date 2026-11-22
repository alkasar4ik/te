from datetime import datetime, timezone

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class OrderStatus:
    PENDING = "pending"
    ACCEPTED = "accepted"
    CLOSED = "closed"


class OrderPriority:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    description: Mapped[str] = mapped_column(
        Text, nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(25),
        default=OrderStatus.PENDING,
        nullable=False
    )

    priority: Mapped[str] = mapped_column(
        String(25),
        default=OrderPriority.MEDIUM,
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