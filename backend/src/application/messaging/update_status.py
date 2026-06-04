from datetime import datetime

from sqlalchemy.orm import Session

from infrastructure.database.models.message import Message as MessageModel


class UpdateStatusUseCase:
    def __init__(self, db: Session):
        self.db = db

    def execute(
        self,
        message_id: str,
        status: str,
        provider_message_id: str = None,
        error_code: str = None,
        error_message: str = None,
    ) -> None:
        row = (
            self.db.query(MessageModel)
            .filter(MessageModel.id == message_id)
            .first()
        )
        if not row:
            return

        row.status = status
        if provider_message_id:
            row.provider_message_id = provider_message_id
        if error_code:
            row.error_code = error_code
        if error_message:
            row.error_message = error_message

        now = datetime.utcnow()
        if status == "sent":
            row.sent_at = now
        elif status == "delivered":
            row.delivered_at = now
        elif status == "read":
            row.read_at = now

        self.db.commit()
