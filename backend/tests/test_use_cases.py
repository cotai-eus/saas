from unittest.mock import MagicMock, patch
from uuid import UUID

import pytest

from domain.entities.channel import Channel, ChannelConfig, ChannelStatus
from domain.entities.message import Message, MessageContent
from domain.value_objects.channel_type import ChannelType, ContentType, MessageStatus
from domain.exceptions.channel_exceptions import (
    ChannelNotFoundError,
    ChannelNotActiveError,
    ChannelValidationError,
)
from domain.exceptions.quota_exceeded import QuotaExceededError
from application.messaging.send_message import SendMessageUseCase
from application.messaging.receive_message import ReceiveMessageUseCase
from application.messaging.update_status import UpdateStatusUseCase
from application.channels.create_channel import CreateChannelUseCase
from application.channels.connect_qr import ConnectQRUseCase
from application.channels.validate_channel import ValidateChannelUseCase
from application.billing.quota_service import QuotaService


def make_active_channel(type: ChannelType = ChannelType.WHATSAPP_OFFICIAL) -> Channel:
    return Channel(
        id=UUID("11111111-1111-1111-1111-111111111111"),
        tenant_id=UUID("22222222-2222-2222-2222-222222222222"),
        type=type,
        name="Test Channel",
        status=ChannelStatus.ACTIVE,
        config=ChannelConfig(wa_access_token="tok"),
    )


def make_text_message() -> Message:
    return Message(
        content=MessageContent(type=ContentType.TEXT, text="Hello"),
        metadata={"recipient_phone": "5511999999999"},
    )


# ---------------------------------------------------------------------------
# SendMessageUseCase
# ---------------------------------------------------------------------------


class TestSendMessageUseCase:
    def test_successful_send(self):
        db, queue, quota = MagicMock(), MagicMock(), MagicMock()
        quota.check_and_increment.return_value = True

        channel = make_active_channel()
        message = make_text_message()

        uc = SendMessageUseCase(db=db, queue=queue, quota=quota)

        with patch(
            "application.messaging.send_message.MessageModel",
        ) as mock_model:
            mock_model.return_value = MagicMock()
            result = uc.execute(channel, message)

        assert result.status == MessageStatus.QUEUED
        assert result.tenant_id == channel.tenant_id
        assert result.channel_id == channel.id
        assert result.channel_type == channel.type
        queue.publish.assert_called_once()
        db.add.assert_called_once()
        db.flush.assert_called_once()

    def test_inactive_channel_raises_error(self):
        db, queue, quota = MagicMock(), MagicMock(), MagicMock()
        channel = make_active_channel()
        channel.status = ChannelStatus.INACTIVE
        message = make_text_message()

        uc = SendMessageUseCase(db=db, queue=queue, quota=quota)
        with pytest.raises(ChannelNotActiveError):
            uc.execute(channel, message)
        queue.publish.assert_not_called()

    def test_quota_exceeded_raises_error(self):
        db, queue, quota = MagicMock(), MagicMock(), MagicMock()
        quota.check_and_increment.return_value = False

        channel = make_active_channel()
        message = make_text_message()

        uc = SendMessageUseCase(db=db, queue=queue, quota=quota)
        with pytest.raises(QuotaExceededError):
            uc.execute(channel, message)
        queue.publish.assert_not_called()


# ---------------------------------------------------------------------------
# ReceiveMessageUseCase
# ---------------------------------------------------------------------------


class TestReceiveMessageUseCase:
    def test_duplicate_event_skipped(self):
        db = MagicMock()
        db.query().filter().first.return_value = MagicMock()
        uc = ReceiveMessageUseCase(db=db)
        with patch("application.messaging.receive_message.WebhookEvent"):
            uc.execute("whatsapp_official", "ch1", {"key": "val"}, {})
        db.add.assert_not_called()

    def test_normal_inbound_parsed(self):
        db = MagicMock()
        db.query().filter().first.side_effect = [None, None]

        with patch(
            "application.messaging.receive_message.WebhookEvent",
        ), patch(
            "application.messaging.receive_message.MessageModel",
        ), patch(
            "infrastructure.providers.whatsapp_cloud.WhatsAppCloudProvider.parse_inbound"
        ) as mock_parse:
            mock_parse.return_value = [
                Message(
                    content=MessageContent(type=ContentType.TEXT, text="Hi"),
                    metadata={},
                )
            ]
            with patch(
                "infrastructure.providers.whatsapp_cloud.WhatsAppCloudProvider.parse_status"
            ) as mock_status:
                mock_status.return_value = []

                uc = ReceiveMessageUseCase(db=db)
                uc.execute(
                    "whatsapp_official",
                    "ch1",
                    {"entry": [{"changes": [{"value": {"messages": []}}]}]},
                    {},
                )
                db.add.assert_called()
                db.commit.assert_called_once()

    def test_baileys_qr_event(self):
        db = MagicMock()
        db.query().filter().first.return_value = None

        uc = ReceiveMessageUseCase(db=db)
        with patch("application.messaging.receive_message.WebhookEvent"), patch(
            "application.channels.connect_qr.get_redis_client",
        ):
            uc.execute(
                "whatsapp_unofficial",
                "ch1",
                {"event": "qr", "data": {"qr_base64": "base64data"}},
                {},
            )
        db.add.assert_called_once()

    def test_baileys_connected_event(self):
        db = MagicMock()
        db.query().filter().first.return_value = None

        uc = ReceiveMessageUseCase(db=db)
        with patch("application.messaging.receive_message.WebhookEvent"), patch(
            "application.channels.connect_qr.get_redis_client",
        ):
            uc.execute(
                "whatsapp_unofficial", "ch1", {"event": "connected"}, {}
            )
        db.commit.assert_called_once()


# ---------------------------------------------------------------------------
# UpdateStatusUseCase
# ---------------------------------------------------------------------------


class TestUpdateStatusUseCase:
    def test_update_to_sent(self):
        db = MagicMock()
        row = MagicMock()
        db.query().filter().first.return_value = row

        uc = UpdateStatusUseCase(db=db)
        uc.execute(
            message_id="33333333-3333-3333-3333-333333333333",
            status="sent",
            provider_message_id="ext123",
        )
        assert row.status == "sent"
        assert row.provider_message_id == "ext123"
        assert row.sent_at is not None
        db.commit.assert_called_once()

    def test_update_unknown_message_does_not_raise(self):
        db = MagicMock()
        db.query().filter().first.return_value = None

        uc = UpdateStatusUseCase(db=db)
        uc.execute(message_id="nonexistent", status="delivered")
        db.commit.assert_not_called()


# ---------------------------------------------------------------------------
# CreateChannelUseCase
# ---------------------------------------------------------------------------


class TestCreateChannelUseCase:
    def test_create_new_channel_returns_channel(self):
        db = MagicMock()
        db.query().filter().first.return_value = None
        tenant_id = UUID("22222222-2222-2222-2222-222222222222")

        with patch(
            "infrastructure.providers.whatsapp_cloud.WhatsAppCloudProvider.validate",
            return_value=True,
        ), patch("application.channels.create_channel.ChannelModel"):
            uc = CreateChannelUseCase(db=db, tenant_id=tenant_id)
            result = uc.execute(
                ChannelType.WHATSAPP_OFFICIAL,
                "My Channel",
                ChannelConfig(wa_access_token="tok"),
            )
            assert result.status == ChannelStatus.ACTIVE
            assert result.tenant_id == tenant_id

    def test_create_duplicate_channel_raises_error(self):
        db = MagicMock()
        existing = MagicMock()
        existing.status = "active"
        db.query().filter().first.return_value = existing
        tenant_id = UUID("22222222-2222-2222-2222-222222222222")

        uc = CreateChannelUseCase(db=db, tenant_id=tenant_id)
        with pytest.raises(ChannelValidationError) as exc:
            uc.execute(
                ChannelType.WHATSAPP_OFFICIAL,
                "Duplicate",
                ChannelConfig(wa_access_token="tok"),
            )
        assert "already has" in str(exc.value).lower()

    def test_validation_failure_sets_pending_auth(self):
        db = MagicMock()
        db.query().filter().first.return_value = None
        tenant_id = UUID("22222222-2222-2222-2222-222222222222")

        with patch(
            "infrastructure.providers.whatsapp_cloud.WhatsAppCloudProvider.validate",
            return_value=False,
        ), patch("application.channels.create_channel.ChannelModel"):
            uc = CreateChannelUseCase(db=db, tenant_id=tenant_id)
            result = uc.execute(
                ChannelType.WHATSAPP_OFFICIAL,
                "Pending",
                ChannelConfig(wa_access_token="invalid"),
            )
            assert result.status == ChannelStatus.PENDING_AUTH


# ---------------------------------------------------------------------------
# ConnectQRUseCase
# ---------------------------------------------------------------------------


class TestConnectQRUseCase:
    def _make_row(self):
        row = MagicMock()
        row.type = "whatsapp_unofficial"
        row.id = UUID("11111111-1111-1111-1111-111111111111")
        row.config = {"baileys_service_url": "http://baileys:3000"}
        row.daily_limit = 1000
        row.monthly_limit = 30000
        row.status = "pending_auth"
        return row

    def test_get_qr_returns_cached_value(self):
        db = MagicMock()
        db.query().filter().first.return_value = self._make_row()

        redis = MagicMock()
        redis.get.return_value = "cached-qr-data"

        with patch(
            "application.channels.connect_qr.get_redis_client",
            return_value=redis,
        ):
            uc = ConnectQRUseCase(db=db)
            qr = uc.get_qr(
                UUID("11111111-1111-1111-1111-111111111111"),
                UUID("22222222-2222-2222-2222-222222222222"),
            )
            assert qr == "cached-qr-data"
            redis.get.assert_called_once_with("qr:11111111-1111-1111-1111-111111111111")

    def test_get_qr_fetches_from_provider_when_cache_empty(self):
        db = MagicMock()
        db.query().filter().first.return_value = self._make_row()

        redis = MagicMock()
        redis.get.return_value = None

        with patch(
            "application.channels.connect_qr.get_redis_client", return_value=redis
        ), patch(
            "infrastructure.providers.whatsapp_baileys.WhatsAppBaileysProvider.get_qr",
            return_value="provider-qr-data",
        ):
            uc = ConnectQRUseCase(db=db)
            qr = uc.get_qr(
                UUID("11111111-1111-1111-1111-111111111111"),
                UUID("22222222-2222-2222-2222-222222222222"),
            )
            assert qr == "provider-qr-data"
            redis.setex.assert_called_once()

    def test_get_qr_raises_not_found(self):
        db = MagicMock()
        db.query().filter().first.return_value = None

        with patch("application.channels.connect_qr.get_redis_client"):
            uc = ConnectQRUseCase(db=db)
            with pytest.raises(ChannelNotFoundError):
                uc.get_qr(
                    UUID("11111111-1111-1111-1111-111111111111"),
                    UUID("22222222-2222-2222-2222-222222222222"),
                )

    def test_store_qr_saves_to_redis(self):
        db = MagicMock()
        redis = MagicMock()
        with patch(
            "application.channels.connect_qr.get_redis_client",
            return_value=redis,
        ):
            uc = ConnectQRUseCase(db=db)
            uc.store_qr("ch1", "base64qr")
            redis.setex.assert_called_once_with("qr:ch1", 120, "base64qr")

    def test_confirm_connected_updates_channel(self):
        db = MagicMock()
        channel_id = UUID("11111111-1111-1111-1111-111111111111")
        redis = MagicMock()
        with patch(
            "application.channels.connect_qr.get_redis_client",
            return_value=redis,
        ):
            uc = ConnectQRUseCase(db=db)
            uc.confirm_connected(channel_id)
            redis.delete.assert_called_once_with(f"qr:{channel_id}")


# ---------------------------------------------------------------------------
# ValidateChannelUseCase
# ---------------------------------------------------------------------------


class TestValidateChannelUseCase:
    def test_validate_success(self):
        db = MagicMock()
        row = MagicMock()
        row.type = "whatsapp_official"
        row.status = "inactive"
        row.config = {"wa_access_token": "tok"}
        row.daily_limit = 1000
        row.monthly_limit = 30000
        db.query().filter().first.return_value = row

        with patch(
            "infrastructure.providers.whatsapp_cloud.WhatsAppCloudProvider.validate",
            return_value=True,
        ):
            uc = ValidateChannelUseCase(db=db)
            assert uc.execute(UUID("11111111-1111-1111-1111-111111111111"))
            assert row.status == "active"
            db.commit.assert_called_once()

    def test_validate_failure_sets_error_status(self):
        db = MagicMock()
        row = MagicMock()
        row.type = "whatsapp_official"
        row.status = "inactive"
        row.config = {"wa_access_token": "bad"}
        row.daily_limit = 1000
        row.monthly_limit = 30000
        db.query().filter().first.return_value = row

        with patch(
            "infrastructure.providers.whatsapp_cloud.WhatsAppCloudProvider.validate",
            return_value=False,
        ):
            uc = ValidateChannelUseCase(db=db)
            assert not uc.execute(UUID("11111111-1111-1111-1111-111111111111"))
            assert row.status == "error"

    def test_validate_not_found_raises_error(self):
        db = MagicMock()
        db.query().filter().first.return_value = None

        uc = ValidateChannelUseCase(db=db)
        with pytest.raises(ChannelNotFoundError):
            uc.execute(UUID("11111111-1111-1111-1111-111111111111"))


# ---------------------------------------------------------------------------
# QuotaService
# ---------------------------------------------------------------------------


class TestQuotaService:
    def test_within_limits_returns_true(self):
        db = MagicMock()
        subscription = MagicMock()
        subscription.plan = "professional"
        
        db.query.return_value.filter.return_value = db.query.return_value
        db.query.return_value.first.return_value = subscription
        db.query.return_value.scalar.return_value = 0

        with patch("application.billing.quota_service.get_redis_client", side_effect=Exception("Redis down")):
            uc = QuotaService(db=db, tenant_id=UUID("22222222-2222-2222-2222-222222222222"))
            assert uc.check_and_increment(UUID("11111111-1111-1111-1111-111111111111"))

    def test_monthly_limit_exceeded_returns_false(self):
        db = MagicMock()
        subscription = MagicMock()
        subscription.plan = "starter"
        
        db.query.return_value.filter.return_value = db.query.return_value
        db.query.return_value.first.return_value = subscription
        db.query.return_value.scalar.return_value = 9999

        with patch("application.billing.quota_service.get_redis_client", side_effect=Exception("Redis down")):
            uc = QuotaService(db=db, tenant_id=UUID("22222222-2222-2222-2222-222222222222"))
            assert not uc.check_and_increment(UUID("11111111-1111-1111-1111-111111111111"))

    def test_no_subscription_returns_false(self):
        db = MagicMock()
        db.query().filter().first.return_value = None

        uc = QuotaService(db=db, tenant_id=UUID("22222222-2222-2222-2222-222222222222"))
        assert not uc.check_and_increment(UUID("11111111-1111-1111-1111-111111111111"))

    def test_redis_quota_success(self):
        db = MagicMock()
        subscription = MagicMock()
        subscription.plan = "starter"
        db.query().filter().first.return_value = subscription

        redis = MagicMock()
        redis.eval.return_value = 1 # Success in Lua script

        with patch("application.billing.quota_service.get_redis_client", return_value=redis):
            uc = QuotaService(db=db, tenant_id=UUID("22222222-2222-2222-2222-222222222222"))
            assert uc.check_and_increment(UUID("11111111-1111-1111-1111-111111111111"))
            redis.eval.assert_called_once()

    def test_redis_quota_exceeded(self):
        db = MagicMock()
        subscription = MagicMock()
        subscription.plan = "starter"
        db.query().filter().first.return_value = subscription

        redis = MagicMock()
        redis.eval.return_value = 0 # Limit reached in Lua script

        with patch("application.billing.quota_service.get_redis_client", return_value=redis):
            uc = QuotaService(db=db, tenant_id=UUID("22222222-2222-2222-2222-222222222222"))
            assert not uc.check_and_increment(UUID("11111111-1111-1111-1111-111111111111"))
