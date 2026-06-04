from uuid import UUID

from domain.value_objects.channel_type import ChannelType, MessageStatus, ContentType
from domain.value_objects.message_content import MessageContent
from domain.value_objects.phone_number import PhoneNumber
from domain.entities.channel import Channel, ChannelConfig, ChannelStatus
from domain.entities.message import Message


def test_channel_type_values():
    assert ChannelType.WHATSAPP_OFFICIAL.value == "whatsapp_official"
    assert ChannelType.WHATSAPP_UNOFFICIAL.value == "whatsapp_unofficial"
    assert ChannelType.FACEBOOK_MESSENGER.value == "facebook_messenger"
    assert ChannelType.INSTAGRAM_CHAT.value == "instagram_chat"
    assert ChannelType.TELEGRAM.value == "telegram"


def test_message_status_values():
    assert MessageStatus.PENDING.value == "pending"
    assert MessageStatus.QUEUED.value == "queued"
    assert MessageStatus.SENT.value == "sent"
    assert MessageStatus.DELIVERED.value == "delivered"
    assert MessageStatus.READ.value == "read"
    assert MessageStatus.FAILED.value == "failed"
    assert MessageStatus.RECEIVED.value == "received"


def test_content_type_values():
    assert ContentType.TEXT.value == "text"
    assert ContentType.TEMPLATE.value == "template"


def test_message_content_defaults():
    content = MessageContent(type=ContentType.TEXT, text="Hello")
    assert content.type == ContentType.TEXT
    assert content.text == "Hello"
    assert content.media_url is None
    assert content.template_name is None
    assert content.template_vars == {}


def test_channel_creation():
    channel = Channel(
        name="Test WA",
        type=ChannelType.WHATSAPP_OFFICIAL,
        status=ChannelStatus.ACTIVE,
    )
    assert isinstance(channel.id, UUID)
    assert channel.name == "Test WA"
    assert channel.status == ChannelStatus.ACTIVE
    assert channel.daily_limit == 1000
    assert channel.monthly_limit == 30000


def test_channel_config_defaults():
    config = ChannelConfig()
    assert config.wa_phone_number_id is None
    assert config.wa_access_token is None
    assert config.tg_bot_token is None


def test_message_creation():
    content = MessageContent(type=ContentType.TEXT, text="Test message")
    msg = Message(content=content, direction="outbound")
    assert isinstance(msg.id, UUID)
    assert msg.direction == "outbound"
    assert msg.status == MessageStatus.PENDING
    assert msg.content.text == "Test message"


def test_phone_number_valid():
    phone = PhoneNumber.validate("+5511999999999")
    assert phone == "+5511999999999"


def test_phone_number_invalid():
    import pytest

    with pytest.raises(ValueError):
        PhoneNumber.validate("123")


def test_channel_entity_status_enum():
    assert ChannelStatus.ACTIVE.value == "active"
    assert ChannelStatus.INACTIVE.value == "inactive"
    assert ChannelStatus.PENDING_AUTH.value == "pending_auth"
    assert ChannelStatus.ERROR.value == "error"
