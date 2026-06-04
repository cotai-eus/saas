from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from api.routers.auth import require_tenant

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("/")
def list_templates(
    request: Request,
    db=Depends(lambda: None),
):
    require_tenant(request)
    return JSONResponse(
        status_code=501,
        content={"detail": "Template management not yet implemented"},
    )
