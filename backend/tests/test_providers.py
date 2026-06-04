from domain.entities.channel import Channel, ChannelConfig
from domain.entities.message import Message
from domain.value_objects.message_content import MessageContent
from domain.value_objects.channel_type import ChannelType, ContentType
from infrastructure.providers.whatsapp_cloud import WhatsAppCloudProvider
from infrastructure.providers.telegram import TelegramProvider
from infrastructure.providers.factory import ProviderFactory


def make_wa_channel():
    return Channel(
        type=ChannelType.WHATSAPP_OFFICIAL,
        config=ChannelConfig(
            wa_phone_number_id="123456",
            wa_access_token="fake-token",
            wa_verify_token="verify123",
        ),
    )


def make_tg_channel():
    return Channel(
        type=ChannelType.TELEGRAM,
        config=ChannelConfig(tg_bot_token="123:ABC"),
    )


def test_whatsapp_cloud_parse_status():
    provider = WhatsAppCloudProvider()
    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "statuses": [
                                {
                                    "id": "wamid.abc",
                                    "status": "delivered",
                                    "timestamp": "1700000000",
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    result = provider.parse_status(payload)
    assert len(result) == 1
    assert result[0]["provider_message_id"] == "wamid.abc"
    assert result[0]["status"] == "delivered"


def test_whatsapp_cloud_parse_inbound():
    provider = WhatsAppCloudProvider()
    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "id": "wamid.inbound",
                                    "from": "5511999999999",
                                    "text": {"body": "Hello!"},
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    msgs = provider.parse_inbound(payload, {})
    assert len(msgs) == 1
    assert msgs[0].provider_message_id == "wamid.inbound"
    assert msgs[0].metadata["sender_phone"] == "5511999999999"
    assert msgs[0].content.text == "Hello!"


def test_whatsapp_cloud_build_text_payload():
    provider = WhatsAppCloudProvider()
    msg = Message(
        content=MessageContent(type=ContentType.TEXT, text="Hi there"),
        metadata={"recipient_phone": "5511999999999"},
    )
    payload = provider._build_payload(msg)
    assert payload["messaging_product"] == "whatsapp"
    assert payload["to"] == "5511999999999"
    assert payload["type"] == "text"
    assert payload["text"]["body"] == "Hi there"


def test_telegram_parse_inbound():
    provider = TelegramProvider()
    payload = {
        "message": {
            "message_id": 42,
            "text": "Hello from Telegram",
            "chat": {"id": 12345},
        }
    }
    msgs = provider.parse_inbound(payload, {})
    assert len(msgs) == 1
    assert msgs[0].provider_message_id == "42"
    assert msgs[0].metadata["chat_id"] == 12345
    assert msgs[0].content.text == "Hello from Telegram"


def test_telegram_parse_inbound_no_message():
    provider = TelegramProvider()
    assert provider.parse_inbound({}, {}) == []


def test_telegram_parse_status_empty():
    provider = TelegramProvider()
    assert provider.parse_status({}) == []


def test_provider_factory_get():
    provider = ProviderFactory.get(ChannelType.WHATSAPP_OFFICIAL)
    from infrastructure.providers.whatsapp_cloud import WhatsAppCloudProvider
    assert isinstance(provider, WhatsAppCloudProvider)


def test_provider_factory_unknown():
    import pytest

    class FakeType:
        value = "unknown"

    with pytest.raises(ValueError):
        ProviderFactory.get(FakeType())
