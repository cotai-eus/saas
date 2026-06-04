import logging
import re
import uuid as uuid_lib

from jose import jwt
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

logger = logging.getLogger(__name__)


def _resolve_tenant_id(keycloak_user_id: str, email: str | None) -> str | None:
    from infrastructure.database.session import SessionFactory
    from infrastructure.database.models.tenant import Tenant as TenantModel
    from infrastructure.database.models.user import User as UserModel

    db = SessionFactory()
    try:
        user = (
            db.query(UserModel)
            .filter(UserModel.keycloak_user_id == keycloak_user_id)
            .first()
        )
        if user:
            return str(user.tenant_id)

        name = f"{email.split('@')[0] if email else 'Default'}'s Workspace"
        slug = (email.split("@")[0] if email else "default").lower()
        slug = re.sub(r"[^a-z0-9-]", "", slug)[:42] or "workspace"
        slug = f"{slug}-{uuid_lib.uuid4().hex[:8]}"

        tenant = TenantModel(name=name, slug=slug)
        db.add(tenant)
        db.flush()

        user = UserModel(
            tenant_id=tenant.id,
            keycloak_user_id=keycloak_user_id,
            email=email or "",
        )
        db.add(user)
        db.commit()

        logger.info("Auto-provisioned tenant=%s user=%s", tenant.id, keycloak_user_id)
        return str(tenant.id)
    except Exception:
        logger.exception("Failed to resolve tenant_id for %s", keycloak_user_id)
        db.rollback()
        return None
    finally:
        db.close()


class ProxyAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        user_id = request.headers.get("X-Auth-Request-User")
        email = request.headers.get("X-Auth-Request-Email")
        groups_raw = request.headers.get("X-Auth-Request-Groups", "")
        groups = [g.strip() for g in groups_raw.split(",") if g.strip()]

        tenant_id = None
        roles = []
        keycloak_user_id = None

        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.removeprefix("Bearer ")
            try:
                claims = jwt.get_unverified_claims(token)
                tenant_id = claims.get("tenant_id")
                roles = claims.get("realm_roles", [])
                keycloak_user_id = claims.get("sub")

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

        if not tenant_id and keycloak_user_id:
            tenant_id = _resolve_tenant_id(keycloak_user_id, email)

        header_tenant_id = request.headers.get("X-Tenant-ID")
        if header_tenant_id:
            tenant_id = header_tenant_id

        request.state.user_id = user_id
        request.state.email = email
        request.state.tenant_id = tenant_id
        request.state.roles = roles
        request.state.groups = groups

        return await call_next(request)
