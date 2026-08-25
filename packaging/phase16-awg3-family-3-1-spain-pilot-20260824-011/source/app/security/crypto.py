import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken


class SecretBoxError(ValueError):
    pass


class SecretBox:
    def __init__(self, fernet: Fernet) -> None:
        self._fernet = fernet

    @classmethod
    def from_app_secret(
        cls,
        secret: str,
        *,
        allow_weak_secret: bool = False,
    ) -> "SecretBox":
        if not allow_weak_secret and _is_weak_secret(secret):
            raise SecretBoxError(
                "App secret must be at least 32 characters with sufficient variety"
            )
        digest = hashlib.sha256(secret.encode("utf-8")).digest()
        key = base64.urlsafe_b64encode(digest)
        return cls(Fernet(key))

    def encrypt_text(self, value: str) -> str:
        token = self._fernet.encrypt(value.encode("utf-8")).decode("ascii")
        return f"v1:{token}"

    def decrypt_text(self, value: str) -> str:
        try:
            version, token = value.split(":", 1)
        except ValueError as exc:
            raise SecretBoxError("Malformed secret token") from exc

        if version != "v1":
            raise SecretBoxError(f"Unsupported secret version: {version}")

        try:
            return self._fernet.decrypt(token.encode("ascii")).decode("utf-8")
        except (InvalidToken, UnicodeEncodeError, UnicodeDecodeError) as exc:
            raise SecretBoxError("Malformed or invalid secret token") from exc


def _is_weak_secret(secret: str) -> bool:
    return len(secret) < 32 or len(set(secret)) < 8
