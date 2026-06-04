import hashlib
import hmac
import logging
from uuid import UUID

from fastapi import APIRouter, Request, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse

from domain.value_objects.channel_type import ChannelType
from infrastructure.database.session import get_db
from infrastructure.database.mappers import channel_from_orm
from infrastructure.database.models.channel import Channel as ChannelModel
from application.messaging.receive_message import ReceiveMessageUseCase
from infrastructure.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/{channel_type}/{channel_id}")
async def inbound_webhook(
    channel_type: str,
    channel_id: str,
    request: Request,
    db=Depends(get_db),
):
    try:
        ChannelType(channel_type)
    except ValueError:
        raise HTTPException(400, f"Invalid channel_type: {channel_type}")

    try:
        UUID(channel_id)
    except ValueError:
        raise HTTPException(400, f"Invalid channel_id: {channel_id}")

    body = await request.body()

    channel = (
        db.query(ChannelModel)
        .filter(ChannelModel.id == channel_id)
        .first()
    )

    if channel:
        domain_channel = channel_from_orm(channel)
        cfg = domain_channel.config
        signature = request.headers.get("X-Hub-Signature-256", "")
        if signature and cfg.wa_access_token:
            expected = hmac.new(
                cfg.wa_access_token.encode(),
                body,
                hashlib.sha256,
            ).hexdigest()
            expected_sig = f"sha256={expected}"
            if not hmac.compare_digest(signature, expected_sig):
                logger.warning("Invalid webhook signature for channel %s", channel_id)
                raise HTTPException(401, "Invalid signature")

    payload = await request.json()

    uc = ReceiveMessageUseCase(db=db)
    uc.execute(channel_type, channel_id, payload, dict(request.headers))
    return {"status": "ok"}


@router.get("/whatsapp_official/{channel_id}")
def verify_meta_webhook(
    channel_id: str,
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    db=Depends(get_db),
):
    if hub_mode != "subscribe":
        raise HTTPException(400, "Invalid mode")

    try:
        UUID(channel_id)
    except ValueError:
        raise HTTPException(400, "Invalid channel_id")

    channel = (
        db.query(ChannelModel)
        .filter(ChannelModel.id == channel_id)
        .first()
    )
    if not channel:
        raise HTTPException(404, "Channel not found")

    domain_channel = channel_from_orm(channel)
    expected_token = domain_channel.config.wa_verify_token
    if not expected_token or hub_verify_token != expected_token:
        raise HTTPException(403, "Invalid verify token")

    return PlainTextResponse(hub_challenge)
