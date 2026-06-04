import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Index

from sqlalchemy.dialects.postgresql import UUID

from infrastructure.database.base import Base


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    event_hash = Column(String(64), nullable=False)
    channel_id = Column(UUID(as_uuid=True), nullable=False)
    received_at = Column(
        DateTime, default=datetime.utcnow, server_default="CURRENT_TIMESTAMP"
    )


Index("idx_webhook_events_hash", WebhookEvent.event_hash, unique=True)
