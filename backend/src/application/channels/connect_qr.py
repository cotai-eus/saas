from uuid import UUID

from sqlalchemy.orm import Session

from domain.entities.channel import ChannelStatus
from domain.exceptions.channel_exceptions import ChannelNotFoundError
from domain.value_objects.channel_type import ChannelType
from infrastructure.database.models.channel import Channel as ChannelModel
from infrastructure.database.mappers import channel_from_orm
from infrastructure.cache.redis_client import get_redis_client
from infrastructure.providers.whatsapp_baileys import WhatsAppBaileysProvider


class ConnectQRUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.redis = get_redis_client()

    def get_qr(self, channel_id: UUID, tenant_id: UUID) -> str | None:
        row = (
            self.db.query(ChannelModel)
            .filter(
                ChannelModel.id == channel_id,
                ChannelModel.tenant_id == tenant_id,
                ChannelModel.type == ChannelType.WHATSAPP_UNOFFICIAL.value,
            )
            .first()
        )
        if not row:
            raise ChannelNotFoundError(f"Channel {channel_id} not found")

        cached = self.redis.get(f"qr:{channel_id}")
        if cached:
            return cached

        channel = channel_from_orm(row)
        provider = WhatsAppBaileysProvider()
        qr = provider.get_qr(channel)
        if qr:
            self.redis.setex(f"qr:{channel_id}", 120, qr)
        return qr

    def store_qr(self, channel_id: str, qr_base64: str) -> None:
        self.redis.setex(f"qr:{channel_id}", 120, qr_base64)

    def confirm_connected(self, channel_id: UUID) -> None:
        self.db.query(ChannelModel).filter(
            ChannelModel.id == channel_id
        ).update(
            {"status": ChannelStatus.ACTIVE.value}
        )
        self.db.commit()
        self.redis.delete(f"qr:{channel_id}")
