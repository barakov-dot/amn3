from __future__ import annotations

import hashlib
import hmac
import secrets
from collections.abc import MutableMapping


PASSWORD_HASH_ERROR = "WEB_ADMIN_PASSWORD_HASH must be a valid pbkdf2_sha256 hash"


def create_password_hash(password: str, *, salt: str | None = None) -> str:
    actual_salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        actual_salt.encode("utf-8"),
        200_000,
    ).hex()
    return f"pbkdf2_sha256${actual_salt}${digest}"


def check_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, salt, expected = password_hash.split("$", maxsplit=2)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    actual = create_password_hash(password, salt=salt).split("$", maxsplit=2)[2]
    return hmac.compare_digest(actual, expected)


def generate_csrf_token(session: MutableMapping[str, object]) -> str:
    token = secrets.token_urlsafe(32)
    session["csrf_token"] = token
    return token


def verify_csrf_token(session: MutableMapping[str, object], token: str | None) -> bool:
    expected = session.get("csrf_token")
    return (
        isinstance(expected, str)
        and isinstance(token, str)
        and hmac.compare_digest(expected, token)
    )


def _is_valid_password_hash(password_hash: str) -> bool:
    parts = password_hash.split("$")
    if len(parts) != 3:
        return False
    algorithm, salt, digest = parts
    if algorithm != "pbkdf2_sha256" or not salt.strip():
        return False
    if len(digest) != 64:
        return False
    try:
        bytes.fromhex(digest)
    except ValueError:
        return False
    return True


def require_web_admin_config(*, password_hash: str, session_secret: str) -> None:
    stripped_password_hash = password_hash.strip()
    stripped_session_secret = session_secret.strip()
    if not stripped_password_hash or stripped_password_hash.startswith("replace-with-"):
        raise ValueError("WEB_ADMIN_PASSWORD_HASH must be set before starting web admin")
    if not _is_valid_password_hash(stripped_password_hash):
        raise ValueError(PASSWORD_HASH_ERROR)
    if (
        not stripped_session_secret
        or stripped_session_secret.startswith("replace-with-")
        or len(stripped_session_secret) < 32
    ):
        raise ValueError("WEB_ADMIN_SESSION_SECRET must be at least 32 characters")
