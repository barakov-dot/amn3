# Local Operator Indefinite Unassigned Access Slots Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an admin-only local batch workflow that issues multiple immediately active, indefinite-by-default VPN access slots to a recipient without inventing physical-device passports, while preserving explicit expiry, independent revoke/disable, idempotent replay, and optional later assignment.

**Architecture:** Extend the existing `devices` access-record contract instead of creating a second peer lifecycle. Add explicit expiry policy and `recipient_unassigned` assignment mode, make passport creation conditional, expand batch quantities deterministically, and persist safe receipts. Reuse remote-first revoke semantics and add a local idempotent assignment service that creates a passport only after the operator supplies real endpoint facts.

**Tech Stack:** Python 3.14, SQLite, pytest, existing AMN2 `AccessService`, `Repository`, CLI, fake peer clients, encrypted config material.

## Global Constraints

- Local operator batch defaults to `expiry_policy=indefinite`, `duration_days=NULL`, `expires_at=NULL`.
- Expiry exists only when explicit `duration_days` or future UTC `expires_at` is supplied; both together are invalid.
- `recipient_unassigned` creates an active access record and peer but no Device Passport.
- One recipient may receive multiple numbered slots; each counts against the access limit and is independently disabled/revoked.
- Existing dedicated-device, plan, order, bot, backup/restore and public-surface behavior must remain compatible.
- Dry-run performs no DB, artifact, key-generation, SSH, or peer mutation.
- Apply remains configured-admin-only and requires the existing VPS write gate before settings, DB or remote access.
- Raw `.conf`, private keys and PSKs never appear in safe JSON, receipts, audit, Git or logs.
- No Spain/VPS/Telegram/AWG live action is part of implementation or tests.

---

## File map

- Create `app/access_expiry.py`: strict expiry-policy value object and canonical manifest parsing.
- Modify `app/config_assignment.py`: add `recipient_unassigned` and passport-required policy metadata.
- Modify `app/db/schema.py`: atomic access-record and receipt migrations plus assignment-request table.
- Modify `app/db/repositories.py`: nullable expiry, fingerprint, slot receipt and assignment persistence.
- Modify `app/services/access.py`: create access slots without passports and retain dedicated behavior.
- Modify `app/services/admin_config_issuance.py`: quantity expansion, full-batch admission, expiry and safe receipts.
- Create `app/services/access_slot_assignment.py`: idempotent one-time later passport assignment.
- Create `app/services/access_slot_lifecycle.py`: independent remote-first disable/revoke plans.
- Modify `app/cli.py`: manifest dry-run/apply contract and local assignment/lifecycle commands.
- Modify focused tests under `tests/db`, `tests/services`, `tests/cli`, `tests/bot`, and `tests/web`.

### Task 1: Explicit expiry policy and SQLite migration

**Files:**
- Create: `app/access_expiry.py`
- Modify: `app/db/schema.py`
- Modify: `app/db/repositories.py`
- Test: `tests/db/test_repositories.py`
- Test: `tests/services/test_access_expiry.py`

**Interfaces:**
- Produces `AccessExpiry(policy: str, duration_days: int | None, expires_at: str | None)`.
- Produces `parse_access_expiry(value: object | None, *, now: datetime | None = None) -> AccessExpiry`.
- Extends `Repository.create_device(..., duration_days: int | None, expires_at: str | None = None, expiry_policy: str = "duration", config_fingerprint: str | None = None)`.

- [ ] **Step 1: Write failing expiry tests**

Add tests proving omitted/`{"kind":"indefinite"}` produces null values, positive duration produces `duration`, future UTC deadline produces `absolute`, and conflicts/past deadlines fail.

- [ ] **Step 2: Run RED**

Run: `python -m pytest tests/services/test_access_expiry.py tests/db/test_repositories.py -q`

Expected: failures because `app.access_expiry`, `expiry_policy` and nullable duration do not exist.

- [ ] **Step 3: Implement the value object**

Use constants `DURATION`, `ABSOLUTE`, `INDEFINITE`; normalize UTC to `Z`; accept only exact object keys for manifest input.

- [ ] **Step 4: Implement atomic schema migration**

Rebuild `devices` preserving IDs and foreign keys. Add:

```sql
expiry_policy TEXT NOT NULL DEFAULT 'duration'
  CHECK (expiry_policy IN ('duration','absolute','indefinite')),
duration_days INTEGER,
config_fingerprint TEXT
  CHECK (config_fingerprint IS NULL OR
         (length(config_fingerprint)=71 AND
          config_fingerprint GLOB 'sha256:[0-9a-f]*')),
CHECK (
  (expiry_policy='duration' AND duration_days > 0 AND expires_at IS NOT NULL) OR
  (expiry_policy='absolute' AND duration_days IS NULL AND expires_at IS NOT NULL) OR
  (expiry_policy='indefinite' AND duration_days IS NULL AND expires_at IS NULL)
)
```

Migrate existing rows as `duration`, retain current values, recreate reserved-IP index, run `PRAGMA foreign_key_check` and rollback on any failure.

- [ ] **Step 5: Extend repository creation**

Generate duration expiry in SQL, persist absolute expiry verbatim, and persist nulls for indefinite. Require a valid fingerprint for new locally generated records at service level, not for legacy/external rows.

- [ ] **Step 6: Run GREEN and regressions**

Run: `python -m pytest tests/services/test_access_expiry.py tests/db/test_repositories.py -q`

Expected: all pass.

- [ ] **Step 7: Commit**

```text
git add app/access_expiry.py app/db/schema.py app/db/repositories.py tests/services/test_access_expiry.py tests/db/test_repositories.py
git commit -m "Add explicit access expiry policy"
```

### Task 2: Recipient-unassigned access creation without fake passports

**Files:**
- Modify: `app/config_assignment.py`
- Modify: `app/services/access.py`
- Modify: `app/db/schema.py`
- Test: `tests/services/test_access_service.py`
- Test: `tests/services/test_config_assignment.py`

**Interfaces:**
- Produces `RECIPIENT_UNASSIGNED = "recipient_unassigned"`.
- Extends `ConfigAssignmentPolicy` with `passport_required: bool`.
- Extends `OperatorDeviceCreateResult` with `passport_device_id: str | None` and `config_fingerprint: str`.
- Extends `AccessService.create_operator_device` with `expiry: AccessExpiry` while retaining `duration_days` compatibility for existing callers.

- [ ] **Step 1: Write failing policy/access tests**

Cover: unassigned is valid, counts as enforceable unique access, creates one peer and one device row, stores null expiry/fingerprint, and creates zero passports/lifecycle events. Dedicated mode still creates one passport.

- [ ] **Step 2: Run RED**

Run: `python -m pytest tests/services/test_config_assignment.py tests/services/test_access_service.py -q`

Expected: failures for missing mode/result fields and unconditional passport creation.

- [ ] **Step 3: Implement assignment policy**

Set unassigned policy to `physical_device_limit=None`, `physical_device_count_enforceable=True`, `unique_peer_per_physical_device=False`, `passport_required=False`. Existing dedicated policy uses `passport_required=True`.

- [ ] **Step 4: Make access creation conditional**

Validate device context and create lifecycle/passport only when `passport_required`. Always compute `fingerprint_config(config_text)` and persist it on the access row. Audit only policy, expiry and safe IDs.

- [ ] **Step 5: Preserve old callers**

Translate existing positive `duration_days` into `AccessExpiry(duration, ...)`; reject conflicting old/new inputs. Order approval remains duration-based dedicated mode.

- [ ] **Step 6: Run GREEN and regressions**

Run: `python -m pytest tests/services/test_config_assignment.py tests/services/test_access_service.py tests/services/test_device_passports.py -q`

- [ ] **Step 7: Commit**

```text
git add app/config_assignment.py app/services/access.py app/db/schema.py tests/services/test_config_assignment.py tests/services/test_access_service.py
git commit -m "Add recipient unassigned access slots"
```

### Task 3: Quantity manifests, full-batch admission and safe receipts

**Files:**
- Modify: `app/services/admin_config_issuance.py`
- Modify: `app/db/schema.py`
- Modify: `app/db/repositories.py`
- Modify: `app/services/config_identity.py`
- Test: `tests/services/test_admin_config_issuance.py`
- Test: `tests/services/test_config_identity.py`
- Test: `tests/db/test_repositories.py`

**Interfaces:**
- `IssuanceManifestItem(mode, recipient_label, quantity, device_label, platform, expiry)`.
- `ExpandedIssuanceSlot(item_index, recipient_label, assignment_mode, slot_ordinal, device_label, platform, expiry)`.
- Receipt fields add `assignment_mode`, `slot_sequence`, nullable `passport_device_id`, and safe `expiry_policy`.

- [ ] **Step 1: Write failing manifest tests**

Cover exact key validation, quantity `1..100`, expanded total cap `100`, duplicate normalized recipient item rejection, default indefinite, explicit overrides, deterministic expansion and request-fingerprint mismatch.

- [ ] **Step 2: Write failing issuance tests**

For quantity four assert four unique peers/files/receipts, null expiry, no passports, four quota slots, replay creates nothing, modified replay fails before mutation, and fifth slot fails full-batch admission before any peer call when limit is four.

- [ ] **Step 3: Run RED**

Run: `python -m pytest tests/services/test_admin_config_issuance.py tests/services/test_config_identity.py tests/db/test_repositories.py -q`

- [ ] **Step 4: Implement deterministic expansion and naming**

Use numbered labels `01`, `02`, ... and canonical filenames `NEOBYATNAYA.NET-<recipient>-<nn>.conf`. Persist sequence on receipt at start so resume cannot select a new number.

- [ ] **Step 5: Migrate receipt constraints**

Completed dedicated receipts require passport; completed unassigned receipts require null passport plus non-null device, filename and slot sequence. Preserve existing rows as dedicated.

- [ ] **Step 6: Implement full-batch admission**

Resolve existing recipients and compare active count plus requested slots against configured maximum before recipient creation, key generation, artifact write or peer apply.

- [ ] **Step 7: Implement safe sequential apply/resume**

Stop after first partial failure; reuse completed receipts; never include payload/secrets in result. Use create-new private artifact writer.

- [ ] **Step 8: Run GREEN and regressions**

Run: `python -m pytest tests/services/test_admin_config_issuance.py tests/services/test_config_identity.py tests/db/test_repositories.py -q`

- [ ] **Step 9: Commit**

```text
git add app/services/admin_config_issuance.py app/services/config_identity.py app/db/schema.py app/db/repositories.py tests/services/test_admin_config_issuance.py tests/services/test_config_identity.py tests/db/test_repositories.py
git commit -m "Add idempotent multi slot issuance"
```

### Task 4: CLI dry-run and apply contract

**Files:**
- Modify: `app/cli.py`
- Test: `tests/cli/test_admin_config_issuance.py`
- Test: `tests/security/test_surface_policy_bindings.py`

**Interfaces:**
- `build_admin_config_issuance_plan` returns expanded filenames, quota deltas and expiry policies without mutation.
- `run_admin_config_issue_manifest` consumes expiry from manifest; no hidden 30-day default.

- [ ] **Step 1: Write failing CLI tests**

Assert dry-run quantity four, filename preview, indefinite policy, no settings/DB/client/key calls, and explicit duration/absolute previews. Assert apply gate runs before settings and admin validation remains fail-closed.

- [ ] **Step 2: Run RED**

Run: `python -m pytest tests/cli/test_admin_config_issuance.py tests/security/test_surface_policy_bindings.py -q`

- [ ] **Step 3: Implement parser/dispatch changes**

Remove the `issue-manifest` default duration injection. Keep `--apply` and configured admin checks. The manifest is the only expiry authority for this command.

- [ ] **Step 4: Implement mutation-free preview**

Return only safe canonical fields and do not instantiate `Settings`, repository, SSH client or key generator.

- [ ] **Step 5: Run GREEN**

Run: `python -m pytest tests/cli/test_admin_config_issuance.py tests/security/test_surface_policy_bindings.py -q`

- [ ] **Step 6: Commit**

```text
git add app/cli.py tests/cli/test_admin_config_issuance.py tests/security/test_surface_policy_bindings.py
git commit -m "Expose indefinite batch issuance CLI"
```

### Task 5: Independent disable/revoke and optional later assignment

**Files:**
- Create: `app/services/access_slot_assignment.py`
- Create: `app/services/access_slot_lifecycle.py`
- Modify: `app/db/schema.py`
- Modify: `app/db/repositories.py`
- Modify: `app/cli.py`
- Test: `tests/services/test_access_slot_assignment.py`
- Test: `tests/services/test_access_slot_lifecycle.py`
- Test: `tests/cli/test_admin_config_slots.py`

**Interfaces:**
- `assign_access_slot(repo, *, request_id, local_device_id, device_label, context, admin_telegram_id) -> DevicePassport`.
- `build_access_slot_disable_plan(repo, *, local_device_id) -> OperationPlan`.
- `disable_access_slot(..., peer_remover, apply_remote) -> AccessSlotLifecycleResult`.
- `revoke_access_slot(..., peer_remover, apply_remote) -> AccessSlotLifecycleResult`.

- [ ] **Step 1: Write failing assignment tests**

Assert only unassigned non-revoked owner access can be assigned; stored fingerprint is used; one passport is created; peer/key/filename do not change; identical request replays; conflicting request or second assignment fails without mutation.

- [ ] **Step 2: Write failing lifecycle tests**

Assert remote-first gate for active slot, independent disable/revoke, other recipient slots unchanged, revoked slot cannot assign, safe metadata excludes peer/private/PSK, and remote-success/local-failure raises explicit partial failure.

- [ ] **Step 3: Run RED**

Run: `python -m pytest tests/services/test_access_slot_assignment.py tests/services/test_access_slot_lifecycle.py -q`

- [ ] **Step 4: Add assignment request table and repository APIs**

Persist request id, canonical fingerprint, local device id, passport id and status. Enforce one completed assignment per local slot and exact replay.

- [ ] **Step 5: Implement assignment service**

Create passport from stored config fingerprint, update access label/mode to dedicated, record redacted audit, and never read raw config or decrypted secrets.

- [ ] **Step 6: Implement lifecycle service**

Use existing remote peer remover protocol and `cascade_revoke_device_access`. Add single-device disable repository method; do not use user-wide disable. Refuse local-only mutation while remote peer exists.

- [ ] **Step 7: Add admin CLI commands**

Add dry-run/apply commands for `assign-slot`, `disable-slot`, and `revoke-slot`; configured admin and VPS write gate are required before applicable mutation. Safe JSON only.

- [ ] **Step 8: Run GREEN and regressions**

Run: `python -m pytest tests/services/test_access_slot_assignment.py tests/services/test_access_slot_lifecycle.py tests/services/test_device_revoke.py tests/cli/test_admin_config_slots.py -q`

- [ ] **Step 9: Commit**

```text
git add app/services/access_slot_assignment.py app/services/access_slot_lifecycle.py app/db/schema.py app/db/repositories.py app/cli.py tests/services/test_access_slot_assignment.py tests/services/test_access_slot_lifecycle.py tests/cli/test_admin_config_slots.py
git commit -m "Add unassigned slot lifecycle"
```

### Task 6: Compatibility projections and regression boundaries

**Files:**
- Modify: `app/bot/workflows.py`
- Modify: `app/web/app.py`
- Modify: `app/web/templates/user_detail.html`
- Test: `tests/bot/test_bot_workflows.py`
- Test: `tests/web/test_users.py`
- Test: `tests/web/test_device_passport_views.py`

**Interfaces:**
- Existing dedicated Telegram issuance continues to require a passport.
- Admin projections render `recipient_unassigned`, `indefinite`, and `не назначено` without exposing secrets.

- [ ] **Step 1: Write failing compatibility tests**

Assert bot dedicated path unchanged, safe admin list handles null expiry/passport, and passport views contain only actual passports.

- [ ] **Step 2: Run RED**

Run: `python -m pytest tests/bot/test_bot_workflows.py tests/web/test_users.py tests/web/test_device_passport_views.py -q`

- [ ] **Step 3: Implement minimal safe projections**

Do not add public write forms. Render assignment/expiry status only in existing authenticated admin surfaces.

- [ ] **Step 4: Run GREEN**

Run: `python -m pytest tests/bot/test_bot_workflows.py tests/web/test_users.py tests/web/test_device_passport_views.py -q`

- [ ] **Step 5: Commit**

```text
git add app/bot/workflows.py app/web/app.py app/web/templates/user_detail.html tests/bot/test_bot_workflows.py tests/web/test_users.py tests/web/test_device_passport_views.py
git commit -m "Project unassigned slots safely"
```

### Task 7: Full verification, security review and status sync

**Files:**
- Modify: `docs/PROJECT_STATUS_CURRENT.ru.md`
- Modify: `docs/NEXT_CHAT_AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS.ru.md`
- Create: `docs/POST_RELEASE_OPERATOR_UNASSIGNED_SLOTS_IMPLEMENTATION_EVIDENCE.ru.md`

- [ ] **Step 1: Run focused AMN2 suite**

Run all tests touched above plus migration, backup/restore, bot and web compatibility suites.

- [ ] **Step 2: Run full AMN2 suite**

Run: `python -m pytest tests -q`

Expected: zero failures; only previously accepted warnings/skips may remain.

- [ ] **Step 3: Run diff and secret review**

Run `git diff --check`; inspect exact branch diff; scan added lines for private keys, PSK, config payloads, passwords, tokens, private targets and `vpn://` payloads.

- [ ] **Step 4: Run Codex Security diff scan**

Threat areas: schema migration integrity, nullable expiry bypass, quota admission, request replay, filename collisions, secret leakage, remote/local partial failure, unauthorized assignment and revoke.

- [ ] **Step 5: Sync status docs**

Record exact AMN2 head, tests, security coverage/findings and negative live-action evidence. Do not touch `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` or unrelated monitoring docs.

- [ ] **Step 6: Run root tests and diff check**

Run: `python -m pytest tests -q`

- [ ] **Step 7: Commit and push**

Commit AMN2 code/tests, then AMN3 docs/status. Push `codex-vps-test-prep` and `codex-spark-phase9-docs-sync`; fetch both and require local/origin SHA equality.
