# AMN2 P4-I003 Read-only API Status Schema Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Lock the existing AMN2 read-only API/status surface into a machine-checkable local contract without adding routes, public exposure, config delivery, write CRUD, Local Agent mutations or live VPS commands.

**Architecture:** Start from the current Phase 4 AMN2 stack and add only local policy bindings, tests and docs around the existing six `/api/*` routes. The runtime behavior stays read-only: FastAPI still serves the same routes, scopes remain `server:read` and `metrics:read`, smoke still checks exactly six routes, and `/api/integration/status` keeps the service-mode loopback boundary visible.

**Tech Stack:** AMN2 Python/FastAPI, pytest, local SQLite test repositories, `app.security.surface_policy`, `app.security.surface_bindings`, AMN2 docs. AMN3 receives only return evidence after the AMN2 commit.

---

## Source Context

Design source:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB\research\amn2\phase-4-read-only-api-status-design-2026-06-09.md
```

Implementation branch:

```text
codex/phase-4-read-only-api-status-schema
```

Base:

```text
codex/phase-4-service-mode-status-wording
```

Allowed AMN2 scope:

- local tests;
- policy binding registry for existing API routes;
- docs describing the existing read-only API/status contract.

Blocked AMN2 scope:

- new API routes;
- `/api/clients`;
- `config:read`;
- public/self-service config delivery;
- public API `3040`;
- direct public web/admin `3030`;
- token issue/revoke against real operator state;
- Local Agent `/configs` or mutation routes;
- live VPS commands;
- backup/import/reboot;
- production peer/user mutation.

## File Structure

AMN2 files to modify:

- `app/security/surface_bindings.py`: add `API_RUNTIME_ROUTE_BINDINGS` for the six existing read-only `/api/*` routes and include them in `SURFACE_BINDINGS`.
- `tests/security/test_surface_policy_bindings.py`: add a runtime drift test proving mounted API routes match `API_RUNTIME_ROUTE_BINDINGS`.
- `tests/api/test_read_only_status_contract.py`: new focused test file for route matrix, scope split, safe audit metadata and forbidden marker coverage.
- `docs/API_TOKEN_POLICY.ru.md`: add a short P4-I003 contract-hardening note.
- `docs/ROUTE_AUTH_OPERATION_POLICY.ru.md`: add a short note that runtime API bindings are now machine-checked.

AMN3 return evidence after AMN2 commit:

- `research/amn2/phase-4-read-only-api-status-schema-implementation-2026-06-09.md`
- update `research/amn2/transfer-backlog.md`
- update `docs/PROJECT_STATUS_CURRENT.ru.md`

## Task 1: Prepare AMN2 Worktree

**Files:**

- No file edits in this task.

- [ ] **Step 1: Check current AMN2 reference worktree**

Run:

```powershell
git -C C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-p4-i002 status --short --branch
```

Expected:

```text
## codex/phase-4-service-mode-status-wording
```

- [ ] **Step 2: Create the implementation worktree**

Run from AMN3 workspace:

```powershell
git -C C:\Users\SooL\Documents\Amneziya worktree add C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-p4-i003-read-only-api-status-schema codex/phase-4-service-mode-status-wording
git -C C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-p4-i003-read-only-api-status-schema switch -c codex/phase-4-read-only-api-status-schema
```

Expected:

```text
branch codex/phase-4-read-only-api-status-schema
```

## Task 2: Add Failing API Runtime Binding Test

**Files:**

- Modify: `tests/security/test_surface_policy_bindings.py`

- [ ] **Step 1: Write the failing test**

Update imports:

```python
from app.api.app import create_api_app
from app.security.surface_bindings import (
    API_RUNTIME_ROUTE_BINDINGS,
    WEB_RUNTIME_ROUTE_BINDINGS,
    policy_backed_bindings,
)
```

Add this test after `test_web_post_runtime_routes_have_policy_bindings`:

```python
def test_api_runtime_routes_match_policy_bindings(tmp_path: Path):
    actual_routes = _route_keys(create_api_app(_settings(tmp_path)))
    bindings = _binding_map(API_RUNTIME_ROUTE_BINDINGS)

    assert actual_routes == set(bindings)
    assert [
        binding
        for binding in API_RUNTIME_ROUTE_BINDINGS
        if binding.policy_id is None
    ] == []
```

- [ ] **Step 2: Run the test and verify it fails**

Run:

```powershell
pytest tests/security/test_surface_policy_bindings.py::test_api_runtime_routes_match_policy_bindings -v
```

Expected:

```text
ImportError: cannot import name 'API_RUNTIME_ROUTE_BINDINGS'
```

## Task 3: Add API Runtime Bindings

**Files:**

- Modify: `app/security/surface_bindings.py`

- [ ] **Step 1: Add API bindings for the existing six routes**

Insert after `LOCAL_AGENT_RUNTIME_ROUTE_BINDINGS`:

```python
API_RUNTIME_ROUTE_BINDINGS: tuple[SurfaceBinding, ...] = (
    _binding(
        "api",
        "GET",
        "/api/servers",
        source="app.api.app:create_api_app",
        policy_id="api.servers.list",
    ),
    _binding(
        "api",
        "GET",
        "/api/integration/status",
        source="app.api.app:create_api_app",
        policy_id="api.integration.status",
    ),
    _binding(
        "api",
        "GET",
        "/api/local-agent/runtime/summary",
        source="app.api.app:create_api_app",
        policy_id="api.local_agent.runtime_summary",
    ),
    _binding(
        "api",
        "GET",
        "/api/servers/{server_name}/summary",
        source="app.api.app:create_api_app",
        policy_id="api.servers.summary",
    ),
    _binding(
        "api",
        "GET",
        "/api/metrics/summary",
        source="app.api.app:create_api_app",
        policy_id="api.metrics.summary",
    ),
    _binding(
        "api",
        "GET",
        "/api/users/summary",
        source="app.api.app:create_api_app",
        policy_id="api.users.summary",
    ),
)
```

Update `SURFACE_BINDINGS`:

```python
SURFACE_BINDINGS: tuple[SurfaceBinding, ...] = (
    *WEB_RUNTIME_ROUTE_BINDINGS,
    *LOCAL_AGENT_RUNTIME_ROUTE_BINDINGS,
    *API_RUNTIME_ROUTE_BINDINGS,
    *BOT_ACTION_BINDINGS,
    *OPERATION_BINDINGS,
)
```

- [ ] **Step 2: Run the new binding test**

Run:

```powershell
pytest tests/security/test_surface_policy_bindings.py::test_api_runtime_routes_match_policy_bindings -v
```

Expected:

```text
1 passed
```

- [ ] **Step 3: Run policy binding regression tests**

Run:

```powershell
pytest tests/security/test_surface_policy_bindings.py tests/security/test_surface_policy.py -v
```

Expected:

```text
all selected tests passed
```

## Task 4: Add Read-only API Status Contract Tests

**Files:**

- Create: `tests/api/test_read_only_status_contract.py`

- [ ] **Step 1: Create the contract test file**

Create `tests/api/test_read_only_status_contract.py`:

```python
from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from app.api.app import create_api_app
from app.config.settings import Settings
from app.db.connection import connect
from app.db.repositories import Repository
from app.db.schema import initialize_schema
from app.services.api_tokens import hash_api_token


API_ROUTE_CONTRACT = (
    ("GET", "/api/servers", "server:read"),
    ("GET", "/api/integration/status", "server:read"),
    ("GET", "/api/local-agent/runtime/summary", "server:read"),
    ("GET", "/api/servers/{server_name}/summary", "server:read"),
    ("GET", "/api/metrics/summary", "metrics:read"),
    ("GET", "/api/users/summary", "metrics:read"),
)

REQUEST_MATRIX = (
    ("/api/servers", "/api/servers", "server-token", "metrics-token", "server:read"),
    (
        "/api/integration/status",
        "/api/integration/status",
        "server-token",
        "metrics-token",
        "server:read",
    ),
    (
        "/api/local-agent/runtime/summary",
        "/api/local-agent/runtime/summary",
        "server-token",
        "metrics-token",
        "server:read",
    ),
    (
        "/api/servers/local/summary",
        "/api/servers/{server_name}/summary",
        "server-token",
        "metrics-token",
        "server:read",
    ),
    (
        "/api/metrics/summary",
        "/api/metrics/summary",
        "metrics-token",
        "server-token",
        "metrics:read",
    ),
    (
        "/api/users/summary",
        "/api/users/summary",
        "metrics-token",
        "server-token",
        "metrics:read",
    ),
)

FORBIDDEN_MARKERS = (
    "PrivateKey",
    "PresharedKey",
    "psk",
    "vpn://",
    "token_hash",
    "raw-token",
    "raw token",
    "peer_public_key",
    "server_public_key",
    "ssh_port",
    "endpoint_host",
    "Authorization",
    ".conf",
    "container_name",
    "interface",
    "config_path",
    "docker exec",
    "awg show",
    "10.9.0.10",
    "3041",
)


def test_runtime_api_route_contract_is_exactly_six_read_only_routes(tmp_path: Path):
    settings, _repo = _seed_api_data(tmp_path)
    routes = sorted(_route_keys(create_api_app(settings)))

    assert routes == sorted((method, path) for method, path, _scope in API_ROUTE_CONTRACT)


@pytest.mark.parametrize(
    "request_path,route_template,allowed_token,denied_token,required_scope",
    REQUEST_MATRIX,
)
def test_read_only_api_scope_matrix_and_safe_payloads(
    tmp_path: Path,
    request_path: str,
    route_template: str,
    allowed_token: str,
    denied_token: str,
    required_scope: str,
):
    settings, repo = _seed_api_data(
        tmp_path,
        local_agent_enabled=True,
        local_agent_host="10.9.0.10",
        local_agent_port=3041,
        local_agent_token_hash="sha256:" + "a" * 64,
        local_agent_token_id="agent-token-id",
        local_agent_token_owner="agent-token-owner",
    )
    _store_token(
        repo,
        raw_token="server-token",
        scopes=["server:read"],
        token_id="api_server_read",
    )
    _store_token(
        repo,
        raw_token="metrics-token",
        scopes=["metrics:read"],
        token_id="api_metrics_read",
    )
    client = TestClient(create_api_app(settings))

    denied = client.get(
        request_path,
        headers={"Authorization": f"Bearer {denied_token}"},
    )
    allowed = client.get(
        request_path,
        headers={"Authorization": f"Bearer {allowed_token}"},
    )

    assert denied.status_code == 403
    assert allowed.status_code == 200
    assert _forbidden_markers_absent(allowed.json())

    row = repo._conn.execute(
        "SELECT action, metadata_json FROM admin_actions ORDER BY id DESC LIMIT 1"
    ).fetchone()
    assert row is not None
    assert row["action"] == "api_read"
    metadata = json.loads(row["metadata_json"])
    assert metadata == {
        "aggregate_only": True,
        "method": "GET",
        "owner_label": "ops",
        "path": route_template,
        "scope": required_scope,
        "status": "allowed",
        "token_id": (
            "api_server_read"
            if required_scope == "server:read"
            else "api_metrics_read"
        ),
        "token_name": "API token",
    }
    assert "server-token" not in row["metadata_json"]
    assert "metrics-token" not in row["metadata_json"]
    assert "Authorization" not in row["metadata_json"]
    assert "token_hash" not in row["metadata_json"]


def test_integration_status_keeps_service_mode_public_and_write_boundaries(
    tmp_path: Path,
):
    settings, repo = _seed_api_data(tmp_path)
    _store_token(
        repo,
        raw_token="server-token",
        scopes=["server:read"],
        token_id="api_server_read",
    )
    client = TestClient(create_api_app(settings))

    response = client.get(
        "/api/integration/status",
        headers={"Authorization": "Bearer server-token"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "service_mode_loopback_ready"
    assert payload["api_baseline"]["allowed_scopes"] == ["metrics:read", "server:read"]
    assert payload["api_baseline"]["write_routes_enabled"] is False
    assert payload["api_baseline"]["public_api_exposed"] is False
    assert payload["service_mode_boundary"] == {
        "web_bot_services": "active",
        "web_admin_listener": "127.0.0.1:3030_loopback_only",
        "operator_access": "ssh_tunnel_only",
        "public_web_admin": "closed",
        "public_api_3040": "absent_closed",
        "tcp_80_443": "absent",
        "domain_https_cutover": "deferred_no_domain",
        "vps_apply_enabled": False,
    }
    assert payload["local_read_only_extension"]["checked_routes"] == 6
    assert "/api/clients write CRUD" in payload["blocked_lanes"]
    assert "public API 3040 exposure" in payload["blocked_lanes"]
    assert "public/self-service config delivery" in payload["blocked_lanes"]
    assert "Local Agent configs or mutations" in payload["blocked_lanes"]
    assert "backup/import/reboot routes" in payload["blocked_lanes"]
    assert _forbidden_markers_absent(payload)


def _route_keys(app) -> set[tuple[str, str]]:
    routes: set[tuple[str, str]] = set()
    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        for method in route.methods or ():
            if method in {"HEAD", "OPTIONS"}:
                continue
            routes.add((method, route.path))
    return routes


def _seed_api_data(
    tmp_path: Path,
    **settings_overrides: object,
) -> tuple[Settings, Repository]:
    db_path = tmp_path / "api.sqlite3"
    settings_values = {
        "_env_file": None,
        "telegram_bot_token": "CHANGE_ME",
        "app_secret_key": "test-secret",
        "database_path": str(db_path),
    }
    settings_values.update(settings_overrides)
    settings = Settings(**settings_values)
    conn = connect(db_path)
    initialize_schema(conn)
    repo = Repository(conn)
    user_id = repo.upsert_user(
        telegram_id=2001,
        username="bob",
        first_name="Bob",
        last_name=None,
    )
    blocked_user_id = repo.create_user_for_admin(
        telegram_id=3002,
        username="secret-user",
        first_name="Secret",
        last_name="Person",
        email="secret@example.com",
        status="blocked",
        is_admin=False,
    )
    repo.create_order(user_id=blocked_user_id, plan_id=None, payment_mode="manual")
    server_id = repo.ensure_default_server(name="local", network_cidr="10.8.0.0/24")
    active_device_id = _insert_device(
        repo,
        user_id=user_id,
        server_id=server_id,
        vpn_ip="10.8.0.2",
        peer_public_key="active-public",
        status="active",
    )
    _insert_device(
        repo,
        user_id=user_id,
        server_id=server_id,
        vpn_ip="10.8.0.3",
        peer_public_key="revoked-public",
        status="revoked",
    )
    repo.record_server_health(
        server_id=server_id,
        status="online",
        latency_ms=20,
        ssh_ok=True,
        awg_ok=True,
        udp_port_ok=True,
        error="must not appear in API",
    )
    repo.record_device_traffic_snapshot(
        device_id=active_device_id,
        server_id=server_id,
        peer_public_key="active-public",
        rx_bytes=150,
        tx_bytes=250,
        source="test",
        collected_at="2026-06-01T10:05:00Z",
    )
    return settings, repo


def _store_token(
    repo: Repository,
    *,
    raw_token: str,
    scopes: list[str],
    token_id: str,
) -> None:
    repo.create_api_token(
        token_id=token_id,
        name="API token",
        owner_user_id=None,
        owner_label="ops",
        token_hash=hash_api_token(raw_token),
        scopes=scopes,
        expires_at="2099-01-01T00:00:00+00:00",
    )


def _insert_device(
    repo: Repository,
    *,
    user_id: int,
    server_id: int,
    vpn_ip: str,
    peer_public_key: str,
    status: str,
) -> int:
    cursor = repo._conn.execute(
        """
        INSERT INTO devices (
            user_id,
            server_id,
            name,
            duration_days,
            status,
            vpn_ip,
            peer_public_key,
            peer_private_key_encrypted,
            preshared_key_encrypted,
            config_version
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            server_id,
            f"{status}-device",
            7,
            status,
            vpn_ip,
            peer_public_key,
            f"v1:{status}-private",
            f"v1:{status}-psk",
            "amneziawg_v2",
        ),
    )
    repo._conn.commit()
    return int(cursor.lastrowid)


def _forbidden_markers_absent(payload: object) -> bool:
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return all(marker.lower() not in serialized.lower() for marker in FORBIDDEN_MARKERS)
```

- [ ] **Step 2: Run the new contract tests**

Run:

```powershell
pytest tests/api/test_read_only_status_contract.py -v
```

Expected:

```text
all selected tests passed
```

## Task 5: Update AMN2 API Policy Docs

**Files:**

- Modify: `docs/API_TOKEN_POLICY.ru.md`
- Modify: `docs/ROUTE_AUTH_OPERATION_POLICY.ru.md`

- [ ] **Step 1: Update `docs/API_TOKEN_POLICY.ru.md`**

Append this section after `## Connected read-only route shell`:

```markdown
### P4-I003 contract hardening

Phase 4 `P4-I003` keeps the connected route shell at exactly six read-only aggregate routes. The implementation adds local tests for runtime route drift, scope split, service-mode boundary fields, safe `api_read` audit metadata and forbidden response markers. It does not add `/api/clients`, `config:read`, public/self-service config delivery, public API exposure, Local Agent config/mutation routes, token lifecycle operations against production state or live VPS commands.
```

- [ ] **Step 2: Update `docs/ROUTE_AUTH_OPERATION_POLICY.ru.md`**

Append this paragraph after the implemented read-only route list:

```markdown
Phase 4 `P4-I003` adds `API_RUNTIME_ROUTE_BINDINGS` in `app.security.surface_bindings` so the mounted FastAPI `/api/*` routes are checked against the same policy ids as the route/auth policy registry. This is a local drift guard only; it does not mount new routes or relax any gate.
```

## Task 6: Run Focused Verification

**Files:**

- All changed AMN2 files.

- [ ] **Step 1: Run focused API/security/status tests**

Run:

```powershell
pytest tests/security/test_surface_policy_bindings.py tests/security/test_surface_policy.py tests/api/test_app.py tests/api/test_api_integration_status.py tests/api/test_cli_tokens.py tests/api/test_read_only_status_contract.py tests/services/test_integration_status_service.py -v
```

Expected:

```text
all selected tests passed
```

- [ ] **Step 2: Run whitespace check**

Run:

```powershell
git diff --check
```

Expected:

```text
exit code 0
```

## Task 7: Commit AMN2 Slice

**Files:**

- All changed AMN2 files.

- [ ] **Step 1: Inspect changed files**

Run:

```powershell
git status --short --branch
git diff --stat
```

Expected changed files:

```text
app/security/surface_bindings.py
tests/security/test_surface_policy_bindings.py
tests/api/test_read_only_status_contract.py
docs/API_TOKEN_POLICY.ru.md
docs/ROUTE_AUTH_OPERATION_POLICY.ru.md
```

- [ ] **Step 2: Commit**

Run:

```powershell
git add app/security/surface_bindings.py tests/security/test_surface_policy_bindings.py tests/api/test_read_only_status_contract.py docs/API_TOKEN_POLICY.ru.md docs/ROUTE_AUTH_OPERATION_POLICY.ru.md
git commit -m "Lock read-only API status contract"
```

Expected:

```text
one local AMN2 commit on codex/phase-4-read-only-api-status-schema
```

## Task 8: Return Evidence To AMN3

**Files:**

- Create: `research/amn2/phase-4-read-only-api-status-schema-implementation-2026-06-09.md`
- Modify: `research/amn2/transfer-backlog.md`
- Modify: `docs/PROJECT_STATUS_CURRENT.ru.md`
- Modify: `research/amn2/phase-4-candidate-registry-2026-06-09.md`

- [ ] **Step 1: Create AMN3 evidence**

The evidence file must include:

```text
candidate_id: P4-I003
AMN2 branch:
AMN2 commit:
changed_files:
verification:
live_vps_commands: none
new_routes: none
public_exposure: none
config_delivery: none
write_crud: none
local_agent_mutation: none
backup_import_reboot: none
token_lifecycle_real_operator_action: none
```

- [ ] **Step 2: Update AMN3 status docs**

Record the AMN2 branch, commit and verification result. State explicitly that no live VPS commands, public exposure, config delivery, write CRUD, Local Agent mutation, backup/import/reboot or production peer/user mutation was performed.

- [ ] **Step 3: Commit AMN3 return evidence**

Run from AMN3 workspace:

```powershell
git add research/amn2/phase-4-read-only-api-status-schema-implementation-2026-06-09.md research/amn2/transfer-backlog.md docs/PROJECT_STATUS_CURRENT.ru.md research/amn2/phase-4-candidate-registry-2026-06-09.md
git commit -m "Record Phase 4 read-only API status implementation"
```

Expected:

```text
one local AMN3 evidence commit
```
