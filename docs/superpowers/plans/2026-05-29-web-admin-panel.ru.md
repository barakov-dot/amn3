# Web Admin Panel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a FastAPI/Jinja2 web admin panel on port `3030` with login/password auth, users CRUD, servers CRUD, live server health, logs viewer, and `.env`-controlled logging.

**Architecture:** Add a separate `app.web` package that reuses existing `Settings`, SQLite `Repository`, redaction, and server check code. The web panel runs as a separate process through `python -m app.cli web serve`, uses signed cookie sessions, server-rendered templates, and records admin actions through the existing database. Live server state is stored in `server_health_checks` and refreshed by explicit UI/CLI actions.

**Tech Stack:** Python 3.12+, FastAPI, Starlette sessions, Jinja2, Uvicorn, SQLite, pytest, standard-library logging.

---

## File Structure

- Modify `pyproject.toml`: add `fastapi`, `uvicorn`, `jinja2`, `python-multipart`.
- Modify `.env.example`: add web admin and logging settings.
- Modify `app/config/settings.py`: add web/log fields and validators.
- Modify `app/db/schema.py`: add `server_health_checks`.
- Modify `app/db/repositories.py`: add web admin CRUD/query methods and health persistence.
- Create `app/logging_config.py`: configure console/file logging with redaction and log depth support.
- Create `app/web/__init__.py`: export app factory.
- Create `app/web/auth.py`: password hashing/checking, session auth, CSRF helpers.
- Create `app/web/server_health.py`: TCP reachability and read-only server check summary.
- Create `app/web/logs.py`: tail and redact log files.
- Create `app/web/forms.py`: small validation helpers for users and servers.
- Create `app/web/app.py`: FastAPI app factory and routes.
- Create `app/web/templates/*.html`: base, login, dashboard, users, user form/detail, servers, server form/detail/health, orders, logs, settings.
- Create `app/web/static/admin.css`: compact operational UI.
- Modify `app/cli.py`: add `web serve`.
- Create tests under `tests/web/`.
- Update `docs/PRODUCTION_VPS_CHECKLIST.ru.md` and `.en.md`: web panel launch and firewall note.

---

### Task 1: Dependencies, Settings, And Logging Config

**Files:**
- Modify: `pyproject.toml`
- Modify: `.env.example`
- Modify: `app/config/settings.py`
- Create: `app/logging_config.py`
- Test: `tests/config/test_settings.py`
- Test: `tests/test_logging_config.py`

- [ ] **Step 1: Write failing settings test**

Add to `tests/config/test_settings.py`:

```python
def test_settings_reads_web_admin_and_logging_settings():
    settings = Settings(
        _env_file=None,
        telegram_bot_token="TEST_TOKEN",
        app_secret_key="test-secret",
        web_admin_enabled=True,
        web_admin_host="0.0.0.0",
        web_admin_port=3030,
        web_admin_username="admin",
        web_admin_password_hash="sha256$abc",
        web_admin_session_secret="session-secret-value-with-32-plus-chars",
        app_log_enabled=True,
        app_log_level="DEBUG",
        app_log_max_lines=250,
        app_log_path="logs/app.log",
    )

    assert settings.web_admin_enabled is True
    assert settings.web_admin_host == "0.0.0.0"
    assert settings.web_admin_port == 3030
    assert settings.web_admin_username == "admin"
    assert settings.web_admin_password_hash == "sha256$abc"
    assert settings.web_admin_session_secret.startswith("session-secret")
    assert settings.app_log_enabled is True
    assert settings.app_log_level == "DEBUG"
    assert settings.app_log_max_lines == 250
    assert settings.app_log_path == "logs/app.log"
```

- [ ] **Step 2: Run settings test to verify it fails**

Run:

```bash
python -m pytest tests/config/test_settings.py::test_settings_reads_web_admin_and_logging_settings -q
```

Expected: FAIL because `Settings` has no web/log fields.

- [ ] **Step 3: Implement settings and dependencies**

In `pyproject.toml`, add:

```toml
"fastapi>=0.115,<1",
"uvicorn>=0.30,<1",
"jinja2>=3.1,<4",
"python-multipart>=0.0.9,<1",
```

In `.env.example`, add:

```env
WEB_ADMIN_ENABLED=true
WEB_ADMIN_HOST=0.0.0.0
WEB_ADMIN_PORT=3030
WEB_ADMIN_USERNAME=admin
WEB_ADMIN_PASSWORD_HASH=replace-with-password-hash
WEB_ADMIN_SESSION_SECRET=replace-with-generated-random-secret-32-plus-chars
APP_LOG_ENABLED=true
APP_LOG_LEVEL=INFO
APP_LOG_MAX_LINES=500
APP_LOG_PATH=logs/app.log
```

In `app/config/settings.py`, add fields:

```python
web_admin_enabled: bool = Field(default=True, alias="WEB_ADMIN_ENABLED")
web_admin_host: str = Field(default="0.0.0.0", alias="WEB_ADMIN_HOST")
web_admin_port: int = Field(default=3030, alias="WEB_ADMIN_PORT")
web_admin_username: str = Field(default="admin", alias="WEB_ADMIN_USERNAME")
web_admin_password_hash: str = Field(default="", alias="WEB_ADMIN_PASSWORD_HASH")
web_admin_session_secret: str = Field(default="", alias="WEB_ADMIN_SESSION_SECRET")
app_log_enabled: bool = Field(default=True, alias="APP_LOG_ENABLED")
app_log_level: str = Field(default="INFO", alias="APP_LOG_LEVEL")
app_log_max_lines: int = Field(default=500, alias="APP_LOG_MAX_LINES")
app_log_path: str = Field(default="logs/app.log", alias="APP_LOG_PATH")
```

Extend the existing model validator:

```python
allowed_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR"}
if self.app_log_level.upper() not in allowed_log_levels:
    raise ValueError("APP_LOG_LEVEL must be DEBUG, INFO, WARNING, or ERROR")
if not 1 <= self.web_admin_port <= 65535:
    raise ValueError("WEB_ADMIN_PORT must be in 1..65535")
if self.app_log_max_lines < 1:
    raise ValueError("APP_LOG_MAX_LINES must be positive")
self.app_log_level = self.app_log_level.upper()
return self
```

- [ ] **Step 4: Write failing logging config test**

Create `tests/test_logging_config.py`:

```python
import logging

from app.logging_config import configure_logging


def test_configure_logging_writes_redacted_file(tmp_path):
    log_path = tmp_path / "app.log"
    logger = configure_logging(
        enabled=True,
        level="INFO",
        log_path=log_path,
    )

    logger.info("TELEGRAM_PROXY_URL=socks5://user:pass@example.com:1080")

    text = log_path.read_text(encoding="utf-8")
    assert "user:pass@example.com" not in text
    assert "[REDACTED]" in text


def test_configure_logging_can_disable_file_logging(tmp_path):
    log_path = tmp_path / "app.log"
    logger = configure_logging(
        enabled=False,
        level="INFO",
        log_path=log_path,
    )

    logger.info("hello")

    assert not log_path.exists()
```

- [ ] **Step 5: Run logging config test to verify it fails**

Run:

```bash
python -m pytest tests/test_logging_config.py -q
```

Expected: FAIL because `app.logging_config` does not exist.

- [ ] **Step 6: Implement logging config**

Create `app/logging_config.py`:

```python
from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.security.redaction import redact


class RedactingFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        rendered = super().format(record)
        return redact(rendered)


def configure_logging(
    *,
    enabled: bool,
    level: str,
    log_path: str | Path,
) -> logging.Logger:
    logger = logging.getLogger("amneziya")
    logger.setLevel(getattr(logging, level.upper()))
    logger.handlers.clear()
    logger.propagate = False

    formatter = RedactingFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

    if enabled:
        path = Path(log_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            path,
            maxBytes=1_000_000,
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
```

- [ ] **Step 7: Run tests**

Run:

```bash
python -m pytest tests/config/test_settings.py tests/test_logging_config.py -q
```

Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add pyproject.toml .env.example app/config/settings.py app/logging_config.py tests/config/test_settings.py tests/test_logging_config.py
git commit -m "Add web admin settings and logging config"
```

---

### Task 2: Database And Repository Support

**Files:**
- Modify: `app/db/schema.py`
- Modify: `app/db/repositories.py`
- Test: `tests/db/test_repositories.py`
- Test: `tests/server/test_checks.py`

- [ ] **Step 1: Write failing schema/repository test for server health**

Add to `tests/db/test_repositories.py`:

```python
def test_repository_records_latest_server_health(conn):
    repo = Repository(conn)
    server_id = repo.ensure_default_server(name="local", network_cidr="10.8.0.0/24")

    repo.record_server_health(
        server_id=server_id,
        status="online",
        latency_ms=42,
        ssh_ok=True,
        awg_ok=True,
        udp_port_ok=True,
        error=None,
    )

    latest = repo.get_latest_server_health(server_id)
    assert latest["status"] == "online"
    assert latest["latency_ms"] == 42
    assert latest["ssh_ok"] == 1
    assert latest["awg_ok"] == 1
    assert latest["udp_port_ok"] == 1
    assert latest["error"] is None
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
python -m pytest tests/db/test_repositories.py::test_repository_records_latest_server_health -q
```

Expected: FAIL because methods/table do not exist.

- [ ] **Step 3: Add schema**

In `app/db/schema.py`, add:

```sql
CREATE TABLE IF NOT EXISTS server_health_checks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_id INTEGER NOT NULL,
    status TEXT NOT NULL
        CHECK (status IN ('online', 'degraded', 'offline', 'unknown')),
    latency_ms INTEGER,
    ssh_ok INTEGER NOT NULL DEFAULT 0 CHECK (ssh_ok IN (0, 1)),
    awg_ok INTEGER NOT NULL DEFAULT 0 CHECK (awg_ok IN (0, 1)),
    udp_port_ok INTEGER NOT NULL DEFAULT 0 CHECK (udp_port_ok IN (0, 1)),
    error TEXT,
    checked_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_server_health_latest
    ON server_health_checks(server_id, checked_at DESC, id DESC);
```

- [ ] **Step 4: Add repository methods**

In `app/db/repositories.py`, add:

```python
def record_server_health(
    self,
    *,
    server_id: int,
    status: str,
    latency_ms: int | None,
    ssh_ok: bool,
    awg_ok: bool,
    udp_port_ok: bool,
    error: str | None,
) -> int:
    cursor = self._conn.execute(
        """
        INSERT INTO server_health_checks (
            server_id,
            status,
            latency_ms,
            ssh_ok,
            awg_ok,
            udp_port_ok,
            error
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            server_id,
            status,
            latency_ms,
            int(ssh_ok),
            int(awg_ok),
            int(udp_port_ok),
            error,
        ),
    )
    self._commit()
    return int(cursor.lastrowid)


def get_latest_server_health(self, server_id: int):
    return self._conn.execute(
        """
        SELECT *
        FROM server_health_checks
        WHERE server_id = ?
        ORDER BY checked_at DESC, id DESC
        LIMIT 1
        """,
        (server_id,),
    ).fetchone()
```

- [ ] **Step 5: Add web repository queries**

Add focused methods:

```python
def list_servers_for_admin(self, *, limit: int = 100):
    return self._conn.execute(
        """
        SELECT
            servers.*,
            COUNT(devices.id) AS total_device_count,
            COALESCE(SUM(CASE WHEN devices.status = 'active' THEN 1 ELSE 0 END), 0)
                AS active_device_count,
            latest.status AS health_status,
            latest.latency_ms AS health_latency_ms,
            latest.checked_at AS health_checked_at,
            latest.error AS health_error
        FROM servers
        LEFT JOIN devices ON devices.server_id = servers.id
        LEFT JOIN server_health_checks AS latest
            ON latest.id = (
                SELECT id
                FROM server_health_checks
                WHERE server_id = servers.id
                ORDER BY checked_at DESC, id DESC
                LIMIT 1
            )
        GROUP BY servers.id
        ORDER BY servers.id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
```

Also add:

```python
def list_orders_for_admin(self, *, limit: int = 100):
    return self._conn.execute(
        """
        SELECT
            orders.*,
            users.telegram_id,
            users.username,
            users.first_name,
            users.last_name
        FROM orders
        JOIN users ON users.id = orders.user_id
        ORDER BY orders.id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
```

- [ ] **Step 6: Run repository tests**

Run:

```bash
python -m pytest tests/db/test_repositories.py -q
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add app/db/schema.py app/db/repositories.py tests/db/test_repositories.py
git commit -m "Add web admin repository support"
```

---

### Task 3: Authentication, Sessions, And CSRF

**Files:**
- Create: `app/web/__init__.py`
- Create: `app/web/auth.py`
- Test: `tests/web/test_auth.py`

- [ ] **Step 1: Write failing auth tests**

Create `tests/web/test_auth.py`:

```python
from app.web.auth import (
    check_password,
    create_password_hash,
    generate_csrf_token,
    verify_csrf_token,
)


def test_password_hash_round_trip():
    password_hash = create_password_hash("secret-password")

    assert password_hash != "secret-password"
    assert check_password("secret-password", password_hash) is True
    assert check_password("wrong", password_hash) is False


def test_csrf_token_round_trip():
    session = {}
    token = generate_csrf_token(session)

    assert verify_csrf_token(session, token) is True
    assert verify_csrf_token(session, "bad-token") is False
```

- [ ] **Step 2: Run auth tests to verify they fail**

Run:

```bash
python -m pytest tests/web/test_auth.py -q
```

Expected: FAIL because `app.web.auth` does not exist.

- [ ] **Step 3: Implement auth helpers**

Create `app/web/auth.py`:

```python
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
    return isinstance(expected, str) and isinstance(token, str) and hmac.compare_digest(expected, token)


def require_web_admin_config(*, password_hash: str, session_secret: str) -> None:
    if not password_hash or password_hash.startswith("replace-with-"):
        raise ValueError("WEB_ADMIN_PASSWORD_HASH must be set before starting web admin")
    if not session_secret or session_secret.startswith("replace-with-") or len(session_secret) < 32:
        raise ValueError("WEB_ADMIN_SESSION_SECRET must be at least 32 characters")
```

- [ ] **Step 4: Run auth tests**

Run:

```bash
python -m pytest tests/web/test_auth.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/web/__init__.py app/web/auth.py tests/web/test_auth.py
git commit -m "Add web admin auth helpers"
```

---

### Task 4: FastAPI App Skeleton, Login, Dashboard

**Files:**
- Create: `app/web/app.py`
- Create: `app/web/templates/base.html`
- Create: `app/web/templates/login.html`
- Create: `app/web/templates/dashboard.html`
- Create: `app/web/static/admin.css`
- Modify: `pyproject.toml`
- Test: `tests/web/test_app.py`

- [ ] **Step 1: Write failing web app tests**

Create `tests/web/test_app.py`:

```python
from fastapi.testclient import TestClient

from app.config import Settings
from app.db.connection import connect
from app.db.schema import initialize_schema
from app.web.app import create_web_app
from app.web.auth import create_password_hash


def _settings(tmp_path):
    return Settings(
        _env_file=None,
        telegram_bot_token="TEST_TOKEN",
        app_secret_key="test-secret",
        database_path=str(tmp_path / "app.sqlite3"),
        web_admin_username="admin",
        web_admin_password_hash=create_password_hash("secret"),
        web_admin_session_secret="session-secret-value-with-32-plus-chars",
    )


def test_login_protects_dashboard(tmp_path):
    settings = _settings(tmp_path)
    conn = connect(settings.database_path)
    initialize_schema(conn)
    app = create_web_app(settings=settings)
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_login_success_shows_dashboard(tmp_path):
    settings = _settings(tmp_path)
    conn = connect(settings.database_path)
    initialize_schema(conn)
    app = create_web_app(settings=settings)
    client = TestClient(app)

    response = client.post(
        "/login",
        data={"username": "admin", "password": "secret"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Dashboard" in response.text
```

- [ ] **Step 2: Run web app tests to verify they fail**

Run:

```bash
python -m pytest tests/web/test_app.py -q
```

Expected: FAIL because `app.web.app` does not exist.

- [ ] **Step 3: Implement app factory and login routes**

Create `app/web/app.py` with:

```python
from __future__ import annotations

from pathlib import Path

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.config import Settings
from app.db.connection import connect
from app.db.repositories import Repository
from app.db.schema import initialize_schema
from app.web.auth import check_password, require_web_admin_config

PACKAGE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(PACKAGE_DIR / "templates"))


def create_web_app(*, settings: Settings | None = None) -> FastAPI:
    actual_settings = settings or Settings()
    require_web_admin_config(
        password_hash=actual_settings.web_admin_password_hash,
        session_secret=actual_settings.web_admin_session_secret,
    )
    app = FastAPI(title="Amneziya Admin")
    app.add_middleware(SessionMiddleware, secret_key=actual_settings.web_admin_session_secret)
    app.mount("/static", StaticFiles(directory=str(PACKAGE_DIR / "static")), name="static")
    app.state.settings = actual_settings

    @app.get("/login", response_class=HTMLResponse)
    async def login_form(request: Request):
        return templates.TemplateResponse("login.html", {"request": request, "error": None})

    @app.post("/login")
    async def login(request: Request, username: str = Form(...), password: str = Form(...)):
        if username != actual_settings.web_admin_username or not check_password(password, actual_settings.web_admin_password_hash):
            return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password"}, status_code=401)
        request.session["web_admin"] = True
        return RedirectResponse("/", status_code=303)

    @app.post("/logout")
    async def logout(request: Request):
        request.session.clear()
        return RedirectResponse("/login", status_code=303)

    @app.get("/", response_class=HTMLResponse)
    async def dashboard(request: Request, repo: Repository = Depends(_repo)):
        auth = _require_auth(request)
        if auth is not None:
            return auth
        stats = {
            "users": len(repo.list_users_for_admin(limit=1000)),
            "servers": len(repo.list_servers_for_admin(limit=1000)),
            "pending_orders": len(repo.list_pending_orders(limit=1000)),
        }
        return templates.TemplateResponse("dashboard.html", {"request": request, "stats": stats})

    return app


def _repo(request: Request) -> Repository:
    settings: Settings = request.app.state.settings
    conn = connect(settings.database_path)
    initialize_schema(conn)
    return Repository(conn)


def _require_auth(request: Request):
    if request.session.get("web_admin") is True:
        return None
    return RedirectResponse("/login", status_code=303)
```

- [ ] **Step 4: Add templates and CSS**

`app/web/templates/base.html`:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ title or "Amneziya Admin" }}</title>
    <link rel="stylesheet" href="/static/admin.css">
  </head>
  <body>
    <header class="topbar">
      <a class="brand" href="/">Amneziya Admin</a>
      <nav>
        <a href="/users">Users</a>
        <a href="/servers">Servers</a>
        <a href="/orders">Orders</a>
        <a href="/logs">Logs</a>
        <a href="/settings">Settings</a>
      </nav>
      <form method="post" action="/logout"><button type="submit">Logout</button></form>
    </header>
    <main class="page">{% block content %}{% endblock %}</main>
  </body>
</html>
```

`app/web/templates/login.html`:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Login - Amneziya Admin</title>
    <link rel="stylesheet" href="/static/admin.css">
  </head>
  <body class="login-page">
    <form class="login-box" method="post" action="/login">
      <h1>Amneziya Admin</h1>
      {% if error %}<p class="error">{{ error }}</p>{% endif %}
      <label>Username <input name="username" autocomplete="username" required></label>
      <label>Password <input name="password" type="password" autocomplete="current-password" required></label>
      <button type="submit">Login</button>
    </form>
  </body>
</html>
```

`app/web/templates/dashboard.html`:

```html
{% extends "base.html" %}
{% block content %}
<h1>Dashboard</h1>
<section class="metrics">
  <div><strong>{{ stats.users }}</strong><span>Users</span></div>
  <div><strong>{{ stats.servers }}</strong><span>Servers</span></div>
  <div><strong>{{ stats.pending_orders }}</strong><span>Pending orders</span></div>
</section>
{% endblock %}
```

`app/web/static/admin.css`:

```css
body { margin: 0; font-family: Arial, sans-serif; background: #f6f7f9; color: #18202a; }
.topbar { display: flex; gap: 18px; align-items: center; padding: 10px 18px; background: #17202a; color: white; }
.topbar a { color: white; text-decoration: none; }
.topbar nav { display: flex; gap: 12px; flex: 1; }
.topbar button, .login-box button, .button { border: 0; padding: 8px 12px; background: #2563eb; color: white; cursor: pointer; border-radius: 6px; }
.page { padding: 20px; }
.metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; }
.metrics div, .panel { background: white; border: 1px solid #d9dee7; border-radius: 8px; padding: 14px; }
.metrics strong { display: block; font-size: 28px; }
.login-page { min-height: 100vh; display: grid; place-items: center; }
.login-box { width: min(360px, calc(100vw - 32px)); background: white; border: 1px solid #d9dee7; border-radius: 8px; padding: 20px; display: grid; gap: 12px; }
input, select, textarea { width: 100%; box-sizing: border-box; padding: 8px; border: 1px solid #b7c0ce; border-radius: 6px; }
.error { color: #b42318; }
```

- [ ] **Step 5: Run web app tests**

Run:

```bash
python -m pytest tests/web/test_app.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml app/web tests/web/test_app.py
git commit -m "Add web admin login dashboard"
```

---

### Task 5: Users CRUD

**Files:**
- Modify: `app/db/repositories.py`
- Modify: `app/web/app.py`
- Create: `app/web/templates/users.html`
- Create: `app/web/templates/user_form.html`
- Create: `app/web/templates/user_detail.html`
- Test: `tests/web/test_users.py`

- [ ] **Step 1: Write failing users route tests**

Create `tests/web/test_users.py` with helpers copied from `tests/web/test_app.py`:

```python
from fastapi.testclient import TestClient

from app.config import Settings
from app.db.connection import connect
from app.db.repositories import Repository
from app.db.schema import initialize_schema
from app.web.app import create_web_app
from app.web.auth import create_password_hash


def _client(tmp_path):
    settings = Settings(
        _env_file=None,
        telegram_bot_token="TEST_TOKEN",
        app_secret_key="test-secret",
        database_path=str(tmp_path / "app.sqlite3"),
        web_admin_username="admin",
        web_admin_password_hash=create_password_hash("secret"),
        web_admin_session_secret="session-secret-value-with-32-plus-chars",
    )
    conn = connect(settings.database_path)
    initialize_schema(conn)
    app = create_web_app(settings=settings)
    client = TestClient(app)
    client.post("/login", data={"username": "admin", "password": "secret"})
    return client, Repository(conn)


def test_users_page_lists_users(tmp_path):
    client, repo = _client(tmp_path)
    repo.upsert_user(telegram_id=1001, username="alice", first_name="Alice", last_name=None)

    response = client.get("/users")

    assert response.status_code == 200
    assert "alice" in response.text


def test_create_user_from_web(tmp_path):
    client, repo = _client(tmp_path)

    response = client.post(
        "/users/new",
        data={
            "telegram_id": "1001",
            "username": "alice",
            "first_name": "Alice",
            "last_name": "",
            "status": "active",
            "is_admin": "1",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    user = repo.get_user_by_telegram_id(1001)
    assert user["username"] == "alice"
    assert user["is_admin"] == 1
```

- [ ] **Step 2: Run users tests to verify they fail**

Run:

```bash
python -m pytest tests/web/test_users.py -q
```

Expected: FAIL because routes do not exist.

- [ ] **Step 3: Add repository methods**

In `app/db/repositories.py`, add:

```python
def update_user_admin_fields(
    self,
    *,
    user_id: int,
    telegram_id: int,
    username: str | None,
    first_name: str | None,
    last_name: str | None,
    status: str,
    is_admin: bool,
) -> None:
    self._conn.execute(
        """
        UPDATE users
        SET telegram_id = ?,
            username = ?,
            first_name = ?,
            last_name = ?,
            status = ?,
            is_admin = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (telegram_id, username, first_name, last_name, status, int(is_admin), user_id),
    )
    self._commit()
```

- [ ] **Step 4: Add user routes**

In `app/web/app.py`, add:

```python
@app.get("/users", response_class=HTMLResponse)
async def users(request: Request, repo: Repository = Depends(_repo)):
    auth = _require_auth(request)
    if auth is not None:
        return auth
    return templates.TemplateResponse(
        "users.html",
        {"request": request, "users": repo.list_users_for_admin(limit=200)},
    )


@app.get("/users/new", response_class=HTMLResponse)
async def user_new(request: Request):
    auth = _require_auth(request)
    if auth is not None:
        return auth
    return templates.TemplateResponse("user_form.html", {"request": request, "user": None})


@app.post("/users/new")
async def user_create(
    request: Request,
    telegram_id: int = Form(...),
    username: str = Form(""),
    first_name: str = Form(""),
    last_name: str = Form(""),
    status: str = Form("active"),
    is_admin: str = Form("0"),
    repo: Repository = Depends(_repo),
):
    auth = _require_auth(request)
    if auth is not None:
        return auth
    user_id = repo.upsert_user(
        telegram_id=telegram_id,
        username=username or None,
        first_name=first_name or None,
        last_name=last_name or None,
    )
    repo.update_user_admin_fields(
        user_id=user_id,
        telegram_id=telegram_id,
        username=username or None,
        first_name=first_name or None,
        last_name=last_name or None,
        status=status,
        is_admin=is_admin == "1",
    )
    repo.record_admin_action(admin_telegram_id=0, action="web_user_create", target_user_id=user_id)
    return RedirectResponse(f"/users/{user_id}", status_code=303)
```

Also add `GET /users/{user_id}`, `GET /users/{user_id}/edit`, `POST /users/{user_id}/edit`, `POST /users/{user_id}/block`, and `POST /users/{user_id}/delete` using `update_user_admin_fields()` and `record_admin_action()`.

- [ ] **Step 5: Add templates**

`users.html`:

```html
{% extends "base.html" %}
{% block content %}
<h1>Users</h1>
<p><a class="button" href="/users/new">Add user</a></p>
<table>
  <thead><tr><th>ID</th><th>Telegram</th><th>Name</th><th>Status</th><th>Admin</th><th>Devices</th></tr></thead>
  <tbody>
    {% for user in users %}
    <tr>
      <td><a href="/users/{{ user.id }}">{{ user.id }}</a></td>
      <td>{{ user.telegram_id }} {% if user.username %}@{{ user.username }}{% endif %}</td>
      <td>{{ user.first_name or "" }} {{ user.last_name or "" }}</td>
      <td>{{ user.status }}</td>
      <td>{{ "yes" if user.is_admin else "no" }}</td>
      <td>{{ user.active_device_count }}/{{ user.total_device_count }}</td>
    </tr>
    {% endfor %}
  </tbody>
</table>
{% endblock %}
```

`user_form.html` includes inputs for `telegram_id`, `username`, `first_name`, `last_name`, `status`, `is_admin`.

- [ ] **Step 6: Run users tests**

Run:

```bash
python -m pytest tests/web/test_users.py -q
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add app/db/repositories.py app/web tests/web/test_users.py
git commit -m "Add web admin user management"
```

---

### Task 6: Servers CRUD And Live Health

**Files:**
- Modify: `app/db/repositories.py`
- Create: `app/web/server_health.py`
- Modify: `app/web/app.py`
- Create: `app/web/templates/servers.html`
- Create: `app/web/templates/server_form.html`
- Create: `app/web/templates/server_detail.html`
- Create: `app/web/templates/server_health.html`
- Test: `tests/web/test_servers.py`
- Test: `tests/web/test_server_health.py`

- [ ] **Step 1: Write failing server health unit tests**

Create `tests/web/test_server_health.py`:

```python
from app.server.report import CheckResult, ServerCheckReport
from app.web.server_health import summarize_check_report


def test_summarize_check_report_marks_online_when_all_ok():
    report = ServerCheckReport(
        server_name="debian-vps-1",
        results=[
            CheckResult("debian", "ok", "Debian detected", ""),
            CheckResult("interface", "ok", "active", ""),
            CheckResult("udp-port", "ok", "visible", ""),
        ],
    )

    summary = summarize_check_report(report, latency_ms=25)

    assert summary.status == "online"
    assert summary.latency_ms == 25
    assert summary.ssh_ok is True
    assert summary.awg_ok is True
    assert summary.udp_port_ok is True


def test_summarize_check_report_marks_degraded_on_warning():
    report = ServerCheckReport(
        server_name="debian-vps-1",
        results=[
            CheckResult("debian", "ok", "Debian detected", ""),
            CheckResult("interface", "warning", "not active", "inactive"),
            CheckResult("udp-port", "ok", "visible", ""),
        ],
    )

    summary = summarize_check_report(report, latency_ms=30)

    assert summary.status == "degraded"
    assert summary.awg_ok is False
```

- [ ] **Step 2: Run server health tests to verify they fail**

Run:

```bash
python -m pytest tests/web/test_server_health.py -q
```

Expected: FAIL because `app.web.server_health` does not exist.

- [ ] **Step 3: Implement server health summary**

Create `app/web/server_health.py`:

```python
from __future__ import annotations

from dataclasses import dataclass

from app.server.report import ServerCheckReport


@dataclass(frozen=True)
class ServerHealthSummary:
    status: str
    latency_ms: int | None
    ssh_ok: bool
    awg_ok: bool
    udp_port_ok: bool
    error: str | None


def summarize_check_report(report: ServerCheckReport, *, latency_ms: int | None) -> ServerHealthSummary:
    statuses = {result.name: result.status for result in report.results}
    has_error = any(result.status == "error" for result in report.results)
    has_warning = any(result.status == "warning" for result in report.results)
    status = "offline" if has_error else "degraded" if has_warning else "online"
    error = "\n".join(
        f"{result.name}: {result.message}"
        for result in report.results
        if result.status in {"error", "warning"}
    ) or None
    return ServerHealthSummary(
        status=status,
        latency_ms=latency_ms,
        ssh_ok=not has_error,
        awg_ok=statuses.get("interface") == "ok",
        udp_port_ok=statuses.get("udp-port") == "ok",
        error=error,
    )
```

- [ ] **Step 4: Write failing server route tests**

Create `tests/web/test_servers.py`:

```python
from fastapi.testclient import TestClient

from app.config import Settings
from app.db.connection import connect
from app.db.repositories import Repository
from app.db.schema import initialize_schema
from app.web.app import create_web_app
from app.web.auth import create_password_hash


def _client(tmp_path):
    settings = Settings(
        _env_file=None,
        telegram_bot_token="TEST_TOKEN",
        app_secret_key="test-secret",
        database_path=str(tmp_path / "app.sqlite3"),
        web_admin_username="admin",
        web_admin_password_hash=create_password_hash("secret"),
        web_admin_session_secret="session-secret-value-with-32-plus-chars",
    )
    conn = connect(settings.database_path)
    initialize_schema(conn)
    app = create_web_app(settings=settings)
    client = TestClient(app)
    client.post("/login", data={"username": "admin", "password": "secret"})
    return client, Repository(conn)


def test_servers_page_shows_health_state(tmp_path):
    client, repo = _client(tmp_path)
    server_id = repo.ensure_default_server(name="local", network_cidr="10.8.0.0/24")
    repo.record_server_health(
        server_id=server_id,
        status="online",
        latency_ms=22,
        ssh_ok=True,
        awg_ok=True,
        udp_port_ok=True,
        error=None,
    )

    response = client.get("/servers")

    assert response.status_code == 200
    assert "local" in response.text
    assert "online" in response.text
    assert "22 ms" in response.text
```

- [ ] **Step 5: Run server route tests to verify they fail**

Run:

```bash
python -m pytest tests/web/test_servers.py -q
```

Expected: FAIL because `/servers` route does not exist.

- [ ] **Step 6: Implement server routes and templates**

Add `/servers`, `/servers/new`, `/servers/{server_id}`, `/servers/{server_id}/edit`, `/servers/{server_id}/disable`, `/servers/{server_id}/health`, and `POST /servers/{server_id}/health/run`.

`servers.html`:

```html
{% extends "base.html" %}
{% block content %}
<h1>Servers</h1>
<p><a class="button" href="/servers/new">Add server</a></p>
<table>
  <thead><tr><th>Name</th><th>Host</th><th>VPN port</th><th>Manual status</th><th>Live</th><th>Latency</th><th>Checked</th><th>Devices</th></tr></thead>
  <tbody>
    {% for server in servers %}
    <tr>
      <td><a href="/servers/{{ server.id }}">{{ server.name }}</a></td>
      <td>{{ server.host }}</td>
      <td>{{ server.vpn_port }}</td>
      <td>{{ server.status }}</td>
      <td>{{ server.health_status or "unknown" }}</td>
      <td>{% if server.health_latency_ms is not none %}{{ server.health_latency_ms }} ms{% else %}-{% endif %}</td>
      <td>{{ server.health_checked_at or "-" }}</td>
      <td>{{ server.active_device_count }}/{{ server.total_device_count }}</td>
    </tr>
    {% endfor %}
  </tbody>
</table>
{% endblock %}
```

Use existing `load_server_config()` and `run_server_checks()` for full checks when the server exists in `servers.yml`; otherwise store `unknown` with an actionable error.

- [ ] **Step 7: Run server tests**

Run:

```bash
python -m pytest tests/web/test_server_health.py tests/web/test_servers.py -q
```

Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add app/db app/web tests/web/test_server_health.py tests/web/test_servers.py
git commit -m "Add web admin server management and health"
```

---

### Task 7: Orders, Logs, Settings Pages

**Files:**
- Modify: `app/web/app.py`
- Create: `app/web/logs.py`
- Create: `app/web/templates/orders.html`
- Create: `app/web/templates/logs.html`
- Create: `app/web/templates/settings.html`
- Test: `tests/web/test_logs_settings_orders.py`

- [ ] **Step 1: Write failing tests**

Create `tests/web/test_logs_settings_orders.py`:

```python
from fastapi.testclient import TestClient

from app.config import Settings
from app.db.connection import connect
from app.db.schema import initialize_schema
from app.web.app import create_web_app
from app.web.auth import create_password_hash
from app.web.logs import read_log_tail


def test_read_log_tail_redacts_and_limits_lines(tmp_path):
    log_path = tmp_path / "app.log"
    log_path.write_text(
        "\n".join(
            [
                "one",
                "TELEGRAM_BOT_TOKEN=123:abc",
                "three",
            ]
        ),
        encoding="utf-8",
    )

    lines = read_log_tail(log_path, max_lines=2)

    assert lines == ["TELEGRAM_BOT_TOKEN=[REDACTED]", "three"]


def test_settings_page_redacts_secrets(tmp_path):
    settings = Settings(
        _env_file=None,
        telegram_bot_token="123:abc",
        app_secret_key="test-secret",
        database_path=str(tmp_path / "app.sqlite3"),
        web_admin_username="admin",
        web_admin_password_hash=create_password_hash("secret"),
        web_admin_session_secret="session-secret-value-with-32-plus-chars",
    )
    conn = connect(settings.database_path)
    initialize_schema(conn)
    app = create_web_app(settings=settings)
    client = TestClient(app)
    client.post("/login", data={"username": "admin", "password": "secret"})

    response = client.get("/settings")

    assert response.status_code == 200
    assert "123:abc" not in response.text
    assert "[REDACTED]" in response.text
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
python -m pytest tests/web/test_logs_settings_orders.py -q
```

Expected: FAIL because log helpers and pages do not exist.

- [ ] **Step 3: Implement log helper**

Create `app/web/logs.py`:

```python
from pathlib import Path

from app.security.redaction import redact


def read_log_tail(path: str | Path, *, max_lines: int) -> list[str]:
    log_path = Path(path)
    if not log_path.exists():
        return []
    lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
    return [redact(line) for line in lines[-max_lines:]]
```

- [ ] **Step 4: Implement pages**

Add `/orders`, `/logs`, and `/settings` routes. Use `repo.list_orders_for_admin(limit=200)`, `read_log_tail(settings.app_log_path, max_lines=settings.app_log_max_lines)`, and `redact()` for settings values.

- [ ] **Step 5: Add templates**

`logs.html`:

```html
{% extends "base.html" %}
{% block content %}
<h1>Logs</h1>
<pre class="log-view">{% for line in lines %}{{ line }}
{% endfor %}</pre>
{% endblock %}
```

`settings.html`:

```html
{% extends "base.html" %}
{% block content %}
<h1>Settings</h1>
<table>
  {% for key, value in settings_items %}
  <tr><th>{{ key }}</th><td>{{ value }}</td></tr>
  {% endfor %}
</table>
{% endblock %}
```

- [ ] **Step 6: Run tests**

Run:

```bash
python -m pytest tests/web/test_logs_settings_orders.py -q
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add app/web tests/web/test_logs_settings_orders.py
git commit -m "Add web admin logs and settings pages"
```

---

### Task 8: CLI Serve, Docs, And Full Verification

**Files:**
- Modify: `app/cli.py`
- Modify: `docs/PRODUCTION_VPS_CHECKLIST.ru.md`
- Modify: `docs/PRODUCTION_VPS_CHECKLIST.en.md`
- Test: `tests/web/test_cli_web.py`

- [ ] **Step 1: Write failing CLI test**

Create `tests/web/test_cli_web.py`:

```python
from app.cli import build_parser


def test_cli_accepts_web_serve_options():
    parser = build_parser()

    args = parser.parse_args(["web", "serve", "--host", "0.0.0.0", "--port", "3030"])

    assert args.command == "web"
    assert args.web_command == "serve"
    assert args.host == "0.0.0.0"
    assert args.port == 3030
```

- [ ] **Step 2: Run CLI test to verify it fails**

Run:

```bash
python -m pytest tests/web/test_cli_web.py -q
```

Expected: FAIL because `web serve` does not exist.

- [ ] **Step 3: Implement CLI serve**

In `app/cli.py`, add parser:

```python
web = sub.add_parser("web")
web_sub = web.add_subparsers(dest="web_command", required=True)
serve = web_sub.add_parser("serve")
serve.add_argument("--host", default=None)
serve.add_argument("--port", type=int, default=None)
```

In `main()`:

```python
elif args.command == "web" and args.web_command == "serve":
    import uvicorn
    from app.config import Settings
    from app.web.app import create_web_app

    settings = Settings()
    app = create_web_app(settings=settings)
    uvicorn.run(
        app,
        host=args.host or settings.web_admin_host,
        port=args.port or settings.web_admin_port,
    )
```

- [ ] **Step 4: Update VPS checklist**

Add to RU/EN production checklist:

```bash
python - <<'PY'
from app.web.auth import create_password_hash
print(create_password_hash("replace-this-password"))
PY
python -m app.cli web serve --host 0.0.0.0 --port 3030
```

Mention that port `3030` should be protected by firewall/VPN/reverse proxy.

- [ ] **Step 5: Run full tests**

Run:

```bash
python -m pytest tests -q
git diff --check
```

Expected: all tests pass and `git diff --check` prints nothing.

- [ ] **Step 6: Commit**

```bash
git add app/cli.py docs/PRODUCTION_VPS_CHECKLIST.ru.md docs/PRODUCTION_VPS_CHECKLIST.en.md tests/web/test_cli_web.py
git commit -m "Add web admin serve command"
```

---

## Final Verification

- [ ] Run full test suite:

```bash
python -m pytest tests -q
```

Expected: all tests pass.

- [ ] Run whitespace check:

```bash
git diff --check
```

Expected: no output.

- [ ] Manual local smoke test:

```bash
python -m app.cli web serve --host 127.0.0.1 --port 3030
```

Open `http://127.0.0.1:3030/login`, log in, verify Dashboard, Users, Servers, Logs, Settings pages.

- [ ] VPS update path:

```bash
cd /home/amn2
git pull --ff-only origin codex-vps-test-prep
source venv/bin/activate
python -m pip install -e .
python -m app.cli web serve --host 0.0.0.0 --port 3030
```

---

## Plan Self-Review Notes

- Covers auth, users, servers, server health, logs, settings, CLI, docs, and tests.
- Uses FastAPI/Jinja2 as approved in the spec.
- Keeps web panel separate from Telegram bot process.
- Uses soft-delete/disable instead of physical deletion.
- Does not store SSH private keys, passwords, PSK, bot token, proxy credentials, or `APP_SECRET_KEY` in UI.
- Includes server health display for every server with online/degraded/offline/unknown, latency, check time, and latest error.
