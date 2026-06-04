from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from domain.value_objects.channel_type import ChannelType, MessageStatus
from domain.value_objects.message_content import MessageContent


@dataclass
class Message:
    id: UUID = field(default_factory=uuid4)
    tenant_id: UUID = None
    channel_id: UUID = None
    channel_type: ChannelType = None
    contact_id: UUID = None
    conversation_id: UUID = None
    direction: str = "outbound"
    content: MessageContent = None
    status: MessageStatus = MessageStatus.PENDING
    provider_message_id: str = None
    error_code: str = None
    error_message: str = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    sent_at: datetime = None
    delivered_at: datetime = None
    read_at: datetime = None
    metadata: dict = field(default_factory=dict)
