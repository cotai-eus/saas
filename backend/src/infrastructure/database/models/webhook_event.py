import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Index, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from infrastructure.database.base import Base


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    event_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    channel_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    received_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        server_default=text("CURRENT_TIMESTAMP")
    )


Index("idx_webhook_events_hash", WebhookEvent.event_hash, unique=True)
