# Local Agent Write API Slice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the first safe Local Agent write API slice for managing AmneziaWG peers after read-only VPS smoke passes.

**Architecture:** Keep read-only Local Agent as the production baseline. Add write operations behind explicit route policy, explicit scopes, dry-run/preflight, audit events, and redaction. The first write slice must operate on peers/devices only; it must not expose backup, restore, reboot, raw config, QR, `vpn://`, private keys, or a public root API.

**Tech Stack:** Python 3.12, FastAPI, existing `app.agent` modules, existing `app.server.peer_apply` logic, pytest, SQLite-backed controller app remains outside the Local Agent process.

---

## Stop Gates Before Implementation

- [ ] VPS smoke from `docs/AMN3_LOCAL_AGENT_VPS_SMOKE_CHECKLIST.ru.md` has passed.
- [ ] `amneziya-agent` listens only on `127.0.0.1:3031`.
- [ ] Web admin shows Local Agent status without raw token leakage.
- [ ] Rollback command `sudo systemctl disable --now amneziya-agent` has been checked.
- [ ] `git status --short --branch` is clean before starting the write slice.

Do not implement write routes before these gates are true.

## Execution Split

### Local-Only Work Before VPS Smoke

Можно делать локально до VPS:

- keep `docs/AMN3_LOCAL_AGENT_VPS_SMOKE_CHECKLIST.ru.md` and handoff docs current;
- configure Git remotes and publish/deliver the branch when credentials are ready;
- review `kyoresuas/amnezia-api` ideas and record product/API candidates without copying code;
- refine route policy names, scopes, request/response schemas, and audit requirements in docs;
- add non-invasive tests that prove write routes are still unavailable by default;
- prepare fake adapters and dry-run contracts without enabling production mutations;
- improve runbooks, rollback notes, redaction checks, and smoke result templates.

Выполнено локально:

- `app/agent/write_contracts.py` defines future write API request/result contracts without registering FastAPI routes;
- `tests/agent/test_write_contracts.py` verifies validation, `allowed_ips` normalization, and PSK redaction;
- `tests/agent/test_policy.py` verifies `/agent/clients*` write routes remain inactive before VPS smoke.

Нельзя делать до VPS smoke:

- не включать write routes;
- не добавлять real peer apply/revoke endpoints to the running Local Agent;
- не менять `.env.example` так, чтобы write mode был enabled by default;
- не добавлять public bind for Local Agent;
- не выполнять real user/device/peer mutations through Local Agent.

### VPS-Gated Work After Read-Only Smoke

Только после реального VPS smoke:

- promote the first selected write policies into the active write slice;
- implement Local Agent peer mutation endpoints behind `LOCAL_AGENT_WRITE_ENABLED=true`;
- enable `agent:clients:write` only for a dedicated token/scope set;
- connect web admin mutation buttons to Local Agent dry-run and confirmation flow;
- run rollback and secret-leak checks on real VPS logs after the first mutation test.

## File Structure

- Modify `app/agent/policy.py`: promote only selected `/agent/clients` write policies into the active slice when write mode is enabled.
- Modify `app/agent/api.py`: add guarded endpoints for dry-run and apply/revoke peer operations.
- Create `app/agent/peer_commands.py`: Local Agent side adapter that performs peer apply/revoke using local runtime commands, not SSH.
- Detailed adapter plan: `docs/superpowers/plans/2026-06-01-local-agent-peer-command-adapter.ru.md`.
- Modify `app/agent/config.py`: add write enablement setting if the existing agent settings do not already expose it.
- Modify `app/agent/client.py`: add controller client methods for the selected write operations.
- Modify `app/web/server_health.py` or a new `app/web/local_agent_actions.py`: controller-side wrapper for calling Local Agent write operations.
- Modify web templates only after API/client tests pass.
- Test `tests/agent/test_policy.py`, `tests/agent/test_api.py`, `tests/agent/test_client.py`, and focused web tests.
- Update `docs/LOCAL_AGENT.ru.md`, `docs/AMN3_NEXT_CHAT_HANDOFF.ru.md`, and production checklist after behavior is green.

## Task 1: Write Mode Policy Gate

**Files:**
- Modify: `app/agent/policy.py`
- Test: `tests/agent/test_policy.py`

- [ ] **Step 1: Write failing tests**

Add tests that prove write routes stay blocked by default and can be selected only by an explicit write-slice helper:

```python
def test_write_policies_are_not_first_slice_by_default():
    with pytest.raises(AgentPolicyError, match="No agent route policy"):
        get_policy("POST", "/agent/clients")


def test_write_slice_policies_expose_only_client_peer_mutations():
    policies = write_slice_policies()

    assert {
        (policy.method, policy.path, policy.scope, policy.risk_class)
        for policy in policies
    } == {
        ("POST", "/agent/clients/dry-run", "agent:clients:write", "state-write"),
        ("POST", "/agent/clients", "agent:clients:write", "state-write"),
        ("DELETE", "/agent/clients/{id}", "agent:clients:write", "state-write"),
    }
    assert all(policy.audit_required is True for policy in policies)
```

- [ ] **Step 2: Run test to verify RED**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_policy.py::test_write_slice_policies_expose_only_client_peer_mutations -v
```

Expected: fail because `write_slice_policies` does not exist or the route set differs.

- [ ] **Step 3: Implement minimal policy helper**

Add `write_slice_policies()` and future policy entries for dry-run. Keep `get_policy()` read-only unless an endpoint explicitly chooses the write helper.

- [ ] **Step 4: Run policy tests**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_policy.py -v
```

Expected: pass.

- [ ] **Step 5: Commit**

```powershell
git add app/agent/policy.py tests/agent/test_policy.py
git commit -m "Gate Local Agent write policies"
```

## Task 2: Local Peer Command Adapter

**Files:**
- Create: `app/agent/peer_commands.py`
- Test: `tests/agent/test_peer_commands.py`

Detailed plan for this task: `docs/superpowers/plans/2026-06-01-local-agent-peer-command-adapter.ru.md`.

- [ ] **Step 1: Write failing tests**

Cover dry-run, host runtime commands, Docker runtime commands, redaction, and refusal without explicit write enablement.

Required test names:

```python
def test_peer_apply_dry_run_returns_redacted_plan_for_host_systemd():
    ...


def test_peer_apply_dry_run_returns_redacted_plan_for_docker():
    ...


def test_peer_apply_refuses_when_write_mode_disabled():
    ...


def test_peer_revoke_refuses_blank_public_key():
    ...
```

- [ ] **Step 2: Run test to verify RED**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_peer_commands.py -v
```

Expected: fail because module does not exist.

- [ ] **Step 3: Implement minimal adapter**

Implement a small class with:

```python
class LocalPeerCommandAdapter:
    def __init__(self, *, runtime_adapter: LocalRuntimeAdapter, write_enabled: bool):
        ...

    def apply_dry_run(self, request: AgentPeerApplyRequest) -> AgentPeerMutationResult:
        ...

    def apply_peer(self, request: AgentPeerApplyRequest) -> AgentPeerMutationResult:
        ...

    def revoke_peer(self, request: AgentPeerRevokeRequest) -> AgentPeerMutationResult:
        ...
```

Use local commands only. Do not use SSH from inside Local Agent. Do not persist raw private key, raw PSK, QR, `vpn://`, or full config in responses.

- [ ] **Step 4: Run peer command tests**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_peer_commands.py -v
```

Expected: pass.

- [ ] **Step 5: Commit**

```powershell
git add app/agent/peer_commands.py tests/agent/test_peer_commands.py
git commit -m "Add Local Agent peer command adapter"
```

## Task 3: Write API Endpoints Behind Config

**Files:**
- Modify: `app/agent/api.py`
- Modify: `app/agent/config.py`
- Test: `tests/agent/test_api.py`

- [ ] **Step 1: Write failing tests**

Add tests for:

```python
def test_agent_write_routes_return_404_when_write_mode_disabled():
    ...


def test_agent_peer_apply_dry_run_requires_write_scope():
    ...


def test_agent_peer_apply_records_audit_event_without_secret_payload():
    ...


def test_agent_peer_apply_response_does_not_contain_private_key_psk_qr_or_vpn_link():
    ...
```

- [ ] **Step 2: Run test to verify RED**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_api.py -v
```

Expected: the new write tests fail because routes/config do not exist.

- [ ] **Step 3: Implement routes**

Add routes only when `write_enabled=True` is passed to `create_agent_app()`:

```text
POST /agent/clients/dry-run
POST /agent/clients
DELETE /agent/clients/{id}
```

Return `404` when write mode is disabled. Require `agent:clients:write`. Audit allowed and failed write attempts. Response body must contain operation status and redacted command summary only.

- [ ] **Step 4: Run API tests**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_api.py -v
```

Expected: pass.

- [ ] **Step 5: Commit**

```powershell
git add app/agent/api.py app/agent/config.py tests/agent/test_api.py
git commit -m "Add guarded Local Agent write endpoints"
```

## Task 4: Controller Client Methods

**Files:**
- Modify: `app/agent/client.py`
- Test: `tests/agent/test_client.py`

- [ ] **Step 1: Write failing tests**

Add tests for:

```python
def test_local_agent_client_sends_peer_apply_dry_run_without_secret_leakage():
    ...


def test_local_agent_client_sends_peer_apply_request_with_bearer_token():
    ...


def test_local_agent_client_redacts_token_from_write_errors():
    ...
```

- [ ] **Step 2: Run test to verify RED**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_client.py -v
```

Expected: fail because client write methods do not exist.

- [ ] **Step 3: Implement client methods**

Add methods:

```python
def peer_apply_dry_run(self, request: AgentPeerApplyRequest) -> AgentPeerMutationResult:
    ...

def apply_peer(self, request: AgentPeerApplyRequest) -> AgentPeerMutationResult:
    ...

def revoke_peer(self, client_id: str) -> AgentPeerMutationResult:
    ...
```

Keep `__repr__` redacted. Do not include bearer token in exceptions.

- [ ] **Step 4: Run client tests**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_client.py -v
```

Expected: pass.

- [ ] **Step 5: Commit**

```powershell
git add app/agent/client.py tests/agent/test_client.py
git commit -m "Add Local Agent write client methods"
```

## Task 5: Web Admin Preflight Only

**Files:**
- Create or modify: `app/web/local_agent_actions.py`
- Modify: `app/web/app.py`
- Modify: relevant server/user templates
- Test: focused tests in `tests/web/test_servers.py` or `tests/web/test_users.py`

- [ ] **Step 1: Write failing tests**

The first web integration must expose dry-run/preflight before mutation:

```python
def test_server_missing_device_local_agent_preflight_shows_redacted_plan():
    ...


def test_server_missing_device_local_agent_apply_requires_confirmation_after_preflight():
    ...
```

- [ ] **Step 2: Run test to verify RED**

Run the selected web tests with `-v`.

- [ ] **Step 3: Implement preflight UI**

Add a preflight button that calls Local Agent dry-run and renders the redacted command plan. Mutation button should be shown only after a successful preflight in the same admin flow.

- [ ] **Step 4: Run web tests**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/web/test_servers.py tests/web/test_users.py -v
```

Expected: pass.

- [ ] **Step 5: Commit**

```powershell
git add app/web app/agent tests/web
git commit -m "Add Local Agent write preflight to web admin"
```

## Task 6: Documentation And Final Verification

**Files:**
- Modify: `docs/LOCAL_AGENT.ru.md`
- Modify: `docs/AMN3_NEXT_CHAT_HANDOFF.ru.md`
- Modify: `docs/PRODUCTION_VPS_CHECKLIST.ru.md`
- Test: `tests/deploy/test_runtime_registry.py`, `tests/test_file_hygiene.py`

- [ ] **Step 1: Add docs tests**

Add checks that docs mention:

```text
LOCAL_AGENT_WRITE_ENABLED=false
agent:clients:write
dry-run before mutation
rollback
no public root API
```

- [ ] **Step 2: Run docs tests to verify RED**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/deploy/test_runtime_registry.py tests/test_file_hygiene.py -v
```

- [ ] **Step 3: Update docs**

Document enabled/disabled behavior, scopes, audit requirements, and rollback.

- [ ] **Step 4: Full focused verification**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent tests/web/test_servers.py tests/web/test_users.py tests/deploy/test_runtime_registry.py tests/test_file_hygiene.py -v
git diff --check
git status --short --branch
```

Expected: all selected tests pass and whitespace check is clean.

- [ ] **Step 5: Commit**

```powershell
git add app tests docs .env.example deploy/examples/.env.production.example
git commit -m "Document Local Agent write API gates"
```

## Out Of Scope For This Slice

- Public internet exposure of Local Agent.
- Backup/restore/reboot routes.
- Returning full client config, QR, `vpn://`, private key, or PSK from Local Agent.
- Bulk user import/export.
- Payment automation.
- Multi-server scheduler/failover.
