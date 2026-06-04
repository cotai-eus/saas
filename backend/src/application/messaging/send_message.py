from uuid import UUID

from sqlalchemy.orm import Session

from domain.entities.message import Message, MessageStatus
from domain.entities.channel import Channel, ChannelStatus
from domain.exceptions.channel_exceptions import ChannelNotActiveError
from domain.exceptions.quota_exceeded import QuotaExceededError
from infrastructure.database.models.channel import Channel as ChannelModel
from infrastructure.database.models.message import Message as MessageModel
from infrastructure.queue.producer import QueueProducer
from application.billing.quota_service import QuotaService


class SendMessageUseCase:
    def __init__(self, db: Session, queue: QueueProducer, quota: QuotaService):
        self.db = db
        self.queue = queue
        self.quota = quota

    def execute(self, channel: Channel, message: Message) -> Message:
        if channel.status != ChannelStatus.ACTIVE:
            raise ChannelNotActiveError(f"Canal {channel.id} inativo")

        if not self.quota.check_and_increment(channel.id):
            raise QuotaExceededError("Cota do tenant excedida")

        message.status = MessageStatus.QUEUED
        message.tenant_id = channel.tenant_id
        message.channel_id = channel.id
        message.channel_type = channel.type
        self._persist(message)

        self.queue.publish(
            "messages.outbound",
            {
                "message_id": str(message.id),
                "channel_id": str(channel.id),
                "tenant_id": str(channel.tenant_id),
            },
        )
        return message

    def _persist(self, message: Message) -> None:
        row = MessageModel.from_domain(message)
        self.db.add(row)
        self.db.flush()
