import re
from pathlib import Path

from fastapi.testclient import TestClient

from app.config.settings import Settings
from app.web.app import create_web_app
from app.web.auth import create_password_hash


def test_config_templates_redirects_when_unauthenticated(tmp_path: Path):
    client = _client(settings=_settings(tmp_path))

    response = client.get("/config-templates", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_config_templates_page_lists_versions_placeholders_and_safe_preview(tmp_path: Path):
    template_dir = tmp_path / "client-templates"
    template_dir.mkdir()
    (template_dir / "amneziawg_v1_5.conf.tpl").write_text(
        "\n".join(
            [
                "[Interface]",
                "  PrivateKey: REAL_PRIVATE_KEY_SHOULD_NOT_APPEAR",
                "Address = {address}",
                "",
                "[Peer]",
                "  PresharedKey: REAL_PSK_SHOULD_NOT_APPEAR",
                "Endpoint = {endpoint}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    settings = _settings(
        tmp_path,
        app_secret_key="production-secret-should-not-appear",
        client_config_template_dir=str(template_dir),
    )
    client = _authenticated_client(settings)

    response = client.get("/config-templates")

    assert response.status_code == 200
    assert "Config templates" in response.text
    assert "amneziawg_v1_5" in response.text
    assert "amneziawg_v2" in response.text
    assert "override" in response.text
    assert "default" in response.text
    assert "{private_key}" in response.text
    assert "{preshared_key}" in response.text
    assert "vpn://" in response.text
    assert "REAL_PRIVATE_KEY_SHOULD_NOT_APPEAR" not in response.text
    assert "REAL_PSK_SHOULD_NOT_APPEAR" not in response.text
    assert "production-secret-should-not-appear" not in response.text


def _settings(
    tmp_path: Path,
    *,
    app_secret_key: str = "test-secret",
    client_config_template_dir: str | None = None,
) -> Settings:
    return Settings(
        _env_file=None,
        telegram_bot_token="TEST_TOKEN",
        app_secret_key=app_secret_key,
        database_path=str(tmp_path / "amneziya.sqlite3"),
        web_admin_username="root",
        web_admin_password_hash=create_password_hash(
            "correct-password",
            salt="test-salt",
        ),
        web_admin_session_secret="s" * 32,
        web_admin_session_cookie_secure=True,
        client_config_template_dir=client_config_template_dir or str(tmp_path / "templates"),
    )


def _client(*, settings: Settings) -> TestClient:
    return TestClient(create_web_app(settings), base_url="https://testserver")


def _authenticated_client(settings: Settings) -> TestClient:
    client = _client(settings=settings)
    login_page = client.get("/login")
    response = client.post(
        "/login",
        data={
            "username": "root",
            "password": "correct-password",
            "csrf_token": _csrf_token(login_page.text),
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    return client


def _csrf_token(html: str) -> str:
    match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', html)
    assert match is not None
    return match.group(1)
