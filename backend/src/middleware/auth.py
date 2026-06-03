import os
import httpx
from jose import jwt, JWTError
from jose.constants import Algorithms
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

JWKS_CACHE = None
JWKS_ISSUER = None


async def fetch_jwks():
    global JWKS_CACHE, JWKS_ISSUER
    auth_host = os.getenv("AUTH_HOST", "auth.local.dev")
    issuer = f"https://{auth_host}/realms/saas"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{issuer}/.well-known/openid-configuration",
                timeout=10,
            )
            resp.raise_for_status()
            oidc_config = resp.json()
            jwks_uri = oidc_config["jwks_uri"]
            jwks_resp = await client.get(jwks_uri, timeout=10)
            jwks_resp.raise_for_status()
            JWKS_CACHE = jwks_resp.json()
            JWKS_ISSUER = issuer
    except Exception as e:
        JWKS_CACHE = None
        JWKS_ISSUER = issuer


def verify_jwt(token: str) -> dict | None:
    if not JWKS_CACHE:
        return None
    try:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        key = None
        for k in JWKS_CACHE.get("keys", []):
            if k.get("kid") == kid:
                key = k
                break
        if not key:
            return None
        claims = jwt.decode(
            token,
            key,
            audience="oauth2-proxy",
            issuer=JWKS_ISSUER,
            algorithms=[Algorithms.RS256],
        )
        return claims
    except JWTError:
        return None


class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.removeprefix("Bearer ")
            claims = verify_jwt(token)
            if claims is None:
                return JSONResponse(
                    status_code=401, content={"detail": "Invalid or expired token"}
                )
            request.state.user_id = claims.get("sub")
            request.state.email = claims.get("email")
            request.state.tenant_id = claims.get("tenant_id")
            request.state.roles = claims.get("realm_roles", [])
            request.state.groups = claims.get("groups", [])
        else:
            request.state.user_id = None
            request.state.email = None
            request.state.tenant_id = None
            request.state.roles = []
            request.state.groups = []

        return await call_next(request)