import logging
from jose import jwt
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

logger = logging.getLogger(__name__)


class ProxyAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract user information from headers provided by Traefik/OAuth2-Proxy.
    Assumes the request has already been authenticated by the proxy.
    """
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Extract basic user info from Traefik/OAuth2-Proxy headers
        user_id = request.headers.get("X-Auth-Request-User")
        email = request.headers.get("X-Auth-Request-Email")
        groups_raw = request.headers.get("X-Auth-Request-Groups", "")
        groups = [g.strip() for g in groups_raw.split(",") if g.strip()]
        
        # If headers are missing, try to extract from JWT without verification 
        # (since it was already verified by the proxy)
        tenant_id = None
        roles = []
        
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.removeprefix("Bearer ")
            try:
                # Get unverified claims since signature was already checked by Traefik
                claims = jwt.get_unverified_claims(token)
                tenant_id = claims.get("tenant_id")
                roles = claims.get("realm_roles", [])
                
                # Fallback for user_id/email if headers are missing
                if not user_id:
                    user_id = claims.get("sub")
                if not email:
                    email = claims.get("email")
                if not groups:
                    groups = claims.get("groups", [])
            except Exception as e:
                logger.warning("Failed to parse unverified JWT claims: %s", e)
                return JSONResponse(
                    status_code=401, content={"detail": "Invalid or expired token"}
                )

        # Allow X-Tenant-ID header to override for development or specific cases
        header_tenant_id = request.headers.get("X-Tenant-ID")
        if header_tenant_id:
            tenant_id = header_tenant_id

        request.state.user_id = user_id
        request.state.email = email
        request.state.tenant_id = tenant_id
        request.state.roles = roles
        request.state.groups = groups

        return await call_next(request)
