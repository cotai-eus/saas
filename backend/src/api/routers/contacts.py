from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from infrastructure.database.session import get_db
from infrastructure.database.models.contact import Contact as ContactModel
from api.routers.auth import get_tenant_id

router = APIRouter(prefix="/contacts", tags=["contacts"])


class ContactResponse(BaseModel):
    id: str
    name: str
    phone: str | None
    external_id: str | None
    channel_id: str
    created_at: str | None


class CreateContactRequest(BaseModel):
    name: str
    phone: str | None = None
    external_id: str | None = None
    channel_id: str


@router.get("/")
def list_contacts(
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    channel_id: str = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
):
    q = db.query(ContactModel).filter(ContactModel.tenant_id == tenant_id)
    if channel_id:
        q = q.filter(ContactModel.channel_id == channel_id)

    sort_map = {
        "created_at": ContactModel.created_at,
        "name": ContactModel.name,
        "phone": ContactModel.phone,
    }
    sort_col = sort_map.get(sort_by, ContactModel.created_at)
    order_fn = sort_col.desc if sort_order == "desc" else sort_col.asc

    total = q.count()
    rows = q.order_by(order_fn()).offset(offset).limit(limit).all()

    return {
        "total": total,
        "items": [
            {
                "id": str(r.id),
                "name": r.name,
                "phone": r.phone,
                "external_id": r.external_id,
                "channel_id": str(r.channel_id),
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ],
    }


@router.post("/", response_model=ContactResponse, status_code=201)
def create_contact(
    body: CreateContactRequest,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    try:
        channel_uid = UUID(body.channel_id)
    except ValueError:
        raise HTTPException(400, "Invalid channel_id format")

    from infrastructure.database.models.channel import Channel as ChannelModel

    channel = (
        db.query(ChannelModel)
        .filter(
            ChannelModel.id == channel_uid,
            ChannelModel.tenant_id == tenant_id,
        )
        .first()
    )
    if not channel:
        raise HTTPException(404, "Channel not found")

    row = ContactModel(
        tenant_id=tenant_id,
        channel_id=channel_uid,
        name=body.name,
        phone=body.phone,
        external_id=body.external_id,
    )
    db.add(row)
    db.flush()

    return ContactResponse(
        id=str(row.id),
        name=row.name,
        phone=row.phone,
        external_id=row.external_id,
        channel_id=str(row.channel_id),
        created_at=row.created_at.isoformat() if row.created_at else None,
    )


@router.get("/{contact_id}")
def get_contact(
    contact_id: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
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
