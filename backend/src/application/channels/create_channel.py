from uuid import UUID

from sqlalchemy.orm import Session

from domain.entities.channel import Channel, ChannelConfig, ChannelStatus
from domain.value_objects.channel_type import ChannelType
from domain.exceptions.channel_exceptions import ChannelValidationError
from infrastructure.database.models.channel import Channel as ChannelModel
from infrastructure.providers.factory import ProviderFactory


class CreateChannelUseCase:
    def __init__(self, db: Session, tenant_id: UUID):
        self.db = db
        self.tenant_id = tenant_id

    def execute(
        self,
        channel_type: ChannelType,
        name: str,
        config: ChannelConfig,
    ) -> Channel:
        existing = (
            self.db.query(ChannelModel)
            .filter(
                ChannelModel.tenant_id == self.tenant_id,
                ChannelModel.type == channel_type.value,
                ChannelModel.status.in_(["active", "inactive"]),
            )
            .first()
        )
        if existing:
            raise ChannelValidationError(
                f"Tenant already has a {channel_type.value} channel"
            )

        channel = Channel(
            tenant_id=self.tenant_id,
            type=channel_type,
            name=name,
            status=ChannelStatus.PENDING_AUTH,
            config=config,
        )

        provider = ProviderFactory.get(channel_type)
        if provider.validate(channel):
            channel.status = ChannelStatus.ACTIVE
        else:
            channel.status = ChannelStatus.PENDING_AUTH

        row = ChannelModel.from_domain(channel)
        self.db.add(row)
        self.db.flush()

        return channel
