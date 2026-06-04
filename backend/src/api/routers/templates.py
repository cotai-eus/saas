from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from api.routers.auth import get_tenant_id

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("/")
def list_templates(
    tenant_id: str = Depends(get_tenant_id),
):
    return JSONResponse(
        status_code=501,
        content={"detail": "Template management not yet implemented"},
    )
