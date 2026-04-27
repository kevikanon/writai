import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend

from app.core.config import settings


def get_encryption_key() -> bytes:
    if not settings.ENCRYPTION_KEY:
        raise ValueError("ENCRYPTION_KEY not configured")
    return settings.ENCRYPTION_KEY.encode() if len(settings.ENCRYPTION_KEY) == 44 else settings.ENCRYPTION_KEY.encode()


def encrypt_api_key(api_key: str) -> str:
    key = get_encryption_key()
    f = Fernet(key)
    return f.encrypt(api_key.encode()).decode()


def decrypt_api_key(encrypted_api_key: str) -> str:
    key = get_encryption_key()
    f = Fernet(key)
    return f.decrypt(encrypted_api_key.encode()).decode()