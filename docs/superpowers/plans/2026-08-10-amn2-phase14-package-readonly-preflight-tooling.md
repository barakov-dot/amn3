# AMN2 Phase 14 Package and Read-Only Preflight Tooling Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Реализовать и локально проверить новое standalone Phase 14 tooling для checksum-bound application/runtime package, двух read-only Spain preflight contracts и независимых stage envelopes, не создавая production package и не выполняя SSH или live mutation.

**Architecture:** Канонический package — deterministic directory tree с canonical JSON manifest; hash manifest транзитивно связывает все файлы. Application и AWG3 runtime имеют отдельные schemas, collectors, stage allowlists и rollback boundaries. Runner передаёт checksum-verified collector через stdin, создаёт одноразовый локальный claim/outcome и не пишет на remote filesystem.

**Tech Stack:** Python 3, pytest, JSON Schema, PowerShell, Bash, SHA-256, Git archive.

## Global Constraints

- Source input — exact clean AMN2 HEAD-потомок `4547af1b23e4774822119f98004568c6eb039303` с checksum-verified application receipt.
- Foundation receipt: `research/amn2/phase14-awg3-readiness-local-verification-receipt-2026-08-09.md`, SHA-256 `3DF5A62B23C5BE565E08383288269AA7F486EE23F9E1A60D4D767D53A240316B`.
- Phase 13 — read-only reference; не копировать manifest, outcome, IDs или stale baseline.
- Не изменять `packaging/phase13-*`, `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` и unrelated untracked files.
- Tooling/fixture tests не разрешают package materialization, preflight run, SSH, stage, issuance или live mutation.
- Exact AWG3 resources: `awg3`, `amn2sp3br0`, UDP `30002`, `10.212.13.0/24`, `10.212.13.1/24`, `172.29.252.0/28`, `amn2-spain-awg3`, `amn2-spain-awg3.service`, `/var/lib/amn2-spain/awg3`, `/var/lib/amn2-spain/awg3/awg3.conf`.
- Любой conflict/mismatch/ambiguity — `BLOCKED` без adoption, alternate resource, deletion или blind retry.
- Remote preflight read-only; local claim/outcome — create-new/no-replace и secret-free.
- AWG2 equality и no-restart evidence обязательны.
- Каждый task: RED, минимальный GREEN, focused tests, `git diff --check`, secret/security review, отдельный local commit без push.

---

### Task 1: Define fresh schemas and immutable resource plan

**Files:**

- Create: `packaging/phase14-awg3-contract/package-manifest.schema.json`
- Create: `packaging/phase14-awg3-contract/application-preflight.schema.json`
- Create: `packaging/phase14-awg3-contract/runtime-preflight.schema.json`
- Create: `packaging/phase14-awg3-contract/failure-outcome.schema.json`
- Create: `packaging/phase14-awg3-contract/resource-plan.json`
- Create: `tests/test_phase14_awg3_contract_schemas.py`

**Interfaces:**

- Produces schema IDs `amn2.phase14.package-manifest.v1`, `amn2.phase14.application-readonly-preflight.v1`, `amn2.phase14.runtime-readonly-preflight.v1` and `amn2.phase14.preflight-failure.v1`.
- Produces closed `resource-plan.json` used by every later task.

- [ ] **Step 1: Write RED schema tests**

```python
def test_resource_plan_is_exact_and_closed():
    assert load_json(CONTRACT / "resource-plan.json") == {
        "schema": "amn2.phase14.awg3-resource-plan.v1",
        "interface": "awg3",
        "bridge": "amn2sp3br0",
        "udp_port": 30002,
        "vpn_cidr": "10.212.13.0/24",
        "server_address": "10.212.13.1/24",
        "container_cidr": "172.29.252.0/28",
        "container": "amn2-spain-awg3",
        "service": "amn2-spain-awg3.service",
        "state_root": "/var/lib/amn2-spain/awg3",
        "config_path": "/var/lib/amn2-spain/awg3/awg3.conf",
    }


def test_runtime_schema_rejects_secret_or_unknown_fields(valid_runtime_outcome):
    value = dict(valid_runtime_outcome, raw_config="forbidden")
    with pytest.raises(jsonschema.ValidationError):
        runtime_validator().validate(value)
```

- [ ] **Step 2: Run RED**

```powershell
python -m pytest -q tests/test_phase14_awg3_contract_schemas.py
```

Expected: FAIL because the Phase 14 contract files do not exist.

- [ ] **Step 3: Implement closed schemas**

Use Draft 2020-12, `additionalProperties: false` at every object boundary and lowercase 64-hex patterns. The manifest requires:

```json
{
  "schema": "amn2.phase14.package-manifest.v1",
  "package_id": "phase14-awg3-20260810-001",
  "source_head": "4547af1b23e4774822119f98004568c6eb039303",
  "verification_receipt_sha256": "3df5a62b23c5be565e08383288269aa7f486ee23f9e1a60d4d767d53a240316b",
  "live_mutation_authorized": false,
  "artifacts": []
}
```

Each artifact requires `path`, `size`, `sha256`, `role`, `stage`, `executable`, `secret_classification` and `rollback_boundary`. All schemas forbid raw stdout/stderr, config, key, QR, peer, token and VPN payload fields.

- [ ] **Step 4: Run GREEN and commit**

```powershell
python -m pytest -q tests/test_phase14_awg3_contract_schemas.py
git diff --check
git add packaging/phase14-awg3-contract tests/test_phase14_awg3_contract_schemas.py
git diff --cached --check
git commit -m "test: define Phase 14 package contracts"
```

### Task 2: Add guarded application and runtime stage envelopes

**Files:**

- Create: `scripts/vps/phase14_application_stage_remote.sh`
- Create: `scripts/vps/phase14_awg3_runtime_stage_remote.sh`
- Create: `packaging/phase14-awg3-contract/runtime/Containerfile`
- Create: `packaging/phase14-awg3-contract/runtime/entrypoint.sh`
- Create: `packaging/phase14-awg3-contract/runtime/amn2-spain-awg3.service`
- Create: `tests/test_phase14_awg3_stage_envelopes.py`

**Interfaces:**

- Consumes exact resource plan and manifest hashes.
- Produces two scripts that require explicit mode plus authorization hash and are never executed by this tooling plan.

- [ ] **Step 1: Write RED static and fixture tests**

```python
def test_application_stage_backs_up_before_install():
    text = APPLICATION_STAGE.read_text(encoding="utf-8")
    assert text.index("create_checksum_bound_db_backup") < text.index(
        "install_application_snapshot"
    )
    assert "ENABLE_AWG3_ISSUANCE" not in text


def test_runtime_stage_never_targets_awg2():
    text = RUNTIME_STAGE.read_text(encoding="utf-8")
    assert "systemctl restart amn2-spain-awg2" not in text
    assert "docker rm amn2-spain-awg2" not in text
```

Add a fixture backend proving rollback selects only AWG3 resources recorded by the current stage transaction.

- [ ] **Step 2: Run RED**

```powershell
python -m pytest -q tests/test_phase14_awg3_stage_envelopes.py
```

- [ ] **Step 3: Implement the guarded scripts**

Both scripts begin with:

```bash
set -euo pipefail
[[ $# -eq 2 ]]
mode=$1
authorization_sha256=$2
[[ $authorization_sha256 =~ ^[0-9a-f]{64}$ ]]
```

Application stage verifies hashes, creates a DB backup before writes, applies only additive schema/application files, runs AWG2/bot/web/admin smoke and restores previous code on failure without dropping additive schema.

Runtime stage keeps a transaction-local created-resource ledger, creates only exact AWG3 resources, leaves issuance off and removes only ledger-owned AWG3 resources on failure. Runtime entrypoint refuses an absent config and never generates keys/config.

- [ ] **Step 4: Run GREEN and commit**

```powershell
python -m pytest -q tests/test_phase14_awg3_stage_envelopes.py
git diff --check
git add scripts/vps/phase14_application_stage_remote.sh scripts/vps/phase14_awg3_runtime_stage_remote.sh packaging/phase14-awg3-contract/runtime tests/test_phase14_awg3_stage_envelopes.py
git diff --cached --check
git commit -m "feat: add guarded Phase 14 stage envelopes"
```

### Task 3: Implement the canonical package materializer

**Files:**

- Create: `scripts/phase14_awg3_package.py`
- Create: `tests/test_phase14_awg3_package.py`
- Create: `tests/fixtures/phase14_awg3_package/source-tree/`

**Interfaces:**

- Produces `PackageInputs`, `PackageReceipt`, `canonical_json_bytes` and `materialize_package`.

- [ ] **Step 1: Write RED materializer tests**

```python
def test_manifest_hash_binds_every_file(tmp_path):
    receipt = materialize_package(valid_inputs(), tmp_path / "package")
    manifest_bytes = receipt.manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    assert manifest_bytes == canonical_json_bytes(manifest)
    assert receipt.package_identity_sha256 == sha256(manifest_bytes)
    for item in manifest["artifacts"]:
        path = receipt.root / item["path"]
        assert path.stat().st_size == item["size"]
        assert sha256(path.read_bytes()) == item["sha256"]


def test_wrong_source_head_leaves_no_output(tmp_path):
    inputs = replace(valid_inputs(), source_head="0" * 40)
    with pytest.raises(PackageError, match="source head"):
        materialize_package(inputs, tmp_path / "package")
    assert not (tmp_path / "package").exists()
```

Add create-new/no-overwrite, symlink, traversal, secret pattern, stale Phase 13 outcome and deterministic input tests.

- [ ] **Step 2: Run RED**

```powershell
python -m pytest -q tests/test_phase14_awg3_package.py
```

- [ ] **Step 3: Implement exact models and materialization**

```python
@dataclass(frozen=True)
class PackageInputs:
    package_id: str
    source_root: Path
    source_head: str
    source_branch: str
    verification_receipt: bytes
    verification_receipt_sha256: str
    contract_root: Path
    stage_artifacts: tuple[Path, ...]


@dataclass(frozen=True)
class PackageReceipt:
    root: Path
    manifest_path: Path
    package_identity_sha256: str
    artifact_count: int


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")
```

Copy the source through `git archive <exact-head>` semantics, not filesystem untracked files. Deny `.git`, caches, local DB/env/key/config/QR files and old outcomes. Sort normalized POSIX paths, write a temporary sibling, verify every byte and atomically rename to an absent output root.

- [ ] **Step 4: Run GREEN and commit**

```powershell
python -m pytest -q tests/test_phase14_awg3_package.py tests/test_phase14_awg3_contract_schemas.py tests/test_phase14_awg3_stage_envelopes.py
git diff --check
git add scripts/phase14_awg3_package.py tests/test_phase14_awg3_package.py tests/fixtures/phase14_awg3_package
git diff --cached --check
git commit -m "feat: materialize canonical Phase 14 package"
```

### Task 4: Implement the application read-only collector

**Files:**

- Create: `scripts/vps/phase14_application_readonly_preflight_remote.sh`
- Create: `tests/test_phase14_application_readonly_preflight.py`
- Create: `tests/fixtures/phase14_application_preflight/`

**Interfaces:**

- Produces one bounded `amn2.phase14.application-readonly-preflight.v1` JSON document or one sanitized failure.

- [ ] **Step 1: Write RED read-only tests**

```python
def test_ready_result_is_not_install_authorization(run_fixture):
    outcome = run_fixture("application-ready")
    assert outcome["decision"] == "ready_for_application_stage"
    assert outcome["safety_receipt"] == {
        "mutation_attempted": False,
        "backup_created": False,
        "service_action_attempted": False,
        "remote_file_written": False,
    }


@pytest.mark.parametrize("token", ["systemctl restart", "sqlite3 ", "cp ", "mv ", "rm ", "chmod", "chown", ">"])
def test_collector_has_no_mutation_command(token):
    assert token not in collector_command_surface()
```

- [ ] **Step 2: Run RED**

```powershell
python -m pytest -q tests/test_phase14_application_readonly_preflight.py
```

- [ ] **Step 3: Implement bounded observations**

Observe exact application/source/schema identity, DB integrity/additive migration applicability, backup prerequisites, disk/inodes, app/bot/web/admin state and AWG2 equality/restart count. Emit hashes/counts only; never DB rows, configs, keys, Telegram IDs, endpoints or raw output. Permission/parser ambiguity returns exit `72` with `observation_ambiguous`.

- [ ] **Step 4: Run GREEN and commit**

```powershell
python -m pytest -q tests/test_phase14_application_readonly_preflight.py
git diff --check
git add scripts/vps/phase14_application_readonly_preflight_remote.sh tests/test_phase14_application_readonly_preflight.py tests/fixtures/phase14_application_preflight
git diff --cached --check
git commit -m "feat: add application read only preflight"
```

### Task 5: Implement the AWG3 runtime read-only collector

**Files:**

- Create: `scripts/vps/phase14_awg3_runtime_readonly_preflight_remote.sh`
- Create: `tests/test_phase14_awg3_runtime_readonly_preflight.py`
- Create: `tests/fixtures/phase14_awg3_runtime_preflight/`

**Interfaces:**

- Produces one `amn2.phase14.runtime-readonly-preflight.v1` JSON document or sanitized failure.

- [ ] **Step 1: Write RED conflict tests**

```python
@pytest.mark.parametrize(
    ("fixture", "reason"),
    [
        ("port-occupied", "udp_port_conflict"),
        ("interface-present", "interface_conflict"),
        ("bridge-present", "bridge_conflict"),
        ("vpn-cidr-overlap", "vpn_cidr_conflict"),
        ("container-cidr-overlap", "container_cidr_conflict"),
        ("container-present", "container_conflict"),
        ("service-present", "service_conflict"),
        ("path-present", "path_conflict"),
    ],
)
def test_each_resource_conflict_blocks(run_fixture, fixture, reason):
    result = run_fixture(fixture)
    assert result["decision"] == "blocked"
    assert result["stop_reasons"] == [reason]
```

Add AWG2 equality, restart-count change, incomplete command and secret-output tests.

- [ ] **Step 2: Run RED**

```powershell
python -m pytest -q tests/test_phase14_awg3_runtime_readonly_preflight.py
```

- [ ] **Step 3: Implement exact resource observations**

Observe UDP sockets, interfaces, routes, addresses, Docker networks/containers, systemd units and paths. Resource constants are generated from `resource-plan.json`; runtime overrides are rejected. Success requires every candidate free/absent, AWG2 equal, restart count equal, no remote write and no mutation.

- [ ] **Step 4: Run GREEN and commit**

```powershell
python -m pytest -q tests/test_phase14_awg3_runtime_readonly_preflight.py tests/test_phase13_awg3_readonly_preflight.py
git diff --check
git add scripts/vps/phase14_awg3_runtime_readonly_preflight_remote.sh tests/test_phase14_awg3_runtime_readonly_preflight.py tests/fixtures/phase14_awg3_runtime_preflight
git diff --cached --check
git commit -m "feat: add AWG3 runtime read only preflight"
```

### Task 6: Implement one-time claim, transport and outcome validation

**Files:**

- Create: `scripts/phase14_awg3_preflight_contract.py`
- Create: `scripts/vps/phase14_spain_readonly_preflight_ssh_runner.ps1`
- Create: `tests/test_phase14_awg3_preflight_contract.py`
- Create: `tests/test_phase14_awg3_preflight_runner.py`

**Interfaces:**

- Produces `PreflightClaim`, `create_claim`, `consume_claim`, `validate_outcome` and runner mode `application|runtime`.

- [ ] **Step 1: Write RED replay/transport tests**

```python
def test_claim_is_create_new_and_consumed_once(tmp_path):
    claim = create_claim(valid_claim_inputs(), tmp_path)
    with pytest.raises(PreflightContractError, match="claim already exists"):
        create_claim(valid_claim_inputs(), tmp_path)
    consume_claim(claim, valid_success_outcome())
    with pytest.raises(PreflightContractError, match="claim already consumed"):
        consume_claim(claim, valid_success_outcome())


@pytest.mark.parametrize("transport", ["timeout", "empty", "two-json-documents", "non-json", "extra-bytes"])
def test_transport_never_becomes_partial_success(run_runner, transport):
    result = run_runner(transport)
    assert result.decision == "blocked"
    assert result.success_outcome_written is False
```

- [ ] **Step 2: Run RED**

```powershell
python -m pytest -q tests/test_phase14_awg3_preflight_contract.py tests/test_phase14_awg3_preflight_runner.py
```

- [ ] **Step 3: Implement claim and runner**

```python
@dataclass(frozen=True)
class PreflightClaim:
    preflight_run_id: str
    mode: Literal["application", "runtime"]
    package_identity_sha256: str
    target_role: Literal["spain-primary"]
    collector_sha256: str
    runner_sha256: str
    schema_sha256: str
    created_at: datetime
    expires_at: datetime
```

IDs match `[a-z0-9][a-z0-9-]{2,63}`; expiry is at most 30 minutes. Claim/outcome writes are canonical, exclusive-create and fsynced.

Runner verifies all local hashes, sends one collector through stdin to `bash -s -- preflight`, forbids SCP/SFTP/remote redirection, keeps bounded stdout in memory, accepts one JSON document, validates schema/bindings/secret patterns and consumes the claim on success or failure.

- [ ] **Step 4: Run GREEN and commit**

```powershell
python -m pytest -q tests/test_phase14_awg3_preflight_contract.py tests/test_phase14_awg3_preflight_runner.py
git diff --check
git add scripts/phase14_awg3_preflight_contract.py scripts/vps/phase14_spain_readonly_preflight_ssh_runner.ps1 tests/test_phase14_awg3_preflight_contract.py tests/test_phase14_awg3_preflight_runner.py
git diff --cached --check
git commit -m "feat: bind Phase 14 preflight outcomes"
```

### Task 7: Verify tooling and stop before production materialization

**Files:**

- Create: `research/amn2/phase14-package-preflight-tooling-readiness-receipt.md`

**Interfaces:**

- Produces one secret-free local tooling receipt only.

- [ ] **Step 1: Run focused and full suites**

```powershell
python -m pytest -q tests/test_phase14_awg3_contract_schemas.py tests/test_phase14_awg3_stage_envelopes.py tests/test_phase14_awg3_package.py tests/test_phase14_application_readonly_preflight.py tests/test_phase14_awg3_runtime_readonly_preflight.py tests/test_phase14_awg3_preflight_contract.py tests/test_phase14_awg3_preflight_runner.py
python -m pytest -q
```

- [ ] **Step 2: Review exact scope**

```powershell
git diff --check
git status --short --branch
git diff --name-only HEAD
```

Confirm no Phase 13 edits, baseline edits, raw secrets, production credentials, materialized package, claim or outcome.

- [ ] **Step 3: Write and commit receipt**

```text
PACKAGE_TOOLING_READY=true
APPLICATION_PREFLIGHT_TOOLING_READY=true
RUNTIME_PREFLIGHT_TOOLING_READY=true
STAGE_ENVELOPES_LOCALLY_TESTED=true
PACKAGE_MATERIALIZED=false
PREFLIGHT_RUN=false
SSH_USED=false
LIVE_MUTATION=false
```

```powershell
git add research/amn2/phase14-package-preflight-tooling-readiness-receipt.md
git diff --cached --check
git commit -m "docs: record Phase 14 package tooling readiness"
```

- [ ] **Step 4: Stop and output one next approval**

Do not create `packaging/phase14-awg3-20260810-001`. Output exact tooling HEAD, receipt SHA-256 and one exact next approval for `PACKAGE_MATERIALIZATION`.

### Task 8: Materialize only after a separate PACKAGE_MATERIALIZATION approval

**Files:**

- Create after approval: `packaging/phase14-awg3-20260810-001/`
- Create after approval: `research/amn2/phase14-awg3-20260810-001-verification-receipt.md`

**Interfaces:**

- Produces one local package and verification receipt; no claim, preflight outcome or SSH.

- [ ] **Step 1: Re-run exact local head/clean gates**

```powershell
git -C C:\Users\SooL\Documents\amn2-phase14-awg3-readiness status --short --branch
git -C C:\Users\SooL\Documents\amn2-phase14-awg3-readiness rev-parse HEAD
git status --short --branch
```

Any mismatch stops.

- [ ] **Step 2: Materialize one exact create-new root**

```powershell
python scripts/phase14_awg3_package.py --package-id phase14-awg3-20260810-001 --source-root C:\Users\SooL\Documents\amn2-phase14-awg3-readiness --output-root packaging/phase14-awg3-20260810-001
```

- [ ] **Step 3: Verify and record receipt**

```powershell
python scripts/phase14_awg3_package.py --verify-only packaging/phase14-awg3-20260810-001
python -m pytest -q tests/test_phase14_awg3_package.py tests/test_phase14_awg3_contract_schemas.py
```

Record manifest hash, package identity, file count and secret scan result.

- [ ] **Step 4: Review, commit and stop before preflight**

```powershell
git add packaging/phase14-awg3-20260810-001 research/amn2/phase14-awg3-20260810-001-verification-receipt.md
git diff --cached --check
git diff --cached --name-only
git commit -m "build: materialize Phase 14 AWG3 package"
```

Do not create a claim/outcome and do not run the SSH runner. Output one exact next approval for `APPLICATION_PREFLIGHT`.

## Boundary after this plan

This plan deliberately does not prescribe executable commands for
`APPLICATION_PREFLIGHT`, `APPLICATION_STAGE`, `AWG3_RUNTIME_PREFLIGHT`,
`AWG3_RUNTIME_STAGE`, `AWG3_ADMIN_PILOT`, `AWG3_ACCEPTANCE` or
`ENABLE_AWG3_ISSUANCE`. Their exact commands must be written only after Task 8
produces the actual package identity and verification receipt, because those
hashes are mandatory inputs. Each becomes a separate approval-bound execution
plan; no command may chain two gates.
