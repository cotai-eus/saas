import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB

from infrastructure.database.base import Base


class Channel(Base):
    __tablename__ = "channels"

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
    type = Column(String(32), nullable=False)
    name = Column(String(128), nullable=False)
    status = Column(String(16), default="inactive")
    config = Column(JSONB, nullable=False, default=dict)
    daily_limit = Column(Integer, default=1000)
    monthly_limit = Column(Integer, default=30000)
    created_at = Column(
        DateTime, default=datetime.utcnow, server_default="CURRENT_TIMESTAMP"
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
