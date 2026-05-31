# AMN2 Remote Operations Local/VPS Split Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Разделить следующий блок remote operations work на локально проверяемую часть и отдельный controlled VPS verification gate.

**Architecture:** Сначала проектируем и тестируем state-changing remote operation contract локально: fake SSH runner, fake operation runner, DB transaction simulations, redaction, audit, rollback/resume notes и dry-run previews. Реальный VPS используется только после зеленого локального suite и только для подтверждения read-only/preflight/dry-run/small-scope apply behavior на тестовом устройстве с заранее подготовленным backup и recovery checklist.

**Tech Stack:** Python, pytest, текущие модули `app/server`, `app/services`, `app/bot`, `app/web`, `deploy/runtime`, SQLite test DB, real VPS only after local gate.

---

## File Structure

- Create or modify: `app/server/operations.py` - расширить typed operation contract для state-changing classes без немедленного live execution.
- Create or modify: `app/server/operation_runner.py` - добавить state-changing validation gates, dry-run contract и consistency status, если текущий runner не покрывает это явно.
- Modify: `app/server/peer_apply.py` - только если contract требует typed result/rollback note вокруг существующих apply/revoke функций.
- Modify: `app/services/access.py` - только для локальных transaction/failure simulations around remote success/local failure.
- Modify: `tests/server/test_operation_runner.py` - local fake-runner tests.
- Modify: `tests/server/test_peer_apply.py` - local command/result/rollback-note tests.
- Modify: `tests/services/test_access_service.py` - local DB transaction and partial-failure tests.
- Modify: `tests/bot/test_bot_workflows.py` - bot user reset/revoke partial failure simulations.
- Modify: `tests/web/test_servers.py` or `tests/web/test_users.py` - web/admin remote action audit tests, if a web surface is touched.
- Modify: `docs/RUNTIME_REGISTRY.ru.md` and `docs/RUNTIME_REGISTRY.en.md` - document local gate and VPS gate.
- Modify: `docs/VPS_RETEST_PROTOCOL.ru.md` or create a dedicated checklist if real VPS verification needs explicit operator steps.
- Modify in lab after implementation: `research/amn2/remote-operations-inventory.md`, `ideas/priority-backlog.md`.

## Phase A: Local-Only Gate

Эта фаза не требует реального VPS, не читает `.env` и не выполняет live SSH/Docker/firewall mutations.

### Task 1: State-Changing Operation Contract

**Files:**
- Modify: `app/server/operations.py`
- Modify: `tests/server/test_operation_runner.py`

- [ ] **Step 1: Write failing contract tests**

Add tests that require a state-changing operation to expose these fields before execution:

```python
def test_state_changing_operation_requires_rollback_and_consistency_metadata():
    operation = RemoteOperation(
        operation_id="server.peer.apply",
        risk_class="remote-state-write",
        consistency_status="pending-remote",
        steps=[],
        inputs={"server_id": 1, "device_id": 7},
        rollback_note="Remove the peer remotely and mark local device pending review.",
        local_side_effects=["device-create", "admin-audit"],
        remote_side_effects=["awg-peer-add", "service-reload"],
        idempotency_key="server.peer.apply:1:7",
    )

    validate_operation(operation)
```

Expected failure: current typed contract does not require or expose these exact state-changing fields.

- [ ] **Step 2: Add minimal typed fields**

Extend the operation model with explicit metadata:

```python
risk_class: Literal["read-only-remote", "read-only-remote-telemetry", "remote-state-write", "destructive-remote"]
consistency_status: Literal["read-only", "dry-run", "pending-remote", "remote-applied", "local-applied", "partial-failure", "rolled-back", "manual-review-required"]
rollback_note: str
local_side_effects: tuple[str, ...]
remote_side_effects: tuple[str, ...]
idempotency_key: str | None
```

- [ ] **Step 3: Keep read-only compatibility**

Existing read-only health tests must continue to pass without forcing state-changing-only fields into old callers. If defaults are used, they must be explicit and safe:

```python
consistency_status="read-only"
rollback_note="No remote or local state changes are performed."
local_side_effects=()
remote_side_effects=()
idempotency_key=None
```

- [ ] **Step 4: Run local contract tests**

Run:

```bash
pytest tests/server/test_operation_runner.py tests/server/test_checks.py -v
```

Expected: all tests pass locally.

- [ ] **Step 5: Commit**

```bash
git add app/server/operations.py app/server/operation_runner.py tests/server/test_operation_runner.py tests/server/test_checks.py
git diff --cached --check
git commit -m "Add state-changing operation contract metadata"
```

### Task 2: Local Partial-Failure Simulations

**Files:**
- Modify: `tests/services/test_access_service.py`
- Modify if needed: `app/services/access.py`

- [ ] **Step 1: Write failing test for remote success and local audit failure**

Add a local test with fake peer applier:

```python
def test_approve_order_records_manual_review_when_remote_apply_succeeds_but_local_audit_fails(tmp_path):
    peer_applier = RecordingPeerApplier()
    repo = FailingAuditRepository(...)

    with pytest.raises(RemoteOperationPartialFailure):
        service.approve_order(order_id=1, admin_telegram_id=9001)

    assert peer_applier.applied_peers == ["peer-public"]
    assert repo.device_status(device_id=1) in {"pending_review", "remote_applied_pending_local"}
    assert "manual review" in repo.latest_operation_note()
```

If current architecture cannot store such state yet, the test should define the minimal desired state shape before code changes.

- [ ] **Step 2: Write failing test for multi-device reset partial failure**

Simulate first remote revoke success and second remote revoke failure:

```python
def test_reset_devices_marks_partial_failure_when_one_remote_remove_succeeds_and_next_fails(tmp_path):
    remover = FailingAfterFirstRemove()

    result = workflow.reset_user_devices(user_telegram_id=1001, remover=remover)

    assert result.consistency_status == "partial-failure"
    assert result.remote_removed_device_ids == [first_device_id]
    assert result.local_unchanged_device_ids == [first_device_id, second_device_id]
    assert result.recovery_note
```

- [ ] **Step 3: Implement minimal local consistency result**

Prefer a small typed result instead of broad refactor:

```python
@dataclass(frozen=True)
class RemoteMutationResult:
    operation_id: str
    consistency_status: str
    remote_applied: bool
    local_applied: bool
    recovery_note: str
```

- [ ] **Step 4: Run local service and bot tests**

Run:

```bash
pytest tests/services/test_access_service.py tests/bot/test_bot_workflows.py -v
```

Expected: all tests pass locally using fakes only.

- [ ] **Step 5: Commit**

```bash
git add app/services/access.py tests/services/test_access_service.py tests/bot/test_bot_workflows.py
git diff --cached --check
git commit -m "Add local partial failure simulations"
```

### Task 3: Dry-Run and Audit Contract

**Files:**
- Modify: `tests/server/test_peer_apply.py`
- Modify: `tests/web/test_servers.py` or `tests/web/test_users.py` if web action metadata changes.
- Modify if needed: `app/server/peer_apply.py`, `app/web/*`.

- [ ] **Step 1: Write failing tests for dry-run metadata**

Dry-run output for state-changing operations must include:

```text
operation_id
risk_class
remote_side_effects
local_side_effects
rollback_note
consistency_status=dry-run
```

- [ ] **Step 2: Write failing tests for audit metadata**

Audit metadata must include only safe fields:

```python
assert action["metadata"]["operation_id"] == "server.peer.apply"
assert action["metadata"]["risk_class"] == "remote-state-write"
assert action["metadata"]["consistency_status"] in {"remote-applied", "partial-failure"}
assert "preshared_key" not in serialized_metadata
assert "PrivateKey" not in serialized_metadata
assert "vpn://" not in serialized_metadata
```

- [ ] **Step 3: Implement minimal metadata propagation**

Propagate operation metadata from contract to dry-run/report/audit without adding new live behavior.

- [ ] **Step 4: Run focused local tests**

```bash
pytest tests/server/test_peer_apply.py tests/web/test_servers.py tests/web/test_users.py -v
```

Expected: all tests pass locally.

- [ ] **Step 5: Commit**

```bash
git add app/server/peer_apply.py app/web tests/server/test_peer_apply.py tests/web/test_servers.py tests/web/test_users.py
git diff --cached --check
git commit -m "Add dry-run and audit metadata for remote mutations"
```

### Task 4: Local Gate Verification

**Files:**
- No new production files.

- [ ] **Step 1: Run local focused remote safety suite**

```bash
pytest tests/server/test_operation_runner.py tests/server/test_peer_apply.py tests/services/test_access_service.py tests/bot/test_bot_workflows.py tests/web/test_servers.py tests/web/test_users.py tests/security/test_redaction.py -v
```

Expected: all selected tests pass.

- [ ] **Step 2: Run full local suite**

```bash
pytest tests -v
```

Expected: all tests pass. Known external `StarletteDeprecationWarning` may remain.

- [ ] **Step 3: Update local gate docs**

Update `docs/RUNTIME_REGISTRY.ru.md`:

```markdown
### Local gate before real VPS verification

State-changing remote operations must pass local fake-runner tests, redaction tests,
dry-run/audit metadata tests, and full `pytest tests -v` before any real VPS check.
```

- [ ] **Step 4: Commit**

```bash
git add docs/RUNTIME_REGISTRY.ru.md docs/RUNTIME_REGISTRY.en.md
git diff --cached --check
git commit -m "Document local remote operations gate"
```

## Phase B: Real VPS Verification Gate

Эта фаза начинается только после Phase A. Она требует отдельного operator confirmation, чистого backup/recovery window и тестового устройства. Нельзя использовать production user device как первый live probe.

### Preconditions

- [ ] Branch pushed and PR/open review exists or explicitly accepted local branch is selected.
- [ ] Full local suite is green.
- [ ] VPS access method is confirmed without reading `.env` in lab.
- [ ] Current server config is backed up outside Git.
- [ ] Test user/device is created or selected.
- [ ] Recovery owner is present and can restore service manually if needed.

### VPS Task 1: Read-Only Baseline

Run on operator machine or deployment host:

```bash
python -m app.cli server check --config servers.yml --server debian-vps-1 --dry-run
python -m app.cli server check --config servers.yml --server debian-vps-1
bash deploy/runtime/check_vps.sh
```

Expected:

- health check succeeds or returns known non-blocking warnings;
- no state-changing command is executed in dry-run;
- logs do not expose `.conf`, QR payload, `vpn://`, private key, PSK or tokens.

### VPS Task 2: Dry-Run Remote Mutation Preview

Run:

```bash
python -m app.cli server apply-peer --config servers.yml --server debian-vps-1 --dry-run --public-key TEST_PUBLIC_KEY --preshared-key TEST_PSK --vpn-ip TEST_VPN_IP
python -m app.cli server revoke-peer --config servers.yml --server debian-vps-1 --dry-run --public-key TEST_PUBLIC_KEY
```

Expected:

- output includes operation/risk/rollback metadata;
- no live mutation happens;
- PSK is redacted;
- recovery note is readable by an operator.

### VPS Task 3: Single Test Peer Apply/Revoke

Only after dry-run preview is accepted:

```bash
python -m app.cli server apply-peer --config servers.yml --server debian-vps-1 --apply --public-key TEST_PUBLIC_KEY --preshared-key TEST_PSK --vpn-ip TEST_VPN_IP
python -m app.cli server check --config servers.yml --server debian-vps-1
python -m app.cli server revoke-peer --config servers.yml --server debian-vps-1 --apply --public-key TEST_PUBLIC_KEY
python -m app.cli server check --config servers.yml --server debian-vps-1
```

Expected:

- apply adds only the test peer;
- revoke removes only the test peer;
- no unrelated peer disappears;
- health remains acceptable after each operation;
- audit/report output contains metadata but no raw secrets.

### VPS Task 4: Diagnostic Snapshot After Test

Run:

```bash
bash deploy/runtime/collect_debug_snapshot.sh
```

Expected:

- snapshot is redacted;
- snapshot does not include `.conf`, QR payload, `vpn://`, private key, PSK or tokens;
- any warning is added to lab notes before next live test.

### VPS Task 5: Lab Result Recording

After real VPS verification, update:

- `research/amn2/remote-operations-inventory.md`
- `ideas/priority-backlog.md`
- optional dedicated VPS verification note under `watch-notes/` or `research/amn2/`

Required fields:

```text
branch:
commit:
VPS runtime:
commands run:
focused local tests:
full local tests:
live VPS result:
warnings:
rollback/recovery used:
decision:
```

## Stop Conditions

Stop before real VPS mutation if any of these happens:

- local focused suite fails;
- full local suite fails;
- dry-run output exposes a secret;
- dry-run output does not explain rollback/recovery;
- VPS read-only health is red for unknown reasons;
- backup/recovery owner is unavailable;
- test device cannot be isolated from real users.

## Execution Order

1. Complete Phase A locally.
2. Review local diff and test output.
3. Push branch and open/update PR.
4. Schedule VPS window.
5. Run Phase B using only test device and explicit commands.
6. Record result in lab.
7. Only then consider expanding Docker manager or web/API state-changing surfaces.
