import re
from pathlib import Path


def test_gitignore_excludes_sensitive_runtime_files():
    text = Path(".gitignore").read_text(encoding="utf-8")

    required = [
        ".env",
        "*.db",
        "*.sqlite",
        "*.sqlite3",
        "*.conf",
        "*.qr.png",
        "servers.yml",
        "backups/",
        "tmp/",
    ]

    for pattern in required:
        assert pattern in text


def test_env_example_uses_placeholders_only():
    text = Path(".env.example").read_text(encoding="utf-8")

    assert "TELEGRAM_BOT_TOKEN=CHANGE_ME" in text
    assert "APP_SECRET_KEY=CHANGE_ME_GENERATED_SECRET" in text
    assert "ADMIN_TELEGRAM_IDS=123456789" in text
    assert not re.search(
        r"^TELEGRAM_BOT_TOKEN=\d{6,12}:[A-Za-z0-9_-]{20,}$",
        text,
        re.MULTILINE,
    )
