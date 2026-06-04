import logging

import httpx

from domain.entities.channel import Channel
from domain.entities.message import Message
from domain.value_objects.channel_type import ContentType
from domain.value_objects.message_content import MessageContent
from .base import ChannelProvider, SendResult

logger = logging.getLogger(__name__)

WA_BASE = "https://graph.facebook.com/v19.0"


class WhatsAppCloudProvider(ChannelProvider):
    def send(self, channel: Channel, message: Message) -> SendResult:
        cfg = channel.config
        url = f"{WA_BASE}/{cfg.wa_phone_number_id}/messages"
        headers = {"Authorization": f"Bearer {cfg.wa_access_token}"}
        payload = self._build_payload(message)

        try:
            with httpx.Client(timeout=30) as c:
                r = c.post(url, json=payload, headers=headers)
            r.raise_for_status()
            data = r.json()
            provider_id = data.get("messages", [{}])[0].get("id")
            return SendResult(True, provider_message_id=provider_id)
        except httpx.RequestError as e:
            logger.error("WhatsApp Cloud request failed: %s", e)
            return SendResult(False, error_code="NETWORK", error_message=str(e))
        except (KeyError, IndexError, ValueError) as e:
            logger.error("WhatsApp Cloud parse error: %s", e)
            return SendResult(
                False,
                error_code="PARSE",
                error_message=f"Unexpected response format: {e}",
            )

    def _build_payload(self, msg: Message) -> dict:
        to = msg.metadata.get("recipient_phone")
        base = {"messaging_product": "whatsapp", "to": to}
        ct = msg.content.type

        match ct:
            case ContentType.TEXT:
                base["type"] = "text"
                base["text"] = {"body": msg.content.text}
            case ContentType.TEMPLATE:
                base["type"] = "template"
                base["template"] = {
                    "name": msg.content.template_name,
                    "language": {
                        "code": msg.metadata.get("language", "pt_BR")
                    },
                    "components": [
                        {
                            "type": "body",
                            "parameters": [
                                {"type": "text", "text": v}
                                for v in msg.content.template_vars.values()
                            ],
                        }
                    ],
                }
            case ContentType.IMAGE:
                base["type"] = "image"
                base["image"] = {"link": msg.content.media_url}
        return base

    def validate(self, channel: Channel) -> bool:
        cfg = channel.config
        try:
            with httpx.Client(timeout=10) as c:
                r = c.get(
                    f"{WA_BASE}/{cfg.wa_phone_number_id}",
                    headers={"Authorization": f"Bearer {cfg.wa_access_token}"},
                )
            return r.status_code == 200
        except httpx.RequestError as e:
            logger.warning("WhatsApp Cloud validate error: %s", e)
            return False

    def parse_inbound(self, payload: dict, headers: dict) -> list[Message]:
        msgs = []
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                for raw in change.get("value", {}).get("messages", []):
                    msgs.append(
                        Message(
                            direction="inbound",
                            provider_message_id=raw["id"],
                            content=MessageContent(
                                type=ContentType.TEXT,
                                text=raw.get("text", {}).get("body"),
                            ),
                            metadata={"sender_phone": raw["from"]},
                        )
                    )
        return msgs

    def parse_status(self, payload: dict) -> list[dict]:
        out = []
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                for s in change.get("value", {}).get("statuses", []):
                    out.append(
                        {
                            "provider_message_id": s["id"],
                            "status": s["status"],
                            "timestamp": s["timestamp"],
                        }
                    )
        return out
