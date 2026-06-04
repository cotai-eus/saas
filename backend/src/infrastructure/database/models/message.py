import uuid
from datetime import datetime, timezone
from typing import Optional, Any, Dict

from sqlalchemy import (
    String,
    Integer,
    DateTime,
    ForeignKey,
    Text,
    text
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB

from infrastructure.database.base import Base


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    channel_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("channels.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    channel_type: Mapped[str] = mapped_column(String(32), nullable=False)
    contact_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("contacts.id", ondelete="SET NULL"),
        nullable=True,
    )
    conversation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="SET NULL"),
        nullable=True,
    )
    direction: Mapped[str] = mapped_column(String(10), nullable=False, server_default="outbound")
    content_type: Mapped[str] = mapped_column(String(20), nullable=False)
    content_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_media_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    content_template_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    content_template_vars: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        server_default="pending",
        index=True,
    )
    provider_message_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    error_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    message_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        server_default=text("CURRENT_TIMESTAMP")
    )
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    @classmethod
    def from_domain(cls, msg, direction=None):
        content = msg.content
        return cls(
            id=msg.id,
            tenant_id=msg.tenant_id,
            channel_id=msg.channel_id,
            channel_type=msg.channel_type.value if msg.channel_type else None,
            contact_id=msg.contact_id,
            conversation_id=msg.conversation_id,
            direction=direction or msg.direction,
            content_type=content.type.value if content else None,
            content_text=content.text if content else None,
            content_media_url=content.media_url if content else None,
            content_template_name=content.template_name if content else None,
            content_template_vars=content.template_vars if content else {},
            status=msg.status.value,
            provider_message_id=msg.provider_message_id,
            error_code=msg.error_code,
            error_message=msg.error_message,
            message_metadata=msg.metadata or {},
        )
