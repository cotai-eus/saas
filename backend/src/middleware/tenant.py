from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        tenant_id = getattr(request.state, "tenant_id", None)

        if tenant_id:
            request.state.tenant_id = tenant_id
        else:
            request.state.tenant_id = None

        return await call_next(request)
