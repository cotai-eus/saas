from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from domain.value_objects.channel_type import ChannelType


class ChannelStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING_AUTH = "pending_auth"
    ERROR = "error"


@dataclass
class ChannelConfig:
    wa_phone_number_id: str = None
    wa_access_token: str = None
    wa_verify_token: str = None
    baileys_session_id: str = None
    baileys_service_url: str = None
    baileys_api_key: str = None
    fb_page_id: str = None
    fb_page_access_token: str = None
    fb_app_secret: str = None
    ig_user_id: str = None
    tg_bot_token: str = None
    tg_webhook_secret: str = None


@dataclass
class Channel:
    id: UUID = field(default_factory=uuid4)
    tenant_id: UUID = None
    type: ChannelType = None
    name: str = ""
    status: ChannelStatus = ChannelStatus.INACTIVE
    config: ChannelConfig = field(default_factory=ChannelConfig)
    daily_limit: int = 1000
    monthly_limit: int = 30000
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
