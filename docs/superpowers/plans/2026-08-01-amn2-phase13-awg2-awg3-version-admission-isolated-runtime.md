# AMN2 Phase 13 AWG2/AWG3 Version Admission and Isolated Runtime Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the local-only, fail-closed AWG2/AWG3 protocol-admission control plane, isolated runtime data model, typed renderers, evidence-bound issuance, Passport/Drift metadata, recovery compatibility, and USA retirement readiness evaluator without deploying or mutating any live VPN runtime.

**Architecture:** Start from exact AMN2 source `55dc243b8e6c6bdb57f8301b56326e4cd4072d19` in a new isolated worktree. Add protocol and compatibility as first-class domain types, persist exact client/runtime/evidence identities in SQLite, and require admission before any key, peer, or config generation. Keep accepted AWG2 rendering byte-compatible, add an independent AWG3 renderer behind a secret-reference boundary, and expose only privacy-safe protocol/runtime/evidence facts to Passport, Drift, backup verification, and the USA readiness evaluator.

**Tech Stack:** Python `>=3.12,<3.13`, SQLite, frozen dataclasses and `StrEnum`, pytest `>=8,<9`, existing AMN2 Repository/service architecture, cryptography-backed secret storage already present in AMN2.

## Global Constraints

- Source baseline is exactly `55dc243b8e6c6bdb57f8301b56326e4cd4072d19`; implement in a new isolated AMN2 worktree, never in the VPS-OPS-LAB root `app/` directory.
- Spain operational overlay `f1bf099ddb47da26a4080714376babaf5b0de92c` and USA overlay `0b858c5cdbc5b565cc265966a2edfe2d339d65e0` are evidence inputs only and are not mutation targets for this plan.
- No SSH, VPS, Docker, firewall, systemd, peer, config delivery, reboot, Telegram, public exposure, or live Spain/USA/AWG action is authorized.
- Do not stop, restart, recreate, upgrade, or test against the accepted Spain AWG2 runtime.
- Spain d1-d7 remain byte-identical accepted AWG2 profiles; do not regenerate configs, peers, or keys and do not automatically backfill unknown client versions.
- New issuance targets are only `awg2` and `awg3`; retain legacy `amneziawg_v1_5` parsing/rendering for existing records, but do not expose it as a new Phase 13 issuance target.
- Exact `client_application`, `client_platform`, and `client_version` are mandatory for new issuance. OS-only, `latest`, blank, unknown, unverified, stale, or failed evidence must fail closed before secret generation.
- An official release claim has status `claimed`; it is never sufficient by itself for AWG3 issuance.
- AWG3 remains non-production until a separate accepted server/config/data/reboot/rollback gate exists. Local code may return only `candidate_awg3` when runtime or real-device acceptance is incomplete.
- `HeaderProtectionKey` is secret-bearing material. Persist only a secret reference and domain-separated fingerprint; never render the raw value in logs, exceptions, receipts, Passport, Drift, docs, or test failure messages.
- Preserve quota default `MAX_DEVICES_PER_USER=5`; quota policy is a separate product decision.
- Preserve bot disabled, web loopback-only, USA rollback contour, and foreign Spain service boundaries. This implementation plan cannot authorize their change.
- A readiness notification about USA is not approval to stop, wipe, delete, or reuse it.
- Every task follows red → green → focused regression → explicit commit. Never combine several red tests with a large speculative implementation.

## File Structure

New focused files:

- `app/vpn/protocol_versions.py` — canonical AWG2/AWG3 enums and strict normalization.
- `app/services/client_compatibility.py` — exact compatibility evidence records and lookup policy.
- `app/services/vpn_runtime_instances.py` — runtime lifecycle model and deterministic host-local conflict planner.
- `app/services/protocol_admission.py` — pure fail-closed decision service; no key/config/peer side effects.
- `app/vpn/amneziawg_v3/config.py` — AWG3-only typed input and renderer.
- `app/services/usa_retirement_readiness.py` — pure evidence evaluator and exact notification messages.

Existing files modified:

- `app/db/schema.py` and `app/db/repositories.py` — additive schema, migrations, and bounded repository methods.
- `app/vpn/config_versions.py` — preserve legacy render routing while adding explicit Phase 13 issuance routing.
- `app/services/admin_config_issuance.py` — require exact client/protocol tuple, persist admission IDs, and admit before mutation.
- `app/services/device_passports.py` and `app/services/drift_diagnostics.py` — safe protocol/runtime/evidence metadata and read-only drift reasons.
- `app/backup/service.py` — validate new rows and restore compatibility without exporting raw secrets.
- Corresponding `tests/` modules listed in each task.

---

### Task 1: Establish exact-source worktree and canonical protocol types

**Files:**
- Create: `app/vpn/protocol_versions.py`
- Create: `tests/vpn/test_protocol_versions.py`
- Modify: `app/vpn/config_versions.py`
- Test: `tests/vpn/test_config_versions.py`

**Interfaces:**
- Consumes: exact Git commit `55dc243b8e6c6bdb57f8301b56326e4cd4072d19`.
- Produces: `ProtocolVersion`, `NEW_ISSUANCE_PROTOCOLS`, `normalize_protocol_version()`, and `config_version_for_protocol()`.

- [ ] **Step 1: Create the isolated worktree and prove the baseline**

Run from `VPS-OPS-LAB` after invoking `superpowers:using-git-worktrees`:

```powershell
git -C worktrees/amn2-p7-c005-write-install worktree add ../amn2-phase13-awg2-awg3-local -b codex/phase13-awg2-awg3-local 55dc243b8e6c6bdb57f8301b56326e4cd4072d19
Set-Location worktrees/amn2-phase13-awg2-awg3-local
python -m pytest -q
git status --short --branch
```

Expected: the authoritative suite passes, HEAD is `55dc243`, and the new worktree has no changes. If the baseline fails, stop and record the exact failure; do not start implementation.

- [ ] **Step 2: Write failing protocol-version tests**

```python
import pytest

from app.vpn.protocol_versions import (
    NEW_ISSUANCE_PROTOCOLS,
    ProtocolVersion,
    config_version_for_protocol,
    normalize_protocol_version,
)


def test_new_issuance_protocols_are_exactly_awg2_and_awg3():
    assert NEW_ISSUANCE_PROTOCOLS == (
        ProtocolVersion.AWG2,
        ProtocolVersion.AWG3,
    )


def test_protocol_normalization_is_exact_and_fail_closed():
    assert normalize_protocol_version("awg2") is ProtocolVersion.AWG2
    assert normalize_protocol_version("awg3") is ProtocolVersion.AWG3
    for value in ("", "AWG3", "latest", "amneziawg_v1_5", None):
        with pytest.raises(ValueError, match="unsupported protocol_version"):
            normalize_protocol_version(value)


def test_protocol_to_config_schema_mapping_does_not_alias_awg3_to_awg2():
    assert config_version_for_protocol(ProtocolVersion.AWG2) == "amneziawg_v2"
    assert config_version_for_protocol(ProtocolVersion.AWG3) == "amneziawg_v3"
```

- [ ] **Step 3: Run the focused tests and verify RED**

Run:

```powershell
python -m pytest tests/vpn/test_protocol_versions.py tests/vpn/test_config_versions.py -q
```

Expected: collection fails because `app.vpn.protocol_versions` does not exist.

- [ ] **Step 4: Implement the minimal canonical types**

```python
from enum import StrEnum


class ProtocolVersion(StrEnum):
    AWG2 = "awg2"
    AWG3 = "awg3"


NEW_ISSUANCE_PROTOCOLS = (ProtocolVersion.AWG2, ProtocolVersion.AWG3)


def normalize_protocol_version(value: object) -> ProtocolVersion:
    if not isinstance(value, str):
        raise ValueError("unsupported protocol_version")
    try:
        return ProtocolVersion(value)
    except ValueError as exc:
        raise ValueError("unsupported protocol_version") from exc


def config_version_for_protocol(protocol: ProtocolVersion) -> str:
    return {
        ProtocolVersion.AWG2: "amneziawg_v2",
        ProtocolVersion.AWG3: "amneziawg_v3",
    }[protocol]
```

Keep every current value in `SUPPORTED_CONFIG_VERSIONS` for stored legacy profiles and append `amneziawg_v3` as a distinct readable schema; never alias it to `amneziawg_v2`. Add a separate `NEW_ISSUANCE_CONFIG_VERSIONS = ("amneziawg_v2", "amneziawg_v3")`; legacy values remain readable/replayable but are excluded from new issuance.

- [ ] **Step 5: Verify GREEN and commit**

```powershell
python -m pytest tests/vpn/test_protocol_versions.py tests/vpn/test_config_versions.py -q
git diff --check
git add app/vpn/protocol_versions.py app/vpn/config_versions.py tests/vpn/test_protocol_versions.py tests/vpn/test_config_versions.py
git commit -m "Add canonical AWG2 and AWG3 protocol versions"
```

### Task 2: Add additive compatibility-evidence and runtime-instance persistence

**Files:**
- Modify: `app/db/schema.py`
- Modify: `app/db/repositories.py`
- Test: `tests/db/test_repositories.py`
- Create: `tests/db/test_phase13_protocol_schema.py`

**Interfaces:**
- Consumes: `ProtocolVersion` from Task 1.
- Produces: repository rows for `client_compatibility_evidence` and `vpn_runtime_instances`; nullable protocol/runtime/evidence references on existing device lifecycle rows.

- [ ] **Step 1: Write failing additive-schema and migration tests**

```python
import json
import sqlite3

import pytest

from app.db.repositories import Repository
from app.db.schema import initialize_schema


@pytest.fixture
def repo():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    initialize_schema(conn)
    repository = Repository(conn)
    yield repository
    conn.close()


def seed_user_and_server(repo: Repository) -> tuple[int, int]:
    user_id = repo.upsert_user(
        telegram_id=13001,
        username="phase13",
        first_name="Phase",
        last_name="Thirteen",
    )
    server_id = repo.ensure_default_server(
        name="spain",
        network_cidr="10.212.12.0/24",
    )
    return user_id, server_id


def seed_existing_awg2_device(
    repo: Repository, *, user_id: int, server_id: int
) -> int:
    return repo.create_device(
        user_id=user_id,
        server_id=server_id,
        name="accepted-device",
        duration_days=None,
        expiry_policy="indefinite",
        vpn_ip="10.212.12.2",
        peer_public_key="phase13-public",
        peer_private_key_encrypted="encrypted-private",
        preshared_key_encrypted="encrypted-psk",
        config_version="amneziawg_v2",
    )


def test_phase13_schema_is_additive_and_leaves_legacy_devices_unclassified(repo):
    user_id, server_id = seed_user_and_server(repo)
    device_id = seed_existing_awg2_device(repo, user_id=user_id, server_id=server_id)

    row = repo.get_device(device_id)
    assert row["protocol_version"] is None
    assert row["runtime_instance_id"] is None


def test_runtime_identity_is_unique_per_physical_server(repo):
    _, server_id = seed_user_and_server(repo)
    repo.create_vpn_runtime_instance(
        runtime_instance_id="rt-spain-awg2",
        server_id=server_id,
        protocol_version="awg2",
        runtime_version="accepted-phase12",
        interface_name="awg0",
        udp_port=30001,
        vpn_cidr="10.212.12.0/24",
        container_name="amn2-awg",
        service_name=None,
        config_path="/opt/amnezia/awg/wg0.conf",
        lifecycle_state="accepted",
        acceptance_receipt="sha256:" + "a" * 64,
    )
    with pytest.raises(sqlite3.IntegrityError):
        repo.create_vpn_runtime_instance(
            runtime_instance_id="rt-conflict",
            server_id=server_id,
            protocol_version="awg3",
            runtime_version="3.0.1",
            interface_name="awg0",
            udp_port=30002,
            vpn_cidr="10.212.13.0/24",
            container_name="amn2-awg3",
            service_name=None,
            config_path="/opt/amn2/awg3/wg0.conf",
            lifecycle_state="planned",
            acceptance_receipt=None,
        )


def test_compatibility_evidence_stores_only_safe_reference(repo):
    row = repo.create_client_compatibility_evidence(
        evidence_id="compat-amneziavpn-win-5005-awg3",
        application="amnezia_vpn",
        platform="windows",
        client_version="5.0.0.5",
        protocol_version="awg3",
        source_kind="official_release",
        status="claimed",
        observed_at="2026-08-01T00:00:00Z",
        safe_reference="https://github.com/amnezia-vpn/amnezia-client/releases/tag/5.0.0.5",
        scope="windows exact build",
    )
    assert "PrivateKey" not in json.dumps(dict(row))
    assert row["status"] == "claimed"
```

- [ ] **Step 2: Run schema tests and verify RED**

```powershell
python -m pytest tests/db/test_phase13_protocol_schema.py tests/db/test_repositories.py -q
```

Expected: missing columns/tables/repository methods.

- [ ] **Step 3: Add exact tables, constraints, and nullable columns**

Add these tables inside `initialize_schema()` and use `_ensure_column()` for existing tables:

```sql
CREATE TABLE IF NOT EXISTS vpn_runtime_instances (
    runtime_instance_id TEXT PRIMARY KEY,
    server_id INTEGER NOT NULL,
    protocol_version TEXT NOT NULL CHECK (protocol_version IN ('awg2', 'awg3')),
    runtime_version TEXT NOT NULL,
    interface_name TEXT NOT NULL,
    udp_port INTEGER NOT NULL CHECK (udp_port BETWEEN 1 AND 65535),
    vpn_cidr TEXT NOT NULL,
    container_name TEXT,
    service_name TEXT,
    config_path TEXT NOT NULL,
    lifecycle_state TEXT NOT NULL
        CHECK (lifecycle_state IN ('planned', 'candidate', 'accepted', 'rollback_pending', 'retired')),
    acceptance_receipt TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE,
    UNIQUE (server_id, interface_name),
    UNIQUE (server_id, udp_port)
);

CREATE TABLE IF NOT EXISTS client_compatibility_evidence (
    evidence_id TEXT PRIMARY KEY,
    application TEXT NOT NULL,
    platform TEXT NOT NULL,
    client_version TEXT NOT NULL,
    protocol_version TEXT NOT NULL CHECK (protocol_version IN ('awg2', 'awg3')),
    source_kind TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('claimed', 'passed', 'failed', 'superseded')),
    observed_at TEXT NOT NULL,
    safe_reference TEXT NOT NULL,
    scope TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (application, platform, client_version, protocol_version, source_kind, safe_reference)
);
```

Add nullable `protocol_version`, `runtime_instance_id`, `client_identity_evidence_status`, and `compatibility_evidence_id` to `devices`, `device_passports`, and issuance receipts where the design requires them. Existing rows must remain `NULL`; no automatic `awg2` backfill is allowed.

- [ ] **Step 4: Add bounded Repository methods**

Implement exact methods with parameterized SQL only. Their public signatures are
`create_vpn_runtime_instance(*, runtime_instance_id, server_id,
protocol_version, runtime_version, interface_name, udp_port, vpn_cidr,
container_name, service_name, config_path, lifecycle_state,
acceptance_receipt) -> sqlite3.Row`,
`get_vpn_runtime_instance(runtime_instance_id) -> sqlite3.Row | None`,
`list_vpn_runtime_instances_for_server(server_id) -> list[sqlite3.Row]`,
`create_client_compatibility_evidence(*, evidence_id, application, platform,
client_version, protocol_version, source_kind, status, observed_at,
safe_reference, scope) -> sqlite3.Row`, and
`find_client_compatibility_evidence(*, application, platform, client_version,
protocol_version) -> list[sqlite3.Row]`.

Validate bounded one-line text, exact enums, timestamps, receipt/fingerprint shape, and a maximum list size of 100. Never accept raw config/key fields in these methods.

- [ ] **Step 5: Verify migration, full DB regression, and commit**

```powershell
python -m pytest tests/db/test_phase13_protocol_schema.py tests/db/test_repositories.py -q
git diff --check
git add app/db/schema.py app/db/repositories.py tests/db/test_phase13_protocol_schema.py tests/db/test_repositories.py
git commit -m "Persist protocol compatibility and runtime identities"
```

### Task 3: Implement deterministic isolated-runtime planning

**Files:**
- Create: `app/services/vpn_runtime_instances.py`
- Create: `tests/services/test_vpn_runtime_instances.py`
- Modify: `app/vpn/ipam.py`
- Test: `tests/vpn/test_ipam.py`

**Interfaces:**
- Consumes: repository runtime rows from Task 2.
- Produces: `RuntimeInstanceSpec`, `RuntimeConflict`, `RuntimePlan`, and `plan_runtime_instance()`; no deployment method.

- [ ] **Step 1: Write failing conflict and accepted-state tests**

```python
from dataclasses import replace

import pytest


def accepted_awg2_spec() -> RuntimeInstanceSpec:
    return RuntimeInstanceSpec(
        runtime_instance_id="rt-spain-awg2",
        server_id=1,
        protocol_version=ProtocolVersion.AWG2,
        runtime_version="accepted-phase12",
        interface_name="awg0",
        udp_port=30001,
        vpn_cidr="10.212.12.0/24",
        container_name="amn2-awg",
        service_name=None,
        config_path="/opt/amnezia/awg/wg0.conf",
        lifecycle_state="accepted",
        acceptance_receipt="sha256:" + "a" * 64,
    )


def planned_awg3_spec() -> RuntimeInstanceSpec:
    return RuntimeInstanceSpec(
        runtime_instance_id="rt-spain-awg3",
        server_id=1,
        protocol_version=ProtocolVersion.AWG3,
        runtime_version="3.0.1",
        interface_name="awg3",
        udp_port=30002,
        vpn_cidr="10.212.13.0/24",
        container_name="amn2-awg3",
        service_name=None,
        config_path="/opt/amn2/awg3/wg0.conf",
        lifecycle_state="planned",
        acceptance_receipt=None,
    )


def test_runtime_plan_rejects_port_interface_and_cidr_conflicts():
    existing = (accepted_awg2_spec(),)
    candidate = replace(
        planned_awg3_spec(),
        interface_name="awg0",
        udp_port=30001,
        vpn_cidr="10.212.12.128/25",
    )
    plan = plan_runtime_instance(candidate, existing=existing)
    assert {item.kind for item in plan.conflicts} == {
        "interface_name",
        "udp_port",
        "vpn_cidr_overlap",
    }
    assert plan.admissible is False


def test_accepted_lifecycle_requires_secret_free_receipt():
    with pytest.raises(ValueError, match="acceptance_receipt"):
        replace(accepted_awg2_spec(), acceptance_receipt=None)


class ReadOnlyRuntimeRepository:
    def __init__(self) -> None:
        self.reads = 0

    def list_vpn_runtime_instances_for_server(self, server_id: int):
        self.reads += 1
        assert server_id == 1
        return [row_from_spec(accepted_awg2_spec())]

    def __getattr__(self, name: str):
        if name.startswith(("create_", "update_", "delete_")):
            raise AssertionError(f"runtime planning attempted mutation: {name}")
        raise AttributeError(name)


def test_planning_service_uses_only_read_path():
    repo = ReadOnlyRuntimeRepository()
    result = RuntimePlanningService(repo).plan(planned_awg3_spec())
    assert result.admissible is True
    assert repo.reads == 1
```

- [ ] **Step 2: Run tests and verify RED**

```powershell
python -m pytest tests/services/test_vpn_runtime_instances.py tests/vpn/test_ipam.py -q
```

- [ ] **Step 3: Implement immutable planning models**

```python
import re


@dataclass(frozen=True)
class RuntimeInstanceSpec:
    runtime_instance_id: str
    server_id: int
    protocol_version: ProtocolVersion
    runtime_version: str
    interface_name: str
    udp_port: int
    vpn_cidr: str
    container_name: str | None
    service_name: str | None
    config_path: str
    lifecycle_state: Literal["planned", "candidate", "accepted", "rollback_pending", "retired"]
    acceptance_receipt: str | None

    def __post_init__(self) -> None:
        if self.lifecycle_state == "accepted" and not self.acceptance_receipt:
            raise ValueError("accepted runtime requires acceptance_receipt")
        if self.acceptance_receipt is not None and not re.fullmatch(
            r"sha256:[0-9a-f]{64}", self.acceptance_receipt
        ):
            raise ValueError("invalid acceptance_receipt")


@dataclass(frozen=True)
class RuntimeConflict:
    kind: Literal["interface_name", "udp_port", "vpn_cidr_overlap", "runtime_identity"]
    existing_runtime_instance_id: str


@dataclass(frozen=True)
class RuntimePlan:
    candidate: RuntimeInstanceSpec
    conflicts: tuple[RuntimeConflict, ...]

    @property
    def admissible(self) -> bool:
        return not self.conflicts
```

Parse each CIDR with `ipaddress.ip_network(value, strict=False)` and call
`candidate_network.overlaps(existing_network)`. Do not add Docker, SSH,
firewall, or shell execution.

- [ ] **Step 4: Add repository-backed read-only planning service**

```python
class RuntimePlanningService:
    def __init__(self, repo: Repository) -> None:
        self._repo = repo

    def plan(self, candidate: RuntimeInstanceSpec) -> RuntimePlan:
        rows = self._repo.list_vpn_runtime_instances_for_server(candidate.server_id)
        return plan_runtime_instance(candidate, existing=tuple(spec_from_row(row) for row in rows))
```

- [ ] **Step 5: Verify and commit**

```powershell
python -m pytest tests/services/test_vpn_runtime_instances.py tests/vpn/test_ipam.py -q
git diff --check
git add app/services/vpn_runtime_instances.py app/vpn/ipam.py tests/services/test_vpn_runtime_instances.py tests/vpn/test_ipam.py
git commit -m "Add isolated VPN runtime planner"
```

### Task 4: Add exact client compatibility registry and fail-closed admission

**Files:**
- Create: `app/services/client_compatibility.py`
- Create: `app/services/protocol_admission.py`
- Create: `tests/services/test_client_compatibility.py`
- Create: `tests/services/test_protocol_admission.py`

**Interfaces:**
- Consumes: exact client tuple, compatibility rows, and `RuntimeInstanceSpec`.
- Produces: `ClientIdentity`, `ClientCompatibilityEvidence`, `AdmissionRequest`, `AdmissionResult`, and `ProtocolAdmissionService.decide()`.

- [ ] **Step 1: Write failing normalization and decision-matrix tests**

```python
import re
from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest


NOW = datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc)


def runtime(protocol: ProtocolVersion, *, accepted: bool) -> RuntimeInstanceSpec:
    return RuntimeInstanceSpec(
        runtime_instance_id=f"rt-spain-{protocol.value}",
        server_id=1,
        protocol_version=protocol,
        runtime_version="3.0.1" if protocol is ProtocolVersion.AWG3 else "accepted-phase12",
        interface_name="awg3" if protocol is ProtocolVersion.AWG3 else "awg0",
        udp_port=30002 if protocol is ProtocolVersion.AWG3 else 30001,
        vpn_cidr="10.212.13.0/24" if protocol is ProtocolVersion.AWG3 else "10.212.12.0/24",
        container_name=f"amn2-{protocol.value}",
        service_name=None,
        config_path=f"/opt/amn2/{protocol.value}/wg0.conf",
        lifecycle_state="accepted" if accepted else "candidate",
        acceptance_receipt=("sha256:" + "a" * 64) if accepted else None,
    )


def evidence(status: CompatibilityEvidenceStatus) -> ClientCompatibilityEvidence:
    return ClientCompatibilityEvidence(
        evidence_id=f"compat-win-5005-awg3-{status.value}",
        client=ClientIdentity("amnezia_vpn", "windows", "5.0.0.5"),
        protocol_version=ProtocolVersion.AWG3,
        source_kind="full_data" if status is CompatibilityEvidenceStatus.PASSED else "official_release",
        status=status,
        observed_at=NOW,
        safe_reference=f"receipt:{status.value}",
        scope="windows exact build 5.0.0.5",
    )


def request(application: str, version: str) -> AdmissionRequest:
    return AdmissionRequest(
        client=ClientIdentity(application, "windows", version),
        protocol_version=ProtocolVersion.AWG3,
    )


@pytest.mark.parametrize("version", [None, "", "latest", " 5.0.0.5", "5.0.0.5 "])
def test_client_identity_rejects_unknown_or_ambiguous_version(version):
    with pytest.raises(ValueError, match="exact client_version"):
        ClientIdentity("amnezia_vpn", "windows", version)


def test_official_claim_alone_does_not_admit_awg3():
    service = ProtocolAdmissionService(
        evidence=(evidence(CompatibilityEvidenceStatus.CLAIMED),),
        runtimes=(runtime(ProtocolVersion.AWG3, accepted=True),),
        now=NOW,
    )
    result = service.decide(request("amnezia_vpn", "5.0.0.5"))
    assert result.decision == "blocked_unverified_version"
    assert result.compatibility_evidence_id is None


def test_future_dated_passed_evidence_fails_closed():
    future = replace(
        evidence(CompatibilityEvidenceStatus.PASSED),
        observed_at=NOW + timedelta(seconds=1),
    )
    result = ProtocolAdmissionService(
        evidence=(future,),
        runtimes=(runtime(ProtocolVersion.AWG3, accepted=True),),
        now=NOW,
    ).decide(request("amnezia_vpn", "5.0.0.5"))
    assert result.decision == "blocked_evidence_stale_or_failed"


def test_passed_exact_client_and_accepted_runtime_admit_awg3():
    service = ProtocolAdmissionService(
        evidence=(evidence(CompatibilityEvidenceStatus.PASSED),),
        runtimes=(runtime(ProtocolVersion.AWG3, accepted=True),),
        now=NOW,
    )
    result = service.decide(request("amnezia_vpn", "5.0.0.5"))
    assert result.decision == "admitted_awg3"
    assert result.runtime_instance_id == "rt-spain-awg3"


def test_unknown_awg3_does_not_silently_fallback_to_awg2():
    service = ProtocolAdmissionService(
        evidence=(),
        runtimes=(runtime(ProtocolVersion.AWG2, accepted=True),),
        now=NOW,
    )
    result = service.decide(request("unknown", "1.0.0"))
    assert result.decision == "blocked_unknown_client"
    assert result.protocol_version is ProtocolVersion.AWG3
```

- [ ] **Step 2: Run tests and verify RED**

```powershell
python -m pytest tests/services/test_client_compatibility.py tests/services/test_protocol_admission.py -q
```

- [ ] **Step 3: Implement exact immutable evidence models**

```python
class CompatibilityEvidenceStatus(StrEnum):
    CLAIMED = "claimed"
    PASSED = "passed"
    FAILED = "failed"
    SUPERSEDED = "superseded"


@dataclass(frozen=True)
class ClientIdentity:
    application: str
    platform: str
    version: str

    def __post_init__(self) -> None:
        for field_name in ("application", "platform", "version"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value or value != value.strip():
                raise ValueError(f"exact {field_name} is required")
            if len(value) > 64 or any(ord(char) < 32 for char in value):
                raise ValueError(f"invalid exact {field_name}")
        if self.version.casefold() in {"latest", "current", "unknown"}:
            raise ValueError("exact client_version is required")


@dataclass(frozen=True)
class ClientCompatibilityEvidence:
    evidence_id: str
    client: ClientIdentity
    protocol_version: ProtocolVersion
    source_kind: str
    status: CompatibilityEvidenceStatus
    observed_at: datetime
    safe_reference: str
    scope: str
```

Normalize application/platform with explicit allowlisted canonical identifiers. Preserve the exact bounded version/build string after rejecting whitespace, control characters, `latest`, and values longer than 64 characters.

- [ ] **Step 4: Implement the pure admission service**

```python
AdmissionDecision = Literal[
    "admitted_awg2",
    "admitted_awg3",
    "candidate_awg3",
    "blocked_unknown_client",
    "blocked_unverified_version",
    "blocked_unsupported_platform",
    "blocked_runtime_not_accepted",
    "blocked_evidence_stale_or_failed",
]


@dataclass(frozen=True)
class AdmissionResult:
    decision: AdmissionDecision
    protocol_version: ProtocolVersion
    runtime_instance_id: str | None
    compatibility_evidence_id: str | None

    @property
    def admitted(self) -> bool:
        return self.decision in {"admitted_awg2", "admitted_awg3"}


@dataclass(frozen=True)
class AdmissionRequest:
    client: ClientIdentity
    protocol_version: ProtocolVersion


class ProtocolAdmissionService:
    def __init__(
        self,
        *,
        evidence: tuple[ClientCompatibilityEvidence, ...],
        runtimes: tuple[RuntimeInstanceSpec, ...],
        now: datetime,
        max_evidence_age: timedelta = timedelta(days=90),
    ) -> None:
        self._evidence = evidence
        self._runtimes = runtimes
        self._now = now
        self._max_evidence_age = max_evidence_age

    def decide(self, request: AdmissionRequest) -> AdmissionResult:
        known_apps = {item.client.application for item in self._evidence}
        if request.client.application not in known_apps:
            return AdmissionResult(
                "blocked_unknown_client", request.protocol_version, None, None
            )
        known_platforms = {
            item.client.platform
            for item in self._evidence
            if item.client.application == request.client.application
        }
        if request.client.platform not in known_platforms:
            return AdmissionResult(
                "blocked_unsupported_platform", request.protocol_version, None, None
            )

        exact = tuple(
            item for item in self._evidence
            if item.client == request.client
            and item.protocol_version is request.protocol_version
        )
        passed = next(
            (
                item for item in exact
                if item.status is CompatibilityEvidenceStatus.PASSED
                and timedelta(0) <= self._now - item.observed_at <= self._max_evidence_age
            ),
            None,
        )
        if passed is None:
            decision = (
                "blocked_evidence_stale_or_failed"
                if any(item.status in {
                    CompatibilityEvidenceStatus.FAILED,
                    CompatibilityEvidenceStatus.SUPERSEDED,
                } or not timedelta(0) <= self._now - item.observed_at <= self._max_evidence_age
                for item in exact)
                else "blocked_unverified_version"
            )
            return AdmissionResult(decision, request.protocol_version, None, None)

        runtime = next(
            (
                item for item in self._runtimes
                if item.protocol_version is request.protocol_version
            ),
            None,
        )
        if runtime is None:
            return AdmissionResult(
                "blocked_runtime_not_accepted",
                request.protocol_version,
                None,
                passed.evidence_id,
            )
        if runtime.lifecycle_state != "accepted" or not runtime.acceptance_receipt:
            decision = (
                "candidate_awg3"
                if request.protocol_version is ProtocolVersion.AWG3
                else "blocked_runtime_not_accepted"
            )
            return AdmissionResult(
                decision,
                request.protocol_version,
                runtime.runtime_instance_id,
                passed.evidence_id,
            )
        return AdmissionResult(
            "admitted_awg3" if request.protocol_version is ProtocolVersion.AWG3 else "admitted_awg2",
            request.protocol_version,
            runtime.runtime_instance_id,
            passed.evidence_id,
        )
```

Require exact passed evidence for the requested tuple. Treat `claimed`, `failed`, `superseded`, or stale evidence as non-admitting. Require `lifecycle_state == "accepted"` and a receipt for issuance; otherwise return `candidate_awg3` only when client evidence passed but runtime acceptance is incomplete.

- [ ] **Step 5: Verify and commit**

```powershell
python -m pytest tests/services/test_client_compatibility.py tests/services/test_protocol_admission.py -q
git diff --check
git add app/services/client_compatibility.py app/services/protocol_admission.py tests/services/test_client_compatibility.py tests/services/test_protocol_admission.py
git commit -m "Add fail-closed client protocol admission"
```

### Task 5: Add separate AWG3 typed rendering behind a secret reference

**Files:**
- Create: `app/vpn/amneziawg_v3/__init__.py`
- Create: `app/vpn/amneziawg_v3/config.py`
- Create: `tests/vpn/test_amneziawg_v3_config.py`
- Modify: `app/vpn/config_versions.py`
- Test: `tests/vpn/test_config_versions.py`
- Test: `tests/vpn/test_amneziawg_config.py`

**Interfaces:**
- Consumes: admitted protocol plus `HeaderProtectionSecretRef` and a narrow `SecretResolver`.
- Produces: `Awg3ClientConfigInput` and `render_awg3_client_config()`; AWG2 renderer remains unchanged.

- [ ] **Step 1: Freeze AWG2 output and write AWG2/AWG3 negative tests**

```python
import hashlib
import json

import pytest


def existing_awg2_input() -> ClientConfigInput:
    return ClientConfigInput(
        private_key="client-private",
        address="10.8.0.2/32",
        dns="1.1.1.1",
        server_public_key="server-public",
        preshared_key="psk",
        endpoint="vpn.example.com:30001",
        allowed_ips="0.0.0.0/0",
        persistent_keepalive=25,
        jc=4,
        jmin=40,
        jmax=70,
        s1=0,
        s2=0,
        h1=1,
        h2=2,
        h3=3,
        h4=4,
    )


def existing_awg2_kwargs() -> dict[str, object]:
    return vars(existing_awg2_input())


class StaticResolver:
    def __init__(self, value: str) -> None:
        self._value = value

    def resolve(self, reference: str) -> str:
        assert reference == "secret:awg3:hpk"
        return self._value


def awg3_input() -> Awg3ClientConfigInput:
    return Awg3ClientConfigInput(
        awg2=existing_awg2_input(),
        header_protection_key=HeaderProtectionSecretRef(
            reference="secret:awg3:hpk",
            fingerprint="sha256:" + "b" * 64,
        ),
        content_padding_addition="0-64",
        rekey_after_time="120",
        rekey_timeout="5",
        reject_after_time="180",
        keepalive_timeout="10",
        max_handshake_attempts="20",
    )


def test_awg2_renderer_golden_output_is_byte_unchanged():
    rendered = render_awg2_client_config(existing_awg2_input()).encode()
    assert len(rendered) == 323
    assert hashlib.sha256(rendered).hexdigest() == (
        "8425d1666135621c398e1df29ee82c849a28641a152ddf1f69b5330f6b95e5eb"
    )


def test_awg2_input_rejects_awg3_only_fields():
    with pytest.raises(TypeError):
        ClientConfigInput(**existing_awg2_kwargs(), header_protection_key_ref="secret:awg3")


def test_awg3_requires_secret_reference_and_renders_official_field_names():
    config = render_awg3_client_config(awg3_input(), resolver=StaticResolver("raw-hpk"))
    assert "HeaderProtectionKey = raw-hpk" in config
    assert "ContentPaddingAddition = 0-64" in config
    assert "RekeyAfterTime = 120" in config
    assert "RekeyTimeout = 5" in config
    assert "RejectAfterTime = 180" in config
    assert "KeepaliveTimeout = 10" in config
    assert "MaxHandshakeAttempts = 20" in config


def test_awg3_secret_is_absent_from_repr_metadata_and_errors():
    raw = "never-log-header-protection-key"
    value = awg3_input()
    rendered = value.safe_metadata()
    assert raw not in repr(value)
    assert raw not in json.dumps(rendered)
```

- [ ] **Step 2: Run tests and verify RED**

```powershell
python -m pytest tests/vpn/test_amneziawg_v3_config.py tests/vpn/test_config_versions.py tests/vpn/test_amneziawg_config.py -q
```

- [ ] **Step 3: Implement the secret-reference boundary**

```python
@dataclass(frozen=True)
class HeaderProtectionSecretRef:
    reference: str
    fingerprint: str


class SecretResolver(Protocol):
    def resolve(self, reference: str) -> str:
        raise NotImplementedError


@dataclass(frozen=True)
class Awg3ClientConfigInput:
    awg2: ClientConfigInput
    header_protection_key: HeaderProtectionSecretRef
    content_padding_addition: str
    rekey_after_time: str
    rekey_timeout: str
    reject_after_time: str
    keepalive_timeout: str
    max_handshake_attempts: str

    def safe_metadata(self) -> dict[str, str]:
        return {
            "header_protection_key_fingerprint": self.header_protection_key.fingerprint,
            "protocol_version": "awg3",
        }
```

Validate `fingerprint` as `sha256:` plus 64 lowercase hex characters. Do not include raw key values in validation errors.

- [ ] **Step 4: Implement a dedicated AWG3 renderer and explicit routing**

```python
def render_awg3_client_config(
    config: Awg3ClientConfigInput, *, resolver: SecretResolver
) -> str:
    base = render_awg2_client_config(config.awg2)
    header_key = resolver.resolve(config.header_protection_key.reference)
    awg3_lines = (
        f"HeaderProtectionKey = {header_key}",
        f"ContentPaddingAddition = {config.content_padding_addition}",
        f"RekeyAfterTime = {config.rekey_after_time}",
        f"RekeyTimeout = {config.rekey_timeout}",
        f"RejectAfterTime = {config.reject_after_time}",
        f"KeepaliveTimeout = {config.keepalive_timeout}",
        f"MaxHandshakeAttempts = {config.max_handshake_attempts}",
    )
    marker = "\n\n[Peer]\n"
    if marker not in base:
        raise ValueError("AWG2 base config has no unique Peer boundary")
    interface, peer = base.split(marker, 1)
    rendered_awg3_lines = "\n".join(awg3_lines)
    return interface + "\n" + rendered_awg3_lines + marker + peer
```

Route `amneziawg_v3` only when the caller supplies `Awg3ClientConfigInput` and a resolver. Never append AWG3 fields to an existing stored AWG2 config string.

- [ ] **Step 5: Verify, scan for secret leakage, and commit**

```powershell
python -m pytest tests/vpn/test_amneziawg_v3_config.py tests/vpn/test_config_versions.py tests/vpn/test_amneziawg_config.py -q
rg -n "HeaderProtectionKey|header_protection" app tests
git diff --check
git add app/vpn/amneziawg_v3 app/vpn/config_versions.py tests/vpn/test_amneziawg_v3_config.py tests/vpn/test_config_versions.py tests/vpn/test_amneziawg_config.py
git commit -m "Add isolated AWG3 typed renderer"
```

Review every `rg` match: raw example secrets may exist only as explicit test sentinels and must never enter production logs, receipts, exceptions, or safe metadata.

### Task 6: Enforce admission before issuance mutation and bind idempotency

**Files:**
- Modify: `app/services/admin_config_issuance.py`
- Modify: `app/db/repositories.py`
- Test: `tests/services/test_admin_config_issuance.py`
- Test: `tests/db/test_repositories.py`
- Modify: `app/cli.py`
- Test: `tests/cli/test_admin_config_issuance.py`

**Interfaces:**
- Consumes: `ProtocolAdmissionService`, exact client tuple, runtime/evidence IDs, and existing issuance receipts.
- Produces: admission-bound request/item fingerprints and safe receipts; calls existing access/config generation only after `admitted_awg2|admitted_awg3`.

- [ ] **Step 1: Write fail-before-mutation and replay tests**

```python
from types import SimpleNamespace


class SpyAccessService:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def create_operator_device(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            device_id=1,
            passport_device_id="dev_phase13",
            config_filename="phase13.conf",
            config_text="safe-test-config",
        )


class StaticAdmissionService:
    def __init__(self, result: AdmissionResult) -> None:
        self._result = result

    def decide(self, request: AdmissionRequest) -> AdmissionResult:
        return self._result


def phase13_manifest(client_version: str) -> dict[str, object]:
    return {
        "request_id": "phase13-001",
        "server": "Spain-Madrid",
        "items": [{
            "recipient_label": "SooL",
            "device_label": "NOTEBOOK",
            "client_application": "amnezia_vpn",
            "client_platform": "windows",
            "client_version": client_version,
            "protocol_version": "awg3",
        }],
    }


class LegacyReplayRepository:
    def __init__(
        self,
        *,
        request_id: str,
        config_version: str,
        protocol_version: str | None,
        client_version: str | None,
    ) -> None:
        self.request_id = request_id
        self._request = {
            "request_id": request_id,
            "request_fingerprint": "sha256:" + "c" * 64,
            "item_count": 1,
        }
        self._receipts = [{
            "id": 1,
            "request_id": request_id,
            "item_index": 0,
            "recipient_user_id": 1,
            "device_id": 7,
            "passport_device_id": "dev_phase12",
            "assignment_mode": "dedicated_device",
            "slot_sequence": 1,
            "expiry_policy": "indefinite",
            "status": "completed",
            "config_filename": "SooL-NOTEBOOK.conf",
            "error_code": None,
            "config_version": config_version,
            "protocol_version": protocol_version,
            "runtime_instance_id": None,
            "compatibility_evidence_id": None,
            "client_version": client_version,
            "created_at": "2026-08-01T00:00:00Z",
            "updated_at": "2026-08-01T00:00:00Z",
        }]

    def get_admin_config_issuance_request(self, *, request_id: str):
        return self._request if request_id == self.request_id else None

    def list_admin_config_issuance_receipts(self, request_id: str):
        return list(self._receipts) if request_id == self.request_id else []

    def __getattr__(self, name: str):
        if name.startswith(("create_", "update_", "complete_", "fail_")):
            raise AssertionError(f"legacy replay attempted mutation: {name}")
        raise AttributeError(name)


def test_unknown_client_is_rejected_before_recipient_peer_key_or_config_creation(tmp_path):
    conn, repo = _repo(tmp_path)
    access = SpyAccessService()
    service = AdminConfigIssuanceService(
        repo=repo,
        access_service=access,
        admission_service=StaticAdmissionService(
            AdmissionResult(
                decision="blocked_unknown_client",
                protocol_version=ProtocolVersion.AWG3,
                runtime_instance_id=None,
                compatibility_evidence_id=None,
            )
        ),
        admin_telegram_id=1,
        attachment_builder=lambda filename, config: (filename, config),
    )

    with pytest.raises(ValueError, match="blocked_unknown_client"):
        service.issue_manifest(phase13_manifest("5.0.0.5"))

    assert access.calls == []
    assert conn.execute("SELECT count(*) FROM users").fetchone()[0] == 0
    assert conn.execute("SELECT count(*) FROM admin_config_issuance_receipts").fetchone()[0] == 0


def test_fingerprint_binds_exact_client_protocol_runtime_and_evidence(tmp_path):
    first = validate_admin_config_issuance_manifest(phase13_manifest("5.0.0.5"))
    changed = validate_admin_config_issuance_manifest(phase13_manifest("5.0.0.6"))
    assert _request_fingerprint(first) != _request_fingerprint(changed)


def test_completed_legacy_receipt_replays_without_reissue_or_forced_backfill():
    repo = LegacyReplayRepository(
        request_id="phase12-spain-sool-remaining-20260801-002",
        config_version="amneziawg_v2",
        protocol_version=None,
        client_version=None,
    )
    access = SpyAccessService()
    service = AdminConfigIssuanceService(
        repo=repo,
        access_service=access,
        admission_service=StaticAdmissionService(
            AdmissionResult(
                decision="blocked_unverified_version",
                protocol_version=ProtocolVersion.AWG2,
                runtime_instance_id=None,
                compatibility_evidence_id=None,
            )
        ),
        admin_telegram_id=1,
        attachment_builder=lambda filename, config: (filename, config),
    )
    result = service.replay_existing_request(repo.request_id)
    assert result.status == "completed"
    assert access.calls == []
    assert result.receipts[0].protocol_version is None
```

The test double's mutation guard proves replay cannot generate or backfill
anything.

- [ ] **Step 2: Run focused issuance tests and verify RED**

```powershell
python -m pytest tests/services/test_admin_config_issuance.py tests/cli/test_admin_config_issuance.py tests/db/test_repositories.py -q
```

- [ ] **Step 3: Extend manifest types with exact required identity**

```python
@dataclass(frozen=True)
class ExpandedIssuanceSlot:
    item_index: int
    recipient_label: str
    assignment_mode: str
    slot_sequence: int
    device_label: str
    client_application: str
    client_platform: str
    client_version: str
    protocol_version: ProtocolVersion
    expiry: AccessExpiry
```

Replace the dedicated-device `platform` field with exact `client_application`, `client_platform`, `client_version`, and `protocol_version`. New `recipient_unassigned` manifests must fail closed because exact device/client facts do not yet exist; slot reservation must be designed as a separate non-issuance workflow rather than generating a peer/config for an unknown client. Preserve read-only replay of already completed Phase 12 requests.

- [ ] **Step 4: Admit the entire batch before creating request/recipient/receipt**

```python
admissions = tuple(
    self._admission.decide(
        AdmissionRequest(
            client=ClientIdentity(
                slot.client_application,
                slot.client_platform,
                slot.client_version,
            ),
            protocol_version=slot.protocol_version,
        )
    )
    for slot in validated.expanded_slots
)
blocked = next((item for item in admissions if not item.admitted), None)
if blocked is not None:
    raise ValueError(blocked.decision)
```

Only after the full batch passes may the service create the issuance request. Include client/protocol/runtime/evidence IDs in `_slot_dict()`, `_slot_fingerprint()`, `_request_fingerprint()`, safe receipt columns, and admin audit metadata. Do not store raw configs or key material in receipts.

- [ ] **Step 5: Route manifest identity through CLI, verify no bypass, and commit**

Preserve the existing `admin-config issue-manifest --manifest ... --server ...` CLI shape. Require `client_application`, `client_platform`, `client_version`, and `protocol_version` inside every new manifest item; validate them in both dry-run planning and apply paths. Construct the admission service from repository evidence/runtime rows before `AdminConfigIssuanceService`, and prove there is no apply-path bypass. Do not enable bot/public issuance.

```powershell
python -m pytest tests/services/test_admin_config_issuance.py tests/cli/test_admin_config_issuance.py tests/db/test_repositories.py -q
git diff --check
git add app/services/admin_config_issuance.py app/db/repositories.py app/cli.py tests/services/test_admin_config_issuance.py tests/cli/test_admin_config_issuance.py tests/db/test_repositories.py
git commit -m "Bind issuance to exact protocol admission"
```

### Task 7: Extend Device Passport and read-only Drift with protocol evidence

**Files:**
- Modify: `app/services/device_passports.py`
- Modify: `app/services/drift_diagnostics.py`
- Test: `tests/services/test_device_passports.py`
- Test: `tests/services/test_drift_diagnostics.py`
- Test: `tests/web/test_device_passports.py`
- Test: `tests/web/test_device_passport_views.py`

**Interfaces:**
- Consumes: persisted protocol/runtime/evidence IDs from Tasks 2 and 6.
- Produces: secret-safe Passport metadata and five new read-only drift reasons.

- [ ] **Step 1: Write Passport safe-metadata and unknown-legacy tests**

```python
def test_passport_exposes_safe_protocol_runtime_and_compatibility_facts():
    _, repo, user_id, local_device_id = _repo()
    passport = create_device_passport(
        repo,
        owner_user_id=user_id,
        local_device_id=local_device_id,
        platform="windows",
        official_client_type="amnezia_vpn",
        client_version="5.0.0.5",
        import_method="conf_file",
        config_schema_version="amneziawg_v3",
        config_text=RAW_CONFIG,
        protocol_version="awg3",
        runtime_instance_id="rt-spain-awg3",
        client_identity_evidence_status="verified",
        compatibility_evidence_id="compat-win-5005-awg3-data",
    )
    safe = passport.safe_metadata()
    assert safe["protocol_version"] == "awg3"
    assert safe["runtime_instance_id"] == "rt-spain-awg3"
    assert safe["client_identity_evidence_status"] == "verified"
    assert safe["compatibility_evidence_id"] == "compat-win-5005-awg3-data"
    assert "HeaderProtectionKey" not in json.dumps(safe)


def test_existing_passport_without_exact_client_version_stays_unknown():
    _, repo, user_id, local_device_id = _repo()
    passport = create_device_passport(
        repo,
        owner_user_id=user_id,
        local_device_id=local_device_id,
        platform="android_tv",
        official_client_type="amnezia_vpn",
        client_version=None,
        import_method="conf_file",
        config_schema_version="amneziawg_v2",
        config_text=RAW_CONFIG,
    )
    assert passport.client_identity_evidence_status == "unknown"
    assert passport.compatibility_evidence_id is None
```

- [ ] **Step 2: Write drift taxonomy and no-mutation tests**

```python
@pytest.mark.parametrize(
    ("desired", "observed", "reason"),
    [
        ({"protocol_version": "awg3"}, {"protocol_version": "awg2"}, "protocol_version_mismatch"),
        ({"runtime_instance_id": "rt-a"}, {"runtime_instance_id": "rt-b"}, "runtime_instance_mismatch"),
        ({"compatibility_evidence_id": None}, {}, "compatibility_evidence_missing"),
        ({"compatibility_status": "stale"}, {}, "compatibility_evidence_stale"),
        ({"runtime_state": "candidate"}, {}, "runtime_not_accepted"),
    ],
)
def test_protocol_drift_reasons_are_explainable_and_read_only(desired, observed, reason):
    conn, repo, _, _ = _repo()
    before = conn.total_changes
    snapshot = classify_reconciliation(
        subject_id="device:7",
        desired=DesiredPeerState(
            peer_expected=True,
            peer_public_key="peer",
            allowed_ips=("10.212.12.8/32",),
            device_status="active",
            **desired,
        ),
        observed=ObservedPeerState(
            peer_present=True,
            peer_public_key="peer",
            allowed_ips=("10.212.12.8/32",),
            observation_succeeded=True,
            **observed,
        ),
        observed_at=NOW,
        now=NOW,
        stale_after=timedelta(minutes=5),
    )
    assert snapshot.drift_reason == reason
    assert conn.total_changes == before
```

- [ ] **Step 3: Run focused tests and verify RED**

```powershell
python -m pytest tests/services/test_device_passports.py tests/services/test_drift_diagnostics.py tests/web/test_device_passports.py tests/web/test_device_passport_views.py -q
```

- [ ] **Step 4: Extend immutable states and safe metadata**

Add nullable `protocol_version`, `runtime_instance_id`, `client_identity_evidence_status`, and `compatibility_evidence_id` to `DevicePassport`. Extend desired/observed state with safe protocol/runtime identity only:

```python
@dataclass(frozen=True)
class DesiredPeerState:
    peer_expected: bool | None
    peer_public_key: str | None
    allowed_ips: tuple[str, ...]
    device_status: str | None
    protocol_version: str | None = None
    runtime_instance_id: str | None = None
    compatibility_evidence_id: str | None = None
    compatibility_status: str | None = None
    runtime_state: str | None = None


@dataclass(frozen=True)
class ObservedPeerState:
    peer_present: bool | None
    peer_public_key: str | None
    allowed_ips: tuple[str, ...]
    observation_succeeded: bool
    protocol_version: str | None = None
    runtime_instance_id: str | None = None
```

Observed state may contain observed protocol/runtime IDs and safe peer fingerprints only. Classify `observation_failed`/stale observation first, then protocol mismatch, runtime mismatch, stale compatibility evidence, missing compatibility evidence, unaccepted runtime, and existing peer-state reasons in that deterministic order. Keep diagnostic services free of repository writes and auto-remediation.

- [ ] **Step 5: Verify rendered surfaces remain secret-safe and commit**

```powershell
python -m pytest tests/services/test_device_passports.py tests/services/test_drift_diagnostics.py tests/web/test_device_passports.py tests/web/test_device_passport_views.py -q
rg -n "PrivateKey|PresharedKey|HeaderProtectionKey|vpn://" app/web app/services tests/web tests/services
git diff --check
git add app/services/device_passports.py app/services/drift_diagnostics.py tests/services/test_device_passports.py tests/services/test_drift_diagnostics.py tests/web/test_device_passports.py tests/web/test_device_passport_views.py
git commit -m "Expose protocol evidence in Passport and Drift"
```

Treat every secret-scan match as a review item; tests may contain sentinels only when they assert the value is absent from output.

### Task 8: Preserve backup/restore compatibility for additive Phase 13 state

**Files:**
- Modify: `app/backup/service.py`
- Test: `tests/backup/test_backup_service.py`
- Test: `tests/db/test_phase13_protocol_schema.py`

**Interfaces:**
- Consumes: new tables and nullable references from Task 2.
- Produces: backup validation that accepts safe metadata, rejects dangling identities, and never exports raw secret values beyond the existing encrypted DB boundary.

- [ ] **Step 1: Write failing backup validation tests**

```python
def _seed_phase13_database(path):
    _create_database_with_encrypted_device(path)
    conn = connect(path)
    repo = Repository(conn)
    server_id = repo.ensure_default_server(name="local", network_cidr="10.8.0.0/24")
    for protocol, port, interface in (("awg2", 30001, "awg0"), ("awg3", 30002, "awg3")):
        repo.create_vpn_runtime_instance(
            runtime_instance_id=f"rt-local-{protocol}",
            server_id=server_id,
            protocol_version=protocol,
            runtime_version="test-runtime",
            interface_name=interface,
            udp_port=port,
            vpn_cidr=f"10.212.{12 if protocol == 'awg2' else 13}.0/24",
            container_name=f"amn2-{protocol}",
            service_name=None,
            config_path=f"/opt/amn2/{protocol}/wg0.conf",
            lifecycle_state="accepted",
            acceptance_receipt="sha256:" + protocol[-1] * 64,
        )
    for index in range(3):
        repo.create_client_compatibility_evidence(
            evidence_id=f"compat-test-{index}",
            application="amnezia_vpn",
            platform="windows",
            client_version=f"5.0.0.{5 + index}",
            protocol_version="awg3",
            source_kind="full_data",
            status="passed",
            observed_at="2026-08-01T00:00:00Z",
            safe_reference=f"receipt:test-{index}",
            scope="test exact build",
        )
    conn.close()
    return path


def test_backup_accepts_phase13_runtime_and_compatibility_rows(tmp_path):
    source = _seed_phase13_database(tmp_path / "source.db")
    service = BackupService(app_version="0.1.0")
    backup = service.create(source, tmp_path / "backups")
    restored = service.restore(backup, tmp_path / "restored.db")
    conn = connect(restored)
    assert conn.execute("SELECT count(*) FROM vpn_runtime_instances").fetchone()[0] == 2
    assert conn.execute("SELECT count(*) FROM client_compatibility_evidence").fetchone()[0] == 3
    conn.close()


def test_backup_rejects_dangling_runtime_or_evidence_reference(tmp_path):
    source = _seed_phase13_database(tmp_path / "source.db")
    conn = connect(source)
    conn.execute("PRAGMA foreign_keys = OFF")
    conn.execute("UPDATE devices SET runtime_instance_id = 'missing-runtime'")
    conn.commit()
    conn.close()
    service = BackupService(app_version="0.1.0")
    backup = service.create(source, tmp_path / "backups")
    with pytest.raises(ValueError, match="runtime_instance_id"):
        service.restore(backup, tmp_path / "restored.db")


def test_backup_receipt_contains_no_raw_awg3_secret(tmp_path):
    source = _seed_phase13_database(tmp_path / "source.db")
    service = BackupService(app_version="0.1.0")
    backup = service.create(source, tmp_path / "backups")
    manifest = service.verify(backup)
    assert "never-log-header-protection-key" not in json.dumps(manifest)
```

- [ ] **Step 2: Run backup tests and verify RED**

```powershell
python -m pytest tests/backup/test_backup_service.py tests/db/test_phase13_protocol_schema.py -q
```

- [ ] **Step 3: Add safe referential validation**

Validate:

```python
PHASE13_SAFE_TABLE_FIELDS = {
    "vpn_runtime_instances": {
        "runtime_instance_id", "server_id", "protocol_version", "runtime_version",
        "interface_name", "udp_port", "vpn_cidr", "container_name", "service_name",
        "config_path", "lifecycle_state", "acceptance_receipt",
    },
    "client_compatibility_evidence": {
        "evidence_id", "application", "platform", "client_version",
        "protocol_version", "source_kind", "status", "observed_at",
        "safe_reference", "scope",
    },
}
```

Check protocol enums, accepted-runtime receipts, and every non-null runtime/evidence reference. Do not add plaintext secret fields to manifest or receipt output.

- [ ] **Step 4: Verify restore round-trip and existing recovery regression**

```powershell
python -m pytest tests/backup/test_backup_service.py tests/db/test_phase13_protocol_schema.py tests/services/test_device_passports.py -q
```

- [ ] **Step 5: Commit**

```powershell
git diff --check
git add app/backup/service.py tests/backup/test_backup_service.py tests/db/test_phase13_protocol_schema.py
git commit -m "Validate Phase 13 state in backups"
```

### Task 9: Implement the pure USA retirement readiness notification gate

**Files:**
- Create: `app/services/usa_retirement_readiness.py`
- Create: `tests/services/test_usa_retirement_readiness.py`

**Interfaces:**
- Consumes: already collected secret-free evidence facts only.
- Produces: `UsaRetirementEvidence`, `UsaRetirementReadiness`, and `evaluate_usa_retirement_readiness()`; no shutdown or cleanup method.

- [ ] **Step 1: Write the complete missing-prerequisite matrix**

```python
from dataclasses import replace
from datetime import datetime, timedelta, timezone


NOT_READY = "USA ПОКА НЕЛЬЗЯ ОТКЛЮЧАТЬ: ROLLBACK CONTOUR ЕЩЁ НЕ ЗАМЕНЁН ИЛИ НЕ ПРИНЯТ"
READY = "USA МОЖНО БЕЗОПАСНО ОТКЛЮЧАТЬ И ПЕРЕПРОФИЛИРОВАТЬ ПОСЛЕ ОТДЕЛЬНОГО EXACT APPROVAL"
NOW = datetime(2026, 8, 15, 12, 0, tzinfo=timezone.utc)


def all_ready_evidence(**overrides) -> UsaRetirementEvidence:
    values = {
        "spain_baseline_equal": True,
        "required_devices_accepted": True,
        "unknown_client_facts_listed": True,
        "last_dataplane_mutation": NOW - timedelta(days=14),
        "critical_incident_since_mutation": False,
        "unexplained_drift_since_mutation": False,
        "encrypted_backup_verified": True,
        "backup_checksum_verified": True,
        "backup_secret_inventory_verified": True,
        "backup_retention_defined": True,
        "restore_inputs_documented": True,
        "independent_restore_rehearsed": True,
        "replacement_rollback_accepted": True,
        "no_failover_risk_acceptance_receipt": None,
        "usa_dependency_audit_clear": True,
        "retirement_plan_ready": True,
        "final_readonly_audit_completed": True,
    }
    values.update(overrides)
    return UsaRetirementEvidence(**values)


@pytest.mark.parametrize(
    "missing_field",
    [
        "spain_baseline_equal",
        "required_devices_accepted",
        "unknown_client_facts_listed",
        "encrypted_backup_verified",
        "backup_checksum_verified",
        "backup_secret_inventory_verified",
        "backup_retention_defined",
        "restore_inputs_documented",
        "independent_restore_rehearsed",
        "usa_dependency_audit_clear",
        "retirement_plan_ready",
        "final_readonly_audit_completed",
    ],
)
def test_each_stored_missing_prerequisite_keeps_usa_not_ready(missing_field):
    evidence = replace(all_ready_evidence(), **{missing_field: False})
    result = evaluate_usa_retirement_readiness(evidence, now=NOW)
    assert result.ready is False
    assert result.notification == NOT_READY
    assert missing_field in result.missing


def test_dataplane_mutation_resets_fourteen_day_window():
    evidence = replace(all_ready_evidence(), last_dataplane_mutation=NOW - timedelta(days=13, hours=23))
    result = evaluate_usa_retirement_readiness(evidence, now=NOW)
    assert result.ready is False
    assert "observation_window_complete" in result.missing


def test_missing_rollback_and_missing_risk_acceptance_keeps_usa_not_ready():
    result = evaluate_usa_retirement_readiness(
        all_ready_evidence(
            replacement_rollback_accepted=False,
            no_failover_risk_acceptance_receipt=None,
        ),
        now=NOW,
    )
    assert "rollback_contour_decision" in result.missing


def test_explicit_no_failover_risk_acceptance_can_replace_rollback_evidence():
    result = evaluate_usa_retirement_readiness(
        all_ready_evidence(
            replacement_rollback_accepted=False,
            no_failover_risk_acceptance_receipt="sha256:" + "d" * 64,
        ),
        now=NOW,
    )
    assert result.ready is True
    assert result.live_action_authorized is False


def test_ready_message_still_requires_separate_exact_approval():
    result = evaluate_usa_retirement_readiness(all_ready_evidence(), now=NOW)
    assert result.ready is True
    assert result.notification == READY
    assert result.live_action_authorized is False
```

- [ ] **Step 2: Run tests and verify RED**

```powershell
python -m pytest tests/services/test_usa_retirement_readiness.py -q
```

- [ ] **Step 3: Implement immutable evidence and result types**

```python
@dataclass(frozen=True)
class UsaRetirementEvidence:
    spain_baseline_equal: bool
    required_devices_accepted: bool
    unknown_client_facts_listed: bool
    last_dataplane_mutation: datetime
    critical_incident_since_mutation: bool
    unexplained_drift_since_mutation: bool
    encrypted_backup_verified: bool
    backup_checksum_verified: bool
    backup_secret_inventory_verified: bool
    backup_retention_defined: bool
    restore_inputs_documented: bool
    independent_restore_rehearsed: bool
    replacement_rollback_accepted: bool
    no_failover_risk_acceptance_receipt: str | None
    usa_dependency_audit_clear: bool
    retirement_plan_ready: bool
    final_readonly_audit_completed: bool

    def __post_init__(self) -> None:
        receipt = self.no_failover_risk_acceptance_receipt
        if receipt is not None and not re.fullmatch(r"sha256:[0-9a-f]{64}", receipt):
            raise ValueError("invalid no-failover risk acceptance receipt")


@dataclass(frozen=True)
class UsaRetirementReadiness:
    ready: bool
    missing: tuple[str, ...]
    notification: str
    live_action_authorized: bool = False
```

- [ ] **Step 4: Implement deterministic 14-day evaluation**

```python
def evaluate_usa_retirement_readiness(
    evidence: UsaRetirementEvidence, *, now: datetime
) -> UsaRetirementReadiness:
    window_complete = (
        now - evidence.last_dataplane_mutation >= timedelta(days=14)
        and not evidence.critical_incident_since_mutation
        and not evidence.unexplained_drift_since_mutation
    )
    rollback_contour_decision = (
        evidence.replacement_rollback_accepted
        or bool(evidence.no_failover_risk_acceptance_receipt)
    )
    checks = {
        "spain_baseline_equal": evidence.spain_baseline_equal,
        "required_devices_accepted": evidence.required_devices_accepted,
        "unknown_client_facts_listed": evidence.unknown_client_facts_listed,
        "observation_window_complete": window_complete,
        "encrypted_backup_verified": evidence.encrypted_backup_verified,
        "backup_checksum_verified": evidence.backup_checksum_verified,
        "backup_secret_inventory_verified": evidence.backup_secret_inventory_verified,
        "backup_retention_defined": evidence.backup_retention_defined,
        "restore_inputs_documented": evidence.restore_inputs_documented,
        "independent_restore_rehearsed": evidence.independent_restore_rehearsed,
        "rollback_contour_decision": rollback_contour_decision,
        "usa_dependency_audit_clear": evidence.usa_dependency_audit_clear,
        "retirement_plan_ready": evidence.retirement_plan_ready,
        "final_readonly_audit_completed": evidence.final_readonly_audit_completed,
    }
    missing = tuple(name for name, passed in checks.items() if not passed)
    return UsaRetirementReadiness(
        ready=not missing,
        missing=missing,
        notification=READY if not missing else NOT_READY,
    )
```

Do not add a callback, subprocess, provider API, SSH client, wipe routine, or remote command to this module.

- [ ] **Step 5: Verify and commit**

```powershell
python -m pytest tests/services/test_usa_retirement_readiness.py -q
git diff --check
git add app/services/usa_retirement_readiness.py tests/services/test_usa_retirement_readiness.py
git commit -m "Add USA retirement readiness evaluator"
```

### Task 10: Run full local regression, security review, and documentation gate

**Files:**
- Modify: `docs/PROJECT_STATUS_CURRENT.ru.md` in VPS-OPS-LAB only after AMN2 implementation review passes.
- Create: a Phase 13 local implementation receipt under `research/amn2/` containing only secret-free commit/test/diff evidence.
- Do not modify: `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md`.

**Interfaces:**
- Consumes: commits from Tasks 1-9.
- Produces: reviewed AMN2 source commit and a separate exact approval phrase for any checksum-bound package/preflight work.

- [ ] **Step 1: Run all focused Phase 13 tests**

```powershell
python -m pytest tests/vpn/test_protocol_versions.py tests/db/test_phase13_protocol_schema.py tests/services/test_vpn_runtime_instances.py tests/services/test_client_compatibility.py tests/services/test_protocol_admission.py tests/vpn/test_amneziawg_v3_config.py tests/services/test_admin_config_issuance.py tests/services/test_device_passports.py tests/services/test_drift_diagnostics.py tests/backup/test_backup_service.py tests/services/test_usa_retirement_readiness.py -q
```

Expected: all focused tests pass with no skipped Phase 13 acceptance row.

- [ ] **Step 2: Run the authoritative full suite**

```powershell
python -m pytest -q
```

Expected: zero failures. Record the exact passed/skipped counts; do not reuse Phase 12 counts.

- [ ] **Step 3: Run diff, secret, and security review**

```powershell
git diff 55dc243b8e6c6bdb57f8301b56326e4cd4072d19...HEAD --check
git diff --stat 55dc243b8e6c6bdb57f8301b56326e4cd4072d19...HEAD
rg -n "BEGIN .*PRIVATE KEY|PrivateKey\s*=|PresharedKey\s*=|HeaderProtectionKey\s*=|vpn://|password\s*=|token\s*=" app tests
```

Review every secret-pattern match and run `codex-security:security-diff-scan` against the exact AMN2 base/head diff. No finding may be waived merely because the work is local-only.

- [ ] **Step 4: Verify scope and preserve live boundaries**

Confirm from the diff and receipts:

```text
implementation_scope=local_only
live_spain_mutation=false
live_usa_mutation=false
awg2_restart_or_recreate=false
existing_d1_d7_reissued=false
foreign_spain_service_touched=false
public_or_bot_surface_enabled=false
quota_default_changed=false
```

If any line cannot be proven, stop before docs sync or push.

- [ ] **Step 5: Sync docs, commit, push, and prepare the next approval gate**

Write a secret-free implementation receipt with exact AMN2 base/head, test counts, security report path/hash, and remaining live gates. Update the first block of VPS-OPS-LAB `docs/PROJECT_STATUS_CURRENT.ru.md` to state that local implementation is reviewed but no package/live action is authorized.

Commit AMN2 and VPS-OPS-LAB changes separately, push each exact branch, fetch, and verify local HEAD equals origin. The next approval phrase must authorize only design/preparation of a checksum-bound isolated-runtime package and read-only Spain conflict/equality preflight; it must not authorize deploy, peer/config issuance, reboot, rollback rehearsal, or USA retirement.

## Self-Review Checklist

- [ ] Every design requirement in sections 1-13 maps to a task or is explicitly deferred to the later checksum-bound/live plan.
- [ ] No automatic d1-d7 reissue, key regeneration, peer recreation, or unknown client-version backfill exists.
- [ ] Existing legacy profiles remain readable; new legacy issuance is closed.
- [ ] Admission runs before any recipient, receipt, key, peer, or config mutation.
- [ ] AWG2 and AWG3 typed inputs/renderers cannot accept each other's fields.
- [ ] Raw `HeaderProtectionKey` cannot reach repr, logs, exceptions, Passport, Drift, receipts, or docs.
- [ ] Runtime port/interface/CIDR planning is deterministic and read-only.
- [ ] Passport/Drift additions remain privacy-safe and do not auto-remediate.
- [ ] Backup/restore validation covers the new tables and references.
- [ ] USA readiness is advisory only and always has `live_action_authorized=False`.
- [ ] Quota default stays `5`.
- [ ] Full suite, diff check, secret review, security diff scan, docs sync, commit, push, and origin readback are explicit gates.

## Explicitly Deferred Work

- Checksum-bound AWG3 server/runtime package contents and exact runtime binary/image provenance.
- Spain read-only capacity, port, interface, IPAM, Docker/systemd, AWG2 equality, and foreign-service preflight.
- Isolated AWG3 deployment, real-device import/handshake/full-data matrix, controlled reboot, rollback rehearsal, and production acceptance.
- Evidence-bound classification of actual Spain d1-d7 Passport rows after exact client application/platform/version collection.
- Recipient/plan-specific quota policy or a new default.
- USA shutdown, wipe, deletion, provider changes, or reuse.

These require later plans and separate exact approvals; completion of this local implementation plan does not authorize them.
