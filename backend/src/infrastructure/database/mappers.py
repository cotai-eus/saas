from uuid import UUID

from domain.entities.channel import Channel, ChannelConfig, ChannelStatus
from domain.entities.message import Message, MessageContent, MessageStatus
from domain.value_objects.channel_type import ChannelType, ContentType
from infrastructure.database.models.channel import Channel as ChannelModel
from infrastructure.database.models.message import Message as MessageModel
from infrastructure.crypto import decrypt_json


def channel_from_orm(row: ChannelModel) -> Channel:
    cfg = decrypt_json(row.config) if row.config else {}
    return Channel(
        id=row.id,
        tenant_id=row.tenant_id,
        type=ChannelType(row.type),
        name=row.name,
        status=ChannelStatus(row.status),
        config=ChannelConfig(**cfg),
        daily_limit=row.daily_limit,
        monthly_limit=row.monthly_limit,
    )


def message_from_orm(row: MessageModel) -> Message:
    return Message(
        id=row.id,
        tenant_id=row.tenant_id,
        channel_id=row.channel_id,
        channel_type=ChannelType(row.channel_type) if row.channel_type else None,
        contact_id=row.contact_id,
        conversation_id=row.conversation_id,
        direction=row.direction,
        content=MessageContent(
            type=ContentType(row.content_type),
            text=row.content_text,
            media_url=row.content_media_url,
            template_name=row.content_template_name,
            template_vars=row.content_template_vars or {},
        ),
        status=MessageStatus(row.status),
        provider_message_id=row.provider_message_id,
        error_code=row.error_code,
        error_message=row.error_message,
        metadata=row.message_metadata or {},
    )
