import hashlib
import json
import logging
from datetime import datetime

from sqlalchemy.orm import Session

from domain.value_objects.channel_type import ChannelType
from domain.entities.message import Message, MessageStatus
from infrastructure.providers.factory import ProviderFactory
from infrastructure.database.models.message import Message as MessageModel
from infrastructure.database.models.webhook_event import WebhookEvent
from application.channels.connect_qr import ConnectQRUseCase

logger = logging.getLogger(__name__)


class ReceiveMessageUseCase:
    def __init__(self, db: Session):
        self.db = db

    def execute(
        self, channel_type: str, channel_id: str, payload: dict, headers: dict
    ) -> None:
        event_hash = self._hash(payload)
        if self._already_processed(event_hash):
            logger.info("Duplicate webhook event skipped: %s", event_hash)
            return
        self._mark_processed(event_hash, channel_id)

        ct = ChannelType(channel_type)

        if ct == ChannelType.WHATSAPP_UNOFFICIAL:
            self._handle_baileys(channel_id, payload)
            return

        provider = ProviderFactory.get(ct)

        messages = provider.parse_inbound(payload, headers)
        for msg in messages:
            msg.channel_id = channel_id
            self._save_inbound(msg)

        statuses = provider.parse_status(payload)
        for s in statuses:
            self._update_status(s)

        self.db.commit()

    def _handle_baileys(self, channel_id: str, payload: dict) -> None:
        event = payload.get("event")

        if event == "qr":
            qr = payload.get("data", {}).get("qr_base64")
            if qr:
                ConnectQRUseCase(self.db).store_qr(channel_id, qr)
                self.db.commit()
                logger.info("QR stored for channel %s", channel_id)
            return

        if event == "message":
            from infrastructure.providers.whatsapp_baileys import WhatsAppBaileysProvider
            provider = WhatsAppBaileysProvider()
            messages = provider.parse_inbound(payload, {})
            for msg in messages:
                msg.channel_id = channel_id
                self._save_inbound(msg)
            self.db.commit()
            return

        if event == "connected":
            ConnectQRUseCase(self.db).confirm_connected(channel_id)
            logger.info("Channel %s connected", channel_id)
            return

        logger.info("Unhandled Baileys event: %s", event)

    def _hash(self, payload: dict) -> str:
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True).encode()
        ).hexdigest()

    def _already_processed(self, event_hash: str) -> bool:
        return (
            self.db.query(WebhookEvent)
            .filter(WebhookEvent.event_hash == event_hash)
            .first()
            is not None
        )

    def _mark_processed(self, event_hash: str, channel_id: str) -> None:
        self.db.add(
            WebhookEvent(event_hash=event_hash, channel_id=channel_id)
        )
        self.db.flush()

    def _save_inbound(self, msg: Message) -> None:
        msg.status = MessageStatus.RECEIVED
        row = MessageModel.from_domain(msg, direction="inbound")
        self.db.add(row)

    def _update_status(self, status_data: dict) -> None:
        provider_id = status_data.get("provider_message_id")
        new_status = status_data.get("status")
        timestamp = status_data.get("timestamp")

        if not provider_id or not new_status:
            return

        row = (
            self.db.query(MessageModel)
            .filter(
                MessageModel.provider_message_id == provider_id
            )
            .first()
        )
        if not row:
            logger.warning("Status for unknown message: %s", provider_id)
            return

        status_map = {
            "sent": "sent",
            "delivered": "delivered",
            "read": "read",
            "failed": "failed",
        }
        mapped = status_map.get(new_status)
        if mapped:
            row.status = mapped
            if timestamp:
                try:
                    ts = datetime.fromtimestamp(int(timestamp))
                    if mapped == "sent":
                        row.sent_at = ts
                    elif mapped == "delivered":
                        row.delivered_at = ts
                    elif mapped == "read":
                        row.read_at = ts
                except (ValueError, OSError) as e:
                    logger.warning("Invalid timestamp %s: %s", timestamp, e)
