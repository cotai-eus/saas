from uuid import UUID

from fastapi import APIRouter, Depends, Request, HTTPException, Query
from pydantic import BaseModel

from infrastructure.database.session import get_db
from infrastructure.database.models.contact import Contact as ContactModel
from api.routers.auth import require_tenant

router = APIRouter(prefix="/contacts", tags=["contacts"])


class ContactResponse(BaseModel):
    id: str
    name: str
    phone: str | None
    external_id: str | None
    channel_id: str
    created_at: str | None


@router.get("")
def list_contacts(
    request: Request,
    channel_id: str = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db=Depends(get_db),
):
    tenant_id = require_tenant(request)

    q = db.query(ContactModel).filter(ContactModel.tenant_id == tenant_id)
    if channel_id:
        q = q.filter(ContactModel.channel_id == channel_id)

    rows = q.order_by(ContactModel.created_at.desc()).offset(offset).limit(limit).all()

    return [
        {
            "id": str(r.id),
            "name": r.name,
            "phone": r.phone,
            "external_id": r.external_id,
            "channel_id": str(r.channel_id),
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]


@router.get("/{contact_id}")
def get_contact(contact_id: str, request: Request, db=Depends(get_db)):
    tenant_id = require_tenant(request)

    try:
        uid = UUID(contact_id)
    except ValueError:
        raise HTTPException(400, "Invalid contact_id format")

    row = (
        db.query(ContactModel)
        .filter(
            ContactModel.id == uid,
            ContactModel.tenant_id == tenant_id,
        )
        .first()
    )
    if not row:
        raise HTTPException(404, "Contact not found")

    return {
        "id": str(row.id),
        "name": row.name,
        "phone": row.phone,
        "external_id": row.external_id,
        "avatar_url": row.avatar_url,
        "channel_id": str(row.channel_id),
        "metadata": row.contact_metadata,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }
