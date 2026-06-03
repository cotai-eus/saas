from unittest.mock import patch, MagicMock
import asyncio

from middleware import auth


def test_jwks_fetch_success():
    mock_oidc = {
        "jwks_uri": "https://auth.local.dev/realms/saas/protocol/openid-connect/certs",
        "issuer": "https://auth.local.dev/realms/saas",
    }
    mock_jwks = {"keys": []}

    async def mock_get(url, **kwargs):
        resp = MagicMock()
        if "openid-configuration" in url:
            resp.json.return_value = mock_oidc
        else:
            resp.json.return_value = mock_jwks
        return resp

    auth.JWKS_CACHE = None
    auth.JWKS_ISSUER = None

    with patch("httpx.AsyncClient.get", side_effect=mock_get):
        asyncio.run(auth.fetch_jwks())

    assert auth.JWKS_CACHE == mock_jwks
    assert auth.JWKS_ISSUER == "https://auth.local.dev/realms/saas"


def test_verify_jwt_no_jwks():
    auth.JWKS_CACHE = None
    auth.JWKS_ISSUER = None
    assert auth.verify_jwt("some.token.here") is None


def test_verify_jwt_malformed():
    auth.JWKS_CACHE = {"keys": []}
    auth.JWKS_ISSUER = "https://auth.local.dev/realms/saas"
    assert auth.verify_jwt("not-a-jwt") is None
