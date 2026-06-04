import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB

from infrastructure.database.base import Base


class Contact(Base):
    __tablename__ = "contacts"

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
    external_id = Column(String(255), nullable=True)
    name = Column(String(255), default="")
    phone = Column(String(20), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    contact_metadata = Column("metadata", JSONB, nullable=True)
    created_at = Column(
        DateTime, default=datetime.utcnow, server_default="CURRENT_TIMESTAMP"
    )
    updated_at = Column(DateTime, nullable=True)
