from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)

    content: Mapped[str] = mapped_column(
        Text, nullable=False
    )

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id"), nullable=False
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User")
    order = relationship("Order", foreign_keys=[order_id])

    @property
    def ticket_id(self) -> int:
        return self.order_id

    @ticket_id.setter
    def ticket_id(self, value: int) -> None:
        self.order_id = value

    @property
    def ticket(self):
        return self.order