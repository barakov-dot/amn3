import os

from cryptography.fernet import InvalidToken

from app.security.crypto import SecretBox, SecretBoxError


def secret_box_from_env() -> SecretBox:
    secret = os.environ.get("APP_SECRET_KEY")
    if not secret:
        raise RuntimeError("APP_SECRET_KEY is required for backup operations")
    try:
        return SecretBox.from_app_secret(secret)
    except SecretBoxError as exc:
        raise RuntimeError("APP_SECRET_KEY is not strong enough for backup operations") from exc


def encrypt_archive_bytes(archive_bytes: bytes) -> bytes:
    box = secret_box_from_env()
    return box._fernet.encrypt(archive_bytes)


def decrypt_archive_bytes(encrypted_bytes: bytes) -> bytes:
    box = secret_box_from_env()
    try:
        return box._fernet.decrypt(encrypted_bytes)
    except InvalidToken as exc:
        raise ValueError("Invalid encrypted backup archive") from exc
