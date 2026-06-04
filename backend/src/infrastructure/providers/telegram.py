import logging

import httpx

from domain.entities.channel import Channel
from domain.entities.message import Message
from domain.value_objects.channel_type import ContentType
from domain.value_objects.message_content import MessageContent
from .base import ChannelProvider, SendResult

logger = logging.getLogger(__name__)

TG = "https://api.telegram.org/bot"


class TelegramProvider(ChannelProvider):
    def send(self, channel: Channel, message: Message) -> SendResult:
        token = channel.config.tg_bot_token
        chat_id = message.metadata.get("chat_id")
        ct = message.content.type

        method_map = {
            ContentType.TEXT: (
                "sendMessage",
                {"text": message.content.text, "parse_mode": "HTML"},
            ),
            ContentType.IMAGE: ("sendPhoto", {"photo": message.content.media_url}),
            ContentType.AUDIO: ("sendVoice", {"voice": message.content.media_url}),
            ContentType.DOCUMENT: (
                "sendDocument",
                {"document": message.content.media_url},
            ),
        }

        method, extra = method_map.get(
            ct, ("sendMessage", {"text": message.content.text or ""})
        )

        try:
            with httpx.Client(timeout=30) as c:
                r = c.post(
                    f"{TG}{token}/{method}",
                    json={"chat_id": chat_id, **extra},
                )
            data = r.json()
            if data.get("ok"):
                return SendResult(
                    True,
                    provider_message_id=str(data["result"]["message_id"]),
                )
            return SendResult(
                False,
                error_code=str(data.get("error_code")),
                error_message=data.get("description"),
            )
        except httpx.RequestError as e:
            logger.error("Telegram request failed: %s", e)
            return SendResult(False, error_code="NETWORK", error_message=str(e))
        except (ValueError, KeyError) as e:
            logger.error("Telegram parse error: %s", e)
            return SendResult(False, error_code="PARSE", error_message=str(e))

    def validate(self, channel: Channel) -> bool:
        try:
            with httpx.Client(timeout=10) as c:
                r = c.get(f"{TG}{channel.config.tg_bot_token}/getMe")
            return r.json().get("ok", False)
        except httpx.RequestError as e:
            logger.warning("Telegram validate error: %s", e)
            return False

    def parse_inbound(self, payload: dict, headers: dict) -> list[Message]:
        msg = payload.get("message") or payload.get("channel_post")
        if not msg:
            return []
        return [
            Message(
                direction="inbound",
                provider_message_id=str(msg["message_id"]),
                content=MessageContent(
                    type=ContentType.TEXT,
                    text=msg.get("text") or msg.get("caption"),
                ),
                metadata={"chat_id": msg["chat"]["id"]},
            )
        ]

    def parse_status(self, payload: dict) -> list[dict]:
        return []
