from uuid import UUID

from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import BaseModel, field_validator

from domain.value_objects.channel_type import ChannelType
from domain.entities.channel import ChannelConfig
from domain.exceptions.channel_exceptions import ChannelNotFoundError, ChannelValidationError
from infrastructure.database.session import get_db
from infrastructure.database.mappers import channel_from_orm
from infrastructure.database.models.channel import Channel as ChannelModel
from application.channels.create_channel import CreateChannelUseCase
from application.channels.connect_qr import ConnectQRUseCase
from application.channels.validate_channel import ValidateChannelUseCase
from api.routers.auth import require_tenant

router = APIRouter(prefix="/channels", tags=["channels"])


class CreateChannelRequest(BaseModel):
    type: ChannelType
    name: str
    phone_number_id: str | None = None
    access_token: str | None = None
    verify_token: str | None = None


class ChannelResponse(BaseModel):
    id: str
    type: str
    name: str
    status: str
    created_at: str | None


@router.post("/", response_model=ChannelResponse)
def create_channel(
    body: CreateChannelRequest,
    request: Request,
    db=Depends(get_db),
):
    tenant_id = require_tenant(request)

    config = ChannelConfig(
        wa_phone_number_id=body.phone_number_id,
        wa_access_token=body.access_token,
        wa_verify_token=body.verify_token,
    )

    uc = CreateChannelUseCase(db=db, tenant_id=tenant_id)
    try:
        channel = uc.execute(body.type, body.name, config)
    except ChannelValidationError as e:
        raise HTTPException(409, str(e))

    return ChannelResponse(
        id=str(channel.id),
        type=channel.type.value,
        name=channel.name,
        status=channel.status.value,
        created_at=channel.created_at.isoformat() if channel.created_at else None,
    )


@router.get("/")
def list_channels(request: Request, db=Depends(get_db)):
    tenant_id = require_tenant(request)

    rows = (
        db.query(ChannelModel)
        .filter(ChannelModel.tenant_id == tenant_id)
        .all()
    )
    return {
        "total": len(rows),
        "items": [
            ChannelResponse(
                id=str(r.id),
                type=r.type,
                name=r.name,
                status=r.status,
                created_at=r.created_at.isoformat() if r.created_at else None,
            )
            for r in rows
        ],
    }


@router.get("/{channel_id}")
def get_channel(channel_id: str, request: Request, db=Depends(get_db)):
    tenant_id = require_tenant(request)

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

    return {
        "id": str(row.id),
        "type": row.type,
        "name": row.name,
        "status": row.status,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


@router.delete("/{channel_id}")
def delete_channel(channel_id: str, request: Request, db=Depends(get_db)):
    tenant_id = require_tenant(request)

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

    db.delete(row)
    db.commit()
    return {"status": "deleted"}


@router.post("/{channel_id}/validate")
def validate_channel(
    channel_id: str, request: Request, db=Depends(get_db)
):
    tenant_id = require_tenant(request)

    try:
        uid = UUID(channel_id)
    except ValueError:
        raise HTTPException(400, "Invalid channel_id format")

    uc = ValidateChannelUseCase(db=db)
    try:
        valid = uc.execute(uid)
    except ChannelNotFoundError:
        raise HTTPException(404, "Channel not found")

    return {"valid": valid}


@router.get("/{channel_id}/qr")
def get_qr_code(channel_id: str, request: Request, db=Depends(get_db)):
    tenant_id = require_tenant(request)

    try:
        uid = UUID(channel_id)
    except ValueError:
        raise HTTPException(400, "Invalid channel_id format")

    uc = ConnectQRUseCase(db=db)
    try:
        qr = uc.get_qr(uid, tenant_id)
    except ChannelNotFoundError:
        raise HTTPException(404, "Channel not found")

    if not qr:
        raise HTTPException(404, "QR code not available")

    return {"qr_base64": qr}
