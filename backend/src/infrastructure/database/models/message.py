import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    ForeignKey,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB

from infrastructure.database.base import Base


class Message(Base):
    __tablename__ = "messages"

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
    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="SET NULL"),
        nullable=True,
    )
    direction = Column(String(10), nullable=False, default="outbound")
    content_type = Column(String(20), nullable=False)
    content_text = Column(Text, nullable=True)
    content_media_url = Column(String(500), nullable=True)
    content_template_name = Column(String(128), nullable=True)
    content_template_vars = Column(JSONB, nullable=True)
    status = Column(
        String(16),
        nullable=False,
        default="pending",
        index=True,
    )
    provider_message_id = Column(String(255), nullable=True, index=True)
    error_code = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)
    message_metadata = Column("metadata", JSONB, nullable=True)
    created_at = Column(
        DateTime, default=datetime.utcnow, server_default="CURRENT_TIMESTAMP"
    )
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)

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
