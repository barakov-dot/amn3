import pytest

from app.security.crypto import SecretBox, SecretBoxError


def test_secret_box_round_trips_text_without_plaintext_storage():
    box = SecretBox.from_app_secret("test-secret", allow_weak_secret=True)

    encrypted = box.encrypt_text("private-value")

    assert encrypted != "private-value"
    assert encrypted.startswith("v1:")
    assert box.decrypt_text(encrypted) == "private-value"


def test_secret_box_rejects_weak_app_secret_by_default():
    with pytest.raises(SecretBoxError):
        SecretBox.from_app_secret("test-secret")


def test_secret_box_can_use_explicit_test_only_weak_secret():
    box = SecretBox.from_app_secret("test-secret", allow_weak_secret=True)

    assert box.decrypt_text(box.encrypt_text("private-value")) == "private-value"


def test_secret_box_rejects_repeated_app_secret_by_default():
    with pytest.raises(SecretBoxError):
        SecretBox.from_app_secret("a" * 32)


def test_secret_box_raises_public_error_for_wrong_key():
    encrypted = SecretBox.from_app_secret(
        "source-secret-material-32-chars-ok"
    ).encrypt_text("private-value")
    other_box = SecretBox.from_app_secret("other-secret-material-32-chars-ok")

    with pytest.raises(SecretBoxError):
        other_box.decrypt_text(encrypted)


def test_secret_box_raises_public_error_for_unsupported_version():
    box = SecretBox.from_app_secret("test-secret", allow_weak_secret=True)

    with pytest.raises(SecretBoxError):
        box.decrypt_text("v2:token")


def test_secret_box_raises_public_error_for_missing_prefix():
    box = SecretBox.from_app_secret("test-secret", allow_weak_secret=True)

    with pytest.raises(SecretBoxError):
        box.decrypt_text("token-without-prefix")


def test_secret_box_raises_public_error_for_malformed_token():
    box = SecretBox.from_app_secret("test-secret", allow_weak_secret=True)

    with pytest.raises(SecretBoxError):
        box.decrypt_text("v1:not-a-fernet-token")


def test_secret_box_raises_public_error_for_decrypted_non_utf8_payload():
    box = SecretBox.from_app_secret("test-secret", allow_weak_secret=True)
    token = box._fernet.encrypt(b"\xff").decode("ascii")

    with pytest.raises(SecretBoxError):
        box.decrypt_text(f"v1:{token}")
