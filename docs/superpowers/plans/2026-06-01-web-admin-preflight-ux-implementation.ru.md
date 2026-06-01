# Web Admin Preflight UX Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the web admin operator UX for Local Agent write preflight after VPS `GO-1`.

**Architecture:** The web admin remains a controller surface: it never shells into the VPS and never exposes raw delivery secrets. UI actions call `app/web/local_agent_actions.py`, which uses the controller-side `LocalAgentClient` from `docs/superpowers/plans/2026-06-01-local-agent-controller-client-implementation.ru.md`; the Local Agent still enforces `LOCAL_AGENT_WRITE_ENABLED`, `LOCAL_AGENT_CONTROLLER_WRITE_TOKEN_PATH`, `agent:clients:write`, preflight, confirmation, audit, and rollback boundaries. The operator must pass through `dry-run -> confirmation -> apply/revoke -> audit -> rollback`; there is no one click mutation.

**Tech Stack:** Python 3.12, FastAPI, Starlette sessions, Jinja templates, existing web admin CSS, existing Local Agent write contracts, pytest.

---

## Scope And Gates

This is the code-ready plan for `Phase 4 - web admin preflight` in `docs/AMN3_POST_VPS_IMPLEMENTATION_MAP.ru.md`.
It consumes `AgentPeerApplyRequest`, `AgentPeerRevokeRequest`, and `AgentPeerMutationResult` through the controller client wrappers.

Execute this plan only after `GO-1` in `docs/AMN3_POST_VPS_IMPLEMENTATION_MAP.ru.md` and only after these plans are implemented:

- `docs/superpowers/plans/2026-06-01-local-agent-write-settings-implementation.ru.md`
- `docs/superpowers/plans/2026-06-01-local-agent-write-audit-storage-schema.ru.md`
- `docs/superpowers/plans/2026-06-01-local-agent-peer-command-adapter.ru.md`
- `docs/superpowers/plans/2026-06-01-local-agent-write-endpoints-implementation.ru.md`
- `docs/superpowers/plans/2026-06-01-local-agent-controller-client-implementation.ru.md`

Before `GO-1`:

```text
LOCAL_AGENT_WRITE_ENABLED=false
No web admin write buttons are rendered
No route calls /agent/clients*
Read-only Local Agent probe remains unchanged
```

After `GO-1`:

```text
LOCAL_AGENT_WRITE_ENABLED=true only for controlled write test
LOCAL_AGENT_CONTROLLER_WRITE_TOKEN_PATH points to the dedicated write token
agent:clients:write is separate from read-only token scopes
Preview peer apply and revoke require dry-run before confirmation
Confirm apply and revoke require a fresh confirmation nonce
```

Sensitive values that must never appear in HTML, session, logs, audit metadata, test snapshots, exceptions, or operator messages:

- raw token
- bearer token
- Authorization header value
- private key
- PSK
- QR
- `vpn://`
- full client config

Implementation rule:

```text
do not log Authorization
```

## File Structure

- Modify `app/web/local_agent_actions.py`: add web-safe action view models, apply/revoke preflight wrappers, apply/revoke confirmation wrappers, and redacted error mapping.
- Modify `app/web/server_health.py`: keep `probe_local_agent_controller` read-only; do not add write behavior to probe.
- Modify `app/web/app.py`: add CSRF-protected web admin routes for preview and confirmation; store only redacted preflight state in `request.session`.
- Modify `app/web/templates/server_detail.html`: show Local Agent action panels, preview result, confirmation form, and blocked states.
- Modify `app/web/templates/server_health.html`: keep health page read-only; link back to server detail for write workflow.
- Modify `app/web/static/admin.css`: add compact, work-focused styles for preflight state, command preview, and confirmation controls.
- Modify `tests/web/test_server_health.py`: test wrapper redaction and write-token boundary.
- Modify `tests/web/test_app.py`: test routes, session flow, CSRF, preview rendering, confirmation, expiry, and secret redaction.
- Verify `tests/security/test_redaction.py`: page-level and exception strings must not leak secret markers.

## Web Routes

Add these web admin routes after the controller client plan is green:

```text
POST /servers/{server_id}/devices/{device_id}/agent/apply/preview
POST /servers/{server_id}/devices/{device_id}/agent/apply/confirm
POST /servers/{server_id}/peers/{client_id}/agent/revoke/preview
POST /servers/{server_id}/peers/{client_id}/agent/revoke/confirm
```

Route behavior:

- preview routes call `peer_apply_dry_run` or revoke dry-run through `app/web/local_agent_actions.py`;
- confirm routes call `apply_peer` or `revoke_peer` only if session preflight is fresh;
- every route verifies CSRF before reading or writing session state;
- routes redirect back to `/servers/{server_id}` after success or blocked states;
- failures show safe messages such as `Apply blocked`, `preflight_required`, `runtime_degraded`, `mutation_failed`, or `expired_preflight`;
- no route prints raw token, private key, PSK, QR, `vpn://`, or full client config.

## UI States

The server detail screen should expose operational controls only when all local gates are satisfied:

- Local Agent online;
- write mode enabled after `GO-1`;
- controller write token configured;
- device or peer identity is known;
- operator has a fresh CSRF token.

Required labels:

```text
Preview peer apply
Confirm apply
Revoke peer
Apply blocked
```

The preview must show:

- user/device/server identity;
- `risk_class`;
- `planned_commands`;
- `rollback_reference` when present;
- `peer_public_key_fingerprint`;
- `confirmation nonce` form field;
- expiry in operator-readable text.

The preview must not show:

- raw peer public key unless already visible in existing peer inventory;
- private key;
- PSK;
- QR;
- `vpn://`;
- full client config;
- `Authorization`.

## Task 1: Web Action View Models And Wrappers

**Files:**
- Modify: `tests/web/test_server_health.py`
- Modify: `app/web/local_agent_actions.py`

- [ ] **Step 1: Write the failing wrapper tests**

Append this import block to `tests/web/test_server_health.py` after the current Local Agent imports:

```python
from app.web.local_agent_actions import WebAgentActionError
from app.web.local_agent_actions import WebAgentPreflightSession
from app.web.local_agent_actions import run_local_agent_peer_apply_confirmation
from app.web.local_agent_actions import run_local_agent_peer_apply_preflight
from app.web.local_agent_actions import run_local_agent_peer_revoke_confirmation
from app.web.local_agent_actions import run_local_agent_peer_revoke_preflight
```

Add these tests:

```python
def test_run_local_agent_peer_apply_preflight_returns_safe_operator_plan(tmp_path):
    write_token_path = tmp_path / "local-agent-write.token"
    write_token_path.write_text("write-token", encoding="utf-8")
    calls = []

    class FakeWriteClient:
        def __init__(self, *, base_url, bearer_token):
            calls.append(("init", base_url, bearer_token))

        def peer_apply_dry_run(self, request, *, actor_surface, actor_id, server_alias):
            calls.append(("dry-run", request.client_id, actor_surface, actor_id, server_alias))
            return FakeWriteResult(
                operation_id="local_agent.clients.apply.dry_run",
                status="planned",
                rollback_reference="rollback:apply:client-1",
            )

    settings = _settings(
        local_agent_controller_enabled=True,
        local_agent_controller_base_url="http://127.0.0.1:3031",
        local_agent_controller_write_token_path=str(write_token_path),
    )

    plan = run_local_agent_peer_apply_preflight(
        settings,
        client_id="client-1",
        peer_public_key="peer-public",
        preshared_key="secret-psk",
        vpn_ip="10.8.0.2",
        actor_id="admin-1",
        server_alias="demo-vps",
        user_id="user-1",
        device_id="device-1",
        device_label="phone",
        client_factory=FakeWriteClient,
    )

    assert plan.operation_id == "local_agent.clients.apply.dry_run"
    assert plan.status == "planned"
    assert plan.action == "apply"
    assert plan.client_id == "client-1"
    assert plan.server_alias == "demo-vps"
    assert plan.risk_class == "state-write"
    assert plan.preflight.preflight_id == "preflight-1"
    assert plan.confirmation_prompt == "Confirm apply"
    assert calls[0] == ("init", "http://127.0.0.1:3031", "write-token")
    assert "secret-psk" not in repr(plan)
    assert "write-token" not in repr(plan)
    assert "vpn://" not in repr(plan)


def test_run_local_agent_peer_apply_confirmation_uses_stored_preflight_without_secret_output(tmp_path):
    write_token_path = tmp_path / "local-agent-write.token"
    write_token_path.write_text("write-token", encoding="utf-8")
    calls = []

    class FakeWriteClient:
        def __init__(self, *, base_url, bearer_token):
            calls.append(("init", bearer_token))

        def apply_peer(self, request, *, preflight, confirmation):
            calls.append(("apply", request.client_id, preflight.preflight_id, confirmation.confirmation_id))
            return FakeWriteResult(
                operation_id="local_agent.clients.apply",
                status="applied",
                rollback_reference="rollback:apply:client-1",
            )

    settings = _settings(
        local_agent_controller_enabled=True,
        local_agent_controller_base_url="http://127.0.0.1:3031",
        local_agent_controller_write_token_path=str(write_token_path),
    )

    session = WebAgentPreflightSession(
        action="apply",
        preflight_id="preflight-1",
        operation_id="local_agent.clients.apply",
        actor_surface="web_admin",
        actor_id="admin-1",
        server_alias="demo-vps",
        client_id="client-1",
        peer_public_key="peer-public",
        request_hash="sha256:request",
        issued_at_epoch=100,
        expires_at_epoch=400,
        result_state="passed",
        message="No changes will be made.",
        peer_public_key_fingerprint="sha256:peerfingerprint",
        user_id="user-1",
        device_id="device-1",
        device_label="phone",
    )

    result = run_local_agent_peer_apply_confirmation(
        settings,
        session=session,
        confirmation_nonce="operator typed nonce",
        preshared_key="secret-psk",
        vpn_ip="10.8.0.2",
        client_factory=FakeWriteClient,
    )

    assert result.operation_id == "local_agent.clients.apply"
    assert result.status == "applied"
    assert calls == [("init", "write-token"), ("apply", "client-1", "preflight-1", result.confirmation_id)]
    assert "secret-psk" not in repr(result)
    assert "write-token" not in repr(result)


def test_run_local_agent_peer_revoke_flow_uses_delete_client_method(tmp_path):
    write_token_path = tmp_path / "local-agent-write.token"
    write_token_path.write_text("write-token", encoding="utf-8")
    calls = []

    class FakeWriteClient:
        def __init__(self, *, base_url, bearer_token):
            calls.append(("init", bearer_token))

        def peer_revoke_dry_run(self, request, *, actor_surface, actor_id, server_alias):
            calls.append(("revoke-dry-run", request.client_id, actor_surface, actor_id, server_alias))
            return FakeWriteResult(
                operation_id="local_agent.clients.revoke.dry_run",
                status="planned",
                rollback_reference="rollback:revoke:client-1",
            )

        def revoke_peer(self, request, *, preflight, confirmation):
            calls.append(("revoke", request.client_id, preflight.preflight_id, confirmation.confirmation_id))
            return FakeWriteResult(
                operation_id="local_agent.clients.revoke",
                status="revoked",
                rollback_reference="rollback:revoke:client-1",
            )

    settings = _settings(
        local_agent_controller_enabled=True,
        local_agent_controller_base_url="http://127.0.0.1:3031",
        local_agent_controller_write_token_path=str(write_token_path),
    )

    preview = run_local_agent_peer_revoke_preflight(
        settings,
        client_id="client-1",
        peer_public_key="peer-public",
        actor_id="admin-1",
        server_alias="demo-vps",
        user_id="user-1",
        device_id="device-1",
        device_label="phone",
        client_factory=FakeWriteClient,
    )
    result = run_local_agent_peer_revoke_confirmation(
        settings,
        session=preview.to_session(),
        confirmation_nonce="operator typed nonce",
        client_factory=FakeWriteClient,
    )

    assert preview.action == "revoke"
    assert result.status == "revoked"
    assert calls[1][0] == "revoke-dry-run"
    assert calls[3][0] == "revoke"
```

Add these fake models at the end of `tests/web/test_server_health.py`:

```python
class FakeWritePreflight:
    preflight_id = "preflight-1"
    operation_id = "local_agent.clients.apply"
    actor_surface = "web_admin"
    actor_id = "admin-1"
    server_alias = "demo-vps"
    client_id = "client-1"
    peer_public_key_fingerprint = "sha256:peerfingerprint"
    request_hash = "sha256:request"
    issued_at_epoch = 100
    expires_at_epoch = 400
    result_state = "passed"
    message = "No changes will be made."


class FakeWriteResult:
    def __init__(
        self,
        *,
        operation_id: str,
        status: str,
        rollback_reference: str,
    ):
        self.operation_id = operation_id
        self.status = status
        self.dry_run = operation_id.endswith(".dry_run")
        self.risk_class = "state-write"
        self.consistency_status = "dry-run" if self.dry_run else "mutated"
        self.message = "Peer mutation completed."
        self.planned_commands = (
            "awg set awg0 peer sha256:peerfingerprint allowed-ips 10.8.0.2/32",
        )
        self.preflight = FakeWritePreflight() if self.dry_run else None
        self.rollback_reference = rollback_reference
        self.peer_public_key_fingerprint = "sha256:peerfingerprint"

    def __repr__(self) -> str:
        return f"FakeWriteResult(operation_id={self.operation_id!r}, status={self.status!r})"
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/web/test_server_health.py::test_run_local_agent_peer_apply_preflight_returns_safe_operator_plan tests/web/test_server_health.py::test_run_local_agent_peer_apply_confirmation_uses_stored_preflight_without_secret_output tests/web/test_server_health.py::test_run_local_agent_peer_revoke_flow_uses_delete_client_method -v
```

Expected: fail because `WebAgentPreflightSession`, `run_local_agent_peer_apply_confirmation`, `run_local_agent_peer_revoke_preflight`, and `run_local_agent_peer_revoke_confirmation` are not implemented.

- [ ] **Step 3: Add safe view models**

Add these imports to `app/web/local_agent_actions.py`:

```python
from dataclasses import asdict
from dataclasses import dataclass
from uuid import uuid4

from app.agent.write_confirmation import WriteConfirmationChallenge
from app.agent.write_confirmation import WritePreflightReference
from app.agent.write_contracts import AgentPeerApplyRequest
from app.agent.write_contracts import AgentPeerRevokeRequest
from app.security.redaction import redact
from app.time import utc_now_epoch
```

Add these models:

```python
@dataclass(frozen=True, repr=False)
class WebAgentPreflightSession:
    action: str
    preflight_id: str
    operation_id: str
    actor_surface: str
    actor_id: str
    server_alias: str
    client_id: str
    peer_public_key: str
    request_hash: str
    issued_at_epoch: int
    expires_at_epoch: int
    result_state: str
    message: str
    peer_public_key_fingerprint: str
    user_id: str
    device_id: str
    device_label: str

    def __repr__(self) -> str:
        return (
            "WebAgentPreflightSession("
            f"action={self.action!r}, preflight_id={self.preflight_id!r}, "
            f"client_id={self.client_id!r}, server_alias={self.server_alias!r})"
        )

    def to_payload(self) -> dict[str, object]:
        payload = asdict(self)
        payload.pop("peer_public_key", None)
        return payload

    def to_reference(self) -> WritePreflightReference:
        return WritePreflightReference(
            preflight_id=self.preflight_id,
            operation_id=self.operation_id,
            actor_surface=self.actor_surface,
            actor_id=self.actor_id,
            server_alias=self.server_alias,
            client_id=self.client_id,
            peer_public_key=self.peer_public_key,
            request_hash=self.request_hash,
            issued_at_epoch=self.issued_at_epoch,
            expires_at_epoch=self.expires_at_epoch,
            result_state=self.result_state,
            message=self.message,
        )


@dataclass(frozen=True, repr=False)
class WebAgentActionPlan:
    action: str
    operation_id: str
    status: str
    risk_class: str
    consistency_status: str
    message: str
    planned_commands: tuple[str, ...]
    preflight: WebAgentPreflightSession
    confirmation_prompt: str
    rollback_reference: str | None
    peer_public_key_fingerprint: str | None
    confirmation_id: str | None = None

    def __repr__(self) -> str:
        return (
            "WebAgentActionPlan("
            f"action={self.action!r}, operation_id={self.operation_id!r}, "
            f"status={self.status!r}, client_id={self.client_id!r})"
        )

    @property
    def client_id(self) -> str:
        return self.preflight.client_id

    @property
    def server_alias(self) -> str:
        return self.preflight.server_alias

    def to_session(self) -> WebAgentPreflightSession:
        return self.preflight
```

- [ ] **Step 4: Add wrapper functions**

Add these helpers below `build_local_agent_write_client()`:

```python
def run_local_agent_peer_apply_preflight(
    settings: Settings,
    *,
    client_id: str,
    peer_public_key: str,
    preshared_key: str,
    vpn_ip: str,
    actor_id: str,
    server_alias: str,
    user_id: str,
    device_id: str,
    device_label: str,
    client_factory=LocalAgentClient,
) -> WebAgentActionPlan:
    client = build_local_agent_write_client(settings, client_factory=client_factory)
    request = AgentPeerApplyRequest(
        client_id=client_id,
        peer_public_key=peer_public_key,
        preshared_key=preshared_key,
        vpn_ip=vpn_ip,
        protocol="amneziawg",
    )
    result = client.peer_apply_dry_run(
        request,
        actor_surface="web_admin",
        actor_id=actor_id,
        server_alias=server_alias,
    )
    return _plan_from_result(
        "apply",
        result,
        peer_public_key=peer_public_key,
        user_id=user_id,
        device_id=device_id,
        device_label=device_label,
        confirmation_prompt="Confirm apply",
    )


def run_local_agent_peer_revoke_preflight(
    settings: Settings,
    *,
    client_id: str,
    peer_public_key: str,
    actor_id: str,
    server_alias: str,
    user_id: str,
    device_id: str,
    device_label: str,
    client_factory=LocalAgentClient,
) -> WebAgentActionPlan:
    client = build_local_agent_write_client(settings, client_factory=client_factory)
    request = AgentPeerRevokeRequest(client_id=client_id, peer_public_key=peer_public_key)
    result = client.peer_revoke_dry_run(
        request,
        actor_surface="web_admin",
        actor_id=actor_id,
        server_alias=server_alias,
    )
    return _plan_from_result(
        "revoke",
        result,
        peer_public_key=peer_public_key,
        user_id=user_id,
        device_id=device_id,
        device_label=device_label,
        confirmation_prompt="Confirm revoke",
    )


def run_local_agent_peer_apply_confirmation(
    settings: Settings,
    *,
    session: WebAgentPreflightSession,
    confirmation_nonce: str,
    preshared_key: str,
    vpn_ip: str,
    client_factory=LocalAgentClient,
) -> WebAgentActionPlan:
    _ensure_fresh_session(session)
    client = build_local_agent_write_client(settings, client_factory=client_factory)
    confirmation = _confirmation_from_session(session, confirmation_nonce)
    result = client.apply_peer(
        AgentPeerApplyRequest(
            client_id=session.client_id,
            peer_public_key=session.peer_public_key,
            preshared_key=preshared_key,
            vpn_ip=vpn_ip,
            protocol="amneziawg",
        ),
        preflight=session.to_reference(),
        confirmation=confirmation,
    )
    return _completed_plan("apply", result, session, confirmation.confirmation_id)


def run_local_agent_peer_revoke_confirmation(
    settings: Settings,
    *,
    session: WebAgentPreflightSession,
    confirmation_nonce: str,
    client_factory=LocalAgentClient,
) -> WebAgentActionPlan:
    _ensure_fresh_session(session)
    client = build_local_agent_write_client(settings, client_factory=client_factory)
    confirmation = _confirmation_from_session(session, confirmation_nonce)
    result = client.revoke_peer(
        AgentPeerRevokeRequest(
            client_id=session.client_id,
            peer_public_key=session.peer_public_key,
        ),
        preflight=session.to_reference(),
        confirmation=confirmation,
    )
    return _completed_plan("revoke", result, session, confirmation.confirmation_id)
```

Add parser helpers:

```python
def _plan_from_result(
    action: str,
    result,
    *,
    peer_public_key: str,
    user_id: str,
    device_id: str,
    device_label: str,
    confirmation_prompt: str,
) -> WebAgentActionPlan:
    if result.preflight is None:
        raise WebAgentActionError("Local Agent did not return preflight data")
    preflight = WebAgentPreflightSession(
        action=action,
        preflight_id=result.preflight.preflight_id,
        operation_id=result.preflight.operation_id,
        actor_surface=result.preflight.actor_surface,
        actor_id=result.preflight.actor_id,
        server_alias=result.preflight.server_alias,
        client_id=result.preflight.client_id,
        peer_public_key=peer_public_key,
        request_hash=result.preflight.request_hash,
        issued_at_epoch=result.preflight.issued_at_epoch,
        expires_at_epoch=result.preflight.expires_at_epoch,
        result_state=result.preflight.result_state,
        message=redact(result.preflight.message),
        peer_public_key_fingerprint=result.preflight.peer_public_key_fingerprint,
        user_id=user_id,
        device_id=device_id,
        device_label=device_label,
    )
    return WebAgentActionPlan(
        action=action,
        operation_id=result.operation_id,
        status=result.status,
        risk_class=result.risk_class,
        consistency_status=result.consistency_status,
        message=redact(result.message),
        planned_commands=tuple(redact(command) for command in result.planned_commands),
        preflight=preflight,
        confirmation_prompt=confirmation_prompt,
        rollback_reference=redact(result.rollback_reference) if result.rollback_reference else None,
        peer_public_key_fingerprint=result.peer_public_key_fingerprint,
    )


def _completed_plan(
    action: str,
    result,
    session: WebAgentPreflightSession,
    confirmation_id: str,
) -> WebAgentActionPlan:
    return WebAgentActionPlan(
        action=action,
        operation_id=result.operation_id,
        status=result.status,
        risk_class=result.risk_class,
        consistency_status=result.consistency_status,
        message=redact(result.message),
        planned_commands=tuple(redact(command) for command in result.planned_commands),
        preflight=session,
        confirmation_prompt="Confirmed",
        rollback_reference=redact(result.rollback_reference) if result.rollback_reference else None,
        peer_public_key_fingerprint=result.peer_public_key_fingerprint,
        confirmation_id=confirmation_id,
    )


def _confirmation_from_session(
    session: WebAgentPreflightSession,
    confirmation_nonce: str,
) -> WriteConfirmationChallenge:
    now = utc_now_epoch()
    return WriteConfirmationChallenge(
        confirmation_id=f"web-confirmation-{uuid4().hex}",
        preflight=session.to_reference(),
        actor_surface="web_admin",
        actor_id=session.actor_id,
        confirmation_nonce=confirmation_nonce,
        issued_at_epoch=now,
        expires_at_epoch=min(session.expires_at_epoch, now + 300),
        message="Web admin confirmation nonce accepted.",
    )


def _ensure_fresh_session(session: WebAgentPreflightSession) -> None:
    if session.expires_at_epoch <= utc_now_epoch():
        raise WebAgentActionError("expired_preflight")
```

- [ ] **Step 5: Run wrapper tests to verify GREEN**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/web/test_server_health.py -v
```

Expected: pass.

- [ ] **Step 6: Commit**

```powershell
git add app/web/local_agent_actions.py tests/web/test_server_health.py
git commit -m "Add web admin Local Agent action wrappers"
```

## Task 2: Web Routes And Session State

**Files:**
- Modify: `tests/web/test_app.py`
- Modify: `app/web/app.py`

- [ ] **Step 1: Write failing route tests**

Add imports to `tests/web/test_app.py`:

```python
import app.web.app as web_app
from app.web.local_agent_actions import WebAgentActionPlan
from app.web.local_agent_actions import WebAgentPreflightSession
```

Add this test:

```python
def test_server_agent_apply_preview_stores_redacted_preflight_session(tmp_path: Path, monkeypatch):
    settings = _settings(tmp_path)
    _seed_dashboard_data(Path(settings.database_path))
    server_id = 1
    device_id = 1
    calls = []

    def fake_preview(settings, **kwargs):
        calls.append(kwargs)
        return _fake_action_plan(action="apply", status="planned")

    monkeypatch.setattr(web_app, "run_local_agent_peer_apply_preflight", fake_preview)
    client = _client(settings=settings)
    page = _login(client)

    response = client.post(
        f"/servers/{server_id}/devices/{device_id}/agent/apply/preview",
        data={"csrf_token": _csrf_token(page.text)},
        follow_redirects=False,
    )
    detail = client.get(f"/servers/{server_id}")

    assert response.status_code == 303
    assert response.headers["location"] == f"/servers/{server_id}"
    assert calls[0]["actor_id"] == "root"
    assert "Preview peer apply" in detail.text
    assert "Confirm apply" in detail.text
    assert "sha256:peerfingerprint" in detail.text
    assert "secret-psk" not in detail.text
    assert "raw-agent-token" not in detail.text
    assert "vpn://" not in detail.text
```

Add this confirmation test:

```python
def test_server_agent_apply_confirm_requires_stored_preflight_and_records_action(
    tmp_path: Path,
    monkeypatch,
):
    settings = _settings(tmp_path)
    _seed_dashboard_data(Path(settings.database_path))
    server_id = 1
    device_id = 1
    calls = []

    monkeypatch.setattr(
        web_app,
        "run_local_agent_peer_apply_preflight",
        lambda settings, **kwargs: _fake_action_plan(action="apply", status="planned"),
    )

    def fake_confirm(settings, **kwargs):
        calls.append(kwargs)
        return _fake_action_plan(
            action="apply",
            operation_id="local_agent.clients.apply",
            status="applied",
        )

    monkeypatch.setattr(web_app, "run_local_agent_peer_apply_confirmation", fake_confirm)
    client = _client(settings=settings)
    page = _login(client)
    client.post(
        f"/servers/{server_id}/devices/{device_id}/agent/apply/preview",
        data={"csrf_token": _csrf_token(page.text)},
    )
    detail = client.get(f"/servers/{server_id}")

    response = client.post(
        f"/servers/{server_id}/devices/{device_id}/agent/apply/confirm",
        data={
            "csrf_token": _csrf_token(detail.text),
            "confirmation_nonce": "operator typed nonce",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == f"/servers/{server_id}"
    assert calls[0]["confirmation_nonce"] == "operator typed nonce"
```

Add this blocked confirmation test:

```python
def test_server_agent_apply_confirm_without_preview_is_blocked(tmp_path: Path):
    settings = _settings(tmp_path)
    _seed_dashboard_data(Path(settings.database_path))
    client = _client(settings=settings)
    page = _login(client)

    response = client.post(
        "/servers/1/devices/1/agent/apply/confirm",
        data={
            "csrf_token": _csrf_token(page.text),
            "confirmation_nonce": "operator typed nonce",
        },
        follow_redirects=False,
    )

    assert response.status_code == 400
    assert "preflight_required" in response.text
```

Add fake helpers:

```python
def _login(client: TestClient):
    page = client.get("/login")
    client.post(
        "/login",
        data={
            "username": "root",
            "password": "correct-password",
            "csrf_token": _csrf_token(page.text),
        },
    )
    return client.get("/")


def _fake_action_plan(
    *,
    action: str,
    operation_id: str = "local_agent.clients.apply.dry_run",
    status: str,
) -> WebAgentActionPlan:
    preflight = WebAgentPreflightSession(
        action=action,
        preflight_id="preflight-1",
        operation_id="local_agent.clients.apply",
        actor_surface="web_admin",
        actor_id="root",
        server_alias="demo-vps",
        client_id="client-1",
        peer_public_key="peer-public",
        request_hash="sha256:request",
        issued_at_epoch=100,
        expires_at_epoch=400,
        result_state="passed",
        message="No changes will be made.",
        peer_public_key_fingerprint="sha256:peerfingerprint",
        user_id="user-1",
        device_id="device-1",
        device_label="phone",
    )
    return WebAgentActionPlan(
        action=action,
        operation_id=operation_id,
        status=status,
        risk_class="state-write",
        consistency_status="dry-run" if operation_id.endswith(".dry_run") else "mutated",
        message="No changes will be made.",
        planned_commands=("awg set awg0 peer sha256:peerfingerprint allowed-ips 10.8.0.2/32",),
        preflight=preflight,
        confirmation_prompt="Confirm apply",
        rollback_reference="rollback:apply:client-1",
        peer_public_key_fingerprint="sha256:peerfingerprint",
    )
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/web/test_app.py::test_server_agent_apply_preview_stores_redacted_preflight_session tests/web/test_app.py::test_server_agent_apply_confirm_requires_stored_preflight_and_records_action tests/web/test_app.py::test_server_agent_apply_confirm_without_preview_is_blocked -v
```

Expected: fail with `404 Not Found` because routes do not exist.

- [ ] **Step 3: Add route imports and session helpers**

In `app/web/app.py`, add imports:

```python
from app.web.local_agent_actions import WebAgentActionError
from app.web.local_agent_actions import WebAgentActionPlan
from app.web.local_agent_actions import WebAgentPreflightSession
from app.web.local_agent_actions import run_local_agent_peer_apply_confirmation
from app.web.local_agent_actions import run_local_agent_peer_apply_preflight
from app.web.local_agent_actions import run_local_agent_peer_revoke_confirmation
from app.web.local_agent_actions import run_local_agent_peer_revoke_preflight
```

Add helpers near `_peer_sync_session_key()`:

```python
def _agent_action_session_key(server_id: int, action: str, identity_id: int) -> str:
    return f"server_agent_action:{server_id}:{action}:{identity_id}"


def _store_agent_action_plan(
    request: Request,
    *,
    server_id: int,
    action: str,
    identity_id: int,
    plan: WebAgentActionPlan,
) -> None:
    request.session[_agent_action_session_key(server_id, action, identity_id)] = json.dumps(
        plan.to_session().to_payload()
    )
    request.session[f"{_agent_action_session_key(server_id, action, identity_id)}:view"] = json.dumps(
        {
            "action": plan.action,
            "operation_id": plan.operation_id,
            "status": plan.status,
            "risk_class": plan.risk_class,
            "consistency_status": plan.consistency_status,
            "message": redact(plan.message),
            "planned_commands": [redact(command) for command in plan.planned_commands],
            "confirmation_prompt": plan.confirmation_prompt,
            "rollback_reference": redact(plan.rollback_reference or ""),
            "peer_public_key_fingerprint": plan.peer_public_key_fingerprint,
            "client_id": plan.client_id,
            "server_alias": plan.server_alias,
        }
    )


def _load_agent_action_session(
    request: Request,
    *,
    server_id: int,
    action: str,
    identity_id: int,
) -> WebAgentPreflightSession | None:
    raw = request.session.get(_agent_action_session_key(server_id, action, identity_id))
    if not raw:
        return None
    data = json.loads(raw)
    return WebAgentPreflightSession(
        action=str(data["action"]),
        preflight_id=str(data["preflight_id"]),
        operation_id=str(data["operation_id"]),
        actor_surface=str(data["actor_surface"]),
        actor_id=str(data["actor_id"]),
        server_alias=str(data["server_alias"]),
        client_id=str(data["client_id"]),
        peer_public_key="",
        request_hash=str(data["request_hash"]),
        issued_at_epoch=int(data["issued_at_epoch"]),
        expires_at_epoch=int(data["expires_at_epoch"]),
        result_state=str(data["result_state"]),
        message=str(data["message"]),
        peer_public_key_fingerprint=str(data["peer_public_key_fingerprint"]),
        user_id=str(data["user_id"]),
        device_id=str(data["device_id"]),
        device_label=str(data["device_label"]),
    )
```

During confirm, restore `peer_public_key` from the current database row instead of trusting session payload.

- [ ] **Step 4: Add apply preview and confirm routes**

Add routes near existing `/servers/{server_id}/missing-devices/{device_id}/add`:

```python
    @app.post("/servers/{server_id}/devices/{device_id}/agent/apply/preview")
    async def preview_agent_peer_apply(
        request: Request,
        server_id: int,
        device_id: int,
        csrf_token: str = Form(""),
    ):
        if not _is_authenticated(request):
            return RedirectResponse("/login", status_code=303)
        if not verify_csrf_token(request.session, csrf_token):
            return PlainTextResponse("Invalid CSRF token", status_code=403)
        try:
            device = _load_device_for_agent_action(actual_settings, server_id, device_id)
            plan = run_local_agent_peer_apply_preflight(
                actual_settings,
                client_id=str(device["client_id"]),
                peer_public_key=str(device["peer_public_key"]),
                preshared_key=str(device["preshared_key"]),
                vpn_ip=str(device["vpn_ip"]),
                actor_id=str(request.session.get("web_admin_username", "")),
                server_alias=str(device["server_name"]),
                user_id=str(device["user_id"]),
                device_id=str(device["id"]),
                device_label=str(device["name"]),
            )
            _store_agent_action_plan(
                request,
                server_id=server_id,
                action="apply",
                identity_id=device_id,
                plan=plan,
            )
        except (LookupError, ValueError, WebAgentActionError) as exc:
            request.session[_agent_action_flash_key(server_id)] = redact(f"Apply blocked: {exc}")
        return RedirectResponse(f"/servers/{server_id}", status_code=303)

    @app.post("/servers/{server_id}/devices/{device_id}/agent/apply/confirm")
    async def confirm_agent_peer_apply(
        request: Request,
        server_id: int,
        device_id: int,
        confirmation_nonce: str = Form(""),
        csrf_token: str = Form(""),
    ):
        if not _is_authenticated(request):
            return RedirectResponse("/login", status_code=303)
        if not verify_csrf_token(request.session, csrf_token):
            return PlainTextResponse("Invalid CSRF token", status_code=403)
        session = _load_agent_action_session(
            request,
            server_id=server_id,
            action="apply",
            identity_id=device_id,
        )
        if session is None:
            return PlainTextResponse("preflight_required", status_code=400)
        try:
            device = _load_device_for_agent_action(actual_settings, server_id, device_id)
            session = replace(session, peer_public_key=str(device["peer_public_key"]))
            plan = run_local_agent_peer_apply_confirmation(
                actual_settings,
                session=session,
                confirmation_nonce=confirmation_nonce,
                preshared_key=str(device["preshared_key"]),
                vpn_ip=str(device["vpn_ip"]),
            )
            _record_web_server_action(
                _repo_from_request(actual_settings),
                actual_settings,
                request,
                action="web_agent_peer_apply",
                server_id=server_id,
                metadata={
                    "client_id": plan.client_id,
                    "operation_id": plan.operation_id,
                    "status": plan.status,
                    "peer_public_key_fingerprint": plan.peer_public_key_fingerprint,
                },
            )
        except WebAgentActionError as exc:
            request.session[_agent_action_flash_key(server_id)] = redact(f"Apply blocked: {exc}")
        finally:
            request.session.pop(_agent_action_session_key(server_id, "apply", device_id), None)
        return RedirectResponse(f"/servers/{server_id}", status_code=303)
```

When implementing, use the repository context pattern already used in adjacent routes instead of `_repo_from_request()`. The metadata keys above are the exact safe metadata set; do not include raw peer key, PSK, token, QR, `vpn://`, or full client config.

- [ ] **Step 5: Add revoke preview and confirm routes**

Add the same route pattern for:

```text
POST /servers/{server_id}/peers/{client_id}/agent/revoke/preview
POST /servers/{server_id}/peers/{client_id}/agent/revoke/confirm
```

Use `run_local_agent_peer_revoke_preflight` and `run_local_agent_peer_revoke_confirmation`. The safe action metadata is:

```python
{
    "client_id": plan.client_id,
    "operation_id": plan.operation_id,
    "status": plan.status,
    "peer_public_key_fingerprint": plan.peer_public_key_fingerprint,
    "rollback_reference": plan.rollback_reference,
}
```

- [ ] **Step 6: Run route tests to verify GREEN**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/web/test_app.py -v
```

Expected: pass.

- [ ] **Step 7: Commit**

```powershell
git add app/web/app.py tests/web/test_app.py
git commit -m "Add web admin Local Agent preflight routes"
```

## Task 3: Server Detail Template And Styling

**Files:**
- Modify: `tests/web/test_app.py`
- Modify: `app/web/templates/server_detail.html`
- Modify: `app/web/templates/server_health.html`
- Modify: `app/web/static/admin.css`

- [ ] **Step 1: Write failing rendering tests**

Add:

```python
def test_server_detail_renders_local_agent_preflight_controls_without_secrets(tmp_path: Path, monkeypatch):
    settings = _settings(tmp_path)
    _seed_dashboard_data(Path(settings.database_path))
    monkeypatch.setattr(
        web_app,
        "run_local_agent_peer_apply_preflight",
        lambda settings, **kwargs: _fake_action_plan(action="apply", status="planned"),
    )
    client = _client(settings=settings)
    page = _login(client)
    client.post(
        "/servers/1/devices/1/agent/apply/preview",
        data={"csrf_token": _csrf_token(page.text)},
    )

    response = client.get("/servers/1")

    assert response.status_code == 200
    assert "Local Agent write preview" in response.text
    assert "Preview peer apply" in response.text
    assert "Confirm apply" in response.text
    assert "risk_class" in response.text
    assert "planned_commands" in response.text
    assert "rollback:apply:client-1" in response.text
    assert "secret-psk" not in response.text
    assert "raw-agent-token" not in response.text
    assert "private key" not in response.text
    assert "vpn://" not in response.text
```

Add:

```python
def test_server_health_page_remains_read_only_and_links_to_server_detail(tmp_path: Path):
    settings = _settings(tmp_path)
    _seed_dashboard_data(Path(settings.database_path))
    client = _client(settings=settings)
    _login(client)

    response = client.get("/servers/1/health")

    assert response.status_code == 200
    assert "Run health check" in response.text
    assert "Preview peer apply" not in response.text
    assert "Confirm apply" not in response.text
    assert 'href="/servers/1"' in response.text
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/web/test_app.py::test_server_detail_renders_local_agent_preflight_controls_without_secrets tests/web/test_app.py::test_server_health_page_remains_read_only_and_links_to_server_detail -v
```

Expected: first test fails because the preview panel is not rendered.

- [ ] **Step 3: Add template context**

When rendering `server_detail.html`, add:

```python
agent_action_preview=_load_agent_action_view(request, server_id),
agent_action_error=_pop_agent_action_flash(request, server_id),
```

Add helper:

```python
def _load_agent_action_view(request: Request, server_id: int) -> dict[str, object] | None:
    prefix = f"server_agent_action:{server_id}:"
    for key, value in request.session.items():
        if key.startswith(prefix) and key.endswith(":view"):
            return json.loads(str(value))
    return None
```

- [ ] **Step 4: Add server detail panel**

In `app/web/templates/server_detail.html`, add a panel after the Local Agent status panel:

```html
  <section class="panel panel-spaced agent-action-panel">
    <div class="panel-header">
      <h2>Local Agent write preview</h2>
    </div>
    {% if agent_action_error %}
      <p class="alert alert-warning">Apply blocked: {{ agent_action_error }}</p>
    {% endif %}
    {% if agent_action_preview %}
      <dl class="details">
        <div>
          <dt>operation_id</dt>
          <dd>{{ agent_action_preview.operation_id }}</dd>
        </div>
        <div>
          <dt>risk_class</dt>
          <dd>{{ agent_action_preview.risk_class }}</dd>
        </div>
        <div>
          <dt>planned_commands</dt>
          <dd>
            <ol class="command-list">
              {% for command in agent_action_preview.planned_commands %}
                <li><code>{{ command }}</code></li>
              {% endfor %}
            </ol>
          </dd>
        </div>
        <div>
          <dt>rollback</dt>
          <dd>{{ agent_action_preview.rollback_reference or "-" }}</dd>
        </div>
      </dl>
      <form action="/servers/{{ server.id }}/devices/{{ agent_action_preview.device_id }}/agent/apply/confirm" method="post">
        <input name="csrf_token" type="hidden" value="{{ csrf_token }}">
        <label>
          <span>confirmation nonce</span>
          <input name="confirmation_nonce" type="text" autocomplete="off">
        </label>
        <button class="button button-danger" type="submit">Confirm apply</button>
      </form>
    {% else %}
      <p class="empty-state">Run Preview peer apply before confirming a mutation.</p>
    {% endif %}
  </section>
```

Place `Preview peer apply` forms next to missing peers/devices after peer sync data is loaded. Do not render `Confirm apply` without a stored preflight view.

- [ ] **Step 5: Keep health template read-only**

In `app/web/templates/server_health.html`, keep existing Local Agent status fields and add only:

```html
      <a class="button button-secondary" href="/servers/{{ server.id }}">Open server actions</a>
```

Do not add `Preview peer apply`, `Confirm apply`, `Revoke peer`, or mutation forms to `server_health.html`.

- [ ] **Step 6: Add CSS**

Append to `app/web/static/admin.css`:

```css
.agent-action-panel {
  border-left: 4px solid var(--color-warning);
}

.agent-action-panel .command-list {
  margin: 0;
}

.agent-action-panel input[name="confirmation_nonce"] {
  max-width: 24rem;
}

.alert-warning {
  border: 1px solid var(--color-warning);
  padding: 0.75rem;
}
```

- [ ] **Step 7: Run rendering tests to verify GREEN**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/web/test_app.py -v
```

Expected: pass.

- [ ] **Step 8: Commit**

```powershell
git add app/web/templates/server_detail.html app/web/templates/server_health.html app/web/static/admin.css tests/web/test_app.py
git commit -m "Render web admin Local Agent preflight panel"
```

## Task 4: Error Mapping, Expiry, And Redaction

**Files:**
- Modify: `tests/web/test_app.py`
- Modify: `tests/web/test_server_health.py`
- Modify: `app/web/local_agent_actions.py`
- Modify: `app/web/app.py`

- [ ] **Step 1: Write failing error tests**

Add:

```python
def test_agent_preflight_expiry_blocks_confirmation_with_safe_message(tmp_path: Path, monkeypatch):
    settings = _settings(tmp_path)
    _seed_dashboard_data(Path(settings.database_path))
    expired_plan = _fake_action_plan(action="apply", status="planned")
    expired_plan.preflight = replace(expired_plan.preflight, expires_at_epoch=1)
    monkeypatch.setattr(
        web_app,
        "run_local_agent_peer_apply_preflight",
        lambda settings, **kwargs: expired_plan,
    )
    client = _client(settings=settings)
    page = _login(client)
    client.post(
        "/servers/1/devices/1/agent/apply/preview",
        data={"csrf_token": _csrf_token(page.text)},
    )
    detail = client.get("/servers/1")

    response = client.post(
        "/servers/1/devices/1/agent/apply/confirm",
        data={
            "csrf_token": _csrf_token(detail.text),
            "confirmation_nonce": "operator typed nonce",
        },
    )

    assert response.status_code == 200
    assert "expired_preflight" in response.text
    assert "secret-psk" not in response.text
    assert "raw-agent-token" not in response.text
```

Add:

```python
def test_agent_action_error_mapping_preserves_public_codes_and_redacts_secrets(tmp_path: Path, monkeypatch):
    settings = _settings(tmp_path)
    _seed_dashboard_data(Path(settings.database_path))

    def fake_preview(settings, **kwargs):
        raise WebAgentActionError("runtime_degraded: raw-agent-token secret-psk")

    monkeypatch.setattr(web_app, "run_local_agent_peer_apply_preflight", fake_preview)
    client = _client(settings=settings)
    page = _login(client)

    client.post(
        "/servers/1/devices/1/agent/apply/preview",
        data={"csrf_token": _csrf_token(page.text)},
    )
    response = client.get("/servers/1")

    assert "runtime_degraded" in response.text
    assert "raw-agent-token" not in response.text
    assert "secret-psk" not in response.text
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/web/test_app.py::test_agent_preflight_expiry_blocks_confirmation_with_safe_message tests/web/test_app.py::test_agent_action_error_mapping_preserves_public_codes_and_redacts_secrets -v
```

Expected: fail because expiry and public code mapping are not wired to the page.

- [ ] **Step 3: Add public error mapping**

In `app/web/local_agent_actions.py`, add:

```python
PUBLIC_AGENT_ERROR_CODES = {
    "preflight_required",
    "runtime_degraded",
    "mutation_failed",
    "missing_scope",
    "expired_preflight",
}


def safe_agent_action_error(exc: Exception) -> str:
    message = redact(str(exc))
    for code in PUBLIC_AGENT_ERROR_CODES:
        if code in message:
            return code
    return message
```

In `app/web/app.py`, store only `safe_agent_action_error(exc)` in session flash.

- [ ] **Step 4: Add response hygiene assertion**

Add to `tests/security/test_redaction.py`:

```python
def test_web_agent_action_redaction_markers_are_removed():
    text = (
        "Authorization: Bearer raw-agent-token "
        "private key secret-psk QR vpn://config full client config"
    )

    redacted = redact(text)

    assert "raw-agent-token" not in redacted
    assert "secret-psk" not in redacted
    assert "vpn://" not in redacted
```

- [ ] **Step 5: Run error and redaction tests to verify GREEN**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/web/test_app.py tests/web/test_server_health.py tests/security/test_redaction.py -v
```

Expected: pass. This is the core command string: `pytest tests/web/test_app.py tests/web/test_server_health.py tests/security/test_redaction.py`.

- [ ] **Step 6: Commit**

```powershell
git add app/web/app.py app/web/local_agent_actions.py tests/web/test_app.py tests/web/test_server_health.py tests/security/test_redaction.py
git commit -m "Harden web admin Local Agent action errors"
```

## Task 5: Final Verification And Documentation

**Files:**
- Verify: `tests/web/test_app.py`
- Verify: `tests/web/test_server_health.py`
- Verify: `tests/security/test_redaction.py`
- Verify: `tests/agent/test_client.py`
- Verify: `tests/agent/test_write_contracts.py`
- Verify: `tests/agent/test_write_confirmation.py`
- Modify: `docs/AMN3_NEXT_CHAT_HANDOFF.ru.md`
- Modify: `docs/AMN3_POST_VPS_IMPLEMENTATION_MAP.ru.md`
- Modify: `docs/AMN3_WRITE_API_UX_FLOW.ru.md`

- [ ] **Step 1: Run web action suite**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/web/test_app.py tests/web/test_server_health.py tests/security/test_redaction.py -v
```

Expected: pass.

- [ ] **Step 2: Run controller contract suite**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_client.py tests/agent/test_write_contracts.py tests/agent/test_write_confirmation.py -v
```

Expected: pass.

- [ ] **Step 3: Run registry and hygiene suite**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/deploy/test_runtime_registry.py tests/test_file_hygiene.py -v
```

Expected: pass.

- [ ] **Step 4: Run whitespace check**

Run:

```powershell
git diff --check
```

Expected: no output and exit code 0.

- [ ] **Step 5: Commit documentation links if they changed during execution**

```powershell
git add docs/AMN3_NEXT_CHAT_HANDOFF.ru.md docs/AMN3_POST_VPS_IMPLEMENTATION_MAP.ru.md docs/AMN3_WRITE_API_UX_FLOW.ru.md
git commit -m "Document web admin Local Agent preflight UX"
```

Skip this commit only when those links were already committed in the same branch.
