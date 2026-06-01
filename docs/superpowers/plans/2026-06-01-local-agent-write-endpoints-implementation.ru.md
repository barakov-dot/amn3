# Local Agent Write Endpoints Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add guarded Local Agent `/agent/clients*` write endpoints after VPS `GO-1`.

**Architecture:** This plan wires together the already separated pieces: write settings, dedicated write token set, active write route policies, `LocalPeerCommandAdapter`, preflight/confirmation, and authoritative audit storage. `get_policy() remains read-only`; write endpoints are activated only through explicit `write_enabled=True` construction after `LOCAL_AGENT_WRITE_ENABLED=true`. Responses stay redacted and never return delivery secrets or full client configs.

**Tech Stack:** Python 3.12, FastAPI, existing `app.agent` modules, existing Local Agent auth/policy stack, pytest, SQLite-backed audit storage.

---

## Scope And Gates

Execute this plan only after `GO-1` in `docs/AMN3_POST_VPS_IMPLEMENTATION_MAP.ru.md`.

Before that:

- `LOCAL_AGENT_WRITE_ENABLED=false`;
- no write routes;
- read-only token remains read-only;
- `agent:clients:write` is not added to `LOCAL_AGENT_TOKEN_SCOPES`;
- no mutation through Local Agent.

After the gate:

```text
LOCAL_AGENT_WRITE_ENABLED=true
dedicated write token set
agent:clients:write
dry-run before mutation
confirmation nonce before mutation
audit write fails, block mutation
```

This plan does not replace these prerequisite plans:

- `docs/superpowers/plans/2026-06-01-local-agent-write-settings-implementation.ru.md`
- `docs/superpowers/plans/2026-06-01-local-agent-write-audit-storage-schema.ru.md`
- `docs/superpowers/plans/2026-06-01-local-agent-peer-command-adapter.ru.md`

## File Structure

- Modify `app/agent/policy.py`: add selected write slice helpers while preserving `get_policy() remains read-only`.
- Modify `tests/agent/test_policy.py`: prove write policies are explicit and not part of first read-only slice.
- Modify `app/agent/api.py`: register `/agent/clients*` only when `write_enabled=True`.
- Modify `tests/agent/test_api.py`: prove disabled routes stay 404, enabled routes require `agent:clients:write`, dry-run returns preflight data, mutation requires confirmation, and secret markers are absent.
- Use `app/agent/config.py` and `tests/agent/test_config.py`: tokens are supplied by the dedicated write token set from settings.
- Use `app/agent/peer_commands.py` and `tests/agent/test_peer_commands.py`: endpoint calls `LocalPeerCommandAdapter`, not runtime commands directly.
- Use `app/agent/write_contracts.py`: `AgentPeerApplyRequest`, `AgentPeerRevokeRequest`, and `AgentPeerMutationResult`.
- Use `app/agent/write_confirmation.py`: `WritePreflightReference`, `WriteConfirmationChallenge`, `ensure_mutation_allowed`, `WritePreflightRequiredError`.
- Use `app/agent/write_audit.py`: `WriteAuditEvent` payload boundaries.
- Preserve public error codes: `preflight_required`, `runtime_degraded`, `mutation_failed`.
- Use `local_agent_write_audit_events`: endpoint layer must persist redacted audit events before returning success.

## Endpoint Contract

Routes:

```text
POST /agent/clients/dry-run
POST /agent/clients
DELETE /agent/clients/{id}
```

Required scope:

```text
agent:clients:write
```

Feature flag behavior:

```text
write_enabled=False -> route not registered or 404
write_enabled=True -> route registered, still protected by token scope and preflight
```

Secrets that must never be returned:

- raw token;
- private key;
- PSK;
- QR;
- `vpn://`;
- full client config;
- raw confirmation nonce;
- full `.env`;
- SSH credentials.

Safe audit and UX fields:

- `user_id`;
- `device_id`;
- `client_id`;
- `server_alias`;
- `protocol=amneziawg`;
- `peer_public_key_fingerprint`;
- `rollback_reference`.

## Task 1: Write Slice Policy Gate

**Files:**
- Modify: `tests/agent/test_policy.py`
- Modify: `app/agent/policy.py`

- [ ] **Step 1: Write the failing policy tests**

Add these tests to `tests/agent/test_policy.py`:

```python
def test_get_policy_remains_read_only_after_write_slice_helpers_exist():
    with pytest.raises(AgentPolicyError, match="No agent route policy"):
        get_policy("POST", "/agent/clients")


def test_write_slice_policies_are_explicit_and_not_first_slice():
    from app.agent.policy import write_slice_policies

    policies = write_slice_policies()

    assert tuple((policy.method, policy.path, policy.scope, policy.risk_class) for policy in policies) == (
        ("POST", "/agent/clients/dry-run", "agent:clients:write", "state-write"),
        ("POST", "/agent/clients", "agent:clients:write", "state-write"),
        ("DELETE", "/agent/clients/{id}", "agent:clients:write", "state-write"),
    )
    assert all(policy.audit_required is True for policy in policies)
    assert all(policy.first_slice is False for policy in policies)
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_policy.py::test_get_policy_remains_read_only_after_write_slice_helpers_exist tests/agent/test_policy.py::test_write_slice_policies_are_explicit_and_not_first_slice -v
```

Expected: fail because `write_slice_policies` does not exist and `/agent/clients/dry-run` is not yet represented in `AGENT_ROUTE_POLICIES`.

- [ ] **Step 3: Add selected write policies**

In `app/agent/policy.py`, add a policy entry for dry-run near the existing client write policies:

```python
    AgentRoutePolicy(
        method="POST",
        path="/agent/clients/dry-run",
        risk_class="state-write",
        scope="agent:clients:write",
        audit_required=True,
        first_slice=False,
    ),
```

Add this helper below `first_slice_policies()`:

```python
def write_slice_policies() -> tuple[AgentRoutePolicy, ...]:
    selected = {
        ("POST", "/agent/clients/dry-run"),
        ("POST", "/agent/clients"),
        ("DELETE", "/agent/clients/{id}"),
    }
    return tuple(
        policy
        for policy in AGENT_ROUTE_POLICIES
        if (policy.method, policy.path) in selected
    )
```

Do not change `get_policy()`. `get_policy() remains read-only`.

- [ ] **Step 4: Run policy tests to verify GREEN**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_policy.py tests/agent/test_write_policy_matrix.py -v
```

Expected: pass.

- [ ] **Step 5: Commit**

```powershell
git add app/agent/policy.py tests/agent/test_policy.py
git commit -m "Gate Local Agent write route policies"
```

## Task 2: API Construction And Disabled Route Safety

**Files:**
- Modify: `tests/agent/test_api.py`
- Modify: `app/agent/api.py`

- [ ] **Step 1: Write the failing disabled/enabled construction tests**

Add helpers to `tests/agent/test_api.py`:

```python
WRITE_RAW_TOKEN = "raw-write-token"


def _write_token() -> AgentToken:
    return AgentToken(
        token_id="write-token-1",
        token_hash=hash_agent_token(WRITE_RAW_TOKEN),
        scopes=frozenset({"agent:clients:write"}),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        owner="write-controller",
    )


def _write_auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {WRITE_RAW_TOKEN}"}
```

Add this test:

```python
def test_agent_write_routes_return_404_when_write_mode_disabled():
    client, audit = _client({"agent:clients:write"})

    assert client.post("/agent/clients/dry-run", headers=_auth_headers()).status_code == 404
    assert client.post("/agent/clients", headers=_auth_headers()).status_code == 404
    assert client.delete("/agent/clients/client-1", headers=_auth_headers()).status_code == 404
    assert audit.events == []
```

Add this test:

```python
def test_agent_write_routes_require_write_scope_when_enabled():
    audit = InMemoryAgentAuditSink()
    adapter = FakeLocalRuntimeAdapter(
        RuntimeSnapshot(
            server_name="demo-vps",
            runtime_type="docker",
            status="running",
            protocols=(),
        )
    )
    app = create_agent_app(
        adapter=adapter,
        tokens=(_token({"agent:health"}), _write_token()),
        audit_sink=audit,
        write_enabled=True,
        peer_command_adapter=RecordingPeerCommandAdapter(),
    )
    client = TestClient(app)

    response = client.post(
        "/agent/clients/dry-run",
        headers=_auth_headers(),
        json=_apply_payload(),
    )

    assert response.status_code == 403
    assert "scope" in response.json()["detail"].lower()
    assert audit.events == []
```

Add helper payload and fake adapter:

```python
def _apply_payload() -> dict[str, str]:
    return {
        "client_id": "client-1",
        "peer_public_key": "peer-public",
        "preshared_key": "secret-psk",
        "vpn_ip": "10.8.0.2",
        "protocol": "amneziawg",
        "actor_surface": "web_admin",
        "actor_id": "admin-1",
        "server_alias": "demo-vps",
    }


class RecordingPeerCommandAdapter:
    def __init__(self):
        self.apply_dry_run_requests = []
        self.apply_requests = []
        self.revoke_requests = []

    def apply_dry_run(self, request):
        self.apply_dry_run_requests.append(request)
        return AgentPeerMutationResult(
            operation_id="local_agent.clients.apply.dry_run",
            status="planned",
            dry_run=True,
            message="No changes will be made.",
            planned_commands=("awg set awg0 peer peer-public allowed-ips 10.8.0.2/32",),
            secret_values=("secret-psk",),
        )
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_api.py::test_agent_write_routes_return_404_when_write_mode_disabled tests/agent/test_api.py::test_agent_write_routes_require_write_scope_when_enabled -v
```

Expected: fail because `create_agent_app` does not accept `write_enabled` or `peer_command_adapter`.

- [ ] **Step 3: Add API construction parameters**

In `app/agent/api.py`, extend `create_agent_app`:

```python
def create_agent_app(
    *,
    adapter: LocalRuntimeAdapter,
    tokens: Sequence[AgentToken],
    audit_sink: AgentAuditSink | None = None,
    build_version: str = "dev",
    write_enabled: bool = False,
    peer_command_adapter=None,
) -> FastAPI:
```

Change `/agent/version`:

```python
            "write_enabled": write_enabled,
```

Import write helpers:

```python
from app.agent.policy import AgentRoutePolicy, get_policy, write_slice_policies
from app.agent.write_contracts import AgentPeerApplyRequest
```

Register write policies only inside:

```python
    if write_enabled:
        if peer_command_adapter is None:
            raise ValueError("peer_command_adapter is required when write_enabled=True")
        write_policies = {
            (policy.method, policy.path): policy for policy in write_slice_policies()
        }
```

- [ ] **Step 4: Add dry-run route skeleton**

Inside `if write_enabled:`, add:

```python
        dry_run_policy = write_policies[("POST", "/agent/clients/dry-run")]

        @app.post("/agent/clients/dry-run")
        def clients_dry_run(
            payload: dict[str, object],
            token: AgentToken = Depends(require_policy(dry_run_policy)),
        ) -> dict[str, object]:
            request = AgentPeerApplyRequest(
                client_id=str(payload.get("client_id", "")),
                peer_public_key=str(payload.get("peer_public_key", "")),
                preshared_key=str(payload.get("preshared_key", "")),
                vpn_ip=str(payload.get("vpn_ip", "")),
                protocol=str(payload.get("protocol", "amneziawg")),
            )
            result = peer_command_adapter.apply_dry_run(request)
            audit_allowed(dry_run_policy, token)
            return result.redacted_payload()
```

- [ ] **Step 5: Run tests to verify GREEN for construction and scope**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_api.py::test_agent_write_routes_return_404_when_write_mode_disabled tests/agent/test_api.py::test_agent_write_routes_require_write_scope_when_enabled -v
```

Expected: pass.

- [ ] **Step 6: Commit**

```powershell
git add app/agent/api.py tests/agent/test_api.py
git commit -m "Gate Local Agent write endpoints"
```

## Task 3: Dry-Run Preflight Response

**Files:**
- Modify: `tests/agent/test_api.py`
- Modify: `app/agent/api.py`

- [ ] **Step 1: Write failing dry-run preflight test**

Add:

```python
def test_agent_write_dry_run_returns_redacted_preflight_reference():
    audit = InMemoryAgentAuditSink()
    peer_adapter = RecordingPeerCommandAdapter()
    app = create_agent_app(
        adapter=FakeLocalRuntimeAdapter(RuntimeSnapshot("demo-vps", "docker", "running", ())),
        tokens=(_write_token(),),
        audit_sink=audit,
        build_version="test-build",
        write_enabled=True,
        peer_command_adapter=peer_adapter,
    )
    client = TestClient(app)

    response = client.post(
        "/agent/clients/dry-run",
        headers=_write_auth_headers(),
        json=_apply_payload(),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["operation_id"] == "local_agent.clients.apply.dry_run"
    assert payload["status"] == "planned"
    assert payload["dry_run"] is True
    assert payload["preflight"]["result_state"] == "passed"
    assert payload["preflight"]["server_alias"] == "demo-vps"
    assert payload["preflight"]["client_id"] == "client-1"
    assert payload["preflight"]["peer_public_key_fingerprint"].startswith("sha256:")
    assert "secret-psk" not in response.text
    assert "raw-write-token" not in response.text
    assert audit.events[-1].path == "/agent/clients/dry-run"
```

- [ ] **Step 2: Run test to verify RED**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_api.py::test_agent_write_dry_run_returns_redacted_preflight_reference -v
```

Expected: fail because dry-run response does not yet include `preflight`.

- [ ] **Step 3: Add preflight construction**

Import:

```python
from hashlib import sha256
import time
from app.agent.write_confirmation import WritePreflightReference
```

Add helpers near `_extract_bearer_token`:

```python
def _request_hash(payload: dict[str, object]) -> str:
    stable = "|".join(f"{key}={payload.get(key, '')}" for key in sorted(payload))
    return "sha256:" + sha256(stable.encode("utf-8")).hexdigest()


def _preflight_for_payload(
    *,
    payload: dict[str, object],
    operation_id: str,
    result_message: str,
    now_epoch: int,
) -> WritePreflightReference:
    return WritePreflightReference(
        preflight_id=f"preflight:{operation_id}:{now_epoch}",
        operation_id=operation_id,
        actor_surface=str(payload.get("actor_surface", "api")),
        actor_id=str(payload.get("actor_id", "unknown")),
        server_alias=str(payload.get("server_alias", "")),
        client_id=str(payload.get("client_id", "")),
        peer_public_key=str(payload.get("peer_public_key", "")),
        request_hash=_request_hash(payload),
        issued_at_epoch=now_epoch,
        expires_at_epoch=now_epoch + 300,
        result_state="passed",
        message=result_message,
        secret_values=(str(payload.get("preshared_key", "")),),
    )
```

Update dry-run route response:

```python
            now_epoch = int(time.time())
            preflight = _preflight_for_payload(
                payload=payload,
                operation_id="local_agent.clients.apply",
                result_message=str(result.redacted_payload()["message"]),
                now_epoch=now_epoch,
            )
            response = result.redacted_payload()
            response["preflight"] = preflight.redacted_payload()
            return response
```

- [ ] **Step 4: Run dry-run test to verify GREEN**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_api.py::test_agent_write_dry_run_returns_redacted_preflight_reference -v
```

Expected: pass.

- [ ] **Step 5: Commit**

```powershell
git add app/agent/api.py tests/agent/test_api.py
git commit -m "Add Local Agent write dry-run preflight"
```

## Task 4: Apply/Revoke Confirmation And Audit Blocking

**Files:**
- Modify: `tests/agent/test_api.py`
- Modify: `app/agent/api.py`

- [ ] **Step 1: Write failing mutation safety tests**

Add:

```python
def test_agent_write_apply_requires_fresh_confirmation():
    app = create_agent_app(
        adapter=FakeLocalRuntimeAdapter(RuntimeSnapshot("demo-vps", "docker", "running", ())),
        tokens=(_write_token(),),
        write_enabled=True,
        peer_command_adapter=RecordingPeerCommandAdapter(),
    )
    client = TestClient(app)

    response = client.post(
        "/agent/clients",
        headers=_write_auth_headers(),
        json={**_apply_payload(), "confirmation": {}},
    )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "preflight_required"


def test_agent_write_apply_blocks_mutation_when_audit_write_fails():
    audit = FailingWriteAuditSink()
    peer_adapter = RecordingPeerCommandAdapter()
    app = create_agent_app(
        adapter=FakeLocalRuntimeAdapter(RuntimeSnapshot("demo-vps", "docker", "running", ())),
        tokens=(_write_token(),),
        write_enabled=True,
        peer_command_adapter=peer_adapter,
        write_audit_sink=audit,
    )
    client = TestClient(app)

    response = client.post(
        "/agent/clients",
        headers=_write_auth_headers(),
        json=_confirmed_apply_payload(),
    )

    assert response.status_code == 500
    assert response.json()["detail"]["code"] == "mutation_failed"
    assert peer_adapter.apply_requests == []
```

Add helpers:

```python
def _confirmed_apply_payload() -> dict[str, object]:
    payload = _apply_payload()
    payload["preflight"] = {
        "preflight_id": "preflight-1",
        "operation_id": "local_agent.clients.apply",
        "actor_surface": "web_admin",
        "actor_id": "admin-1",
        "server_alias": "demo-vps",
        "client_id": "client-1",
        "peer_public_key": "peer-public",
        "request_hash": "sha256:test",
        "issued_at_epoch": 100,
        "expires_at_epoch": 9999999999,
        "result_state": "passed",
        "message": "No changes will be made.",
    }
    payload["confirmation"] = {
        "confirmation_id": "confirmation-1",
        "confirmation_nonce": "nonce-secret",
        "issued_at_epoch": 101,
        "expires_at_epoch": 9999999999,
        "message": "Confirm peer apply.",
    }
    return payload


class FailingWriteAuditSink:
    def record(self, event):
        raise RuntimeError("audit db unavailable")
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_api.py::test_agent_write_apply_requires_fresh_confirmation tests/agent/test_api.py::test_agent_write_apply_blocks_mutation_when_audit_write_fails -v
```

Expected: fail because apply route and `write_audit_sink` are not implemented.

- [ ] **Step 3: Add mutation route dependencies**

Extend `create_agent_app`:

```python
    write_audit_sink=None,
```

Import:

```python
from app.agent.write_confirmation import (
    WriteConfirmationChallenge,
    WritePreflightReference,
    WritePreflightRequiredError,
    ensure_mutation_allowed,
)
from app.agent.write_audit import WriteAuditEvent
```

Add helper:

```python
def _write_error(code: str, message: str, status_code: int) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail={"code": code, "message": message},
    )
```

- [ ] **Step 4: Add apply route with audit-before-mutation**

Inside `if write_enabled:`, add:

```python
        apply_policy = write_policies[("POST", "/agent/clients")]

        @app.post("/agent/clients")
        def clients_apply(
            payload: dict[str, object],
            token: AgentToken = Depends(require_policy(apply_policy)),
        ) -> dict[str, object]:
            request = AgentPeerApplyRequest(
                client_id=str(payload.get("client_id", "")),
                peer_public_key=str(payload.get("peer_public_key", "")),
                preshared_key=str(payload.get("preshared_key", "")),
                vpn_ip=str(payload.get("vpn_ip", "")),
                protocol=str(payload.get("protocol", "amneziawg")),
            )
            try:
                preflight, confirmation = _confirmation_from_payload(payload)
                ensure_mutation_allowed(
                    preflight=preflight,
                    confirmation=confirmation,
                    operation_id="local_agent.clients.apply",
                    actor_surface=preflight.actor_surface,
                    actor_id=preflight.actor_id,
                    now_epoch=int(time.time()),
                )
            except WritePreflightRequiredError as exc:
                raise _write_error("preflight_required", str(exc), status.HTTP_409_CONFLICT) from exc

            try:
                _record_write_audit_start(
                    write_audit_sink=write_audit_sink,
                    operation_id="local_agent.clients.apply",
                    payload=payload,
                    peer_public_key=request.peer_public_key,
                )
            except RuntimeError as exc:
                raise _write_error("mutation_failed", "audit write failed", status.HTTP_500_INTERNAL_SERVER_ERROR) from exc

            receipt = peer_command_adapter.apply_peer(request, preflight_confirmed=True)
            response = receipt.result.redacted_payload()
            response["rollback_reference"] = receipt.rollback_reference
            response["peer_public_key_fingerprint"] = receipt.peer_public_key_fingerprint
            audit_allowed(apply_policy, token)
            return response
```

- [ ] **Step 5: Add confirmation and audit helpers**

Add:

```python
def _confirmation_from_payload(
    payload: dict[str, object],
) -> tuple[WritePreflightReference, WriteConfirmationChallenge]:
    preflight_payload = dict(payload.get("preflight") or {})
    confirmation_payload = dict(payload.get("confirmation") or {})
    preflight = WritePreflightReference(
        preflight_id=str(preflight_payload.get("preflight_id", "")),
        operation_id=str(preflight_payload.get("operation_id", "")),
        actor_surface=str(preflight_payload.get("actor_surface", "")),
        actor_id=str(preflight_payload.get("actor_id", "")),
        server_alias=str(preflight_payload.get("server_alias", "")),
        client_id=str(preflight_payload.get("client_id", "")),
        peer_public_key=str(preflight_payload.get("peer_public_key", "")),
        request_hash=str(preflight_payload.get("request_hash", "")),
        issued_at_epoch=int(preflight_payload.get("issued_at_epoch", 0)),
        expires_at_epoch=int(preflight_payload.get("expires_at_epoch", 0)),
        result_state=str(preflight_payload.get("result_state", "")),
        message=str(preflight_payload.get("message", "")),
    )
    confirmation = WriteConfirmationChallenge(
        confirmation_id=str(confirmation_payload.get("confirmation_id", "")),
        preflight=preflight,
        actor_surface=preflight.actor_surface,
        actor_id=preflight.actor_id,
        confirmation_nonce=str(confirmation_payload.get("confirmation_nonce", "")),
        issued_at_epoch=int(confirmation_payload.get("issued_at_epoch", 0)),
        expires_at_epoch=int(confirmation_payload.get("expires_at_epoch", 0)),
        message=str(confirmation_payload.get("message", "")),
    )
    return preflight, confirmation


def _record_write_audit_start(
    *,
    write_audit_sink,
    operation_id: str,
    payload: dict[str, object],
    peer_public_key: str,
) -> None:
    if write_audit_sink is None:
        return
    event = WriteAuditEvent(
        audit_id=f"audit:{operation_id}:{int(time.time())}",
        operation_id=operation_id,
        actor_surface=str(payload.get("actor_surface", "api")),
        actor_id=str(payload.get("actor_id", "unknown")),
        result_state="mutation_planned",
        server_alias=str(payload.get("server_alias", "")),
        client_id=str(payload.get("client_id", "")),
        peer_public_key=peer_public_key,
        rollback_reference="rollback:pending",
        message="Local Agent write mutation requested.",
    )
    write_audit_sink.record(event)
```

This is intentionally strict: audit write fails, block mutation.

- [ ] **Step 6: Run mutation safety tests to verify GREEN**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_api.py::test_agent_write_apply_requires_fresh_confirmation tests/agent/test_api.py::test_agent_write_apply_blocks_mutation_when_audit_write_fails -v
```

Expected: pass.

- [ ] **Step 7: Commit**

```powershell
git add app/agent/api.py tests/agent/test_api.py
git commit -m "Add Local Agent write apply guard"
```

## Task 5: Revoke Route And Redaction

**Files:**
- Modify: `tests/agent/test_api.py`
- Modify: `app/agent/api.py`

- [ ] **Step 1: Write failing revoke tests**

Add:

```python
def test_agent_write_revoke_requires_confirmation_and_returns_redacted_receipt():
    peer_adapter = RecordingPeerCommandAdapter()
    app = create_agent_app(
        adapter=FakeLocalRuntimeAdapter(RuntimeSnapshot("demo-vps", "docker", "running", ())),
        tokens=(_write_token(),),
        write_enabled=True,
        peer_command_adapter=peer_adapter,
    )
    client = TestClient(app)

    response = client.delete(
        "/agent/clients/client-1",
        headers=_write_auth_headers(),
        json=_confirmed_revoke_payload(),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["operation_id"] == "local_agent.clients.revoke"
    assert payload["status"] == "revoked"
    assert payload["rollback_reference"].startswith("rollback:")
    assert payload["peer_public_key_fingerprint"].startswith("sha256:")
    assert "private key" not in response.text.lower()
    assert "secret-psk" not in response.text
    assert "vpn://" not in response.text
```

Add:

```python
def _confirmed_revoke_payload() -> dict[str, object]:
    payload = _confirmed_apply_payload()
    payload.pop("preshared_key", None)
    payload["operation_id"] = "local_agent.clients.revoke"
    payload["preflight"]["operation_id"] = "local_agent.clients.revoke"
    return payload
```

Extend `RecordingPeerCommandAdapter`:

```python
    def apply_peer(self, request, *, preflight_confirmed: bool):
        self.apply_requests.append((request, preflight_confirmed))
        return PeerCommandReceipt(
            result=AgentPeerMutationResult(
                operation_id="local_agent.clients.apply",
                status="applied",
                dry_run=False,
                message="Peer apply succeeded.",
                planned_commands=("awg set awg0 peer peer-public allowed-ips 10.8.0.2/32",),
                secret_values=("secret-psk",),
            ),
            rollback_reference="rollback:apply:client-1",
            peer_public_key_fingerprint="sha256:peerfingerprint",
        )

    def revoke_peer(self, request, *, preflight_confirmed: bool):
        self.revoke_requests.append((request, preflight_confirmed))
        return PeerCommandReceipt(
            result=AgentPeerMutationResult(
                operation_id="local_agent.clients.revoke",
                status="revoked",
                dry_run=False,
                message="Peer revoke succeeded.",
                planned_commands=("awg set awg0 peer peer-public remove",),
            ),
            rollback_reference="rollback:revoke:client-1",
            peer_public_key_fingerprint="sha256:peerfingerprint",
        )
```

- [ ] **Step 2: Run test to verify RED**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_api.py::test_agent_write_revoke_requires_confirmation_and_returns_redacted_receipt -v
```

Expected: fail because revoke route is not implemented.

- [ ] **Step 3: Add revoke route**

Inside `if write_enabled:`, add:

```python
        revoke_policy = write_policies[("DELETE", "/agent/clients/{id}")]

        @app.delete("/agent/clients/{client_id}")
        def clients_revoke(
            client_id: str,
            payload: dict[str, object],
            token: AgentToken = Depends(require_policy(revoke_policy)),
        ) -> dict[str, object]:
            request = AgentPeerRevokeRequest(
                client_id=client_id,
                peer_public_key=str(payload.get("peer_public_key", "")),
            )
            try:
                preflight, confirmation = _confirmation_from_payload(payload)
                ensure_mutation_allowed(
                    preflight=preflight,
                    confirmation=confirmation,
                    operation_id="local_agent.clients.revoke",
                    actor_surface=preflight.actor_surface,
                    actor_id=preflight.actor_id,
                    now_epoch=int(time.time()),
                )
            except WritePreflightRequiredError as exc:
                raise _write_error("preflight_required", str(exc), status.HTTP_409_CONFLICT) from exc

            try:
                _record_write_audit_start(
                    write_audit_sink=write_audit_sink,
                    operation_id="local_agent.clients.revoke",
                    payload={**payload, "client_id": client_id},
                    peer_public_key=request.peer_public_key,
                )
            except RuntimeError as exc:
                raise _write_error("mutation_failed", "audit write failed", status.HTTP_500_INTERNAL_SERVER_ERROR) from exc

            receipt = peer_command_adapter.revoke_peer(request, preflight_confirmed=True)
            response = receipt.result.redacted_payload()
            response["rollback_reference"] = receipt.rollback_reference
            response["peer_public_key_fingerprint"] = receipt.peer_public_key_fingerprint
            audit_allowed(revoke_policy, token)
            return response
```

- [ ] **Step 4: Run API tests to verify GREEN**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_api.py -v
```

Expected: pass.

- [ ] **Step 5: Commit**

```powershell
git add app/agent/api.py tests/agent/test_api.py
git commit -m "Add Local Agent write revoke guard"
```

## Task 6: Final Verification

**Files:**
- Verify: `tests/agent/test_policy.py`
- Verify: `tests/agent/test_api.py`
- Verify: `tests/agent/test_peer_commands.py`
- Verify: `tests/agent/test_write_contracts.py`
- Verify: `tests/agent/test_write_confirmation.py`
- Verify: `tests/agent/test_write_audit.py`
- Verify: `tests/security/test_redaction.py`
- Verify: `tests/test_file_hygiene.py`

- [ ] **Step 1: Run focused Local Agent write endpoint suite**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_policy.py tests/agent/test_api.py tests/agent/test_peer_commands.py tests/agent/test_write_contracts.py tests/agent/test_write_confirmation.py tests/agent/test_write_audit.py -v
```

Expected: pass. This is the core command string: `pytest tests/agent/test_policy.py tests/agent/test_api.py tests/agent/test_peer_commands.py tests/agent/test_write_contracts.py tests/agent/test_write_confirmation.py tests/agent/test_write_audit.py`.

- [ ] **Step 2: Run redaction and hygiene suite**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/security/test_redaction.py tests/test_file_hygiene.py tests/deploy/test_runtime_registry.py -v
```

Expected: pass. Public examples still keep write disabled and no secret markers appear in responses.

- [ ] **Step 3: Run whitespace check**

Run:

```powershell
git diff --check
```

Expected: no output and exit code 0.

- [ ] **Step 4: Commit final docs update if needed**

```powershell
git add docs/AMN3_NEXT_CHAT_HANDOFF.ru.md docs/AMN3_POST_VPS_IMPLEMENTATION_MAP.ru.md docs/superpowers/plans/2026-05-31-local-agent-write-api-slice.ru.md
git commit -m "Document Local Agent write endpoint gates"
```

Skip this commit if the implementation tasks already updated docs in earlier commits.
