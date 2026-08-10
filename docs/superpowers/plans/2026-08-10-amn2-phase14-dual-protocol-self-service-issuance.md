# AMN2 Phase 14 Dual-Protocol Self-Service Issuance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Довести проверенный Phase 14 source HEAD до полноценной двойной модели AWG2/AWG3 с exact-build admission, глобальными gates, одним AWG2 и одним AWG3 profile на устройство, self-service выдачей и единым revoke/audit contract.

**Architecture:** Существующие `ClientIdentity`, `ProtocolAdmissionService`, `DevicePassport` и config-delivery сервисы остаются foundation. Additive schema добавляет exact build acceptance, global AWG3 control state, protocol profiles и append-only events. Новый orchestration layer проверяет control state до генерации секретов; bot/web являются тонкими presentation adapters.

**Tech Stack:** Python 3, SQLite, dataclasses/StrEnum, pytest, существующие AMN2 Repository/service/bot/FastAPI/Jinja boundaries.

## Global Constraints

- Выполнять только в изолированном worktree от exact HEAD `4547af1b23e4774822119f98004568c6eb039303`.
- До отдельного package gate не создавать package, manifest или preflight outcome.
- До отдельных live gates не выполнять SSH, config/QR/peer issuance, deploy, service/firewall/runtime/client mutation.
- AWG2 остаётся протоколом по умолчанию и не меняет golden bytes, runtime или lifecycle.
- AWG3 требует exact `platform + application + version + build`, stable release, свежие `local_import` и `full_data` evidence.
- Общая AWG3 issuance требует `GLOBAL_AWG3_ACCEPTED=true` и отдельного `ENABLE_AWG3_ISSUANCE=true`.
- После enable совместимому пользователю не требуется per-user admin approval.
- Incompatible/unknown AWG3 никогда не вызывает silent AWG2 fallback.
- Один device passport допускает не более одного активного AWG2 profile и одного активного AWG3 profile.
- USER block/disable затрагивает все configs пользователя; DEVICE disable — оба protocol profiles устройства; CONFIG revoke — только выбранный config.
- Config и QR не входят в logs/audit/status; доставка владельцу идёт двумя отдельными Telegram-сообщениями.
- Monitoring alerts не входят в этот plan.
- Каждый task: RED, минимальный GREEN, focused regressions, `git diff --check`, scoped secret/security review, отдельный local commit без push.

---

### Task 1: Add the additive dual-protocol persistence contract

**Files:**

- Create: `app/db/phase14_dual_protocol.py`
- Modify: `app/db/schema.py`
- Modify: `app/db/repositories.py`
- Create: `tests/db/test_phase14_dual_protocol_schema.py`
- Modify: `tests/db/test_schema.py`

**Interfaces:**

- Consumes: `initialize_schema(conn: sqlite3.Connection) -> None`.
- Produces Repository methods:
  - `get_awg3_control_state() -> sqlite3.Row`
  - `update_awg3_control_state(*, runtime_accepted: bool, global_accepted: bool, issuance_enabled: bool, emergency_suspended: bool, runtime_receipt: str | None, actor_id: int, reason: str) -> None`
  - `upsert_client_build_acceptance(*, application: str, platform: str, client_version: str, client_build: str, state: str, evidence_ids: tuple[str, ...], actor_id: int, reason: str) -> None`
  - `get_client_build_acceptance(*, application: str, platform: str, client_version: str, client_build: str) -> sqlite3.Row | None`
  - `create_device_protocol_profile(*, passport_device_id: str, protocol_version: str, local_device_id: int, lifecycle_state: str) -> int`
  - `get_device_protocol_profile(*, passport_device_id: str, protocol_version: str) -> sqlite3.Row | None`
  - `update_device_protocol_profile(*, profile_id: int, lifecycle_state: str, replacement_device_id: int | None) -> None`
  - `append_protocol_config_event(*, event_type: str, actor_kind: str, actor_id: int, reason: str, passport_device_id: str | None, protocol_version: str | None, local_device_id: int | None, metadata: dict[str, object]) -> int`

- [ ] **Step 1: Write the failing additive-schema tests**

Create `tests/db/test_phase14_dual_protocol_schema.py`:

```python
def test_phase14_schema_is_idempotent_and_additive(conn):
    initialize_schema(conn)
    initialize_schema(conn)
    tables = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    assert {
        "awg3_control_state",
        "client_build_acceptances",
        "device_protocol_profiles",
        "protocol_config_events",
    } <= tables
    columns = {
        row[1]
        for row in conn.execute("PRAGMA table_info(client_compatibility_evidence)")
    }
    assert {"client_build", "release_kind"} <= columns


def test_one_protocol_profile_per_passport_is_enforced(conn):
    seed_user_server_device_and_passport(conn)
    conn.execute(
        "INSERT INTO device_protocol_profiles"
        "(passport_device_id, protocol_version, local_device_id, lifecycle_state)"
        " VALUES ('device-1', 'awg3', 1, 'active')"
    )
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO device_protocol_profiles"
            "(passport_device_id, protocol_version, local_device_id, lifecycle_state)"
            " VALUES ('device-1', 'awg3', 2, 'active')"
        )
```

- [ ] **Step 2: Run RED**

Run:

```powershell
python -m pytest -q tests/db/test_phase14_dual_protocol_schema.py tests/db/test_schema.py
```

Expected: FAIL because the four Phase 14 tables and exact build columns do not exist.

- [ ] **Step 3: Implement the additive schema helper**

Create `app/db/phase14_dual_protocol.py` with `ensure_phase14_dual_protocol_schema(conn)`. It must add missing columns by inspecting `PRAGMA table_info` and then execute these closed tables:

```python
def ensure_phase14_dual_protocol_schema(conn: sqlite3.Connection) -> None:
    columns = {
        str(row[1])
        for row in conn.execute("PRAGMA table_info(client_compatibility_evidence)")
    }
    if "client_build" not in columns:
        conn.execute(
            "ALTER TABLE client_compatibility_evidence "
            "ADD COLUMN client_build TEXT"
        )
    if "release_kind" not in columns:
        conn.execute(
            "ALTER TABLE client_compatibility_evidence "
            "ADD COLUMN release_kind TEXT "
            "CHECK (release_kind IS NULL OR release_kind IN "
            "('stable','prerelease','unreleased'))"
        )
    conn.executescript(PHASE14_DUAL_PROTOCOL_SQL)
```

`PHASE14_DUAL_PROTOCOL_SQL` must define:

```sql
CREATE TABLE IF NOT EXISTS awg3_control_state (
    singleton_id INTEGER PRIMARY KEY CHECK (singleton_id = 1),
    runtime_accepted INTEGER NOT NULL DEFAULT 0 CHECK (runtime_accepted IN (0,1)),
    global_accepted INTEGER NOT NULL DEFAULT 0 CHECK (global_accepted IN (0,1)),
    issuance_enabled INTEGER NOT NULL DEFAULT 0 CHECK (issuance_enabled IN (0,1)),
    emergency_suspended INTEGER NOT NULL DEFAULT 0 CHECK (emergency_suspended IN (0,1)),
    runtime_receipt TEXT,
    actor_id INTEGER,
    reason TEXT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (issuance_enabled = 0 OR (global_accepted = 1 AND emergency_suspended = 0))
);
INSERT OR IGNORE INTO awg3_control_state(singleton_id) VALUES (1);

CREATE TABLE IF NOT EXISTS client_build_acceptances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application TEXT NOT NULL,
    platform TEXT NOT NULL,
    client_version TEXT NOT NULL,
    client_build TEXT NOT NULL,
    protocol_version TEXT NOT NULL DEFAULT 'awg3' CHECK (protocol_version = 'awg3'),
    state TEXT NOT NULL CHECK (state IN (
        'candidate','accepted','superseded',
        'compatibility_rejected','security_revoked'
    )),
    evidence_ids_json TEXT NOT NULL,
    actor_id INTEGER NOT NULL,
    reason TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(application, platform, client_version, client_build, protocol_version)
);

CREATE TABLE IF NOT EXISTS device_protocol_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    passport_device_id TEXT NOT NULL,
    protocol_version TEXT NOT NULL CHECK (protocol_version IN ('awg2','awg3')),
    local_device_id INTEGER NOT NULL UNIQUE,
    lifecycle_state TEXT NOT NULL CHECK (lifecycle_state IN (
        'active','pending_replacement','review_required',
        'temporarily_unavailable','revoked'
    )),
    replacement_device_id INTEGER,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(passport_device_id, protocol_version),
    FOREIGN KEY(passport_device_id) REFERENCES device_passports(device_id),
    FOREIGN KEY(local_device_id) REFERENCES devices(id),
    FOREIGN KEY(replacement_device_id) REFERENCES devices(id)
);

CREATE TABLE IF NOT EXISTS protocol_config_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    actor_kind TEXT NOT NULL CHECK (actor_kind IN ('user','admin','system')),
    actor_id INTEGER NOT NULL,
    reason TEXT NOT NULL,
    passport_device_id TEXT,
    protocol_version TEXT CHECK (protocol_version IS NULL OR protocol_version IN ('awg2','awg3')),
    local_device_id INTEGER,
    metadata_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

Call `ensure_phase14_dual_protocol_schema(conn)` at the end of `initialize_schema` and add the exact Repository methods listed in Interfaces. JSON writes use `sort_keys=True` and compact separators.

- [ ] **Step 4: Run GREEN**

```powershell
python -m pytest -q tests/db/test_phase14_dual_protocol_schema.py tests/db/test_phase14_source_integration.py tests/db/test_phase13_protocol_schema.py tests/db/test_schema.py
git diff --check
```

Expected: all pass; existing schema initialisation remains idempotent.

- [ ] **Step 5: Commit**

```powershell
git add app/db/phase14_dual_protocol.py app/db/schema.py app/db/repositories.py tests/db/test_phase14_dual_protocol_schema.py tests/db/test_schema.py
git diff --cached --check
git commit -m "feat: add Phase 14 dual protocol state"
```

### Task 2: Implement global AWG3 acceptance and issuance gates

**Files:**

- Create: `app/services/awg3_control.py`
- Create: `tests/services/test_awg3_control.py`
- Modify: `app/services/protocol_admission.py`
- Modify: `tests/services/test_protocol_admission.py`

**Interfaces:**

- Consumes: Task 1 Repository methods and existing `ProtocolAdmissionService.decide`.
- Produces:
  - `Awg3ControlState`
  - `Awg3ControlService.accept_runtime`
  - `Awg3ControlService.accept_build`
  - `Awg3ControlService.set_issuance_enabled`
  - `Awg3ControlService.emergency_suspend`
  - `Awg3ControlService.resume_after_preflight`
  - new admission decisions `blocked_global_acceptance`, `blocked_issuance_disabled`, `blocked_runtime_suspended`.

- [ ] **Step 1: Write gate-order RED tests**

```python
@pytest.mark.parametrize(
    ("runtime", "build", "enabled", "suspended", "decision"),
    [
        (False, False, False, False, "blocked_global_acceptance"),
        (True, False, False, False, "blocked_global_acceptance"),
        (True, True, False, False, "blocked_issuance_disabled"),
        (True, True, True, True, "blocked_runtime_suspended"),
        (True, True, True, False, "admitted_awg3"),
    ],
)
def test_awg3_gate_order(runtime, build, enabled, suspended, decision):
    result = decide_exact_awg3(runtime, build, enabled, suspended)
    assert result.decision == decision
```

Add a regression proving AWG2 admission does not read or mutate `awg3_control_state`.

- [ ] **Step 2: Run RED**

```powershell
python -m pytest -q tests/services/test_awg3_control.py tests/services/test_protocol_admission.py
```

Expected: FAIL because global acceptance and issuance switch are not represented.

- [ ] **Step 3: Implement the control service**

Create these closed types:

```python
class ClientBuildState(StrEnum):
    CANDIDATE = "candidate"
    ACCEPTED = "accepted"
    SUPERSEDED = "superseded"
    COMPATIBILITY_REJECTED = "compatibility_rejected"
    SECURITY_REVOKED = "security_revoked"


@dataclass(frozen=True)
class Awg3ControlState:
    runtime_accepted: bool
    global_accepted: bool
    issuance_enabled: bool
    emergency_suspended: bool
    runtime_receipt: str | None

    @property
    def permits_new_issuance(self) -> bool:
        return (
            self.runtime_accepted
            and self.global_accepted
            and self.issuance_enabled
            and not self.emergency_suspended
        )
```

`accept_build` must call `classify_awg3_compatibility` and accept only `ACCEPTED` with the three current evidence kinds. `set_issuance_enabled(True)` must fail unless runtime and at least one exact build are accepted. `emergency_suspend` must set suspended and issuance false. `resume_after_preflight` requires a fresh receipt formatted `sha256:<64 lowercase hex>` and does not enable issuance.

Inject `Awg3ControlState` and exact build acceptance into `ProtocolAdmissionService`. Check gates before returning `admitted_awg3` and after pure evidence classification; AWG2 behavior remains unchanged.

- [ ] **Step 4: Run GREEN and exact-evidence regressions**

```powershell
python -m pytest -q tests/services/test_awg3_control.py tests/services/test_protocol_admission.py tests/services/test_phase14_awg3_client_admission.py tests/services/test_client_compatibility.py
git diff --check
```

- [ ] **Step 5: Commit**

```powershell
git add app/services/awg3_control.py app/services/protocol_admission.py tests/services/test_awg3_control.py tests/services/test_protocol_admission.py
git diff --cached --check
git commit -m "feat: gate AWG3 issuance globally"
```

### Task 3: Model one AWG2 and one AWG3 profile per device passport

**Files:**

- Create: `app/services/dual_protocol_profiles.py`
- Create: `tests/services/test_dual_protocol_profiles.py`
- Modify: `app/services/device_passports.py`
- Modify: `tests/services/test_device_passports.py`

**Interfaces:**

- Consumes: Task 1 profile Repository methods.
- Produces:
  - `ProtocolProfile`
  - `DualProtocolProfileService.attach_active`
  - `DualProtocolProfileService.start_replacement`
  - `DualProtocolProfileService.activate_replacement`
  - `DualProtocolProfileService.compromise_reissue`
  - `DualProtocolProfileService.mark_review_required`
  - `DualProtocolProfileService.mark_temporarily_unavailable`.

- [ ] **Step 1: Write RED profile and replacement tests**

```python
def test_one_passport_can_hold_one_active_profile_per_protocol(service):
    awg2 = service.attach_active("device-1", ProtocolVersion.AWG2, 11)
    awg3 = service.attach_active("device-1", ProtocolVersion.AWG3, 12)
    assert (awg2.local_device_id, awg3.local_device_id) == (11, 12)
    with pytest.raises(ValueError, match="active awg3 profile already exists"):
        service.attach_active("device-1", ProtocolVersion.AWG3, 13)


def test_normal_replacement_keeps_old_active_until_activation(service):
    old = service.attach_active("device-1", ProtocolVersion.AWG3, 12)
    pending = service.start_replacement(old.profile_id, replacement_device_id=13)
    assert pending.lifecycle_state == "pending_replacement"
    activated = service.activate_replacement(old.profile_id)
    assert activated.local_device_id == 13
    assert service.by_local_device_id(12).lifecycle_state == "revoked"


def test_compromise_reissue_revokes_old_before_new_issue(service, issuer):
    old = service.attach_active("device-1", ProtocolVersion.AWG3, 12)
    result = service.compromise_reissue(
        old.profile_id,
        replacement_factory=issuer.issue_device,
        actor_id=700,
        reason="suspected config leak",
    )
    assert service.by_local_device_id(12).lifecycle_state == "revoked"
    assert result.protocol_version is ProtocolVersion.AWG3
    assert issuer.events[:2] == ["old_revoked", "replacement_issued"]
```

- [ ] **Step 2: Run RED**

```powershell
python -m pytest -q tests/services/test_dual_protocol_profiles.py tests/services/test_device_passports.py
```

- [ ] **Step 3: Implement the profile service**

```python
@dataclass(frozen=True)
class ProtocolProfile:
    profile_id: int
    passport_device_id: str
    protocol_version: ProtocolVersion
    local_device_id: int
    lifecycle_state: str
    replacement_device_id: int | None
```

All state transitions run inside `repo.transaction()` and append one `protocol_config_events` row. `start_replacement` rejects a second pending replacement. `activate_replacement` changes only the selected protocol. `compromise_reissue` commits old-config revoke before calling the replacement factory; a replacement failure leaves the old config revoked and records `compromise_reissue_failed` without restoring it. Extend `DevicePassport.safe_metadata()` with a sorted `protocol_profiles` list; do not replace its legacy fields until all consumers migrate.

- [ ] **Step 4: Run GREEN**

```powershell
python -m pytest -q tests/services/test_dual_protocol_profiles.py tests/services/test_device_passports.py tests/web/test_device_passports.py
git diff --check
```

- [ ] **Step 5: Commit**

```powershell
git add app/services/dual_protocol_profiles.py app/services/device_passports.py tests/services/test_dual_protocol_profiles.py tests/services/test_device_passports.py
git diff --cached --check
git commit -m "feat: add per-device protocol profiles"
```

### Task 4: Add fail-closed self-service issuance orchestration

**Files:**

- Create: `app/services/self_service_issuance.py`
- Create: `tests/services/test_self_service_issuance.py`
- Modify: `app/services/admin_config_issuance.py`
- Modify: `tests/services/test_admin_config_issuance.py`

**Interfaces:**

- Consumes: `ProtocolAdmissionService`, `Awg3ControlService`, `DualProtocolProfileService` and existing config creator.
- Produces:
  - `SelfServiceIssuanceRequest`
  - `SelfServiceIssuanceResult`
  - `SelfServiceIssuanceService.decide`
  - `SelfServiceIssuanceService.issue_after_confirmation`.
  - `SelfServiceIssuanceService.issue_admin_pilot`.

- [ ] **Step 1: Write RED issuance tests**

```python
def test_compatible_awg3_issues_without_per_user_admin_approval(service):
    request = accepted_awg3_request(user_id=7, passport_device_id="device-1")
    decision = service.decide(request)
    assert decision.status == "confirmation_required"
    result = service.issue_after_confirmation(request, confirmation_token=decision.token)
    assert result.status == "issued"
    assert result.protocol_version is ProtocolVersion.AWG3


def test_incompatible_awg3_only_offers_awg2(service):
    result = service.decide(unknown_build_request())
    assert result.status == "blocked"
    assert result.offer_awg2 is True
    assert result.issued_device_id is None
    assert service.issuer.calls == []


def test_admin_pilot_allows_one_test_profile_without_general_enable(service):
    result = service.issue_admin_pilot(
        admin_telegram_id=700,
        request=accepted_candidate_awg3_request(
            user_id=7,
            passport_device_id="pilot-device-1",
        ),
    )
    assert result.status == "issued"
    assert result.reason_code == "admin_pilot"
    with pytest.raises(ValueError, match="pilot profile already exists"):
        service.issue_admin_pilot(
            admin_telegram_id=700,
            request=accepted_candidate_awg3_request(
                user_id=7,
                passport_device_id="pilot-device-1",
            ),
        )
```

Also prove secret generation is not called before all admission/gate/profile checks pass.

- [ ] **Step 2: Run RED**

```powershell
python -m pytest -q tests/services/test_self_service_issuance.py
```

- [ ] **Step 3: Implement the orchestrator**

```python
@dataclass(frozen=True)
class SelfServiceIssuanceRequest:
    user_id: int
    telegram_id: int
    passport_device_id: str
    protocol_version: ProtocolVersion
    client: ClientIdentity


@dataclass(frozen=True)
class SelfServiceIssuanceResult:
    status: Literal["confirmation_required", "issued", "blocked"]
    protocol_version: ProtocolVersion
    reason_code: str
    offer_awg2: bool
    issued_device_id: int | None
    token: str | None
```

`decide` validates owner/user/device/profile/admission in that order and returns a short-lived, request-bound confirmation token without secrets. `issue_after_confirmation` rechecks all conditions, calls the issuer once, attaches the profile and appends an event. AWG2 fallback requires a new request with `ProtocolVersion.AWG2`.

`issue_admin_pilot` requires a configured bot admin, the single configured pilot user/device identity and an exact candidate build with fresh evidence. It bypasses only general acceptance/issuance flags, never evidence or runtime-candidate checks, permits one AWG3 pilot profile and appends `admin_pilot_issued`. It does not change global control state.

Add `client_build` to `IssuanceManifestItem`, `ExpandedIssuanceSlot` and safe receipts. AWG3 admin/pilot issuance must supply it; AWG2 may preserve existing legacy inputs.

- [ ] **Step 4: Run GREEN and issuance regressions**

```powershell
python -m pytest -q tests/services/test_self_service_issuance.py tests/services/test_admin_config_issuance.py tests/cli/test_admin_config_issuance.py tests/services/test_protocol_admission.py
git diff --check
```

- [ ] **Step 5: Commit**

```powershell
git add app/services/self_service_issuance.py app/services/admin_config_issuance.py tests/services/test_self_service_issuance.py tests/services/test_admin_config_issuance.py
git diff --cached --check
git commit -m "feat: add fail closed self service issuance"
```

### Task 5: Expose the simple Telegram and admin/web flows

**Files:**

- Modify: `app/bot/workflows.py`
- Modify: `app/bot/handlers.py`
- Modify: `app/bot/delivery.py`
- Modify: `app/bot/texts.py`
- Modify: `tests/bot/test_bot_workflows.py`
- Modify: `tests/bot/test_bot_handlers.py`
- Modify: `tests/bot/test_delivery.py`
- Modify: `app/web/device_passports.py`
- Modify: `app/web/templates/device_passport_detail.html`
- Modify: `app/web/app.py`
- Modify: `tests/web/test_device_passport_views.py`
- Modify: `tests/web/test_device_passports.py`

**Interfaces:**

- Consumes: Task 4 self-service service and Task 3 passport metadata.
- Produces bot callbacks `awg3:select:<passport>:<build-id>`, `awg3:confirm:<token>` and admin control/view actions.

- [ ] **Step 1: Write RED bot delivery and ownership tests**

```python
async def test_awg3_delivery_is_private_owner_only_and_two_messages(fake_bot, workflow):
    callback = callback_from_private_chat(user_id=700, data="awg3:confirm:token-1")
    await handle_awg3_confirm(callback, workflow=workflow)
    assert [call.kind for call in fake_bot.calls] == ["document", "photo"]
    assert all(call.chat_id == 700 for call in fake_bot.calls)


async def test_awg3_delivery_rejects_group_or_wrong_owner(fake_bot, workflow):
    callback = callback_from_group(user_id=701, data="awg3:confirm:token-1")
    await handle_awg3_confirm(callback, workflow=workflow)
    assert fake_bot.secret_media_calls == []


async def test_delivery_does_not_schedule_message_deletion(fake_bot, workflow):
    callback = callback_from_private_chat(user_id=700, data="awg3:confirm:token-1")
    await handle_awg3_confirm(callback, workflow=workflow)
    assert fake_bot.delete_message_calls == []
```

Add view tests proving one card renders separate AWG2/AWG3 states and admin details include exact build/evidence while user text does not.

- [ ] **Step 2: Run RED**

```powershell
python -m pytest -q tests/bot/test_bot_workflows.py tests/bot/test_bot_handlers.py tests/bot/test_delivery.py tests/web/test_device_passport_views.py tests/web/test_device_passports.py
```

- [ ] **Step 3: Implement presentation adapters**

Add `BotWorkflow.list_awg3_client_choices`, `request_awg3` and `confirm_awg3`. Handler parsing must reject malformed callback IDs and non-private chat before loading secret material.

Reuse `ConfigDeliveryPackage` and keep the send order exact:

```python
async def _send_awg3_delivery(bot, *, chat_id: int, delivery: ConfigDeliveryPackage) -> None:
    await bot.send_document(
        chat_id=chat_id,
        document=BufferedInputFile(
            delivery.config_bytes,
            filename=delivery.config_filename,
        ),
        caption=delivery.config_caption,
    )
    await bot.send_photo(
        chat_id=chat_id,
        photo=BufferedInputFile(
            delivery.qr_png_bytes,
            filename=delivery.qr_filename,
        ),
        caption=delivery.qr_caption,
    )
```

Web/device passport detail renders protocol, runtime, client build, lifecycle and evidence references for admins. Opening raw config/QR uses the existing authenticated admin boundary and appends `config_secret_viewed` before returning; the audit payload contains IDs only.

- [ ] **Step 4: Run GREEN and secret-boundary regressions**

```powershell
python -m pytest -q tests/bot/test_bot_workflows.py tests/bot/test_bot_handlers.py tests/bot/test_delivery.py tests/web/test_device_passport_views.py tests/web/test_device_passports.py tests/security/test_redaction.py
git diff --check
```

- [ ] **Step 5: Commit**

```powershell
git add app/bot/workflows.py app/bot/handlers.py app/bot/delivery.py app/bot/texts.py tests/bot/test_bot_workflows.py tests/bot/test_bot_handlers.py tests/bot/test_delivery.py app/web/device_passports.py app/web/templates/device_passport_detail.html app/web/app.py tests/web/test_device_passport_views.py tests/web/test_device_passports.py
git diff --cached --check
git commit -m "feat: expose dual protocol bot and admin flows"
```

### Task 6: Enforce cascade revoke, build-state and emergency projections

**Files:**

- Create: `app/services/protocol_config_lifecycle.py`
- Create: `tests/services/test_protocol_config_lifecycle.py`
- Modify: `app/services/device_revoke.py`
- Modify: `tests/services/test_device_revoke.py`
- Modify: `app/web/app.py`
- Modify: `tests/web/test_users.py`

**Interfaces:**

- Consumes: Task 1 events/profiles, Task 2 build/control state and existing remote-first revoke plan.
- Produces `ProtocolConfigLifecycleService` methods `apply_build_state`, `disable_device`, `disable_user`, `revoke_config` and `project_emergency_suspend`.

- [ ] **Step 1: Write RED cascade tests**

```python
def test_user_disable_targets_every_protocol_profile(lifecycle):
    result = lifecycle.disable_user(user_id=7, actor_id=1, reason="operator block")
    assert {(item.passport_device_id, item.protocol_version.value) for item in result} == {
        ("device-1", "awg2"),
        ("device-1", "awg3"),
        ("device-2", "awg2"),
    }


def test_security_revoked_build_never_mass_revokes(lifecycle):
    result = lifecycle.apply_build_state(exact_build(), "security_revoked")
    assert result.new_issuance_allowed is False
    assert result.configs_revoked == 0
    assert result.emergency_proposal_required is True
```

Add checks for `superseded`, `compatibility_rejected -> review_required` and emergency `temporarily_unavailable`.

- [ ] **Step 2: Run RED**

```powershell
python -m pytest -q tests/services/test_protocol_config_lifecycle.py tests/services/test_device_revoke.py tests/web/test_users.py
```

- [ ] **Step 3: Implement lifecycle projections**

```python
BUILD_STATE_EFFECTS = {
    "superseded": ("continue", "offer_update"),
    "compatibility_rejected": ("review_required", "no_auto_revoke"),
    "security_revoked": ("continue", "emergency_proposal_required"),
}
```

USER/DEVICE cascades enumerate all linked protocol profiles and build exact remote-first operation plans. CONFIG revoke targets one `local_device_id`. Emergency projection changes only AWG3 profile state and never deletes rows, keys or configs. Preserve existing partial-failure recovery semantics in `device_revoke.py`.

- [ ] **Step 4: Run GREEN**

```powershell
python -m pytest -q tests/services/test_protocol_config_lifecycle.py tests/services/test_device_revoke.py tests/services/test_device_lifecycle.py tests/web/test_users.py
git diff --check
```

- [ ] **Step 5: Commit**

```powershell
git add app/services/protocol_config_lifecycle.py app/services/device_revoke.py tests/services/test_protocol_config_lifecycle.py tests/services/test_device_revoke.py app/web/app.py tests/web/test_users.py
git diff --cached --check
git commit -m "feat: enforce dual protocol lifecycle cascades"
```

### Task 7: Verify the application stage candidate and produce a local receipt

**Files:**

- Create: `research/amn2/phase14-dual-protocol-application-readiness-receipt.md`

**Interfaces:**

- Consumes all previous tasks.
- Produces a secret-free local readiness receipt; it does not produce a package or live approval.

- [ ] **Step 1: Run the focused integrated suite**

```powershell
python -m pytest -q tests/db/test_phase14_dual_protocol_schema.py tests/services/test_awg3_control.py tests/services/test_dual_protocol_profiles.py tests/services/test_self_service_issuance.py tests/services/test_protocol_config_lifecycle.py tests/bot/test_bot_workflows.py tests/bot/test_bot_handlers.py tests/bot/test_delivery.py tests/web/test_device_passport_views.py tests/web/test_device_passports.py tests/services/test_protocol_admission.py tests/services/test_phase14_awg3_client_admission.py
```

Expected: all pass.

- [ ] **Step 2: Run the full source suite**

```powershell
python -m pytest -q
```

Expected: no new failures; record exact counts.

- [ ] **Step 3: Review exact source diff**

```powershell
git diff --check
git status --short --branch
git log --oneline --decorate -12
```

Manually confirm: no raw config/key/QR in tests or logs, no AWG2 golden/runtime changes, no monitoring code, no package/preflight/live scripts.

- [ ] **Step 4: Write and commit the receipt**

The receipt records exact HEAD, parent `4547af1b23e4774822119f98004568c6eb039303`, task commits, focused/full results and these booleans:

```text
AWG2_DEFAULT_PRESERVED=true
AWG3_GLOBAL_ACCEPTANCE_REQUIRED=true
AWG3_PER_USER_ADMIN_APPROVAL_REQUIRED=false
AWG3_ISSUANCE_ENABLED=false
PACKAGE_MATERIALIZED=false
PREFLIGHT_RUN=false
SSH_USED=false
LIVE_MUTATION=false
```

```powershell
git add research/amn2/phase14-dual-protocol-application-readiness-receipt.md
git diff --cached --check
git commit -m "docs: record dual protocol application readiness"
```

- [ ] **Step 5: Stop before package work**

Output exact application HEAD and receipt SHA-256. Do not execute the package/preflight plan without a separate `PACKAGE_TOOLING_IMPLEMENTATION` approval.
