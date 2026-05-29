from pathlib import Path

from app.cli import build_parser
from app.cli import run_web_password_hash
from app.cli import run_web_server
from app.config.settings import Settings
from app.web.auth import check_password
from app.web.auth import create_password_hash


def test_cli_accepts_web_serve_arguments():
    parser = build_parser()

    args = parser.parse_args(
        ["web", "serve", "--host", "0.0.0.0", "--port", "3030"]
    )

    assert args.command == "web"
    assert args.web_command == "serve"
    assert args.host == "0.0.0.0"
    assert args.port == 3030


def test_cli_accepts_web_hash_password_argument():
    parser = build_parser()

    args = parser.parse_args(["web", "hash-password", "--password", "secret"])

    assert args.command == "web"
    assert args.web_command == "hash-password"
    assert args.password == "secret"


def test_run_web_password_hash_outputs_valid_pbkdf2_hash():
    password_hash = run_web_password_hash("secret")

    assert password_hash.startswith("pbkdf2_sha256$")
    assert check_password("secret", password_hash)
    assert not check_password("other", password_hash)


def test_run_web_server_invokes_uvicorn_with_selected_host_and_port(tmp_path: Path):
    settings = _settings(tmp_path)
    calls = []

    def fake_uvicorn_run(app, *, host: str, port: int) -> None:
        calls.append({"app_title": app.title, "host": host, "port": port})

    run_web_server(
        host="127.0.0.1",
        port=3031,
        settings=settings,
        uvicorn_run=fake_uvicorn_run,
    )

    assert calls == [
        {
            "app_title": "Amneziya Web Admin",
            "host": "127.0.0.1",
            "port": 3031,
        }
    ]


def test_run_web_server_uses_settings_defaults_when_host_port_omitted(tmp_path: Path):
    settings = _settings(tmp_path, host="0.0.0.0", port=3030)
    calls = []

    def fake_uvicorn_run(app, *, host: str, port: int) -> None:
        calls.append({"host": host, "port": port})

    run_web_server(
        host=None,
        port=None,
        settings=settings,
        uvicorn_run=fake_uvicorn_run,
    )

    assert calls == [{"host": "0.0.0.0", "port": 3030}]


def _settings(
    tmp_path: Path,
    *,
    host: str = "127.0.0.1",
    port: int = 3031,
) -> Settings:
    return Settings(
        _env_file=None,
        telegram_bot_token="TEST_TOKEN",
        app_secret_key="test-secret",
        database_path=str(tmp_path / "amneziya.sqlite3"),
        web_admin_enabled=True,
        web_admin_host=host,
        web_admin_port=port,
        web_admin_username="admin",
        web_admin_password_hash=create_password_hash(
            "correct-password",
            salt="test-salt",
        ),
        web_admin_session_secret="s" * 32,
    )
