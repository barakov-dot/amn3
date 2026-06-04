# AMN2 API/Web Panel Finish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finish the next safe API/web-panel slice by adding web-admin visibility and controls for the already-merged read-only API baseline without enabling live VPS writes.

**Architecture:** Keep the API route surface read-only for server and metrics data. Add web-panel pages that use existing repository/service boundaries for API readiness and API token lifecycle, while preserving hash-only token storage and one-time raw token display. VPS verification remains loopback-only with `VPS_APPLY_ENABLED=false`; SSH/server dry-run is a separate gate.

**Tech Stack:** Python, FastAPI, Jinja2 templates, SQLite repository layer, pytest, AMN3 VPS smoke scripts.

---

## File Structure

- Modify `app/web/app.py`: add authenticated web routes for API readiness and API tokens; keep route handlers thin and repository-backed.
- Create `app/web/templates/api_readiness.html`: read-only API baseline status page with no secret-bearing output.
- Create `app/web/templates/api_tokens.html`: API token list/issue/revoke page with one-time raw token display.
- Modify `app/web/templates/base.html`: add navigation links for API readiness and API tokens.
- Modify `app/web/static/admin.css`: add compact table/form styles only if existing styles do not cover the new pages.
- Create `tests/web/test_api_readiness.py`: TestClient coverage for route auth, no secret markers, and readiness data.
- Create `tests/web/test_api_tokens.py`: TestClient coverage for token issue/revoke, one-time display, no token hash/raw token leakage after redirect.
- Modify `tests/security/test_route_policy_bindings.py` or the current route policy binding test file: bind new web routes to existing policies.
- Modify AMN3 `docs/AMN2_API_WEB_PANEL_VPS_TEST_RUNBOOK.ru.md`: update only after implementation changes alter VPS commands.

## Scope Boundaries

Allowed in this slice:

- web-admin-only routes;
- local DB API token issue/list/revoke;
- API readiness/status using aggregate-only data;
- route policy tests;
- local pytest suite;
- VPS loopback API smoke and web UI smoke with `VPS_APPLY_ENABLED=false`.

Blocked in this slice:

- `/api/clients` write CRUD;
- API `config:read`;
- public/self-service config download;
- backup/import/reboot;
- Local Agent `/configs`;
- live peer apply/revoke;
- web routes that trigger live Docker writes.

### Task 1: API Readiness Web Page

**Files:**
- Modify: `app/web/app.py`
- Create: `app/web/templates/api_readiness.html`
- Modify: `app/web/templates/base.html`
- Test: `tests/web/test_api_readiness.py`

- [ ] **Step 1: Write failing route-auth test**

Create `tests/web/test_api_readiness.py`:

```python
from pathlib import Path

from fastapi.testclient import TestClient

from app.config.settings import Settings
from app.db.connection import connect
from app.db.repositories import Repository
from app.db.schema import initialize_schema
from app.web.app import create_web_app


def test_api_readiness_requires_login(tmp_path: Path):
    settings = _settings(tmp_path)
    client = TestClient(create_web_app(settings), base_url="https://testserver")

    response = client.get("/api-readiness")

    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_api_readiness_shows_aggregate_status_without_secrets(tmp_path: Path):
    settings = _settings(tmp_path)
    _seed_server(Path(settings.database_path))
    client = _authenticated_client(settings)

    response = client.get("/api-readiness")

    assert response.status_code == 200
    assert "API readiness" in response.text
    assert "server:read" in response.text
    assert "metrics:read" in response.text
    forbidden = ["PrivateKey", "PresharedKey", "vpn://", "token_hash", "Authorization", ".conf"]
    assert all(marker not in response.text for marker in forbidden)


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        database_path=tmp_path / "amneziya.sqlite3",
        web_admin_enabled=True,
        web_admin_username="admin",
        web_admin_password_hash="$2b$12$rY2xVh6uYkJHge0Q6R0i0O0TVQtfW8QGCTC2Yj6HphwyeuGQm2G5G",
        web_admin_session_secret="test-session-secret",
    )


def _authenticated_client(settings: Settings) -> TestClient:
    client = TestClient(create_web_app(settings), base_url="https://testserver")
    response = client.post("/login", data={"username": "admin", "password": "password"})
    assert response.status_code == 303
    return client


def _seed_server(db_path: Path) -> None:
    conn = connect(db_path)
    try:
        initialize_schema(conn)
        repo = Repository(conn)
        repo.upsert_server_config(
            name="local",
            host="127.0.0.1",
            ssh_port=22,
            endpoint_host="127.0.0.1",
            vpn_port=51820,
            vpn_network_cidr="10.8.1.0/24",
            server_address="10.8.1.1/24",
            server_public_key="public-key",
            runtime="docker",
            firewall="none",
            max_devices=100,
        )
    finally:
        conn.close()
```

- [ ] **Step 2: Run failing test**

Run in `C:\Users\SooL\Documents\Amneziya`:

```powershell
pytest tests/web/test_api_readiness.py -q
```

Expected before implementation: route returns `404` or missing template.

- [ ] **Step 3: Implement route and template**

Add authenticated `GET /api-readiness` in `app/web/app.py`. The handler must load only aggregate counts and current API route/scope names. It must not read `.env`, token hashes, configs or key material.

Create `app/web/templates/api_readiness.html` with:

```html
{% extends "base.html" %}

{% block content %}
<section class="page-header">
  <h1>API readiness</h1>
  <p>Loopback-only read API baseline. Remote writes, config delivery and client lifecycle routes remain gated.</p>
</section>

<section class="panel">
  <h2>Allowed read scopes</h2>
  <table class="settings-table">
    <tbody>
      {% for scope in allowed_scopes %}
      <tr>
        <td><code>{{ scope }}</code></td>
        <td>read-only</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</section>

<section class="panel">
  <h2>Current aggregate state</h2>
  <table class="settings-table">
    <tbody>
      <tr><td>Servers</td><td>{{ metrics.servers_total }}</td></tr>
      <tr><td>Users</td><td>{{ metrics.users_total }}</td></tr>
      <tr><td>Devices</td><td>{{ metrics.devices_total }}</td></tr>
    </tbody>
  </table>
</section>
{% endblock %}
```

Add a base navigation link:

```html
<a class="nav-link" href="/api-readiness">API</a>
```

- [ ] **Step 4: Run test**

```powershell
pytest tests/web/test_api_readiness.py -q
```

Expected: `2 passed`.

### Task 2: API Token Lifecycle Web Page

**Files:**
- Modify: `app/web/app.py`
- Create: `app/web/templates/api_tokens.html`
- Modify: `app/web/templates/base.html`
- Test: `tests/web/test_api_tokens.py`

- [ ] **Step 1: Write failing tests**

Create `tests/web/test_api_tokens.py` with tests for:

- login required for `GET /api-tokens`;
- issue form accepts `name`, `owner_label`, selected scopes, expiry days;
- response displays raw token exactly once after issue;
- list page after refresh does not display raw token or token hash;
- revoke form marks token revoked and stores safe reason;
- invalid scope is rejected with `400` or form error.

Use existing `run_api_token_issue`, `run_api_token_revoke` and repository helpers rather than duplicating token hashing.

- [ ] **Step 2: Run failing tests**

```powershell
pytest tests/web/test_api_tokens.py -q
```

Expected before implementation: `404` for `/api-tokens`.

- [ ] **Step 3: Implement minimal web routes**

Add routes:

- `GET /api-tokens`: list token id, name, owner, scopes, expires_at, revoked status, last_used_at; never show token hash.
- `POST /api-tokens/issue`: issue token with allowed scopes only: `server:read`, `metrics:read`; show raw token in the immediate response page only.
- `POST /api-tokens/{token_id}/revoke`: revoke with reason `web-admin-revoke`.

Keep raw token out of session, DB metadata, logs and redirects.

- [ ] **Step 4: Implement template**

Create `app/web/templates/api_tokens.html` with:

- issue form;
- one-time raw token panel only when route context includes `issued_raw_token`;
- token table with safe fields only;
- revoke button protected by CSRF.

- [ ] **Step 5: Run focused tests**

```powershell
pytest tests/web/test_api_tokens.py tests/api/test_cli_tokens.py -q
```

Expected: focused tests pass with the existing Starlette/httpx warning allowed.

### Task 3: Route Policy Binding

**Files:**
- Modify: route policy binding test file currently covering web routes
- Modify: route inventory docs if the repo keeps route policy docs in-tree

- [ ] **Step 1: Add expected bindings**

Bind:

- `web.api_readiness.index`: actor `web-admin`, risk `read-only`, secret class `none`;
- `web.api_tokens.index`: actor `web-admin`, risk `read-only`, secret class `api-token-metadata`;
- `web.api_tokens.issue`: actor `web-admin`, risk `state-write-local-db`, secret class `raw-api-token-one-time`;
- `web.api_tokens.revoke`: actor `web-admin`, risk `state-write-local-db`, secret class `none`.

- [ ] **Step 2: Run binding tests**

```powershell
pytest tests/security/test_route_policy_bindings.py -q
```

Expected: route binding tests pass.

### Task 4: Full Local Gate

**Files:**
- No new files.

- [ ] **Step 1: Run focused web/API suite**

```powershell
pytest tests/api tests/web/test_api_readiness.py tests/web/test_api_tokens.py -q
```

Expected: all selected tests pass.

- [ ] **Step 2: Run full suite**

```powershell
pytest -q
```

Expected: full suite passes with known Starlette/httpx warning only.

- [ ] **Step 3: Security scan by grep**

```powershell
rg -n "raw_token|token_hash|Authorization|PrivateKey|PresharedKey|vpn://|\\.conf" app/web/templates app/web/static tests/web
```

Expected: matches only in tests asserting absence or in explicitly safe warning text; no template prints raw token outside the one-time issue result.

### Task 5: VPS Gate

**Files:**
- Use: `docs/AMN2_API_WEB_PANEL_VPS_TEST_RUNBOOK.ru.md`

- [ ] **Step 1: Update VPS package from AMN3**

Run the update commands from `docs/AMN2_API_WEB_PANEL_VPS_TEST_RUNBOOK.ru.md`.

- [ ] **Step 2: API-only smoke**

Run:

```bash
cd /opt/amn2
source venv/bin/activate
export VPS_APPLY_ENABLED=false
export AMN2_RUN_PREFLIGHT=0
export AMN2_SYNC_SERVER_CONFIG=1
export AMN2_REQUIRE_SERVER_DB_SYNC=1
export AMN2_SERVER_NAME=local
bash ./amn2_api_loopback_smoke.sh
```

Expected:

```text
VPS verdict: pass
preflight_status: skipped
server_db_sync_status: passed
api_smoke_status: passed
auth_status: passed
listener_status: passed
audit_status: passed
```

- [ ] **Step 3: Web loopback smoke**

Run:

```bash
cd /opt/amn2
source venv/bin/activate
export VPS_APPLY_ENABLED=false
python -m app.cli web serve --host 127.0.0.1 --port 3030
```

Open through tunnel:

```bash
ssh -L 3030:127.0.0.1:3030 root@<VPS_HOST>
```

Expected:

- `/login` works;
- `/api-readiness` works;
- `/api-tokens` works;
- issuing token shows raw token once;
- refresh/list does not show raw token or token hash;
- revoke works;
- API smoke with revoked token gets `401`;
- no live peer apply/revoke/config delivery happens.

## Self-Review

Spec coverage:

- API/web-panel continuation is covered by API readiness and API token lifecycle pages.
- VPS testing instruction is covered by `docs/AMN2_API_WEB_PANEL_VPS_TEST_RUNBOOK.ru.md` and Task 5.
- Safety boundary covers no live apply, no config delivery, no `/api/clients` write CRUD.

Placeholder scan:

- This plan uses `<VPS_HOST>` only as an operator-owned value that must not be committed or posted to chat.
- No implementation task contains deferred placeholder language.

Type consistency:

- Route names, scopes and status fields match the current read-only API baseline: `server:read`, `metrics:read`, `server_db_sync_status`, `VPS_APPLY_ENABLED=false`.
