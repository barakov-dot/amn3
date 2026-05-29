import pytest

from app.web.auth import (
    check_password,
    create_password_hash,
    generate_csrf_token,
    require_web_admin_config,
    verify_csrf_token,
)


def test_password_hash_round_trip():
    password_hash = create_password_hash("secret-password")

    assert password_hash != "secret-password"
    assert check_password("secret-password", password_hash) is True
    assert check_password("wrong", password_hash) is False


def test_check_password_returns_false_for_malformed_hash():
    assert check_password("secret-password", "not-a-valid-hash") is False


@pytest.mark.parametrize(
    "password_hash",
    ["", "replace-with-generated-password-hash"],
)
def test_require_web_admin_config_rejects_invalid_password_hash(password_hash):
    with pytest.raises(ValueError, match="WEB_ADMIN_PASSWORD_HASH"):
        require_web_admin_config(
            password_hash=password_hash,
            session_secret="x" * 32,
        )


@pytest.mark.parametrize(
    "session_secret",
    ["", "short", "replace-with-generated-session-secret"],
)
def test_require_web_admin_config_rejects_invalid_session_secret(session_secret):
    with pytest.raises(ValueError, match="WEB_ADMIN_SESSION_SECRET"):
        require_web_admin_config(
            password_hash="pbkdf2_sha256$salt$digest",
            session_secret=session_secret,
        )


def test_require_web_admin_config_accepts_valid_config():
    require_web_admin_config(
        password_hash="pbkdf2_sha256$salt$digest",
        session_secret="x" * 32,
    )


def test_csrf_token_round_trip():
    session = {}
    token = generate_csrf_token(session)

    assert verify_csrf_token(session, token) is True
    assert verify_csrf_token(session, "bad-token") is False
