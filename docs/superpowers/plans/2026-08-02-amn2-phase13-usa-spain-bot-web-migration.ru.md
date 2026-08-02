# AMN2 Phase 13: USA → Spain bot/web migration — TDD implementation plan

> **Для agentic workers:** REQUIRED SUB-SKILL: использовать
> `superpowers:subagent-driven-development` (рекомендуется) либо
> `superpowers:executing-plans`; выполнять task-by-task, каждый Task требует
> отдельного approval и commit. Шаги используют checkbox `- [ ]`.

**Goal:** создать local-only, fail-closed tooling для read-only audit,
encrypted backup package, deterministic logical DB merge preview, disabled
Spain stage и two-host single-instance bot cutover без выполнения live gates.

**Architecture:** root VPS-OPS-LAB хранит checksum-bound collectors, package
schemas и SSH orchestration; новый изолированный AMN2 worktree от exact source
`55dc243b8e6c6bdb57f8301b56326e4cd4072d19` получает только pure migration
preview/apply-to-copy logic. Live database, env и services не используются в
Tasks 1–8; все remote/process tests работают через temporary fake harness.

**Tech Stack:** Python stdlib 3.11+, SQLite, JSON Schema, Bash, PowerShell,
pytest; существующие AMN2 `Repository`, `BackupService`, external-only device
contract и Phase 10 recovery-bundle primitives.

## Global Constraints

- Authoritative source: `55dc243b8e6c6bdb57f8301b56326e4cd4072d19`.
- USA overlay `0b858c5cdbc5b565cc265966a2edfe2d339d65e0` является предком source; source
  copy/downgrade запрещены.
- Spain web остаётся только `127.0.0.1:3031`.
- Spain bot при staging inactive и disabled marker absent.
- USA и Spain bot никогда не active одновременно.
- Spain `APP_SECRET_KEY`, web password hash и session secret сохраняются.
- Existing USA bot token и два allowlisted admin identifiers передаются только
  внутри encrypted payload.
- USA API tokens, sessions, device private keys/PSK/configs и recovery tokens
  не оживляются.
- Spain d1–d7, passports, issuance receipts, AWG2 runtime и foreign service не
  меняются.
- `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` не изменять и не добавлять в Git.
- Tasks 1–8: no package build from live inputs, no SSH, no deploy, no issuance,
  no reboot и no live Spain/USA/AWG mutation.

## File map

- `packaging/phase13-bot-web-migration/*.schema.json` — strict canonical
  schemas audit/plan/manifest/failure.
- `scripts/phase13_bot_web_migration_contract.py` — canonical JSON,
  checksums, manifest и offline verify.
- `scripts/vps/phase13_bot_web_migration_readonly_remote.py` — read-only
  aggregate collector.
- `scripts/vps/phase13_bot_web_migration_ssh_runner.ps1` — private trust,
  claim-before-network и bounded two-target transport.
- `app/migration/bot_web.py` — pure preview и apply-to-copy implementation в
  изолированном AMN2 worktree.
- `scripts/phase13_bot_web_migration_package.py` — encrypted bundle wrapper и
  package materialization только из supplied local fixture bytes.
- `scripts/vps/phase13_bot_web_migration_stage_remote.sh` — future disabled
  stage executor; local fake harness only.
- `scripts/vps/phase13_bot_web_migration_cutover_remote.sh` — future two-host
  cutover state machine; local fake harness only.

---

### Task 1: Strict evidence и manifest schemas

**Files:**

- Create: `packaging/phase13-bot-web-migration/audit-evidence.schema.json`
- Create: `packaging/phase13-bot-web-migration/migration-plan.schema.json`
- Create: `packaging/phase13-bot-web-migration/manifest.schema.json`
- Create: `packaging/phase13-bot-web-migration/failure-evidence.schema.json`
- Create: `tests/test_phase13_bot_web_migration_contract.py`

**Interfaces:**

- Produces schemas `amn2.phase13.bot-web-audit.v1`,
  `amn2.phase13.bot-web-migration-plan.v1`,
  `amn2.phase13.bot-web-migration-manifest.v1` и
  `amn2.phase13.bot-web-migration-failure.v1`.
- Все schemas используют `additionalProperties: false` и lowercase SHA-256
  pattern `^[0-9a-f]{64}$`.

- [ ] **Step 1: написать RED tests strict contract**

```python
def test_audit_schema_rejects_raw_secret_and_identifier_fields():
    payload = valid_audit_payload()
    payload["telegram_bot_token"] = "forbidden"
    with pytest.raises(ContractError):
        validate_audit(payload)


def test_manifest_requires_every_bound_artifact_sha256():
    payload = valid_manifest()
    del payload["artifacts"]["merged_target_db"]
    with pytest.raises(ContractError):
        validate_manifest(payload)
```

- [ ] **Step 2: запустить RED**

Run:

```text
python -m pytest tests/test_phase13_bot_web_migration_contract.py -q
```

Expected: collection/import failure, потому что schemas и validator отсутствуют.

- [ ] **Step 3: добавить strict schemas**

Audit schema содержит только role, checked_at, service states, listener
booleans, DB integrity/counts/schema hash, env presence booleans, required
artifact booleans и safety receipt. Manifest содержит exact artifact name,
byte length, SHA-256, outcome ID, expires_at, source/target evidence SHA-256 и
`live_mutation_authorized=false`.

- [ ] **Step 4: запустить GREEN и schema consistency**

```text
python -m pytest tests/test_phase13_bot_web_migration_contract.py -q
python -m json.tool packaging/phase13-bot-web-migration/audit-evidence.schema.json
python -m json.tool packaging/phase13-bot-web-migration/migration-plan.schema.json
python -m json.tool packaging/phase13-bot-web-migration/manifest.schema.json
python -m json.tool packaging/phase13-bot-web-migration/failure-evidence.schema.json
```

- [ ] **Step 5: commit**

```text
git add packaging/phase13-bot-web-migration tests/test_phase13_bot_web_migration_contract.py
git commit -m "Define Phase 13 bot web migration contracts"
```

### Task 2: Canonical manifest/verify tooling

**Files:**

- Create: `scripts/phase13_bot_web_migration_contract.py`
- Modify: `tests/test_phase13_bot_web_migration_contract.py`

**Interfaces:**

- `canonical_json_bytes(value: Mapping[str, object]) -> bytes`
- `sha256_file(path: Path) -> str`
- `build_manifest(root: Path, plan: Mapping[str, object], *, outcome_id: str,
  expires_at: datetime) -> Mapping[str, object]`
- `verify_local(root: Path, manifest: Mapping[str, object], *, now: datetime)
  -> Mapping[str, object]`

- [ ] **Step 1: RED для canonical bytes, traversal и expiry**

```python
def test_verify_local_rejects_symlink_and_path_traversal(tmp_path):
    manifest = manifest_with_artifact("../outside")
    with pytest.raises(ContractError, match="artifact path"):
        verify_local(tmp_path, manifest, now=NOW)


def test_verify_local_rejects_expired_manifest_before_artifact_read(tmp_path):
    with pytest.raises(ContractError, match="expired"):
        verify_local(tmp_path, expired_manifest(), now=NOW)
```

- [ ] **Step 2: RED run**

```text
python -m pytest tests/test_phase13_bot_web_migration_contract.py -q
```

- [ ] **Step 3: minimal stdlib-only implementation**

```python
def canonical_json_bytes(value):
    return (json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ) + "\n").encode("utf-8")
```

`verify_local()` сначала проверяет schema/outcome/expiry, затем no-follow root,
exact artifact set, regular files, sizes и checksums. Outcome и manifest
создаются `CreateNew`; replay/partial root fail closed.

- [ ] **Step 4: GREEN**

```text
python -m pytest tests/test_phase13_bot_web_migration_contract.py -q
```

- [ ] **Step 5: commit**

```text
git add scripts/phase13_bot_web_migration_contract.py tests/test_phase13_bot_web_migration_contract.py
git commit -m "Add canonical bot web migration manifest verifier"
```

### Task 3: Read-only two-server collector и secret-reference proof

**Files:**

- Create: `scripts/vps/phase13_bot_web_migration_readonly_remote.py`
- Create: `scripts/vps/phase13_bot_web_migration_ssh_runner.ps1`
- Create: `tests/test_phase13_bot_web_migration_readonly.py`

**Interfaces:**

- Remote collector consumes fixed role `usa|spain`; no user-supplied paths.
- Runner emits only canonical audit JSON and boolean ephemeral-HMAC equality
  for bot token, APP secret, web password hash и session secret.
- No raw stdout/stderr is persisted.

- [ ] **Step 1: RED static allowlist/denylist tests**

```python
def test_remote_collector_is_read_only_and_sqlite_mode_ro():
    source = REMOTE.read_text(encoding="utf-8")
    assert "mode=ro" in source
    for forbidden in ("systemctl start", "systemctl stop", "INSERT INTO",
                      "UPDATE ", "DELETE FROM", "open(\"w"):
        assert forbidden not in source


def test_runner_never_emits_stable_secret_fingerprints():
    source = RUNNER.read_text(encoding="utf-8")
    assert "RandomNumberGenerator" in source
    assert "stable_fingerprints_persisted = $false" in source
```

- [ ] **Step 2: RED run**

```text
python -m pytest tests/test_phase13_bot_web_migration_readonly.py -q
```

- [ ] **Step 3: implement bounded collector/runner**

Collector reports exact table counts, schema/count hashes, service active/
enabled/restart state, loopback/non-loopback booleans, login health, required
artifact booleans and `safety_receipt`. Runner uses fixed private trust roots,
one SSH process per role, one-time HMAC key, 60-second timeout and 1 MiB cap.

- [ ] **Step 4: fake SSH GREEN и PowerShell parse**

```text
python -m pytest tests/test_phase13_bot_web_migration_readonly.py -q
powershell -NoProfile -Command "$e=$null;[void][System.Management.Automation.Language.Parser]::ParseFile('scripts/vps/phase13_bot_web_migration_ssh_runner.ps1',[ref]$null,[ref]$e);if($e.Count){exit 1}"
```

- [ ] **Step 5: commit**

```text
git add scripts/vps/phase13_bot_web_migration_readonly_remote.py scripts/vps/phase13_bot_web_migration_ssh_runner.ps1 tests/test_phase13_bot_web_migration_readonly.py
git commit -m "Add read-only bot web migration audit tooling"
```

### Task 4: Pure logical merge preview в isolated AMN2 worktree

**Files (isolated AMN2 worktree from exact `55dc243…`):**

- Create: `app/migration/__init__.py`
- Create: `app/migration/bot_web.py`
- Create: `tests/migration/test_bot_web.py`

**Interfaces:**

- `MigrationPolicy` — immutable allowed/excluded table policy.
- `build_bot_web_migration_preview(source_db: Path, target_db: Path,
  *, migration_id: str) -> BotWebMigrationPreview`
- Preview fields: create/update/preserve/exclude counts, conflicts,
  `api_tokens_reissue_required`, invariant hashes и `apply_allowed`.

- [ ] **Step 1: RED policy tests**

```python
def test_preview_preserves_target_spain_invariants_and_excludes_credentials(fixture):
    preview = build_bot_web_migration_preview(
        fixture.usa_db, fixture.spain_db, migration_id="phase13-test-001"
    )
    assert preview.users_create == 5
    assert preview.spain_devices_preserved == 7
    assert preview.spain_passports_preserved == 7
    assert preview.api_tokens_reissue_required == 12
    assert preview.usable_secret_records_imported == 0


def test_preview_blocks_divergent_plan_id(fixture):
    fixture.add_conflicting_target_plan("plan-1")
    preview = build_bot_web_migration_preview(
        fixture.usa_db, fixture.spain_db, migration_id="phase13-test-002"
    )
    assert preview.apply_allowed is False
    assert preview.stop_reasons == ("PLAN_SEMANTIC_CONFLICT",)
```

- [ ] **Step 2: RED run**

```text
python -m pytest tests/migration/test_bot_web.py -q
```

- [ ] **Step 3: implement deterministic preview**

Users map by Telegram ID; existing target privilege always wins. Plans map by
exact ID/semantics. Orders map only after user/plan/device resolution. USA
devices become proposed `external_only`/`revoked` legacy records; server,
tokens, sessions, peer secrets/configs and canonical audit rows are excluded.
Input DBs open URI `mode=ro` and preview has no commit path.

- [ ] **Step 4: GREEN and repeatability**

```text
python -m pytest tests/migration/test_bot_web.py -q
```

Run preview twice against byte-identical fixtures and assert canonical preview
bytes and SHA-256 are equal.

- [ ] **Step 5: commit in AMN2 worktree**

```text
git add app/migration tests/migration/test_bot_web.py
git commit -m "Add bot web migration merge preview"
```

### Task 5: Apply only to a target DB copy with idempotent ledger

**Files (same isolated AMN2 worktree):**

- Modify: `app/db/schema.py`
- Modify: `app/migration/bot_web.py`
- Modify: `tests/migration/test_bot_web.py`
- Modify: `tests/db/test_schema.py`

**Interfaces:**

- New table `legacy_migration_records(migration_id, source_table,
  source_row_sha256, target_row_id, created_at)` with unique
  `(migration_id, source_table, source_row_sha256)`.
- `apply_bot_web_migration_to_copy(preview, *, source_db: Path,
  target_copy_db: Path) -> BotWebMigrationResult`.

- [ ] **Step 1: RED apply/idempotency tests**

```python
def test_apply_to_copy_imports_history_without_resurrecting_config_material(fixture):
    result = apply_bot_web_migration_to_copy(
        fixture.preview, source_db=fixture.usa_db,
        target_copy_db=fixture.spain_copy,
    )
    assert result.integrity_ok is True
    assert result.foreign_key_issues == 0
    assert result.spain_device_fingerprint_unchanged is True
    assert result.imported_legacy_devices == 8
    assert result.usable_secret_records_imported == 0


def test_apply_to_copy_replay_is_idempotent(fixture):
    first = fixture.apply()
    second = fixture.apply()
    assert second.created_rows == 0
    assert second.result_sha256 == first.result_sha256
```

- [ ] **Step 2: RED run**

```text
python -m pytest tests/migration/test_bot_web.py tests/db/test_schema.py -q
```

- [ ] **Step 3: implement one-transaction copy apply**

`BEGIN IMMEDIATE` выполняется только в temporary target copy. Перед commit
повторно проверяются preview hash, source/target schema/count hashes,
d1–d7/passport/receipt/lifecycle/server fingerprints, integrity и FK. Любая
ошибка вызывает rollback transaction и удаление incomplete output copy.

- [ ] **Step 4: GREEN и source suite**

```text
python -m pytest tests/migration/test_bot_web.py tests/db/test_schema.py tests/cli/test_device_import.py -q
```

- [ ] **Step 5: commit**

```text
git add app/db/schema.py app/migration/bot_web.py tests/migration/test_bot_web.py tests/db/test_schema.py
git commit -m "Apply bot web migration only to verified DB copies"
```

### Task 6: Encrypted backup и local package materializer

**Files (VPS-OPS-LAB root):**

- Create: `scripts/phase13_bot_web_migration_package.py`
- Create: `tests/test_phase13_bot_web_migration_package.py`
- Reuse without modifying: `scripts/phase10_full_recovery_bundle.py`

**Interfaces:**

- `materialize_local_package(inputs: PackageInputs, output_root: Path) ->
  PackageReceipt`
- Inputs are already supplied local fixture bytes; function never initiates
  SSH.
- Full backup remains opaque encrypted bytes with separate external key.

- [ ] **Step 1: RED package tests**

```python
def test_materializer_requires_encrypted_source_and_target_backups(tmp_path):
    inputs = package_inputs(source_backup_encrypted=False)
    with pytest.raises(PackageError, match="encrypted source backup"):
        materialize_local_package(inputs, tmp_path / "out")


def test_package_manifest_contains_no_secret_values(tmp_path):
    receipt = materialize_local_package(valid_inputs(), tmp_path / "out")
    text = receipt.manifest_path.read_text(encoding="utf-8")
    assert "TELEGRAM_BOT_TOKEN=" not in text
    assert "ADMIN_TELEGRAM_IDS=" not in text
    assert receipt.live_mutation_authorized is False
```

- [ ] **Step 2: RED run**

```text
python -m pytest tests/test_phase13_bot_web_migration_package.py -q
```

- [ ] **Step 3: implement no-follow/CreateNew materialization**

Package includes exact verified source/target evidence, encrypted source
backup, encrypted target-before backup, encrypted merged DB, merge preview,
rollback plan and reviewed runner bytes. Manifest is canonical and binds every
file. Plain DB/env/config bytes are cleared and never written outside private
temporary roots.

- [ ] **Step 4: GREEN and deterministic double-build**

```text
python -m pytest tests/test_phase13_bot_web_migration_package.py -q
```

Build twice from identical fixtures and assert equal manifest/artifact hashes.

- [ ] **Step 5: commit**

```text
git add scripts/phase13_bot_web_migration_package.py tests/test_phase13_bot_web_migration_package.py
git commit -m "Add local bot web migration package materializer"
```

### Task 7: Disabled Spain stage и persistent bot unit contract

**Files:**

- Create: `scripts/vps/phase13_bot_web_migration_stage_remote.sh`
- Create: `tests/test_phase13_bot_web_migration_stage.py`
- Modify package fixture only: `packaging/phase12-spain/units/amn2-spain-bot.service`

**Interfaces:**

- Modes: `preflight`, `stage`, `verify-stage`, `rollback-stage`.
- Stage may write only exact protected migration root, staged DB, runtime env
  delta and hardened bot unit; it must not start bot or alter live DB.
- Unit retains `ConditionPathExists=/etc/amn2-spain/bot-enabled` and adds exact
  persistent enable contract for future accept.

- [ ] **Step 1: RED lifecycle tests**

```python
def test_stage_never_starts_bot_or_replaces_live_database():
    source = STAGE.read_text(encoding="utf-8")
    assert "systemctl start amn2-spain-bot" not in source
    assert "mv " + LIVE_DB not in source


def test_unit_is_persistable_but_marker_gated():
    unit = BOT_UNIT.read_text(encoding="utf-8")
    assert "ConditionPathExists=/etc/amn2-spain/bot-enabled" in unit
    assert "WantedBy=multi-user.target" in unit
```

- [ ] **Step 2: RED run**

```text
python -m pytest tests/test_phase13_bot_web_migration_stage.py -q
```

- [ ] **Step 3: implement fake-harness-only stage executor**

Stage proves package hashes, bot inactive/process 0, marker absent, Spain web
loopback healthy, target DB unchanged, USA evidence fresh и AWG/foreign
foundation bound. It stages token/admin/env bytes atomically with mode 0600 but
does not activate them in the current task.

- [ ] **Step 4: GREEN, Bash и unit checks**

```text
bash -n scripts/vps/phase13_bot_web_migration_stage_remote.sh
python -m pytest tests/test_phase13_bot_web_migration_stage.py -q
```

- [ ] **Step 5: commit**

```text
git add scripts/vps/phase13_bot_web_migration_stage_remote.sh tests/test_phase13_bot_web_migration_stage.py packaging/phase12-spain/units/amn2-spain-bot.service
git commit -m "Prepare disabled Spain bot web migration stage"
```

### Task 8: Two-host single-instance cutover/rollback state machine

**Files:**

- Create: `scripts/vps/phase13_bot_web_migration_cutover_remote.sh`
- Modify: `scripts/vps/phase13_bot_web_migration_ssh_runner.ps1`
- Create: `tests/test_phase13_bot_web_migration_cutover.py`

**Interfaces:**

- State sequence:
  `preflight -> arm_rollback -> stop_usa -> prove_usa_zero -> start_spain ->
  operator_accept -> postflight`.
- Rollback sequence:
  `stop_spain -> remove_exact_marker -> restore_spain_if_needed -> start_usa ->
  prove_single_usa`.
- Runner owns one outcome claim, exact checksums, expiry and two pinned trust
  bundles; no user-overridable targets/paths.

- [ ] **Step 1: RED ordering/failure-injection tests**

```python
def test_spain_start_is_impossible_before_usa_process_zero(fake):
    fake.usa_process_count = 1
    result = fake.run_cutover()
    assert result.stop_reason == "USA_BOT_STOP_UNCONFIRMED"
    assert fake.spain_start_calls == 0


def test_failed_spain_admission_restores_single_usa_owner(fake):
    fake.spain_admission = False
    result = fake.run_cutover()
    assert result.rolled_back is True
    assert fake.spain_process_count == 0
    assert fake.usa_process_count == 1
```

- [ ] **Step 2: RED run**

```text
python -m pytest tests/test_phase13_bot_web_migration_cutover.py -q
```

- [ ] **Step 3: implement bounded orchestrator contracts**

Rollback is armed before first service action. Every stage emits allowlisted
state only. Terminal receipts contain stage/reason/outcome, service booleans,
DB/AWG/foreign equality booleans и no secret/identifier/raw output fields.
Web/data apply and bot cutover remain separate approval modes.

- [ ] **Step 4: GREEN, syntax и regression scope**

```text
bash -n scripts/vps/phase13_bot_web_migration_cutover_remote.sh
python -m pytest tests/test_phase13_bot_web_migration_contract.py tests/test_phase13_bot_web_migration_readonly.py tests/test_phase13_bot_web_migration_package.py tests/test_phase13_bot_web_migration_stage.py tests/test_phase13_bot_web_migration_cutover.py -q
python -m pytest tests/test_post_release_spain_readonly_preflight.py tests/test_phase13_awg3_readonly_preflight.py -q
```

- [ ] **Step 5: diff/secret/security review и commit**

```text
git diff --check
git add scripts/vps/phase13_bot_web_migration_cutover_remote.sh scripts/vps/phase13_bot_web_migration_ssh_runner.ps1 tests/test_phase13_bot_web_migration_cutover.py
git commit -m "Add single-instance bot migration cutover state machine"
```

## Final local verification gate

После Task 8, без SSH/package/live inputs:

```text
python -m pytest tests/test_phase13_bot_web_migration_contract.py tests/test_phase13_bot_web_migration_readonly.py tests/test_phase13_bot_web_migration_package.py tests/test_phase13_bot_web_migration_stage.py tests/test_phase13_bot_web_migration_cutover.py -q
python -m pytest tests/test_post_release_spain_readonly_preflight.py tests/test_phase13_awg3_readonly_preflight.py -q
git diff --check
```

Дополнительно выполнить scoped secret scan и ручной review:

- no raw env/DB/config/Telegram identifiers in fixtures/results;
- no source/target override;
- no service action outside exact state machine;
- no live DB replacement in stage mode;
- no USA/Spain simultaneous bot start path;
- no AWG/container/network/firewall command;
- no `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` diff.

## Stop boundary

Завершение Tasks 1–8 разрешает только подготовить fresh checksum-bound package
из отдельно утверждённых read-only inputs. Оно не разрешает package build из
live data, SSH, Spain stage, DB apply, bot cutover, USA shutdown или reuse.
