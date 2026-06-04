import logging

import httpx

from domain.entities.channel import Channel
from domain.entities.message import Message
from domain.value_objects.channel_type import ContentType
from domain.value_objects.message_content import MessageContent
from .base import ChannelProvider, SendResult

logger = logging.getLogger(__name__)

FB_BASE = "https://graph.facebook.com/v19.0"


class FacebookProvider(ChannelProvider):
    def send(self, channel: Channel, message: Message) -> SendResult:
        cfg = channel.config
        url = f"{FB_BASE}/me/messages"
        headers = {"Authorization": f"Bearer {cfg.fb_page_access_token}"}
        payload = {
            "recipient": {"id": message.metadata.get("recipient_id")},
            "message": {"text": message.content.text},
        }

        try:
            with httpx.Client(timeout=30) as c:
                r = c.post(url, json=payload, headers=headers)
            r.raise_for_status()
            data = r.json()
            return SendResult(True, provider_message_id=data.get("message_id"))
        except httpx.RequestError as e:
            logger.error("Facebook request failed: %s", e)
            return SendResult(False, error_code="NETWORK", error_message=str(e))
        except (ValueError, KeyError) as e:
            logger.error("Facebook parse error: %s", e)
            return SendResult(False, error_code="PARSE", error_message=str(e))

    def validate(self, channel: Channel) -> bool:
        cfg = channel.config
        try:
            with httpx.Client(timeout=10) as c:
                r = c.get(
                    f"{FB_BASE}/{cfg.fb_page_id}",
                    headers={"Authorization": f"Bearer {cfg.fb_page_access_token}"},
                )
            return r.status_code == 200
        except httpx.RequestError as e:
            logger.warning("Facebook validate error: %s", e)
            return False

    def parse_inbound(self, payload: dict, headers: dict) -> list[Message]:
        msgs = []
        for entry in payload.get("entry", []):
            for msg_event in entry.get("messaging", []):
                if "message" in msg_event:
                    sender = msg_event.get("sender", {})
                    msg = msg_event["message"]
                    msgs.append(
                        Message(
                            direction="inbound",
                            provider_message_id=msg.get("mid"),
                            content=MessageContent(
                                type=ContentType.TEXT,
                                text=msg.get("text"),
                            ),
                            metadata={
                                "sender_id": sender.get("id"),
                                "page_id": entry.get("id"),
                            },
                        )
                    )
        return msgs

    def parse_status(self, payload: dict) -> list[dict]:
        out = []
        for entry in payload.get("entry", []):
            for msg_event in entry.get("messaging", []):
                if "delivery" in msg_event:
                    for mid in msg_event["delivery"].get("mids", []):
                        out.append(
                            {
                                "provider_message_id": mid,
                                "status": "delivered",
                                "timestamp": msg_event["delivery"].get("watermark"),
                            }
                        )
                if "read" in msg_event:
                    out.append(
                        {
                            "provider_message_id": None,
                            "status": "read",
                            "timestamp": msg_event["read"].get("watermark"),
                        }
                    )
        return out
