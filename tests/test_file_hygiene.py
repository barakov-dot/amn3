import re
import tomllib
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


def test_pyproject_limits_setuptools_package_discovery_to_app_package():
    config = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))

    package_find = config["tool"]["setuptools"]["packages"]["find"]

    assert package_find["where"] == ["."]
    assert package_find["include"] == ["app", "app.*"]
    assert "deploy*" in package_find["exclude"]
    assert "docs*" in package_find["exclude"]
    assert "tests*" in package_find["exclude"]
    assert "tmp*" in package_find["exclude"]
    assert "errors_logs*" in package_find["exclude"]
