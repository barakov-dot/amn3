# Local Agent Peer Command Adapter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Local Agent runtime adapter for safe AmneziaWG peer dry-run/apply/revoke after VPS `GO-1`.

**Architecture:** The adapter lives in `app/agent/peer_commands.py` and uses local commands only, with no SSH from inside Local Agent. It converts `AgentPeerApplyRequest` and `AgentPeerRevokeRequest` into `app/server/peer_apply.py` operations through a local runtime runner, returns redacted `AgentPeerMutationResult` payloads, and provides audit handoff data such as `rollback_reference` and `peer_public_key_fingerprint`. The slice remains behind `LOCAL_AGENT_WRITE_ENABLED=true` and does not register FastAPI write routes by itself.

**Tech Stack:** Python 3.12, dataclasses, subprocess-compatible local command runner, existing `app.agent.write_contracts`, existing `app.server.peer_apply`, pytest.

---

## Scope And Gates

Execute this plan only after `GO-1` in `docs/AMN3_POST_VPS_IMPLEMENTATION_MAP.ru.md`.

Before that gate:

- `LOCAL_AGENT_WRITE_ENABLED=false`;
- no write routes;
- no peer mutation from Local Agent;
- no write token in public examples;
- no raw token, private key, PSK, QR, `vpn://`, or full client config in logs, docs, responses, bot messages, screenshots, or issue comments.

After the gate:

```text
LOCAL_AGENT_WRITE_ENABLED=true
dry-run before mutation
confirmation nonce before apply/revoke
audit before and after mutation
rollback_reference required for mutation audit
```

This adapter is not the route layer. `app/agent/api.py` must still enforce auth scope, feature flag, dry-run freshness, confirmation nonce, and audit storage before it calls mutation methods.

Endpoint wiring plan for that route layer: `docs/superpowers/plans/2026-06-01-local-agent-write-endpoints-implementation.ru.md`.

## File Structure

- Create `app/agent/peer_commands.py`: Local Agent command adapter, runtime runner protocol, redacted result assembly, and command failure mapping.
- Create `tests/agent/test_peer_commands.py`: fake local runtime tests for dry-run, apply, revoke, redaction, host_systemd, docker, and disabled write mode.
- Use `app/agent/write_contracts.py`: `AgentPeerApplyRequest`, `AgentPeerRevokeRequest`, `AgentPeerMutationResult`.
- Use `app/agent/write_confirmation.py`: endpoint layer passes a fresh dry-run reference and confirmation nonce before mutation.
- Use `app/agent/write_audit.py`: endpoint layer writes audit records using adapter audit context.
- Use `app/server/peer_apply.py`: `PeerApplyInput`, `build_peer_apply_dry_run`, `build_peer_revoke_dry_run`, `apply_peer`, `revoke_peer`.
- Keep `app/agent/api.py` unchanged during this adapter slice unless this plan is executed as part of the endpoint slice.

## Runtime Contract

The adapter must support both AMN3 runtime modes:

- `host_systemd`: run `awg set ...` and `systemctl reload ...` locally.
- `docker`: read the persistent AmneziaWG config, rewrite the peer block, and restart the container locally.

Hard boundaries:

- local commands only;
- no SSH from inside Local Agent;
- no `SystemSshClient` import in `app/agent/peer_commands.py`;
- no raw PSK in planned commands, logs, or response payloads;
- no private key, QR, `vpn://`, or full client config in response payloads;
- mutation methods refuse when `write_enabled=False`;
- mutation methods require an explicit confirmed preflight from the API layer.

Identity fields that must remain visible only in safe form:

```text
user_id
device_id
client_id
server_alias
protocol=amneziawg
peer_public_key_fingerprint
```

## Task 1: Peer Command Tests

**Files:**
- Create: `tests/agent/test_peer_commands.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/agent/test_peer_commands.py` with:

```python
import pytest

from app.agent.peer_commands import (
    LocalPeerCommandAdapter,
    LocalRuntimeResult,
    PeerCommandError,
)
from app.agent.write_contracts import AgentPeerApplyRequest, AgentPeerRevokeRequest
from app.server.ssh import CommandResult
from app.server_config.loader import load_server_config, select_server
from tests.server_config.test_loader import DOCKER_YAML, VALID_YAML


def test_peer_apply_dry_run_returns_redacted_plan_for_host_systemd(tmp_path):
    adapter = LocalPeerCommandAdapter(
        server=_server(tmp_path),
        runtime=RecordingLocalRuntime(),
        write_enabled=False,
    )

    result = adapter.apply_dry_run(_apply_request())
    payload = result.redacted_payload()

    assert payload["status"] == "planned"
    assert payload["dry_run"] is True
    assert payload["consistency_status"] == "dry-run"
    assert "awg set awg0 peer peer-public" in "\n".join(payload["planned_commands"])
    assert "systemctl reload awg-quick@awg0" in "\n".join(payload["planned_commands"])
    assert "secret-psk" not in repr(result)
    assert "No changes will be made" in payload["message"]


def test_peer_apply_dry_run_returns_redacted_plan_for_docker(tmp_path):
    adapter = LocalPeerCommandAdapter(
        server=_docker_server(tmp_path),
        runtime=RecordingLocalRuntime(),
        write_enabled=False,
    )

    result = adapter.apply_dry_run(_apply_request())
    payload = result.redacted_payload()

    commands = "\n".join(payload["planned_commands"])
    assert "docker exec amnezia-awg cat /opt/amnezia/awg/awg0.conf" in commands
    assert "docker exec -i amnezia-awg sh -c" in commands
    assert "docker restart amnezia-awg" in commands
    assert "secret-psk" not in repr(result)


def test_peer_apply_refuses_when_write_mode_disabled(tmp_path):
    adapter = LocalPeerCommandAdapter(
        server=_server(tmp_path),
        runtime=RecordingLocalRuntime(),
        write_enabled=False,
    )

    with pytest.raises(PeerCommandError, match="LOCAL_AGENT_WRITE_ENABLED"):
        adapter.apply_peer(_apply_request(), preflight_confirmed=True)


def test_peer_apply_refuses_without_confirmed_preflight(tmp_path):
    adapter = LocalPeerCommandAdapter(
        server=_server(tmp_path),
        runtime=RecordingLocalRuntime(),
        write_enabled=True,
    )

    with pytest.raises(PeerCommandError, match="dry-run before mutation"):
        adapter.apply_peer(_apply_request(), preflight_confirmed=False)


def test_peer_apply_uses_local_runtime_adapter_without_ssh_and_redacts_psk(tmp_path):
    runtime = RecordingLocalRuntime()
    adapter = LocalPeerCommandAdapter(
        server=_server(tmp_path),
        runtime=runtime,
        write_enabled=True,
    )

    result = adapter.apply_peer(_apply_request(), preflight_confirmed=True)
    payload = result.redacted_payload()

    assert payload["status"] == "applied"
    assert payload["dry_run"] is False
    assert payload["consistency_status"] == "mutated"
    assert len(runtime.calls) == 1
    command, stdin = runtime.calls[0]
    assert "ssh " not in command
    assert "awg set awg0 peer peer-public" in command
    assert stdin == "secret-psk\n"
    assert "secret-psk" not in repr(result)


def test_peer_revoke_runs_local_runtime_and_includes_safe_rollback_context(tmp_path):
    runtime = RecordingLocalRuntime()
    adapter = LocalPeerCommandAdapter(
        server=_server(tmp_path),
        runtime=runtime,
        write_enabled=True,
    )

    receipt = adapter.revoke_peer(
        AgentPeerRevokeRequest(client_id="client-1", peer_public_key="peer-public"),
        preflight_confirmed=True,
    )

    payload = receipt.result.redacted_payload()
    assert payload["status"] == "revoked"
    assert receipt.rollback_reference.startswith("rollback:")
    assert receipt.peer_public_key_fingerprint.startswith("sha256:")
    assert len(runtime.calls) == 1
    assert "awg set awg0 peer peer-public remove" in runtime.calls[0][0]


def test_peer_revoke_refuses_blank_public_key(tmp_path):
    adapter = LocalPeerCommandAdapter(
        server=_server(tmp_path),
        runtime=RecordingLocalRuntime(),
        write_enabled=True,
    )

    with pytest.raises(ValueError, match="peer_public_key"):
        adapter.revoke_peer(
            AgentPeerRevokeRequest(client_id="client-1", peer_public_key=" "),
            preflight_confirmed=True,
        )


def _apply_request() -> AgentPeerApplyRequest:
    return AgentPeerApplyRequest(
        client_id="client-1",
        peer_public_key="peer-public",
        preshared_key="secret-psk",
        vpn_ip="10.8.0.2",
        protocol="amneziawg",
    )


def _server(tmp_path):
    path = tmp_path / "servers.yml"
    path.write_text(VALID_YAML, encoding="utf-8")
    return select_server(load_server_config(path), "debian-vps-1")


def _docker_server(tmp_path):
    path = tmp_path / "servers.yml"
    path.write_text(DOCKER_YAML, encoding="utf-8")
    return select_server(load_server_config(path), "debian-vps-1")


class RecordingLocalRuntime:
    def __init__(self, results=None):
        self.calls = []
        self._results = list(results or [])

    def run(self, command: str, stdin: str | None = None) -> LocalRuntimeResult:
        self.calls.append((command, stdin))
        if self._results:
            return self._results.pop(0)
        return LocalRuntimeResult(exit_code=0, stdout="ok", stderr="")
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_peer_commands.py -v
```

Expected: fail because `app.agent.peer_commands` does not exist.

## Task 2: Adapter Skeleton And Dry-Run

**Files:**
- Create: `app/agent/peer_commands.py`
- Test: `tests/agent/test_peer_commands.py`

- [ ] **Step 1: Implement local runtime types and dry-run methods**

Create `app/agent/peer_commands.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import subprocess
from typing import Protocol

from app.agent.write_contracts import (
    AgentPeerApplyRequest,
    AgentPeerMutationResult,
    AgentPeerRevokeRequest,
)
from app.security.redaction import redact
from app.server.peer_apply import (
    PeerApplyError,
    PeerApplyInput,
    apply_peer as apply_peer_to_runtime,
    build_peer_apply_dry_run,
    build_peer_revoke_dry_run,
    revoke_peer as revoke_peer_from_runtime,
)
from app.server.ssh import CommandResult
from app.server_config.models import ServerConfig


class PeerCommandError(RuntimeError):
    pass


@dataclass(frozen=True)
class LocalRuntimeResult:
    exit_code: int
    stdout: str
    stderr: str


class LocalRuntimeAdapter(Protocol):
    def run(self, command: str, stdin: str | None = None) -> LocalRuntimeResult:
        pass


class SystemLocalRuntimeAdapter:
    def __init__(self, *, timeout_seconds: int = 20) -> None:
        self._timeout_seconds = timeout_seconds

    def run(self, command: str, stdin: str | None = None) -> LocalRuntimeResult:
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                check=False,
                input=stdin,
                shell=True,
                text=True,
                timeout=self._timeout_seconds,
            )
        except subprocess.TimeoutExpired:
            return LocalRuntimeResult(
                exit_code=124,
                stdout="",
                stderr=f"local command timed out after {self._timeout_seconds} seconds",
            )
        return LocalRuntimeResult(
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )


@dataclass(frozen=True)
class PeerCommandReceipt:
    result: AgentPeerMutationResult
    rollback_reference: str
    peer_public_key_fingerprint: str


class LocalPeerCommandAdapter:
    def __init__(
        self,
        *,
        server: ServerConfig,
        runtime: LocalRuntimeAdapter,
        write_enabled: bool,
    ) -> None:
        self._server = server
        self._runtime = runtime
        self._write_enabled = write_enabled

    def apply_dry_run(self, request: AgentPeerApplyRequest) -> AgentPeerMutationResult:
        peer = _peer_apply_input(request)
        report = _localize_report(build_peer_apply_dry_run(self._server, peer))
        return AgentPeerMutationResult(
            operation_id="local_agent.clients.apply.dry_run",
            status="planned",
            dry_run=True,
            message=report,
            planned_commands=_planned_commands(report),
            secret_values=(request.preshared_key,),
        )

    def revoke_dry_run(self, request: AgentPeerRevokeRequest) -> AgentPeerMutationResult:
        report = _localize_report(
            build_peer_revoke_dry_run(self._server, request.peer_public_key)
        )
        return AgentPeerMutationResult(
            operation_id="local_agent.clients.revoke.dry_run",
            status="planned",
            dry_run=True,
            message=report,
            planned_commands=_planned_commands(report),
        )
```

- [ ] **Step 2: Add helper functions**

Add below the class:

```python
def _peer_apply_input(request: AgentPeerApplyRequest) -> PeerApplyInput:
    return PeerApplyInput(
        public_key=request.peer_public_key,
        preshared_key=request.preshared_key,
        vpn_ip=request.vpn_ip,
    )


def _localize_report(report: str) -> str:
    lines = []
    for line in report.splitlines():
        if line.startswith("Target: ssh "):
            lines.append("Target: local runtime")
        else:
            lines.append(line)
    return "\n".join(lines)


def _planned_commands(report: str) -> tuple[str, ...]:
    commands = []
    for line in report.splitlines():
        if line.startswith("- "):
            commands.append(line[2:])
    return tuple(commands)


def _fingerprint(value: str) -> str:
    return "sha256:" + sha256(value.encode("utf-8")).hexdigest()[:16]
```

- [ ] **Step 3: Run dry-run tests to verify GREEN for dry-run**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_peer_commands.py::test_peer_apply_dry_run_returns_redacted_plan_for_host_systemd tests/agent/test_peer_commands.py::test_peer_apply_dry_run_returns_redacted_plan_for_docker -v
```

Expected: pass for dry-run tests; mutation tests still fail until Task 3.

## Task 3: Apply/Revoke Mutation Methods

**Files:**
- Modify: `app/agent/peer_commands.py`
- Test: `tests/agent/test_peer_commands.py`

- [ ] **Step 1: Add write gate and mutation methods**

Add these methods inside `LocalPeerCommandAdapter`:

```python
    def apply_peer(
        self,
        request: AgentPeerApplyRequest,
        *,
        preflight_confirmed: bool,
    ) -> PeerCommandReceipt:
        self._require_write_enabled()
        self._require_confirmed_preflight(preflight_confirmed)
        peer = _peer_apply_input(request)
        planned = self.apply_dry_run(request)
        try:
            message = apply_peer_to_runtime(
                self._server,
                peer,
                ssh_client=_LocalRuntimeSshCompat(self._runtime),
            )
        except PeerApplyError as exc:
            raise PeerCommandError(redact(str(exc))) from exc
        result = AgentPeerMutationResult(
            operation_id="local_agent.clients.apply",
            status="applied",
            dry_run=False,
            message=message,
            planned_commands=planned.planned_commands,
            secret_values=(request.preshared_key,),
        )
        return PeerCommandReceipt(
            result=result,
            rollback_reference=_rollback_reference("apply", request.client_id),
            peer_public_key_fingerprint=_fingerprint(request.peer_public_key),
        )

    def revoke_peer(
        self,
        request: AgentPeerRevokeRequest,
        *,
        preflight_confirmed: bool,
    ) -> PeerCommandReceipt:
        self._require_write_enabled()
        self._require_confirmed_preflight(preflight_confirmed)
        planned = self.revoke_dry_run(request)
        try:
            message = revoke_peer_from_runtime(
                self._server,
                request.peer_public_key,
                ssh_client=_LocalRuntimeSshCompat(self._runtime),
            )
        except PeerApplyError as exc:
            raise PeerCommandError(redact(str(exc))) from exc
        result = AgentPeerMutationResult(
            operation_id="local_agent.clients.revoke",
            status="revoked",
            dry_run=False,
            message=message,
            planned_commands=planned.planned_commands,
        )
        return PeerCommandReceipt(
            result=result,
            rollback_reference=_rollback_reference("revoke", request.client_id),
            peer_public_key_fingerprint=_fingerprint(request.peer_public_key),
        )

    def _require_write_enabled(self) -> None:
        if not self._write_enabled:
            raise PeerCommandError(
                "LOCAL_AGENT_WRITE_ENABLED=true is required for peer mutation"
            )

    def _require_confirmed_preflight(self, preflight_confirmed: bool) -> None:
        if not preflight_confirmed:
            raise PeerCommandError("dry-run before mutation is required")
```

- [ ] **Step 2: Add local runtime compatibility wrapper**

Add below helper functions:

```python
class _LocalRuntimeSshCompat:
    def __init__(self, runtime: LocalRuntimeAdapter) -> None:
        self._runtime = runtime

    def run(self, command: str, stdin: str | None = None) -> CommandResult:
        result = self._runtime.run(command, stdin=stdin)
        return CommandResult(
            exit_code=result.exit_code,
            stdout=result.stdout,
            stderr=result.stderr,
        )


def _rollback_reference(action: str, client_id: str) -> str:
    return f"rollback:{action}:{client_id}"
```

This wrapper intentionally uses the existing `SshClient`-shaped protocol without importing or constructing `SystemSshClient`. The Local Agent process runs the command locally.

- [ ] **Step 3: Run mutation tests to verify GREEN**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_peer_commands.py -v
```

Expected: pass.

- [ ] **Step 4: Commit**

```powershell
git add app/agent/peer_commands.py tests/agent/test_peer_commands.py
git commit -m "Add Local Agent peer command adapter"
```

## Task 4: Audit Handoff And Secret Boundaries

**Files:**
- Modify: `tests/agent/test_peer_commands.py`
- Verify: `tests/agent/test_write_contracts.py`
- Verify: `tests/agent/test_write_confirmation.py`
- Verify: `tests/agent/test_write_audit.py`

- [ ] **Step 1: Add audit handoff test**

Add this test to `tests/agent/test_peer_commands.py`:

```python
def test_peer_command_receipt_provides_audit_handoff_without_secret_values(tmp_path):
    adapter = LocalPeerCommandAdapter(
        server=_server(tmp_path),
        runtime=RecordingLocalRuntime(),
        write_enabled=True,
    )

    receipt = adapter.apply_peer(_apply_request(), preflight_confirmed=True)
    payload = receipt.result.redacted_payload()

    assert receipt.rollback_reference == "rollback:apply:client-1"
    assert receipt.peer_public_key_fingerprint.startswith("sha256:")
    assert payload["operation_id"] == "local_agent.clients.apply"
    assert payload["risk_class"] == "state-write"
    assert "secret-psk" not in repr(receipt)
    assert "private key" not in repr(receipt).lower()
    assert "vpn://" not in repr(receipt)
```

- [ ] **Step 2: Run adapter and contract tests**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_peer_commands.py tests/agent/test_write_contracts.py tests/agent/test_write_confirmation.py tests/agent/test_write_audit.py -v
```

Expected: pass. This is the core command string: `pytest tests/agent/test_peer_commands.py tests/agent/test_write_contracts.py tests/agent/test_write_confirmation.py tests/agent/test_write_audit.py`.

- [ ] **Step 3: Commit**

```powershell
git add tests/agent/test_peer_commands.py app/agent/peer_commands.py
git commit -m "Add peer command audit handoff"
```

## Task 5: Endpoint Integration Readiness Check

**Files:**
- Verify: `app/agent/api.py`
- Verify: `app/agent/write_policy_matrix.py`
- Verify: `docs/AMN3_WRITE_API_UX_FLOW.ru.md`
- Verify: `docs/AMN3_WRITE_API_PREFLIGHT_CONFIRMATION.ru.md`
- Verify: `docs/AMN3_USER_DEVICE_PEER_IDENTITY_MODEL.ru.md`

- [ ] **Step 1: Confirm this slice has no route registration**

Run:

```powershell
rg -n "clients/dry-run|LocalPeerCommandAdapter|peer_commands" app/agent
```

Expected: `LocalPeerCommandAdapter` appears only in `app/agent/peer_commands.py`. `app/agent/api.py` still has no `/agent/clients*` registration until the endpoint slice.

- [ ] **Step 2: Confirm UX/preflight/identity contracts remain aligned**

Manual checklist:

- `docs/AMN3_WRITE_API_UX_FLOW.ru.md` still says `dry-run -> confirmation -> apply/revoke -> audit -> rollback`;
- `docs/AMN3_WRITE_API_PREFLIGHT_CONFIRMATION.ru.md` still requires a fresh confirmation nonce before mutation;
- `docs/AMN3_USER_DEVICE_PEER_IDENTITY_MODEL.ru.md` still treats `client_id` as controller-owned and `peer_public_key` as runtime-owned;
- `app/agent/write_policy_matrix.py` still marks `local_agent.clients.apply` and `local_agent.clients.revoke` as `confirmation_required=True`.

- [ ] **Step 3: Run local safety suite**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_peer_commands.py tests/agent/test_write_contracts.py tests/agent/test_write_confirmation.py tests/agent/test_write_audit.py tests/agent/test_write_policy_matrix.py tests/agent/test_policy.py tests/security/test_redaction.py tests/test_file_hygiene.py -v
```

Expected: pass. Write routes remain gated by policy and examples remain safe.

- [ ] **Step 4: Run whitespace check**

Run:

```powershell
git diff --check
```

Expected: no output and exit code 0.

- [ ] **Step 5: Commit docs if this plan is executed together with docs updates**

```powershell
git add docs/AMN3_NEXT_CHAT_HANDOFF.ru.md docs/AMN3_POST_VPS_IMPLEMENTATION_MAP.ru.md docs/AMN3_WRITE_API_UX_FLOW.ru.md docs/AMN3_WRITE_API_PREFLIGHT_CONFIRMATION.ru.md docs/AMN3_USER_DEVICE_PEER_IDENTITY_MODEL.ru.md docs/superpowers/plans/2026-05-31-local-agent-write-api-slice.ru.md
git commit -m "Document Local Agent peer command adapter"
```

Use this docs commit only when the related documentation links are part of the same slice.
