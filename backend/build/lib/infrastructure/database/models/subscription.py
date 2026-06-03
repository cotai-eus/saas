import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, text, ForeignKey, BigInteger, Integer
from sqlalchemy.orm import Mapped, mapped_column
from infrastructure.database.base import Base

class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), unique=True, nullable=False)
    plan: Mapped[str] = mapped_column(String(50), nullable=False)
    billing_cycle: Mapped[str] = mapped_column(String(10), server_default="monthly")
    price_cents: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[str] = mapped_column(String(50), server_default="active")
    seats_limit: Mapped[int] = mapped_column(Integer, server_default="5")
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    trial_ends_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    renewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    canceled_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"))
