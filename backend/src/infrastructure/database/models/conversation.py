import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB

from infrastructure.database.base import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    channel_id = Column(
        UUID(as_uuid=True),
        ForeignKey("channels.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    channel_type = Column(String(32), nullable=False)
    contact_id = Column(
        UUID(as_uuid=True),
        ForeignKey("contacts.id", ondelete="SET NULL"),
        nullable=True,
    )
    status = Column(String(16), default="active")
    last_message_at = Column(DateTime, nullable=True)
    conversation_metadata = Column("metadata", JSONB, nullable=True)
    created_at = Column(
        DateTime, default=datetime.utcnow, server_default="CURRENT_TIMESTAMP"
    )
