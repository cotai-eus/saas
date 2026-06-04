import base64
import hashlib
import json
import logging

from infrastructure.settings import settings

logger = logging.getLogger(__name__)

try:
    from cryptography.fernet import Fernet

    _CRYPTO_AVAILABLE = True
except ImportError:
    _CRYPTO_AVAILABLE = False
    Fernet = None


def _derive_key(raw: str) -> bytes:
    raw_bytes = raw.encode("utf-8")
    key = hashlib.sha256(raw_bytes).digest()
    return base64.urlsafe_b64encode(key)


def get_fernet():
    if not _CRYPTO_AVAILABLE:
        return None
    raw = settings.channel_config_encryption_key
    if not raw:
        logger.warning("channel_config_encryption_key not set, config stored in plaintext")
        return None
    try:
        return Fernet(_derive_key(raw))
    except Exception as e:
        logger.warning("Failed to initialize Fernet: %s", e)
        return None


def encrypt_json(data: dict) -> str:
    f = get_fernet()
    if f is None:
        return json.dumps(data)
    plain = json.dumps(data).encode("utf-8")
    return f.encrypt(plain).decode("utf-8")


def decrypt_json(raw: str | dict) -> dict:
    if isinstance(raw, dict):
        return raw
    f = get_fernet()
    if f is None:
        try:
            return json.loads(raw)
        except (ValueError, TypeError):
            return {}
    try:
        decrypted = f.decrypt(raw.encode("utf-8"))
        return json.loads(decrypted)
    except Exception:
        try:
            return json.loads(raw)
        except (ValueError, TypeError):
            return {}
