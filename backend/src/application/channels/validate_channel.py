from uuid import UUID

from sqlalchemy.orm import Session

from domain.entities.channel import Channel, ChannelStatus
from domain.exceptions.channel_exceptions import ChannelNotFoundError
from infrastructure.database.models.channel import Channel as ChannelModel
from infrastructure.database.mappers import channel_from_orm
from infrastructure.providers.factory import ProviderFactory


class ValidateChannelUseCase:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, channel_id: UUID) -> bool:
        row = (
            self.db.query(ChannelModel)
            .filter(ChannelModel.id == channel_id)
            .first()
        )
        if not row:
            raise ChannelNotFoundError(f"Channel {channel_id} not found")

        channel = channel_from_orm(row)
        provider = ProviderFactory.get(channel.type)
        valid = provider.validate(channel)

        new_status = ChannelStatus.ACTIVE if valid else ChannelStatus.ERROR
        row.status = new_status.value
        self.db.commit()

        return valid
