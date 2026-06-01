# AMN2 Read-Only API Route Shell Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the first native `amn2` `/api/*` route shell for scoped, aggregate-only server and metrics reads.

**Architecture:** The API is a separate FastAPI app in `app/api` that reuses the existing SQLite `Repository`, scoped API token service, and surface policy registry. The first slice exposes only aggregate/read-only data and does not call SSH, Local Agent write routes, config delivery, backup/import, Docker control, or peer mutation paths.

**Tech Stack:** Python 3.12, FastAPI, SQLite repository, existing `app.services.api_tokens`, pytest, `TestClient`.

---

## Scope

Allowed endpoints:

- `GET /api/servers`
- `GET /api/servers/{server_name}/summary`
- `GET /api/metrics/summary`

Allowed scopes:

- `server:read` for server list and server summary
- `metrics:read` for aggregate metrics summary

Forbidden in this slice:

- `/api/clients` CRUD
- `config:read`
- `.conf`, QR, `vpn://`, private key, PSK, token hash, raw token, command output
- SSH, peer sync, apply/revoke, Docker restart, backup/import/reboot
- public unauthenticated docs/metrics

## Files

- Create `app/api/__init__.py`: package marker and exported factory.
- Create `app/api/app.py`: FastAPI app factory, auth dependency, and read-only routes.
- Modify `app/db/repositories.py`: add safe aggregate query helpers only.
- Modify `app/security/surface_policy.py`: add API surface policy records.
- Modify `app/config/settings.py`: add `API_HOST` and `API_PORT` settings with port validation.
- Modify `app/cli.py`: add `python -m app.cli api serve`.
- Modify `.env.example`: document safe local API defaults.
- Modify `docs/API_TOKEN_POLICY.ru.md`: record that route shell is now connected for read-only scopes only.
- Test `tests/api/test_app.py`: route auth, scope split, response shape, no secret markers.
- Test `tests/db/test_repositories.py`: repository aggregate summaries.
- Test `tests/security/test_surface_policy.py`: policy coverage for new API routes.
- Test `tests/config/test_settings.py`: API port validation.
- Test `tests/test_file_hygiene.py`: env example includes API safe defaults.

## Task 1: Repository Aggregate Queries

- [ ] Write failing tests in `tests/db/test_repositories.py`:

```python
def test_api_server_summary_queries_expose_safe_aggregate_fields(tmp_path):
    conn = connect(tmp_path / "test.sqlite3")
    initialize_schema(conn)
    repo = Repository(conn)
    user_id, server_id = _create_user_and_server(repo)
    _insert_device(conn, user_id=user_id, server_id=server_id, vpn_ip="10.8.0.2", peer_public_key="active-public", status="active")
    _insert_device(conn, user_id=user_id, server_id=server_id, vpn_ip="10.8.0.3", peer_public_key="disabled-public", status="disabled")
    repo.record_server_health(server_id=server_id, status="online", latency_ms=20, ssh_ok=True, awg_ok=True, udp_port_ok=True, error=None)

    summaries = repo.list_api_server_summaries()
    summary = repo.get_api_server_summary("local")

    assert summaries[0]["name"] == "local"
    assert summary["active_device_count"] == 1
    assert summary["total_device_count"] == 2
    assert "server_public_key" not in summary.keys()
```

```python
def test_api_metrics_summary_aggregates_counts_and_latest_traffic(tmp_path):
    conn = connect(tmp_path / "test.sqlite3")
    initialize_schema(conn)
    repo = Repository(conn)
    user_id, server_id = _create_user_and_server(repo)
    device_id = _insert_device(conn, user_id=user_id, server_id=server_id, vpn_ip="10.8.0.2", peer_public_key="active-public", status="active")
    repo.record_device_traffic_snapshot(device_id=device_id, server_id=server_id, peer_public_key="active-public", rx_bytes=100, tx_bytes=200, source="test", collected_at="2026-06-01T10:00:00Z")
    repo.record_device_traffic_snapshot(device_id=device_id, server_id=server_id, peer_public_key="active-public", rx_bytes=150, tx_bytes=250, source="test", collected_at="2026-06-01T10:05:00Z")

    summary = repo.get_api_metrics_summary()

    assert summary["devices_active"] == 1
    assert summary["traffic_rx_bytes"] == 150
    assert summary["traffic_tx_bytes"] == 250
```

- [ ] Run:

```powershell
$env:PYTHONPATH='.codex_deps;.'
python -m pytest tests/db/test_repositories.py::test_api_server_summary_queries_expose_safe_aggregate_fields tests/db/test_repositories.py::test_api_metrics_summary_aggregates_counts_and_latest_traffic -v
```

Expected: fail because repository methods do not exist.

- [ ] Implement `list_api_server_summaries()`, `get_api_server_summary(name)`, and `get_api_metrics_summary()` in `app/db/repositories.py`.

- [ ] Re-run the two tests. Expected: pass.

## Task 2: API App, Auth, and Routes

- [ ] Write failing tests in `tests/api/test_app.py` for:

```python
def test_api_servers_requires_server_read_scope_and_returns_safe_summary(tmp_path):
    settings, repo = _seed_api_data(tmp_path)
    _store_token(repo, raw_token="server-token", scopes=["server:read"])
    client = TestClient(create_api_app(settings))

    response = client.get("/api/servers", headers={"Authorization": "Bearer server-token"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["servers"][0]["name"] == "local"
    assert "host" not in payload["servers"][0]
    assert _forbidden_markers_absent(payload)
```

```python
def test_api_metrics_requires_metrics_read_scope(tmp_path):
    settings, repo = _seed_api_data(tmp_path)
    _store_token(repo, raw_token="server-token", scopes=["server:read"])
    _store_token(repo, raw_token="metrics-token", scopes=["metrics:read"])
    client = TestClient(create_api_app(settings))

    denied = client.get("/api/metrics/summary", headers={"Authorization": "Bearer server-token"})
    allowed = client.get("/api/metrics/summary", headers={"Authorization": "Bearer metrics-token"})

    assert denied.status_code == 403
    assert allowed.status_code == 200
```

- [ ] Run:

```powershell
$env:PYTHONPATH='.codex_deps;.'
python -m pytest tests/api/test_app.py -v
```

Expected: fail because `app.api` does not exist.

- [ ] Create `app/api/app.py` and `app/api/__init__.py`.

- [ ] Re-run `tests/api/test_app.py`. Expected: pass.

## Task 3: Policy, Settings, CLI, Docs

- [ ] Add API policy tests to `tests/security/test_surface_policy.py`:

```python
def test_api_route_shell_policies_are_read_only_scoped_and_no_live_retest():
    for policy_id, scope in {
        "api.servers.list": "server:read",
        "api.servers.summary": "server:read",
        "api.metrics.summary": "metrics:read",
    }.items():
        policy = get_surface_policy(policy_id)
        assert policy.surface == "api"
        assert policy.risk_class == "read-only"
        assert scope in policy.auth_method
        assert policy.live_retest_required is False
```

- [ ] Add `api` to `SurfaceName`, add three policies, and allow only these API policies to set `enables_new_behavior=True`.

- [ ] Add `API_HOST=127.0.0.1` and `API_PORT=3040` defaults in settings and `.env.example`.

- [ ] Add `python -m app.cli api serve` that starts `create_api_app()`.

- [ ] Update `docs/API_TOKEN_POLICY.ru.md` with the connected read-only route shell and forbidden first-slice surfaces.

## Verification

Run before commit:

```powershell
$env:PYTHONPATH='.codex_deps;.'
python -m pytest tests/api/test_app.py tests/db/test_repositories.py tests/security/test_surface_policy.py tests/services/test_api_tokens.py tests/config/test_settings.py tests/test_file_hygiene.py -v
python -m pytest -q
python -m pip install -e . --no-deps --dry-run
git diff --check
```

Expected:

- focused tests pass;
- full suite passes with only the known Starlette warning;
- editable install dry-run reaches `Would install amneziya-0.1.0`;
- no whitespace errors.
