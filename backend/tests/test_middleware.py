from unittest.mock import MagicMock
import pytest
from starlette.requests import Request
from middleware.auth import ProxyAuthMiddleware


@pytest.mark.asyncio
async def test_proxy_auth_middleware_with_headers():
    middleware = ProxyAuthMiddleware(app=MagicMock())
    
    # Mock request with Traefik headers
    scope = {
        "type": "http",
        "headers": [
            (b"x-auth-request-user", b"user123"),
            (b"x-auth-request-email", b"user@example.com"),
            (b"x-auth-request-groups", b"admin,user"),
            (b"x-tenant-id", b"tenant456"),
        ],
    }
    request = Request(scope=scope)
    
    async def call_next(request):
        return MagicMock()

    await middleware.dispatch(request, call_next)
    
    assert request.state.user_id == "user123"
    assert request.state.email == "user@example.com"
    assert request.state.groups == ["admin", "user"]
    assert request.state.tenant_id == "tenant456"


@pytest.mark.asyncio
async def test_proxy_auth_middleware_with_jwt_fallback():
    middleware = ProxyAuthMiddleware(app=MagicMock())
    
    # Fake JWT with claims (unverified)
    from jose import jwt
    claims = {
        "sub": "user789",
        "email": "jwt@example.com",
        "tenant_id": "tenant789",
        "realm_roles": ["manager"],
        "groups": ["group1"]
    }
    token = jwt.encode(claims, "secret", algorithm="HS256")
    
    scope = {
        "type": "http",
        "headers": [
            (b"authorization", f"Bearer {token}".encode()),
        ],
    }
    request = Request(scope=scope)
    
    async def call_next(request):
        return MagicMock()

    await middleware.dispatch(request, call_next)
    
    assert request.state.user_id == "user789"
    assert request.state.email == "jwt@example.com"
    assert request.state.tenant_id == "tenant789"
    assert request.state.roles == ["manager"]
    assert request.state.groups == ["group1"]
