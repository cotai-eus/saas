import logging

import httpx

from domain.entities.channel import Channel
from domain.entities.message import Message
from domain.value_objects.channel_type import ContentType
from domain.value_objects.message_content import MessageContent
from .base import ChannelProvider, SendResult

logger = logging.getLogger(__name__)


class WhatsAppBaileysProvider(ChannelProvider):
    def _headers(self, cfg) -> dict:
        return {"X-API-Key": cfg.baileys_api_key}

    def send(self, channel: Channel, message: Message) -> SendResult:
        cfg = channel.config
        url = f"{cfg.baileys_service_url}/sessions/{cfg.baileys_session_id}/messages"
        try:
            with httpx.Client(headers=self._headers(cfg), timeout=30) as c:
                r = c.post(
                    url,
                    json={
                        "to": message.metadata.get("recipient_phone"),
                        "type": message.content.type.value,
                        "text": message.content.text,
                        "mediaUrl": message.content.media_url,
                    },
                )
            data = r.json()
            if r.status_code in (200, 201):
                return SendResult(True, provider_message_id=data.get("messageId"))
            return SendResult(
                False,
                error_code=str(r.status_code),
                error_message=data.get("error", str(data)),
            )
        except httpx.RequestError as e:
            logger.error("Baileys request failed: %s", e)
            return SendResult(False, error_code="NETWORK", error_message=str(e))
        except (ValueError, KeyError) as e:
            logger.error("Baileys parse error: %s", e)
            return SendResult(False, error_code="PARSE", error_message=str(e))

    def get_qr(self, channel: Channel) -> str | None:
        cfg = channel.config
        try:
            with httpx.Client(headers=self._headers(cfg), timeout=10) as c:
                r = c.get(
                    f"{cfg.baileys_service_url}/sessions/{cfg.baileys_session_id}/qr"
                )
            if r.status_code == 200:
                return r.json().get("qr_base64")
        except httpx.RequestError as e:
            logger.warning("Baileys QR fetch error: %s", e)
        return None

    def validate(self, channel: Channel) -> bool:
        cfg = channel.config
        try:
            with httpx.Client(headers=self._headers(cfg), timeout=10) as c:
                r = c.get(
                    f"{cfg.baileys_service_url}/sessions/{cfg.baileys_session_id}/status"
                )
            return r.status_code == 200 and r.json().get("status") == "connected"
        except httpx.RequestError as e:
            logger.warning("Baileys validate error: %s", e)
            return False

    def parse_inbound(self, payload: dict, headers: dict) -> list[Message]:
        if payload.get("event") != "message":
            return []
        raw = payload["data"]
        return [
            Message(
                direction="inbound",
                provider_message_id=raw.get("key", {}).get("id"),
                content=MessageContent(
                    type=ContentType.TEXT,
                    text=raw.get("message", {}).get("conversation"),
                ),
                metadata={
                    "sender_phone": raw.get("key", {})
                    .get("remoteJid", "")
                    .split("@")[0]
                },
            )
        ]

    def parse_status(self, payload: dict) -> list[dict]:
        if payload.get("event") != "message-status":
            return []
        d = payload["data"]
        return [
            {
                "provider_message_id": d["id"],
                "status": d["status"],
                "timestamp": d["timestamp"],
            }
        ]
