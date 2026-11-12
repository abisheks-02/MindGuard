from cryptography.fernet import Fernet
import base64
from app.config import get_settings
import sqlalchemy.types as types

settings = get_settings()

# Ensure the key is exactly 32 url-safe base64-encoded bytes
try:
    key = settings.ENCRYPTION_KEY.encode('utf-8')
    if len(base64.urlsafe_b64decode(key)) != 32:
        raise ValueError("Invalid key length")
    cipher_suite = Fernet(key)
except Exception:
    # Fallback to a deterministic dev key if env is broken
    cipher_suite = Fernet(b'M3ZtX1JhYWxMZmRtTnpXNjRzRzVzX3VZZzN6VXlfcTg=')

class EncryptedString(types.TypeDecorator):
    """
    SQLAlchemy custom type that automatically encrypts strings on the way in,
    and decrypts them on the way out using Fernet AES-128-CBC.
    """
    impl = types.String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        return cipher_suite.encrypt(value.encode('utf-8')).decode('utf-8')

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        try:
            return cipher_suite.decrypt(value.encode('utf-8')).decode('utf-8')
        except Exception:
            # If decryption fails (e.g., migrating old unencrypted data), return raw
            return value
