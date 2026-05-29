from __future__ import annotations

import hashlib
import hmac
import secrets
from collections.abc import MutableMapping


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


def require_web_admin_config(*, password_hash: str, session_secret: str) -> None:
    if not password_hash or password_hash.startswith("replace-with-"):
        raise ValueError("WEB_ADMIN_PASSWORD_HASH must be set before starting web admin")
    if (
        not session_secret
        or session_secret.startswith("replace-with-")
        or len(session_secret) < 32
    ):
        raise ValueError("WEB_ADMIN_SESSION_SECRET must be at least 32 characters")
