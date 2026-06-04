from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from domain.value_objects.channel_type import ChannelType


@dataclass
class Conversation:
    id: UUID = field(default_factory=uuid4)
    tenant_id: UUID = None
    channel_id: UUID = None
    channel_type: ChannelType = None
    contact_id: UUID = None
    status: str = "active"
    last_message_at: datetime = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict = field(default_factory=dict)
