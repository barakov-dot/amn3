# Local Agent Runtime Summary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a pure, controller-safe Local Agent runtime summary mapper in AMN2 without adding API routes, public exposure, VPS commands, or write behavior.

**Architecture:** Keep the first implementation as a small service module under `app.agent`. It consumes existing `RuntimeSnapshot` and explicit health/version metadata, returns a typed summary that contains only safe runtime fields, and marks non-false `write_enabled` as unsafe for controller display.

**Tech Stack:** Python 3.12, dataclasses, existing AMN2 `app.agent.runtime` models, pytest, git worktree isolation.

---

## Current Baseline

```text
AMN3 repo: C:\Users\SooL\Documents\VPS-OPS-LAB
AMN3 branch: master
AMN2 repo: C:\Users\SooL\Documents\Amneziya
AMN2 base branch: codex-vps-test-prep
AMN2 base head: 32d01fd Update integration status for controlled prod
VPS read-only smoke: pass, run_id 20260606T185114Z
```

This plan does not mark controlled prod ready. The operator-only controlled-prod decision packet remains a separate gate.

## Scope Boundaries

Allowed in this slice:

- new pure AMN2 mapper/service;
- local unit tests;
- existing Local Agent runtime/API/policy regression tests;
- AMN2 feature branch push;
- AMN3 local evidence note after implementation.

Blocked in this slice:

- new `/api/*` routes;
- public web/API exposure;
- `config:read`;
- `/api/clients` write CRUD;
- Local Agent clients/configs/write routes;
- backup/import/reboot;
- live `apply-peer --apply` or `revoke-peer --apply`;
- `VPS_APPLY_ENABLED=true`;
- VPS commands;
- config delivery;
- publishing `.env`, `servers.yml`, raw tokens, Authorization headers, token hashes, private keys, PSK, `.conf`, QR payloads, VPN URI payloads, or full logs.

## File Structure

- Create `app/agent/runtime_summary.py`: pure typed mapper from safe Local Agent runtime inputs to a controller-safe summary.
- Create `tests/agent/test_runtime_summary.py`: RED/GREEN tests for allowed fields, forbidden omissions, aggregate counts, missing runtime data, and unsafe write flag behavior.
- Update AMN3 after AMN2 implementation:
  - Create `research/amn2/local-agent-runtime-summary-implementation-2026-06-06.md`.
  - Modify `docs/PROJECT_STATUS_CURRENT.ru.md` only at the top override block.
  - Modify `research/amn2/transfer-backlog.md` only if there is an existing matching Local Agent runtime summary backlog item.

No AMN2 API, web, CLI, packaging, or VPS smoke scripts are changed in this slice.

## Task 1: Prepare Isolated AMN2 Worktree

**Files:**

- No file changes.
- Worktree path: `C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-local-agent-runtime-summary`
- Branch: `codex/local-agent-runtime-summary`

- [ ] **Step 1: Verify AMN2 base checkout is clean**

Run from `C:\Users\SooL\Documents\Amneziya`:

```powershell
git status --short --branch
git log -1 --oneline --decorate
```

Expected:

```text
## codex-vps-test-prep...amn2/codex-vps-test-prep
32d01fd ... Update integration status for controlled prod
```

- [ ] **Step 2: Create the feature worktree**

Run from `C:\Users\SooL\Documents\Amneziya`:

```powershell
git worktree add C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-local-agent-runtime-summary -b codex/local-agent-runtime-summary codex-vps-test-prep
```

Expected:

```text
Preparing worktree (new branch 'codex/local-agent-runtime-summary')
HEAD is now at 32d01fd Update integration status for controlled prod
```

- [ ] **Step 3: Verify the worktree branch**

Run from `C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-local-agent-runtime-summary`:

```powershell
git status --short --branch
git log -1 --oneline --decorate
```

Expected:

```text
## codex/local-agent-runtime-summary
32d01fd ... Update integration status for controlled prod
```

## Task 2: RED Tests for Controller-Safe Summary

**Files:**

- Create: `tests/agent/test_runtime_summary.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/agent/test_runtime_summary.py` with:

```python
from dataclasses import asdict

from app.agent.runtime import ProtocolSnapshot, RuntimeSnapshot
from app.agent.runtime_summary import build_runtime_summary


def test_runtime_summary_keeps_only_controller_safe_fields():
    snapshot = RuntimeSnapshot(
        server_name="customer-vps-name",
        runtime_type="docker",
        status="running",
        protocols=(
            ProtocolSnapshot(
                name="amneziawg",
                status="running",
                runtime_type="docker",
                capabilities=("detect", "status"),
                container_name="amnezia-awg2",
                interface="awg0",
                client_count=4,
            ),
        ),
    )

    summary = build_runtime_summary(
        agent_status="ok",
        agent_version="test-build",
        runtime_contract_version=1,
        write_enabled=False,
        runtime=snapshot,
    )

    assert asdict(summary) == {
        "agent_status": "ok",
        "agent_version": "test-build",
        "runtime_contract_version": 1,
        "write_enabled": False,
        "controller_display_status": "safe",
        "runtime_type": "docker",
        "runtime_status": "running",
        "protocols": (
            {
                "name": "amneziawg",
                "status": "running",
                "runtime_type": "docker",
                "capabilities": ("detect", "status"),
                "client_count": 4,
            },
        ),
    }

    joined = repr(asdict(summary)).lower()
    for forbidden in (
        "customer-vps-name",
        "server_name",
        "amnezia-awg2",
        "container_name",
        "awg0",
        "interface",
        "config_path",
        "stdout",
        "stderr",
        "privatekey",
        "private_key",
        "preshared",
        "psk",
        "vpn://",
        "endpoint",
        "latest_handshake",
        "traffic",
        "client_name",
        "configs",
    ):
        assert forbidden not in joined


def test_runtime_summary_marks_non_false_write_enabled_as_unsafe():
    summary = build_runtime_summary(
        agent_status="ok",
        agent_version="test-build",
        runtime_contract_version=1,
        write_enabled=True,
        runtime=RuntimeSnapshot(
            server_name="demo",
            runtime_type="docker",
            status="running",
            protocols=(),
        ),
    )

    assert summary.agent_status == "ok"
    assert summary.write_enabled is True
    assert summary.controller_display_status == "unsafe"
    assert summary.runtime_type == "docker"
    assert summary.runtime_status == "running"
    assert summary.protocols == ()


def test_runtime_summary_handles_missing_runtime_as_unknown():
    summary = build_runtime_summary(
        agent_status="unknown",
        agent_version=None,
        runtime_contract_version=None,
        write_enabled=None,
        runtime=None,
    )

    assert asdict(summary) == {
        "agent_status": "unknown",
        "agent_version": None,
        "runtime_contract_version": None,
        "write_enabled": None,
        "controller_display_status": "unsafe",
        "runtime_type": "unknown",
        "runtime_status": "unknown",
        "protocols": (),
    }
```

- [ ] **Step 2: Run tests to verify RED**

Run from the AMN2 feature worktree:

```powershell
python -m pytest tests/agent/test_runtime_summary.py -q
```

Expected:

```text
ModuleNotFoundError: No module named 'app.agent.runtime_summary'
```

## Task 3: GREEN Minimal Runtime Summary Mapper

**Files:**

- Create: `app/agent/runtime_summary.py`
- Test: `tests/agent/test_runtime_summary.py`

- [ ] **Step 1: Implement the minimal mapper**

Create `app/agent/runtime_summary.py` with:

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.agent.runtime import ProtocolStatus, RuntimeSnapshot, RuntimeStatus


ControllerDisplayStatus = Literal["safe", "unsafe"]


@dataclass(frozen=True)
class ProtocolRuntimeSummary:
    name: str
    status: ProtocolStatus
    runtime_type: str
    capabilities: tuple[str, ...]
    client_count: int | None


@dataclass(frozen=True)
class LocalAgentRuntimeSummary:
    agent_status: str
    agent_version: str | None
    runtime_contract_version: int | None
    write_enabled: bool | None
    controller_display_status: ControllerDisplayStatus
    runtime_type: str
    runtime_status: RuntimeStatus
    protocols: tuple[ProtocolRuntimeSummary, ...]


def build_runtime_summary(
    *,
    agent_status: str,
    agent_version: str | None,
    runtime_contract_version: int | None,
    write_enabled: bool | None,
    runtime: RuntimeSnapshot | None,
) -> LocalAgentRuntimeSummary:
    return LocalAgentRuntimeSummary(
        agent_status=agent_status,
        agent_version=agent_version,
        runtime_contract_version=runtime_contract_version,
        write_enabled=write_enabled,
        controller_display_status="safe" if write_enabled is False else "unsafe",
        runtime_type=runtime.runtime_type if runtime is not None else "unknown",
        runtime_status=runtime.status if runtime is not None else "unknown",
        protocols=_protocol_summaries(runtime),
    )


def _protocol_summaries(
    runtime: RuntimeSnapshot | None,
) -> tuple[ProtocolRuntimeSummary, ...]:
    if runtime is None:
        return ()

    return tuple(
        ProtocolRuntimeSummary(
            name=protocol.name,
            status=protocol.status,
            runtime_type=protocol.runtime_type,
            capabilities=tuple(protocol.capabilities),
            client_count=protocol.client_count,
        )
        for protocol in runtime.protocols
    )
```

- [ ] **Step 2: Run focused tests to verify GREEN**

Run:

```powershell
python -m pytest tests/agent/test_runtime_summary.py -q
```

Expected:

```text
3 passed
```

- [ ] **Step 3: Run adjacent Local Agent regression tests**

Run:

```powershell
python -m pytest tests/agent/test_runtime_summary.py tests/agent/test_runtime.py tests/agent/test_api.py tests/agent/test_policy.py tests/security/test_surface_policy_bindings.py -q
```

Expected:

```text
all selected tests pass
```

## Task 4: Local Evidence and Hygiene

**Files:**

- Create: `research/amn2/local-agent-runtime-summary-implementation-2026-06-06.md` in AMN3.
- Modify: `docs/PROJECT_STATUS_CURRENT.ru.md` in AMN3.
- Modify, only if an existing matching item is present: `research/amn2/transfer-backlog.md` in AMN3.

- [ ] **Step 1: Run code hygiene in the AMN2 worktree**

Run:

```powershell
git diff --check
rg -n "ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{20,}|Authorization: Bearer [A-Za-z0-9._-]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|vpn://[A-Za-z0-9:/?&=._%-]{20,}" app/agent/runtime_summary.py tests/agent/test_runtime_summary.py
```

Expected:

```text
git diff --check exits 0
rg exits 1 with no matches
```

- [ ] **Step 2: Commit AMN2 feature branch**

Run from the AMN2 worktree:

```powershell
git status --short --branch
git add app/agent/runtime_summary.py tests/agent/test_runtime_summary.py
git commit -m "Add Local Agent runtime summary mapper"
git status --short --branch
```

Expected:

```text
commit created
working tree clean on codex/local-agent-runtime-summary
```

- [ ] **Step 3: Push AMN2 feature branch**

Run:

```powershell
git push -u amn2 codex/local-agent-runtime-summary
```

Expected:

```text
new branch pushed to amn2/codex/local-agent-runtime-summary
```

- [ ] **Step 4: Record AMN3 evidence**

Create `research/amn2/local-agent-runtime-summary-implementation-2026-06-06.md` with:

````markdown
# Local Agent Runtime Summary Implementation Evidence

Date: 2026-06-06.

Status: local-only feature branch.

AMN2 branch:

```text
codex/local-agent-runtime-summary
```

Scope:

```text
pure mapper/service only
no API route
no web route
no CLI command
no package change
no VPS commands
no live write operation
```

Verification:

```text
python -m pytest tests/agent/test_runtime_summary.py -q
python -m pytest tests/agent/test_runtime_summary.py tests/agent/test_runtime.py tests/agent/test_api.py tests/agent/test_policy.py tests/security/test_surface_policy_bindings.py -q
git diff --check
secret marker scan on changed AMN2 files
```

Result:

```text
Record the observed AMN2 commit from `git log -1 --oneline --decorate`.
Record the focused pytest summary line from `python -m pytest tests/agent/test_runtime_summary.py -q`.
Record the adjacent pytest summary line from the selected regression command.
Record `git diff --check` exit 0 and secret marker scan exit 1 with no matches.
```

Safety boundary:

```text
No public web/API exposure.
No config:read.
No clients/configs/write Local Agent routes.
No backup/import/reboot.
No VPS_APPLY_ENABLED=true.
No apply-peer --apply or revoke-peer --apply.
No .env, servers.yml, raw tokens, Authorization headers, token hashes, private keys, PSK, .conf, QR, vpn:// payloads, or full logs.
```
````

Then update the top override block in `docs/PROJECT_STATUS_CURRENT.ru.md` to mention the local-only feature branch and evidence path.

- [ ] **Step 5: Commit and push AMN3 evidence**

Run from AMN3:

```powershell
git status --short --branch
git add research/amn2/local-agent-runtime-summary-implementation-2026-06-06.md docs/PROJECT_STATUS_CURRENT.ru.md
git commit -m "Record Local Agent runtime summary branch"
git push origin master
```

Expected:

```text
AMN3 master pushed with local-only evidence
```

## Final Verification

Before reporting completion, run:

```powershell
git status --short --branch
git log -1 --oneline --decorate
```

from:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB
C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-local-agent-runtime-summary
C:\Users\SooL\Documents\Amneziya
```

Report:

- AMN2 feature branch commit;
- AMN2 focused/adjacent test counts;
- AMN3 evidence commit;
- unchanged stable AMN2 checkout state;
- remaining controlled-prod operator packet gate.
