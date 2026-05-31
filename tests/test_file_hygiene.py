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
        "errors_logs/",
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


def test_env_examples_include_local_agent_safe_defaults():
    expected = [
        "LOCAL_AGENT_ENABLED=false",
        "LOCAL_AGENT_HOST=127.0.0.1",
        "LOCAL_AGENT_PORT=3031",
        "LOCAL_AGENT_TOKEN_ID=local-controller",
        "LOCAL_AGENT_TOKEN_HASH=",
        "LOCAL_AGENT_TOKEN_OWNER=local-controller",
        "LOCAL_AGENT_TOKEN_SCOPES=agent:health,agent:read,agent:protocols:read",
        "LOCAL_AGENT_TOKEN_EXPIRES_AT=",
        "LOCAL_AGENT_CONTROLLER_ENABLED=false",
        "LOCAL_AGENT_CONTROLLER_BASE_URL=http://127.0.0.1:3031",
        "LOCAL_AGENT_CONTROLLER_TOKEN_PATH=",
    ]

    for path in [Path(".env.example"), Path("deploy/examples/.env.production.example")]:
        text = path.read_text(encoding="utf-8")
        for line in expected:
            assert line in text, f"{path} is missing {line}"
