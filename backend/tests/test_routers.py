from unittest.mock import MagicMock, patch
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from src.main import app
from infrastructure.database.session import get_db
from infrastructure.queue.producer import get_producer
from middleware import auth as auth_middleware


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def mock_producer():
    p = MagicMock()
    p.publish = MagicMock()
    return p


@pytest.fixture
def auth_header():
    return {"Authorization": "Bearer fake.jwt.token"}


@pytest.fixture
def override_deps(mock_db, mock_producer):
    async def _get_db_override():
        yield mock_db

    app.dependency_overrides[get_db] = _get_db_override
    app.dependency_overrides[get_producer] = lambda: mock_producer

    original_verify = auth_middleware.verify_jwt
    auth_middleware.verify_jwt = lambda token: {
        "sub": "user-123",
        "email": "test@example.com",
        "tenant_id": "22222222-2222-2222-2222-222222222222",
        "realm_roles": [],
        "groups": [],
    }

    yield

    app.dependency_overrides.clear()
    auth_middleware.verify_jwt = original_verify


def make_channel_row(**overrides):
    row = MagicMock()
    row.type = overrides.get("type", "whatsapp_official")
    row.id = overrides.get("id", UUID("11111111-1111-1111-1111-111111111111"))
    row.name = overrides.get("name", "Test")
    row.status = overrides.get("status", "active")
    row.config = overrides.get("config", {"wa_access_token": "tok"})
    row.daily_limit = overrides.get("daily_limit", 1000)
    row.monthly_limit = overrides.get("monthly_limit", 30000)
    row.created_at = overrides.get("created_at", None)
    return row


# ---------------------------------------------------------------------------
# Channels Router
# ---------------------------------------------------------------------------


class TestChannelsRouter:
    def test_create_channel_success(self, client, override_deps, mock_db, auth_header):
        mock_db.query().filter().first.return_value = None
        with patch("application.channels.create_channel.ProviderFactory"), patch(
            "application.channels.create_channel.ChannelModel"
        ):
            resp = client.post(
                "/api/v1/channels/",
                json={
                    "type": "whatsapp_official",
                    "name": "My Channel",
                    "phone_number_id": "123",
                    "access_token": "tok",
                },
                headers=auth_header,
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "My Channel"
        assert data["status"] == "active"

    def test_create_channel_duplicate(self, client, override_deps, mock_db, auth_header):
        existing = MagicMock()
        existing.status = "active"
        mock_db.query().filter().first.return_value = existing

        resp = client.post(
            "/api/v1/channels/",
            json={"type": "whatsapp_official", "name": "Duplicate"},
            headers=auth_header,
        )
        assert resp.status_code == 409

    def test_list_channels_empty(self, client, override_deps, mock_db, auth_header):
        mock_db.query().filter().all.return_value = []

        resp = client.get("/api/v1/channels/", headers=auth_header)
        assert resp.status_code == 200
        assert resp.json() == {"total": 0, "items": []}

    def test_list_channels_with_results(self, client, override_deps, mock_db, auth_header):
        row = make_channel_row()
        mock_db.query().filter().all.return_value = [row]

        resp = client.get("/api/v1/channels/", headers=auth_header)
        assert resp.status_code == 200
        assert resp.json()["total"] == 1

    def test_get_channel(self, client, override_deps, mock_db, auth_header):
        row = make_channel_row()
        mock_db.query().filter().first.return_value = row

        resp = client.get(
            "/api/v1/channels/11111111-1111-1111-1111-111111111111",
            headers=auth_header,
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Test"

    def test_get_channel_not_found(self, client, override_deps, mock_db, auth_header):
        mock_db.query().filter().first.return_value = None

        resp = client.get(
            "/api/v1/channels/11111111-1111-1111-1111-111111111111",
            headers=auth_header,
        )
        assert resp.status_code == 404

    def test_get_channel_invalid_uuid(self, client, override_deps, auth_header):
        resp = client.get(
            "/api/v1/channels/not-a-uuid",
            headers=auth_header,
        )
        assert resp.status_code == 400

    def test_delete_channel(self, client, override_deps, mock_db, auth_header):
        row = make_channel_row()
        mock_db.query().filter().first.return_value = row

        resp = client.delete(
            "/api/v1/channels/11111111-1111-1111-1111-111111111111",
            headers=auth_header,
        )
        assert resp.status_code == 200
        assert resp.json() == {"status": "deleted"}

    def test_delete_channel_not_found(self, client, override_deps, mock_db, auth_header):
        mock_db.query().filter().first.return_value = None

        resp = client.delete(
            "/api/v1/channels/11111111-1111-1111-1111-111111111111",
            headers=auth_header,
        )
        assert resp.status_code == 404

    def test_validate_channel(self, client, override_deps, mock_db, auth_header):
        row = make_channel_row(status="inactive")
        mock_db.query().filter().first.return_value = row

        with patch(
            "infrastructure.providers.whatsapp_cloud.WhatsAppCloudProvider.validate",
            return_value=True,
        ):
            resp = client.post(
                "/api/v1/channels/11111111-1111-1111-1111-111111111111/validate",
                headers=auth_header,
            )
        assert resp.status_code == 200
        assert resp.json() == {"valid": True}

    def test_get_qr_code_not_available(self, client, override_deps, mock_db, auth_header):
        row = make_channel_row(type="whatsapp_unofficial", status="pending_auth")
        mock_db.query().filter().first.return_value = row

        redis = MagicMock()
        redis.get.return_value = None
        with patch(
            "application.channels.connect_qr.get_redis_client",
            return_value=redis,
        ), patch(
            "infrastructure.providers.whatsapp_baileys.WhatsAppBaileysProvider.get_qr",
            return_value=None,
        ):
            resp = client.get(
                "/api/v1/channels/11111111-1111-1111-1111-111111111111/qr",
                headers=auth_header,
            )
        assert resp.status_code == 404

    def test_get_qr_code(self, client, override_deps, mock_db, auth_header):
        row = make_channel_row(type="whatsapp_unofficial", status="pending_auth")
        mock_db.query().filter().first.return_value = row

        redis = MagicMock()
        redis.get.return_value = "qr-data-base64"
        with patch(
            "application.channels.connect_qr.get_redis_client",
            return_value=redis,
        ):
            resp = client.get(
                "/api/v1/channels/11111111-1111-1111-1111-111111111111/qr",
                headers=auth_header,
            )
        assert resp.status_code == 200
        assert resp.json()["qr_base64"] == "qr-data-base64"

    def test_get_qr_channel_not_found(self, client, override_deps, mock_db, auth_header):
        mock_db.query().filter().first.return_value = None

        with patch("application.channels.connect_qr.get_redis_client"):
            resp = client.get(
                "/api/v1/channels/11111111-1111-1111-1111-111111111111/qr",
                headers=auth_header,
            )
        assert resp.status_code == 404

    def test_unauthenticated_returns_401(self, client, override_deps):
        resp = client.get("/api/v1/channels/")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Messages Router
# ---------------------------------------------------------------------------


class TestMessagesRouter:
    def test_send_message(self, client, override_deps, mock_db, mock_producer, auth_header):
        row = make_channel_row()
        mock_db.query().filter().first.return_value = row
        mock_db.query().filter().count.return_value = 0

        with patch("application.messaging.send_message.MessageModel"):
            resp = client.post(
                "/api/v1/messages/send",
                json={
                    "channel_id": "11111111-1111-1111-1111-111111111111",
                    "recipient": "+5511999999999",
                    "content_type": "text",
                    "text": "Hello",
                },
                headers=auth_header,
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data
        assert data["status"] == "queued"

    def test_send_message_inactive_channel(self, client, override_deps, mock_db, auth_header):
        row = make_channel_row(status="inactive")
        mock_db.query().filter().first.return_value = row

        resp = client.post(
            "/api/v1/messages/send",
            json={
                "channel_id": "11111111-1111-1111-1111-111111111111",
                "recipient": "+5511999999999",
                "content_type": "text",
                "text": "Hello",
            },
            headers=auth_header,
        )
        assert resp.status_code == 400

    def test_send_message_invalid_content_type(self, client, override_deps, auth_header):
        resp = client.post(
            "/api/v1/messages/send",
            json={
                "channel_id": "11111111-1111-1111-1111-111111111111",
                "recipient": "+5511999999999",
                "content_type": "invalid_type",
                "text": "Hello",
            },
            headers=auth_header,
        )
        assert resp.status_code == 422

    def test_send_message_invalid_uuid(self, client, override_deps, auth_header):
        resp = client.post(
            "/api/v1/messages/send",
            json={
                "channel_id": "not-a-uuid",
                "recipient": "+5511999999999",
                "content_type": "text",
                "text": "Hello",
            },
            headers=auth_header,
        )
        assert resp.status_code == 422

    def test_list_messages_empty(self, client, override_deps, mock_db, auth_header):
        mock_db.query().filter().count.return_value = 0
        mock_db.query().filter().order_by().offset().limit().all.return_value = []

        resp = client.get("/api/v1/messages/", headers=auth_header)
        assert resp.status_code == 200
        assert resp.json() == {"total": 0, "items": []}

    def test_get_message(self, client, override_deps, mock_db, auth_header):
        row = MagicMock()
        row.id = UUID("33333333-3333-3333-3333-333333333333")
        row.channel_id = UUID("11111111-1111-1111-1111-111111111111")
        row.tenant_id = UUID("22222222-2222-2222-2222-222222222222")
        row.channel_type = "whatsapp_official"
        row.direction = "outbound"
        row.content_type = "text"
        row.content_text = "Hello"
        row.content_media_url = None
        row.content_template_name = None
        row.status = "sent"
        row.provider_message_id = None
        row.error_code = None
        row.error_message = None
        row.created_at = None
        row.sent_at = None
        row.delivered_at = None
        row.read_at = None
        mock_db.query().filter().first.return_value = row

        resp = client.get(
            "/api/v1/messages/33333333-3333-3333-3333-333333333333",
            headers=auth_header,
        )
        assert resp.status_code == 200
        assert resp.json()["content_text"] == "Hello"


# ---------------------------------------------------------------------------
# Contacts Router
# ---------------------------------------------------------------------------


class TestContactsRouter:
    def test_list_contacts_empty(self, client, override_deps, mock_db, auth_header):
        mock_db.query().filter().count.return_value = 0
        mock_db.query().filter().order_by().offset().limit().all.return_value = []

        resp = client.get("/api/v1/contacts/", headers=auth_header)
        assert resp.status_code == 200
        assert resp.json() == {"total": 0, "items": []}

    def test_get_contact(self, client, override_deps, mock_db, auth_header):
        row = MagicMock()
        row.id = UUID("44444444-4444-4444-4444-444444444444")
        row.name = "John"
        row.phone = "+5511999999999"
        row.external_id = "ext123"
        row.channel_id = UUID("11111111-1111-1111-1111-111111111111")
        row.avatar_url = None
        row.contact_metadata = {}
        row.created_at = None
        mock_db.query().filter().first.return_value = row

        resp = client.get(
            "/api/v1/contacts/44444444-4444-4444-4444-444444444444",
            headers=auth_header,
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "John"

    def test_get_contact_not_found(self, client, override_deps, mock_db, auth_header):
        mock_db.query().filter().first.return_value = None

        resp = client.get(
            "/api/v1/contacts/44444444-4444-4444-4444-444444444444",
            headers=auth_header,
        )
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Templates Router
# ---------------------------------------------------------------------------


class TestTemplatesRouter:
    def test_list_templates_returns_501(self, client, override_deps, auth_header):
        resp = client.get("/api/v1/templates/", headers=auth_header)
        assert resp.status_code == 501


# ---------------------------------------------------------------------------
# Webhooks Router
# ---------------------------------------------------------------------------


class TestWebhooksRouter:
    def test_inbound_webhook_invalid_channel_type(self, client, override_deps, auth_header):
        resp = client.post(
            "/webhooks/invalid_type/ch1",
            json={},
            headers=auth_header,
        )
        assert resp.status_code == 400

    def test_inbound_webhook_invalid_channel_id(self, client, override_deps, auth_header):
        resp = client.post(
            "/webhooks/whatsapp_official/not-a-uuid",
            json={},
            headers=auth_header,
        )
        assert resp.status_code == 400

    def test_inbound_webhook_success(self, client, override_deps, mock_db, auth_header):
        mock_db.query().filter().first.return_value = None

        resp = client.post(
            "/webhooks/whatsapp_official/11111111-1111-1111-1111-111111111111",
            json={"entry": [{"changes": [{"value": {"messages": []}}]}]},
            headers=auth_header,
        )
        assert resp.status_code == 200

    def test_verify_meta_webhook_missing_mode(self, client, override_deps, auth_header):
        resp = client.get(
            "/webhooks/whatsapp_official/11111111-1111-1111-1111-111111111111",
            headers=auth_header,
        )
        assert resp.status_code == 400

    def test_verify_meta_webhook_invalid_token(self, client, override_deps, mock_db, auth_header):
        channel = MagicMock()
        channel.type = "whatsapp_official"
        channel.status = "active"
        channel.config = {"wa_verify_token": "expected"}
        channel.daily_limit = 1000
        channel.monthly_limit = 30000
        mock_db.query().filter().first.return_value = channel

        resp = client.get(
            "/webhooks/whatsapp_official"
            "/11111111-1111-1111-1111-111111111111",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "wrong",
                "hub.challenge": "abc123",
            },
            headers=auth_header,
        )
        assert resp.status_code == 403

    def test_verify_meta_webhook_success(self, client, override_deps, mock_db, auth_header):
        channel = MagicMock()
        channel.type = "whatsapp_official"
        channel.status = "active"
        channel.config = {"wa_verify_token": "correct"}
        channel.daily_limit = 1000
        channel.monthly_limit = 30000
        mock_db.query().filter().first.return_value = channel

        resp = client.get(
            "/webhooks/whatsapp_official"
            "/11111111-1111-1111-1111-111111111111",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "correct",
                "hub.challenge": "abc123",
            },
            headers=auth_header,
        )
        assert resp.status_code == 200
        assert resp.text == "abc123"
