from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, field_validator

from domain.entities.message import Message, MessageContent
from domain.entities.channel import Channel
from domain.value_objects.channel_type import ContentType
from domain.exceptions.channel_exceptions import ChannelNotActiveError
from domain.exceptions.quota_exceeded import QuotaExceededError
from infrastructure.database.session import get_db
from infrastructure.database.mappers import channel_from_orm
from infrastructure.database.models.message import Message as MessageModel
from infrastructure.database.models.channel import Channel as ChannelModel
from infrastructure.queue.producer import QueueProducer, get_producer
from application.messaging.send_message import SendMessageUseCase
from application.billing.quota_service import QuotaService
from api.routers.auth import get_tenant_id

router = APIRouter(prefix="/messages", tags=["messages"])


class SendRequest(BaseModel):
    channel_id: str
    recipient: str
    content_type: str = "text"
    text: str | None = None
    media_url: str | None = None
    template_name: str | None = None
    template_vars: dict = {}

    @field_validator("content_type")
    @classmethod
    def validate_content_type(cls, v: str) -> str:
        try:
            ContentType(v)
        except ValueError:
            valid = [e.value for e in ContentType]
            raise ValueError(
                f"Invalid content_type '{v}'. Must be one of: {valid}"
            )
        return v

    @field_validator("channel_id")
    @classmethod
    def validate_channel_id(cls, v: str) -> str:
        try:
            UUID(v)
        except ValueError:
            raise ValueError(f"Invalid channel_id '{v}' - must be a valid UUID")
        return v


class MessageResponse(BaseModel):
    id: str
    status: str


@router.post("/", response_model=MessageResponse, status_code=201)
def send_message(
    body: SendRequest,
    db=Depends(get_db),
    queue: QueueProducer = Depends(get_producer),
    tenant_id: str = Depends(get_tenant_id),
):
    channel = _get_channel(db, body.channel_id, tenant_id)

    msg = Message(
        content=MessageContent(
            type=ContentType(body.content_type),
            text=body.text,
            media_url=body.media_url,
            template_name=body.template_name,
            template_vars=body.template_vars,
        ),
        metadata={
            "recipient_phone": body.recipient,
            "chat_id": body.recipient,
        },
    )

    uc = SendMessageUseCase(
        db=db,
        queue=queue,
        quota=QuotaService(db, tenant_id),
    )
    try:
        result = uc.execute(channel, msg)
    except ChannelNotActiveError as e:
        raise HTTPException(400, str(e))
    except QuotaExceededError as e:
        raise HTTPException(429, str(e))

    return MessageResponse(id=str(result.id), status=result.status.value)


@router.get("/")
def list_messages(
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    channel_id: str = Query(None),
    status: str = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
):
    q = db.query(MessageModel).filter(MessageModel.tenant_id == tenant_id)
    if channel_id:
        q = q.filter(MessageModel.channel_id == channel_id)
    if status:
        q = q.filter(MessageModel.status == status)

    sort_map = {
        "created_at": MessageModel.created_at,
        "status": MessageModel.status,
        "content_type": MessageModel.content_type,
    }
    sort_col = sort_map.get(sort_by, MessageModel.created_at)
    order_fn = sort_col.desc if sort_order == "desc" else sort_col.asc

    total = q.count()
    rows = q.order_by(order_fn()).offset(offset).limit(limit).all()

    return {
        "total": total,
        "items": [
            {
                "id": str(r.id),
                "channel_id": str(r.channel_id),
                "direction": r.direction,
                "content_type": r.content_type,
                "content_text": r.content_text,
                "status": r.status,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ],
    }


@router.get("/{message_id}")
def get_message(
    message_id: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    try:
        uid = UUID(message_id)
    except ValueError:
        raise HTTPException(400, "Invalid message_id format")

    row = (
        db.query(MessageModel)
        .filter(
            MessageModel.id == uid,
            MessageModel.tenant_id == tenant_id,
        )
        .first()
    )
    if not row:
        raise HTTPException(404, "Message not found")

    return {
        "id": str(row.id),
        "channel_id": str(row.channel_id),
        "channel_type": row.channel_type,
        "direction": row.direction,
        "content_type": row.content_type,
        "content_text": row.content_text,
        "content_media_url": row.content_media_url,
        "content_template_name": row.content_template_name,
        "status": row.status,
        "provider_message_id": row.provider_message_id,
        "error_code": row.error_code,
        "error_message": row.error_message,
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "sent_at": row.sent_at.isoformat() if row.sent_at else None,
        "delivered_at": row.delivered_at.isoformat() if row.delivered_at else None,
        "read_at": row.read_at.isoformat() if row.read_at else None,
    }


def _get_channel(db, channel_id: str, tenant_id: str) -> Channel:
    try:
        uid = UUID(channel_id)
    except ValueError:
        raise HTTPException(400, "Invalid channel_id format")

    row = (
        db.query(ChannelModel)
        .filter(
            ChannelModel.id == uid,
            ChannelModel.tenant_id == tenant_id,
        )
        .first()
    )
    if not row:
        raise HTTPException(404, "Channel not found")

    return channel_from_orm(row)
