from app.security.redaction import redact


def test_redaction_removes_tokens_keys_and_config_markers():
    unsafe = """
    TELEGRAM_BOT_TOKEN=123:abc
    PrivateKey = secret-private
    PresharedKey = secret-psk
    [Interface]
    Address = 10.8.0.2/32
    external_payment_id=pay_123
    """

    safe = redact(unsafe)

    assert "123:abc" not in safe
    assert "secret-private" not in safe
    assert "secret-psk" not in safe
    assert "[Interface]" not in safe
    assert "pay_123" not in safe
    assert "[REDACTED" in safe


def test_redaction_handles_realistic_secret_log_formats():
    unsafe = """
    APP_SECRET_KEY = secret-app
    telegram_bot_token: 123456:ABCdef
    {'TELEGRAM_BOT_TOKEN': '123456:ABCdef'}
    "external_payment_id": "pay_123"
    https://api.telegram.org/bot123456:ABCdef/sendMessage
    external_payment_id = pay_456
    PrivateKey   :   secret-private
    PresharedKey = secret-psk
    [Interface]
    Address = 10.8.0.2/32
    PrivateKey = block-private
    [Peer]
    PublicKey = peer-public
    PresharedKey = block-psk
    AllowedIPs = 0.0.0.0/0
    """

    safe = redact(unsafe)

    for unsafe_value in [
        "secret-app",
        "123456:ABCdef",
        "pay_123",
        "pay_456",
        "secret-private",
        "secret-psk",
        "[Interface]",
        "10.8.0.2/32",
        "block-private",
        "[Peer]",
        "peer-public",
        "block-psk",
    ]:
        assert unsafe_value not in safe
    assert "[REDACTED" in safe
