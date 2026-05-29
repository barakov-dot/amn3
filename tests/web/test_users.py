import re
from pathlib import Path

from fastapi.testclient import TestClient

from app.config.settings import Settings
from app.db.connection import connect
from app.db.repositories import Repository
from app.db.schema import initialize_schema
from app.web.app import create_web_app
from app.web.auth import create_password_hash


def test_users_redirects_when_unauthenticated(tmp_path: Path):
    client = _client(tmp_path)

    response = client.get("/users", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_users_lists_existing_telegram_users_and_device_counts(tmp_path: Path):
    settings = _settings(tmp_path)
    user_id = _seed_user(
        Path(settings.database_path),
        telegram_id=1001,
        username="alice",
        first_name="Alice",
        last_name="Admin",
        email="alice@example.com",
        status="active",
        is_admin=True,
    )
    _seed_devices(Path(settings.database_path), user_id=user_id)
    client = _authenticated_client(settings)

    response = client.get("/users")

    assert response.status_code == 200
    assert "1001" in response.text
    assert "alice" in response.text
    assert "Alice Admin" in response.text
    assert "alice@example.com" in response.text
    assert "active" in response.text
    assert "admin" in response.text.lower()
    assert "1 / 2" in response.text


def test_create_user_from_web_stores_email_admin_and_records_action(tmp_path: Path):
    settings = _settings(tmp_path, admin_telegram_ids="9001")
    client = _authenticated_client(settings)
    form = client.get("/users/new")
    assert form.status_code == 200

    response = client.post(
        "/users/new",
        data={
            "telegram_id": "3003",
            "username": "carol",
            "first_name": "Carol",
            "last_name": "Creator",
            "email": "carol@example.com",
            "status": "active",
            "is_admin": "on",
            "csrf_token": _csrf_token(form.text),
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert re.fullmatch(r"/users/\d+", response.headers["location"])
    with _repo(Path(settings.database_path)) as repo:
        user = repo.get_user_by_telegram_id(3003)
        assert user is not None
        assert user["username"] == "carol"
        assert user["first_name"] == "Carol"
        assert user["last_name"] == "Creator"
        assert user["email"] == "carol@example.com"
        assert user["email_verified_at"] is None
        assert user["status"] == "active"
        assert user["is_admin"] == 1
        actions = repo.list_admin_actions_for_target_user(int(user["id"]))
        assert actions[0]["admin_telegram_id"] == 9001
        assert actions[0]["action"] == "web_user_create"


def test_create_user_rejects_duplicate_telegram_id_without_mutating_existing_user(
    tmp_path: Path,
):
    settings = _settings(tmp_path)
    user_id = _seed_user(
        Path(settings.database_path),
        telegram_id=3003,
        username="existing",
        first_name="Existing",
        last_name="User",
        email="existing@example.com",
        email_verified_at="2026-05-29T10:00:00Z",
        status="active",
        is_admin=False,
    )
    client = _authenticated_client(settings)
    form = client.get("/users/new")

    response = client.post(
        "/users/new",
        data={
            "telegram_id": "3003",
            "username": "mutated",
            "first_name": "Mutated",
            "last_name": "Admin",
            "email": "mutated@example.com",
            "status": "blocked",
            "is_admin": "on",
            "csrf_token": _csrf_token(form.text),
        },
        follow_redirects=False,
    )

    assert response.status_code == 400
    with _repo(Path(settings.database_path)) as repo:
        user = repo.get_user(user_id)
        assert user["username"] == "existing"
        assert user["first_name"] == "Existing"
        assert user["last_name"] == "User"
        assert user["email"] == "existing@example.com"
        assert user["email_verified_at"] == "2026-05-29T10:00:00Z"
        assert user["status"] == "active"
        assert user["is_admin"] == 0
        assert repo.list_admin_actions_for_target_user(user_id) == []


def test_user_detail_shows_profile_summaries_and_actions(tmp_path: Path):
    settings = _settings(tmp_path)
    user_id = _seed_user(
        Path(settings.database_path),
        telegram_id=4004,
        username="dana",
        first_name="Dana",
        last_name="Detail",
        email="dana@example.com",
        email_verified_at="2026-05-29T10:00:00Z",
    )
    _seed_devices(Path(settings.database_path), user_id=user_id)
    _seed_order_and_action(Path(settings.database_path), user_id=user_id)
    client = _authenticated_client(settings)

    response = client.get(f"/users/{user_id}")

    assert response.status_code == 200
    assert "dana" in response.text
    assert "dana@example.com" in response.text
    assert ">verified<" in response.text
    assert "active-device" in response.text
    assert "v1:active-private" not in response.text
    assert "v1:active-psk" not in response.text
    assert "manual_review" in response.text
    assert "seed_action" in response.text


def test_edit_user_preserves_and_clears_email_verification(tmp_path: Path):
    settings = _settings(tmp_path, admin_telegram_ids="9001")
    user_id = _seed_user(
        Path(settings.database_path),
        telegram_id=5005,
        username="erin",
        first_name="Erin",
        last_name="Editor",
        email="erin@example.com",
        email_verified_at="2026-05-29T10:00:00Z",
    )
    client = _authenticated_client(settings)

    form = client.get(f"/users/{user_id}/edit")
    assert form.status_code == 200
    same_email_response = client.post(
        f"/users/{user_id}/edit",
        data={
            "telegram_id": "5005",
            "username": "erin-updated",
            "first_name": "Erin",
            "last_name": "Editor",
            "email": "erin@example.com",
            "status": "active",
            "csrf_token": _csrf_token(form.text),
        },
        follow_redirects=False,
    )

    assert same_email_response.status_code == 303
    with _repo(Path(settings.database_path)) as repo:
        user = repo.get_user(user_id)
        assert user["username"] == "erin-updated"
        assert user["email_verified_at"] == "2026-05-29T10:00:00Z"
        assert user["is_admin"] == 0
        assert repo.list_admin_actions_for_target_user(user_id)[0]["action"] == "web_user_update"

    form = client.get(f"/users/{user_id}/edit")
    assert form.status_code == 200
    changed_email_response = client.post(
        f"/users/{user_id}/edit",
        data={
            "telegram_id": "5005",
            "username": "erin-updated",
            "first_name": "Erin",
            "last_name": "Editor",
            "email": "new-erin@example.com",
            "status": "active",
            "is_admin": "on",
            "csrf_token": _csrf_token(form.text),
        },
        follow_redirects=False,
    )

    assert changed_email_response.status_code == 303
    with _repo(Path(settings.database_path)) as repo:
        user = repo.get_user(user_id)
        assert user["email"] == "new-erin@example.com"
        assert user["email_verified_at"] is None
        assert user["is_admin"] == 1


def test_block_and_delete_mutate_status_but_keep_user_row(tmp_path: Path):
    settings = _settings(tmp_path, admin_telegram_ids="9001")
    user_id = _seed_user(
        Path(settings.database_path),
        telegram_id=6006,
        username="frank",
        first_name="Frank",
        last_name=None,
    )
    client = _authenticated_client(settings)

    detail = client.get(f"/users/{user_id}")
    assert detail.status_code == 200
    block_response = client.post(
        f"/users/{user_id}/block",
        data={"csrf_token": _csrf_token(detail.text)},
        follow_redirects=False,
    )

    assert block_response.status_code == 303
    with _repo(Path(settings.database_path)) as repo:
        user = repo.get_user(user_id)
        assert user["status"] == "blocked"
        assert user["telegram_id"] == 6006
        assert repo.list_admin_actions_for_target_user(user_id)[0]["action"] == "web_user_block"

    detail = client.get(f"/users/{user_id}")
    assert detail.status_code == 200
    delete_response = client.post(
        f"/users/{user_id}/delete",
        data={"csrf_token": _csrf_token(detail.text)},
        follow_redirects=False,
    )

    assert delete_response.status_code == 303
    with _repo(Path(settings.database_path)) as repo:
        user = repo.get_user(user_id)
        assert user["status"] == "deleted"
        assert user["telegram_id"] == 6006
        assert repo.list_admin_actions_for_target_user(user_id)[0]["action"] == "web_user_delete"


def test_invalid_csrf_does_not_create_edit_block_or_delete(tmp_path: Path):
    settings = _settings(tmp_path)
    user_id = _seed_user(
        Path(settings.database_path),
        telegram_id=7007,
        username="grace",
        first_name="Grace",
        last_name=None,
        email="grace@example.com",
    )
    client = _authenticated_client(settings)

    create_response = client.post(
        "/users/new",
        data={
            "telegram_id": "8008",
            "username": "hank",
            "first_name": "Hank",
            "last_name": "",
            "email": "hank@example.com",
            "status": "active",
        },
        follow_redirects=False,
    )
    edit_response = client.post(
        f"/users/{user_id}/edit",
        data={
            "telegram_id": "7007",
            "username": "mutated",
            "first_name": "Grace",
            "last_name": "",
            "email": "mutated@example.com",
            "status": "blocked",
            "csrf_token": "bad-token",
        },
        follow_redirects=False,
    )
    block_response = client.post(
        f"/users/{user_id}/block",
        data={"csrf_token": "bad-token"},
        follow_redirects=False,
    )
    delete_response = client.post(
        f"/users/{user_id}/delete",
        data={"csrf_token": "bad-token"},
        follow_redirects=False,
    )

    assert create_response.status_code == 403
    assert edit_response.status_code == 403
    assert block_response.status_code == 403
    assert delete_response.status_code == 403
    with _repo(Path(settings.database_path)) as repo:
        assert repo.get_user_by_telegram_id(8008) is None
        user = repo.get_user(user_id)
        assert user["username"] == "grace"
        assert user["email"] == "grace@example.com"
        assert user["status"] == "active"
        assert repo.list_admin_actions_for_target_user(user_id) == []


def _settings(
    tmp_path: Path,
    *,
    admin_telegram_ids: str = "",
    session_cookie_secure: bool = True,
) -> Settings:
    return Settings(
        _env_file=None,
        telegram_bot_token="TEST_TOKEN",
        app_secret_key="test-secret",
        database_path=str(tmp_path / "amneziya.sqlite3"),
        admin_telegram_ids=admin_telegram_ids,
        web_admin_username="root",
        web_admin_password_hash=create_password_hash(
            "correct-password",
            salt="test-salt",
        ),
        web_admin_session_secret="s" * 32,
        web_admin_session_cookie_secure=session_cookie_secure,
    )


def _client(
    tmp_path: Path | None = None,
    *,
    settings: Settings | None = None,
    base_url: str = "https://testserver",
) -> TestClient:
    actual_settings = settings or _settings(tmp_path or Path("."))
    return TestClient(create_web_app(actual_settings), base_url=base_url)


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


class _repo:
    def __init__(self, database_path: Path) -> None:
        self._database_path = database_path
        self._conn = None

    def __enter__(self) -> Repository:
        self._conn = connect(self._database_path)
        initialize_schema(self._conn)
        return Repository(self._conn)

    def __exit__(self, *args) -> None:
        assert self._conn is not None
        self._conn.close()


def _seed_user(
    database_path: Path,
    *,
    telegram_id: int,
    username: str,
    first_name: str,
    last_name: str | None,
    email: str | None = None,
    email_verified_at: str | None = None,
    status: str = "active",
    is_admin: bool = False,
) -> int:
    conn = connect(database_path)
    try:
        initialize_schema(conn)
        repo = Repository(conn)
        user_id = repo.upsert_user(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        conn.execute(
            """
            UPDATE users
            SET email = ?,
                email_verified_at = ?,
                status = ?,
                is_admin = ?
            WHERE id = ?
            """,
            (email, email_verified_at, status, int(is_admin), user_id),
        )
        conn.commit()
        return user_id
    finally:
        conn.close()


def _seed_devices(database_path: Path, *, user_id: int) -> None:
    conn = connect(database_path)
    try:
        initialize_schema(conn)
        repo = Repository(conn)
        server_id = repo.ensure_default_server(name="local", network_cidr="10.8.0.0/24")
        repo.create_device(
            user_id=user_id,
            server_id=server_id,
            name="active-device",
            duration_days=7,
            vpn_ip=f"10.8.0.{user_id + 2}",
            peer_public_key=f"active-public-{user_id}",
            peer_private_key_encrypted="v1:active-private",
            preshared_key_encrypted="v1:active-psk",
            config_version="amneziawg_v2",
        )
        revoked_id = repo.create_device(
            user_id=user_id,
            server_id=server_id,
            name="revoked-device",
            duration_days=7,
            vpn_ip=f"10.8.0.{user_id + 3}",
            peer_public_key=f"revoked-public-{user_id}",
            peer_private_key_encrypted="v1:revoked-private",
            preshared_key_encrypted="v1:revoked-psk",
            config_version="amneziawg_v2",
        )
        repo.revoke_device(
            revoked_id,
            reason="test",
            revoked_at="2026-05-29T10:00:00Z",
        )
    finally:
        conn.close()


def _seed_order_and_action(database_path: Path, *, user_id: int) -> None:
    conn = connect(database_path)
    try:
        initialize_schema(conn)
        repo = Repository(conn)
        repo.create_order(user_id=user_id, plan_id=None, payment_mode="free_test")
        repo.record_admin_action(
            admin_telegram_id=9001,
            action="seed_action",
            target_user_id=user_id,
            metadata={"source": "test"},
        )
    finally:
        conn.close()
