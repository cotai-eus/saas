from fastapi import APIRouter, Depends, Request, HTTPException

router = APIRouter()


def require_tenant(request: Request) -> str:
    tenant_id = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(401, "Authentication required")
    return tenant_id


def get_tenant_id(request: Request) -> str:
    tenant_id = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(401, "Authentication required")
    return tenant_id


@router.get("/me")
async def me(request: Request):
    return {
        "user_id": getattr(request.state, "user_id", None),
        "email": getattr(request.state, "email", None),
        "tenant_id": getattr(request.state, "tenant_id", None),
        "roles": getattr(request.state, "roles", []),
        "groups": getattr(request.state, "groups", []),
    }
