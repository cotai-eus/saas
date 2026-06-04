import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from sqlalchemy import String, Integer, DateTime, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB

from infrastructure.database.base import Base


class Channel(Base):
    __tablename__ = "channels"

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
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(16), server_default="inactive")
    config: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    daily_limit: Mapped[int] = mapped_column(Integer, server_default="1000")
    monthly_limit: Mapped[int] = mapped_column(Integer, server_default="30000")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        server_default=text("CURRENT_TIMESTAMP")
    )

    @classmethod
    def from_domain(cls, channel):
        cfg = channel.config or {}
        from infrastructure.crypto import encrypt_json
        raw = {
            "wa_phone_number_id": cfg.wa_phone_number_id,
            "wa_access_token": cfg.wa_access_token,
            "wa_verify_token": cfg.wa_verify_token,
            "baileys_session_id": cfg.baileys_session_id,
            "baileys_service_url": cfg.baileys_service_url,
            "baileys_api_key": cfg.baileys_api_key,
            "fb_page_id": cfg.fb_page_id,
            "fb_page_access_token": cfg.fb_page_access_token,
            "fb_app_secret": cfg.fb_app_secret,
            "ig_user_id": cfg.ig_user_id,
            "tg_bot_token": cfg.tg_bot_token,
            "tg_webhook_secret": cfg.tg_webhook_secret,
        }
        return cls(
            id=channel.id,
            tenant_id=channel.tenant_id,
            type=channel.type.value,
            name=channel.name,
            status=channel.status.value,
            config=encrypt_json(raw),
            daily_limit=channel.daily_limit,
            monthly_limit=channel.monthly_limit,
        )
