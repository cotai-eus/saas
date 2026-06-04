from domain.exceptions.channel_exceptions import (
    ChannelError,
    ChannelNotFoundError,
    ChannelNotActiveError,
    ChannelValidationError,
)
from domain.exceptions.quota_exceeded import QuotaExceededError
from domain.exceptions.provider_error import ProviderError


def test_channel_error_hierarchy():
    assert issubclass(ChannelNotFoundError, ChannelError)
    assert issubclass(ChannelNotActiveError, ChannelError)
    assert issubclass(ChannelValidationError, ChannelError)


def test_channel_not_found():
    exc = ChannelNotFoundError("Not found")
    assert str(exc) == "Not found"


def test_channel_not_active():
    exc = ChannelNotActiveError("Channel inactive")
    assert str(exc) == "Channel inactive"


def test_quota_exceeded():
    exc = QuotaExceededError("Quota exceeded")
    assert str(exc) == "Quota exceeded"


def test_provider_error():
    exc = ProviderError("API error", provider="whatsapp", status_code=500)
    assert exc.provider == "whatsapp"
    assert exc.status_code == 500
    assert str(exc) == "API error"
