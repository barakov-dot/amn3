# AMN2 Post Dry-Run Read-Only Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a native `amn2` read-only integration status surface after the verified VPS dry-run gate, without enabling live remote writes or expanding into client/config delivery APIs.

**Architecture:** Keep the new surface policy-driven and local-data-only. Add a small service that reports read-only API/web/remote-operation gate state from code-owned constants and aggregate repository counts, then expose it through an authenticated web page and a scoped read-only API route. The service must not call SSH, read `.env`, read `servers.yml` secrets, emit config artifacts, or claim Phase 2 live-write verification.

**Tech Stack:** Python, FastAPI, Jinja2 templates, SQLite repository layer, pytest, existing `amn2` route/surface policy tests, AMN3 evidence documents.

---

## Current Baseline

Use this plan from `C:\Users\SooL\Documents\Amneziya` after refreshing from the stable branch:

```text
repo: C:\Users\SooL\Documents\Amneziya
stable branch: codex-vps-test-prep
stable head: 708c98e Merge pull request #7 from barakov-dot/codex/remote-operation-vps-gate-prep
remote-operation candidate: codex/remote-operation-vps-gate-prep
remote-operation candidate head: 7281254 Merge stable API web panel baseline into remote operation gate
AMN3 evidence: research/amn2/remote-operation-vps-gate-evidence-2026-06-04.md
VPS decision: dry-run-only-pass
```

The real VPS evidence confirms the read-only/API/web baseline and the remote-operation Phase 1 dry-run contract. It does not confirm live `apply-peer --apply` or `revoke-peer --apply`.

## Scope Boundaries

Allowed in this slice:

- authenticated web-admin integration status page;
- read-only API status route using existing API token auth;
- aggregate repository counts only;
- code-owned status constants for gate decisions;
- route/auth/surface policy tests;
- local pytest verification;
- optional loopback VPS smoke after implementation, with `VPS_APPLY_ENABLED=false`.

Blocked in this slice:

- `/api/clients` write CRUD;
- API `config:read`;
- public or self-service config delivery;
- Local Agent `/configs`;
- Local Agent mutation routes;
- live peer apply/revoke;
- web buttons that call SSH, Docker writes, sync peers, restart containers, emit configs, or mutate runtime state;
- detailed per-peer metrics, raw WireGuard/Amnezia config, QR payloads, `vpn://`, private keys, PSK, token hashes, raw bearer tokens, Authorization headers, command stdout/stderr.

## File Structure

- Create `app/services/integration_status.py`: pure local service that builds a serializable read-only status report from an existing `Repository`.
- Modify `app/api/app.py`: add `GET /api/integration/status` guarded by `server:read`.
- Modify `app/web/app.py`: add authenticated `GET /integration-status`.
- Create `app/web/templates/integration_status.html`: compact operator page for current gates and blocked lanes.
- Modify `app/web/templates/base.html`: add one navigation link for integration status.
- Modify `app/security/surface_policy.py`: add or extend route policy entries for the new API and web routes.
- Modify `app/security/surface_bindings.py` or the current route binding inventory file: bind the new routes to the policy matrix.
- Create `tests/services/test_integration_status_service.py`: service contract and forbidden-marker tests.
- Create `tests/api/test_api_integration_status.py`: API auth/scope/audit/no-secret tests.
- Create `tests/web/test_web_integration_status.py`: web auth/render/no-secret tests.
- Modify `tests/security/test_surface_policy_bindings.py`: web route binding drift guard for the new route.
- Update AMN3 after implementation: `research/amn2/transfer-backlog.md`, `docs/PROJECT_STATUS_CURRENT.ru.md`, and a new implementation evidence note.

## Report Contract

The service returns this shape. Field names are intentionally stable because both API and web will consume the same report.

```python
{
    "status": "dry_run_ready",
    "summary": "Read-only API/web integration is available; remote writes require a separate live gate.",
    "api_baseline": {
        "status": "verified_read_only",
        "stable_head": "708c98e",
        "api_web_baseline_head": "294803e",
        "allowed_scopes": ["metrics:read", "server:read"],
        "write_routes_enabled": False,
    },
    "remote_operation_gate": {
        "candidate_head": "7281254",
        "stable_merge_head": "708c98e",
        "phase_1": "dry_run_only_pass",
        "phase_2": "not_run",
        "write_operations_enabled": False,
    },
    "aggregate_state": {
        "servers": 0,
        "users": 0,
        "devices": 0,
    },
    "allowed_lanes": [
        "read-only API status",
        "aggregate metrics",
        "web evidence UX",
        "API token lifecycle administration",
    ],
    "blocked_lanes": [
        "live peer apply/revoke",
        "/api/clients write CRUD",
        "API config:read",
        "public/self-service config delivery",
        "Local Agent configs or mutations",
        "backup/import/reboot routes",
    ],
    "next_gate": "single test peer live apply/revoke requires separate operator confirmation",
}
```

Do not include environment values, server hostnames, interface names, container names, public keys, preshared keys, token identifiers, token names, raw tokens, token hashes, config paths, command strings, stdout, stderr, peer IPs, endpoint hosts, or per-peer traffic.

### Task 1: Service Contract

**Files:**
- Create: `app/services/integration_status.py`
- Create: `tests/services/test_integration_status_service.py`

- [ ] **Step 1: Write failing service tests**

Create `tests/services/test_integration_status_service.py`:

```python
from pathlib import Path

from app.db.connection import connect
from app.db.repositories import Repository
from app.db.schema import initialize_schema
from app.services.integration_status import build_integration_status


FORBIDDEN_MARKERS = [
    "PrivateKey",
    "PresharedKey",
    "Authorization",
    "token_hash",
    "vpn://",
    ".conf",
    "root@",
    "docker exec",
    "awg show",
]


def test_build_integration_status_reports_dry_run_gate_without_write_enablement(tmp_path: Path):
    db_path = tmp_path / "amneziya.sqlite3"
    conn = connect(db_path)
    try:
        initialize_schema(conn)
        repo = Repository(conn)
        _seed_server(repo)
        report = build_integration_status(repo)
    finally:
        conn.close()

    assert report["status"] == "dry_run_ready"
    assert report["api_baseline"]["status"] == "verified_read_only"
    assert report["api_baseline"]["stable_head"] == "708c98e"
    assert report["api_baseline"]["api_web_baseline_head"] == "294803e"
    assert report["api_baseline"]["write_routes_enabled"] is False
    assert report["remote_operation_gate"]["candidate_head"] == "7281254"
    assert report["remote_operation_gate"]["stable_merge_head"] == "708c98e"
    assert report["remote_operation_gate"]["phase_1"] == "dry_run_only_pass"
    assert report["remote_operation_gate"]["phase_2"] == "not_run"
    assert report["remote_operation_gate"]["write_operations_enabled"] is False
    assert report["aggregate_state"]["servers"] == 1
    assert "live peer apply/revoke" in report["blocked_lanes"]
    assert "/api/clients write CRUD" in report["blocked_lanes"]


def test_build_integration_status_contains_no_secret_or_command_markers(tmp_path: Path):
    db_path = tmp_path / "amneziya.sqlite3"
    conn = connect(db_path)
    try:
        initialize_schema(conn)
        repo = Repository(conn)
        _seed_server(repo)
        report_text = repr(build_integration_status(repo))
    finally:
        conn.close()

    for marker in FORBIDDEN_MARKERS:
        assert marker not in report_text


def _seed_server(repo: Repository) -> None:
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
```

- [ ] **Step 2: Run the focused RED test**

Run:

```powershell
python -m pytest tests/services/test_integration_status_service.py -q
```

Expected before implementation:

```text
ModuleNotFoundError: No module named 'app.services.integration_status'
```

- [ ] **Step 3: Implement the service**

Create `app/services/integration_status.py`:

```python
from __future__ import annotations

from typing import Any

from app.db.repositories import Repository


ALLOWED_API_SCOPES = ["metrics:read", "server:read"]
ALLOWED_LANES = [
    "read-only API status",
    "aggregate metrics",
    "web evidence UX",
    "API token lifecycle administration",
]
BLOCKED_LANES = [
    "live peer apply/revoke",
    "/api/clients write CRUD",
    "API config:read",
    "public/self-service config delivery",
    "Local Agent configs or mutations",
    "backup/import/reboot routes",
]


def build_integration_status(repo: Repository) -> dict[str, Any]:
    aggregate_state = _load_aggregate_state(repo)
    return {
        "status": "dry_run_ready",
        "summary": "Read-only API/web integration is available; remote writes require a separate live gate.",
        "api_baseline": {
            "status": "verified_read_only",
            "stable_head": "708c98e",
            "api_web_baseline_head": "294803e",
            "allowed_scopes": list(ALLOWED_API_SCOPES),
            "write_routes_enabled": False,
        },
        "remote_operation_gate": {
            "candidate_head": "7281254",
            "stable_merge_head": "708c98e",
            "phase_1": "dry_run_only_pass",
            "phase_2": "not_run",
            "write_operations_enabled": False,
        },
        "aggregate_state": aggregate_state,
        "allowed_lanes": list(ALLOWED_LANES),
        "blocked_lanes": list(BLOCKED_LANES),
        "next_gate": "single test peer live apply/revoke requires separate operator confirmation",
    }


def _load_aggregate_state(repo: Repository) -> dict[str, int]:
    summary = repo.get_api_metrics_summary()
    return {
        "servers": summary["servers_total"],
        "users": summary["users_total"],
        "devices": summary["devices_total"],
    }
```

- [ ] **Step 4: Run the focused service test**

Run:

```powershell
python -m pytest tests/services/test_integration_status_service.py -q
```

Expected:

```text
2 passed
```

- [ ] **Step 5: Commit Task 1**

Run:

```powershell
git add app/services/integration_status.py tests/services/test_integration_status_service.py
git commit -m "Add integration status service"
```

### Task 2: API Route

**Files:**
- Modify: `app/api/app.py`
- Create: `tests/api/test_api_integration_status.py`
- Modify: `app/security/surface_policy.py`

- [ ] **Step 1: Write failing API tests**

Create `tests/api/test_api_integration_status.py`:

```python
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.app import create_api_app
from app.config.settings import Settings
from app.db.connection import connect
from app.db.repositories import Repository
from app.db.schema import initialize_schema
from app.services.api_tokens import hash_api_token


def test_integration_status_requires_bearer_token(tmp_path: Path):
    client = TestClient(create_api_app(_settings(tmp_path)))

    response = client.get("/api/integration/status")

    assert response.status_code == 401


def test_integration_status_rejects_missing_server_read_scope(tmp_path: Path):
    settings = _settings(tmp_path)
    _store_token(settings, raw_token="metrics-token", scopes=["metrics:read"])
    client = TestClient(create_api_app(settings))

    response = client.get(
        "/api/integration/status",
        headers={"Authorization": "Bearer metrics-token"},
    )

    assert response.status_code == 403


def test_integration_status_returns_safe_read_only_report(tmp_path: Path):
    settings = _settings(tmp_path)
    _seed_server(Path(settings.database_path))
    _store_token(settings, raw_token="server-token", scopes=["server:read"])
    client = TestClient(create_api_app(settings))

    response = client.get(
        "/api/integration/status",
        headers={"Authorization": "Bearer server-token"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "dry_run_ready"
    assert payload["api_baseline"]["stable_head"] == "708c98e"
    assert payload["api_baseline"]["api_web_baseline_head"] == "294803e"
    assert payload["api_baseline"]["write_routes_enabled"] is False
    assert payload["remote_operation_gate"]["write_operations_enabled"] is False
    assert payload["remote_operation_gate"]["stable_merge_head"] == "708c98e"
    assert payload["remote_operation_gate"]["phase_2"] == "not_run"
    assert payload["aggregate_state"]["servers"] == 1
    assert "live peer apply/revoke" in payload["blocked_lanes"]
    forbidden = ["PrivateKey", "PresharedKey", "Authorization", "token_hash", "vpn://", ".conf"]
    assert all(marker not in response.text for marker in forbidden)


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        _env_file=None,
        telegram_bot_token="CHANGE_ME",
        app_secret_key="test-secret",
        database_path=str(tmp_path / "amneziya.sqlite3"),
    )


def _store_token(settings: Settings, *, raw_token: str, scopes: list[str]) -> None:
    conn = connect(Path(settings.database_path))
    try:
        initialize_schema(conn)
        repo = Repository(conn)
        repo.create_api_token(
            token_id=f"token-{raw_token}",
            name="Integration status test",
            owner_user_id=None,
            owner_label="tests",
            token_hash=hash_api_token(raw_token),
            scopes=scopes,
            expires_at="2099-01-01T00:00:00+00:00",
        )
    finally:
        conn.close()


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

- [ ] **Step 2: Run the API RED test**

Run:

```powershell
python -m pytest tests/api/test_api_integration_status.py -q
```

Expected before route implementation:

```text
1 failed, 2 passed
```

The exact failing assertion should be `404 != 200` for the safe report test, or all three tests may return `404` if the router does not intercept the route before auth.

- [ ] **Step 3: Add the API route**

In `app/api/app.py`, import the service:

```python
from app.services.integration_status import build_integration_status
```

Add this route near the existing read-only server/metrics routes:

```python
    @app.get("/api/integration/status")
    async def integration_status(
        repo: Repository = Depends(_repo),
        auth: ApiAuthContext = Depends(_require_scope("server:read")),
    ):
        payload = build_integration_status(repo)
        _record_api_read(repo, auth, path="/api/integration/status", scope="server:read")
        return payload
```

This uses the same authentication, scope validation and audit helpers as `/api/servers`.

- [ ] **Step 4: Add the API route surface policy**

In `app/security/surface_policy.py`, add this `_p(...)` entry next to the existing API entries:

```python
    _p(
        "api.integration.status",
        "api",
        "GET",
        "/api/integration/status",
        "api-client",
        "bearer token + server:read",
        "read-only",
        "none",
        (),
        ("scoped API token", "aggregate-only", "audit event", "no raw secret", "no SSH"),
        True,
        "Native amn2 read-only integration status route.",
        False,
        "implemented",
        ("tests/api/test_api_integration_status.py",),
        "Reports gate state and aggregate counts without enabling remote writes.",
        enables_new_behavior=True,
    ),
```

- [ ] **Step 5: Run the API and policy tests**

Run:

```powershell
python -m pytest tests/api/test_api_integration_status.py tests/security/test_surface_policy_bindings.py -q
```

Expected:

```text
all selected tests pass
```

- [ ] **Step 6: Commit Task 2**

Run:

```powershell
git add app/api/app.py app/security/surface_policy.py tests/api/test_api_integration_status.py
git commit -m "Add read-only integration status API"
```

### Task 3: Web Page

**Files:**
- Modify: `app/web/app.py`
- Create: `app/web/templates/integration_status.html`
- Modify: `app/web/templates/base.html`
- Modify: `app/security/surface_policy.py`
- Modify: `app/security/surface_bindings.py`
- Test: `tests/security/test_surface_policy_bindings.py`
- Create: `tests/web/test_web_integration_status.py`

- [ ] **Step 1: Write failing web tests**

Create `tests/web/test_web_integration_status.py`:

```python
import re
from pathlib import Path

from fastapi.testclient import TestClient

from app.config.settings import Settings
from app.db.connection import connect
from app.db.repositories import Repository
from app.db.schema import initialize_schema
from app.web.app import create_web_app
from app.web.auth import create_password_hash


def test_integration_status_page_requires_login(tmp_path: Path):
    client = TestClient(create_web_app(_settings(tmp_path)), base_url="https://testserver")

    response = client.get("/integration-status", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_integration_status_page_renders_gate_without_secret_markers(tmp_path: Path):
    settings = _settings(tmp_path)
    _seed_server(Path(settings.database_path))
    client = _authenticated_client(settings)

    response = client.get("/integration-status")

    assert response.status_code == 200
    assert "Integration status" in response.text
    assert "dry-run-only-pass" in response.text
    assert "Phase 2 live write gate" in response.text
    assert "live peer apply/revoke" in response.text
    assert "server:read" in response.text
    forbidden = ["PrivateKey", "PresharedKey", "Authorization", "token_hash", "vpn://", ".conf"]
    assert all(marker not in response.text for marker in forbidden)


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        _env_file=None,
        telegram_bot_token="TEST_TOKEN",
        app_secret_key="test-secret",
        database_path=str(tmp_path / "amneziya.sqlite3"),
        web_admin_username="root",
        web_admin_password_hash=create_password_hash(
            "correct-password",
            salt="test-salt",
        ),
        web_admin_session_secret="s" * 32,
        web_admin_session_cookie_secure=True,
    )


def _authenticated_client(settings: Settings) -> TestClient:
    client = TestClient(create_web_app(settings), base_url="https://testserver")
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

- [ ] **Step 2: Run the web RED test**

Run:

```powershell
python -m pytest tests/web/test_web_integration_status.py -q
```

Expected before implementation:

```text
404 response for /integration-status
```

- [ ] **Step 3: Add the web route**

In `app/web/app.py`, import:

```python
from app.services.integration_status import build_integration_status
```

Add:

```python
    @app.get("/integration-status")
    async def integration_status_index(request: Request):
        if not _is_authenticated(request):
            return RedirectResponse("/login", status_code=303)

        with _open_repository(actual_settings) as (repo, _conn):
            report = build_integration_status(repo)
        return templates.TemplateResponse(
            request,
            "integration_status.html",
            _template_context(
                request,
                title="Integration status",
                authenticated=True,
                report=report,
            ),
        )
```

This mirrors the existing `/api-readiness` route shape.

- [ ] **Step 4: Create the template**

Create `app/web/templates/integration_status.html`:

```html
{% extends "base.html" %}

{% block content %}
<section class="page-header">
  <p class="eyebrow">Read-only integration gate</p>
  <h1>Integration status</h1>
</section>

<section class="panel">
  <h2>Current decision</h2>
  <table class="settings-table">
    <tbody>
      <tr><td>Status</td><td>{{ report.status|replace("_", "-") }}</td></tr>
      <tr><td>API baseline</td><td>{{ report.api_baseline.status }} at {{ report.api_baseline.stable_head }}</td></tr>
      <tr><td>Remote operation Phase 1</td><td>{{ report.remote_operation_gate.phase_1|replace("_", "-") }}</td></tr>
      <tr><td>Phase 2 live write gate</td><td>{{ report.remote_operation_gate.phase_2|replace("_", "-") }}</td></tr>
      <tr><td>Write routes enabled</td><td>{{ report.api_baseline.write_routes_enabled }}</td></tr>
      <tr><td>Remote writes enabled</td><td>{{ report.remote_operation_gate.write_operations_enabled }}</td></tr>
    </tbody>
  </table>
</section>

<section class="panel">
  <h2>Allowed read scopes</h2>
  <table class="settings-table">
    <tbody>
      {% for scope in report.api_baseline.allowed_scopes %}
      <tr><td><code>{{ scope }}</code></td><td>read-only</td></tr>
      {% endfor %}
    </tbody>
  </table>
</section>

<section class="panel-grid">
  <article class="panel">
    <h2>Aggregate state</h2>
    <table class="settings-table">
      <tbody>
        <tr><td>Servers</td><td>{{ report.aggregate_state.servers }}</td></tr>
        <tr><td>Users</td><td>{{ report.aggregate_state.users }}</td></tr>
        <tr><td>Devices</td><td>{{ report.aggregate_state.devices }}</td></tr>
      </tbody>
    </table>
  </article>
  <article class="panel">
    <h2>Next gate</h2>
    <p>{{ report.next_gate }}</p>
  </article>
</section>

<section class="panel-grid">
  <article class="panel">
    <h2>Allowed lanes</h2>
    <ul class="plain-list">
      {% for lane in report.allowed_lanes %}
      <li>{{ lane }}</li>
      {% endfor %}
    </ul>
  </article>
  <article class="panel">
    <h2>Blocked lanes</h2>
    <ul class="plain-list">
      {% for lane in report.blocked_lanes %}
      <li>{{ lane }}</li>
      {% endfor %}
    </ul>
  </article>
</section>
{% endblock %}
```

- [ ] **Step 5: Add navigation**

In `app/web/templates/base.html`, add one nav link next to the existing API readiness/API tokens links:

```html
<a href="/integration-status">Integration status</a>
```

- [ ] **Step 6: Add web policy and binding**

In `app/security/surface_policy.py`, add this `_p(...)` entry next to `web.api_readiness.index`:

```python
    _p(
        "web.integration_status.index",
        "web",
        "GET",
        "/integration-status",
        "web-admin",
        "session",
        "read-only",
        "none",
        (),
        ("session required", "aggregate-only", "no raw secret", "no SSH"),
        False,
        "",
        False,
        "implemented",
        ("tests/web/test_web_integration_status.py",),
        "Web-admin view of post-dry-run integration gates without enabling remote writes.",
    ),
```

In `app/security/surface_bindings.py`, add this binding next to `/api-readiness`:

```python
    _binding(
        "web",
        "GET",
        "/integration-status",
        source="app.web.app:create_web_app",
        policy_id="web.integration_status.index",
    ),
```

- [ ] **Step 7: Run the web tests**

Run:

```powershell
python -m pytest tests/web/test_web_integration_status.py tests/web/test_api_readiness.py tests/web/test_api_tokens.py tests/security/test_surface_policy_bindings.py -q
```

Expected:

```text
all selected tests pass
```

- [ ] **Step 8: Commit Task 3**

Run:

```powershell
git add app/web/app.py app/web/templates/base.html app/web/templates/integration_status.html app/security/surface_policy.py app/security/surface_bindings.py tests/web/test_web_integration_status.py
git commit -m "Add integration status web page"
```

### Task 4: Documentation and AMN3 Evidence

**Files:**
- Modify in `amn2`: `docs/API_TOKEN_POLICY.ru.md` if the project documents API route scopes there
- Create in AMN3: `research/amn2/post-dry-run-read-only-integration-implementation.md`
- Modify in AMN3: `research/amn2/transfer-backlog.md`
- Modify in AMN3: `docs/PROJECT_STATUS_CURRENT.ru.md`

- [ ] **Step 1: Document the route scope in `amn2`**

If `docs/API_TOKEN_POLICY.ru.md` lists route scopes, add:

```text
GET /api/integration/status
scope: server:read
mode: read-only
secret policy: aggregate/no-secret
remote side effects: none
write gate: blocked until separate live verification
```

If the route table lives in another API document, update that document instead.

- [ ] **Step 2: Run documentation grep**

Run:

```powershell
rg -n "integration/status|Integration status|server:read" docs app tests
```

Expected:

```text
The new API route, web route and scope documentation are visible.
No output contains raw tokens, token hashes, private keys, PSK, vpn://, or config bodies.
```

- [ ] **Step 3: Create AMN3 implementation evidence**

After the `amn2` branch is committed and pushed, create `research/amn2/post-dry-run-read-only-integration-implementation.md` in AMN3:

```markdown
# Post Dry-Run Read-Only Integration Implementation

Date: 2026-06-04.

Production repo: `C:\Users\SooL\Documents\Amneziya`
Branch: `codex/post-dry-run-read-only-integration`
Base: `codex-vps-test-prep` at `708c98e`

## Decision

The remote-operation VPS gate remains `dry-run-only-pass`. This implementation adds only read-only integration status visibility in API and web-admin surfaces. It does not enable live peer apply/revoke, client write CRUD, config delivery, Local Agent mutations, backup/import/reboot routes, or public/self-service config routes.

## Implemented Surface

- `GET /api/integration/status`
- Web-admin `/integration-status`
- Shared local-only `integration_status` service
- Route policy and binding coverage

## Verification

```text
python -m pytest tests/services/test_integration_status_service.py tests/api/test_api_integration_status.py tests/web/test_web_integration_status.py tests/security/test_surface_policy_bindings.py -q
result: paste exact focused result

python -m pytest -q -p no:cacheprovider --basetemp tmp/pytest-post-dry-run-read-only
result: paste exact full result
```

## Secret Review

No `.env`, raw tokens, bearer headers, token hashes, private keys, PSK, config bodies, QR payloads, `vpn://`, SSH command output, server hostnames, peer public keys, peer IPs or per-peer traffic were published in this evidence.

## Next Gate

The next live gate is still a separately confirmed single test peer apply/revoke window. Until that operator confirmation exists, the production line should stay read-only for remote operations.
```

- [ ] **Step 4: Update AMN3 backlog/status**

In AMN3, update:

```text
research/amn2/transfer-backlog.md
docs/PROJECT_STATUS_CURRENT.ru.md
```

Record the branch, commit, local test evidence, and the fact that the VPS decision remains `dry-run-only-pass`, not `verified-live`.

- [ ] **Step 5: Commit AMN3 evidence**

Run in `C:\Users\SooL\Documents\VPS-OPS-LAB`:

```powershell
git add research/amn2/post-dry-run-read-only-integration-implementation.md research/amn2/transfer-backlog.md docs/PROJECT_STATUS_CURRENT.ru.md
git commit -m "Record post dry-run read-only integration evidence"
git push origin master
```

### Task 5: Verification Package Decision

**Files:**
- Modify only if needed: `scripts/vps/amn2_api_loopback_smoke.sh`
- Modify only if needed: AMN3 package manifest or packaging script

- [ ] **Step 1: Run focused local verification in `amn2`**

Run:

```powershell
python -m pytest tests/services/test_integration_status_service.py tests/api/test_api_integration_status.py tests/web/test_web_integration_status.py tests/security/test_surface_policy_bindings.py -q
```

Expected:

```text
all selected tests pass
```

- [ ] **Step 2: Run full local verification in `amn2`**

Run:

```powershell
python -m pytest -q -p no:cacheprovider --basetemp tmp/pytest-post-dry-run-read-only
```

Expected:

```text
full suite passes
```

The known Starlette/httpx deprecation warning is acceptable if it matches the current baseline warning.

- [ ] **Step 3: Decide whether to update the VPS smoke script**

Update `scripts/vps/amn2_api_loopback_smoke.sh` only if the new `/api/integration/status` route should become part of the standard loopback API smoke. If updated, the smoke must:

```text
bind API to 127.0.0.1 only
use a short-lived token
check /api/integration/status with server:read
reject forbidden markers in response
revoke token at the end
keep VPS_APPLY_ENABLED=false
avoid server preflight unless AMN2_RUN_PREFLIGHT=1 is explicitly set
```

- [ ] **Step 4: Run optional real VPS loopback verification**

Use this only after a new update package is published and the operator is ready. The operator should run:

```bash
cd /opt/amn2
source venv/bin/activate
export VPS_APPLY_ENABLED=false
export AMN2_RUN_PREFLIGHT=0
export AMN2_SERVER_NAME=local
bash ./amn2_api_loopback_smoke.sh
```

Expected safe summary:

```text
VPS verdict: pass
server_db_sync_status: passed
api_ready_status: passed
api_smoke_status: passed
auth_status: passed
listener_status: passed
audit_status: passed
```

Do not request or publish `api-server.log` unless manually redacted.

- [ ] **Step 5: Do not run live write verification in this slice**

Leave these commands blocked:

```text
python -m app.cli server apply-peer --apply ...
python -m app.cli server revoke-peer --apply ...
```

Those commands require a separate operator approval, a dedicated disposable test peer, a recovery window, and a rollback checklist.

## Final Review Checklist

- [ ] API route uses existing bearer token auth.
- [ ] API route requires `server:read`.
- [ ] API route records safe read audit.
- [ ] Web route requires admin login.
- [ ] No SSH, Docker, remote runner, server preflight, peer apply/revoke, config export or Local Agent mutation is called.
- [ ] No secret markers appear in service, API response, web response, docs or evidence.
- [ ] Route policy/binding tests cover the new route.
- [ ] Focused tests pass.
- [ ] Full suite passes.
- [ ] AMN3 evidence says `dry-run-only-pass`, not `verified-live`.

## Recommended Execution Order

1. Implement Task 1 on a new `amn2` branch named `codex/post-dry-run-read-only-integration`.
2. Implement Task 2 and verify API policy.
3. Implement Task 3 and verify web UX.
4. Run focused and full local tests.
5. Update AMN3 evidence and push.
6. Publish a VPS update kit only if the operator wants the new read-only status route verified on the real VPS.
7. Keep Phase 2 live apply/revoke out of this branch.
