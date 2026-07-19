# Spain Fresh AMN2 Deployment and Admin Config Issuance Implementation Plan

> **Agentic workers:** REQUIRED SKILL: Use `superpowers:subagent-driven-development` when this plan is executed in the current task, or `superpowers:executing-plans` in a separate task. Execute one task at a time with review checkpoints; do not parallelize files that share the database schema or issuance service.

**Goal:** Prepare a clean AMN2 deployment on the Spain VPS that preserves the unrelated resident service, creates only new operator-named recipients/devices, delivers each new config only to the configured admin, and keeps every issued config revocable and auditable.

**Architecture:** Extend the existing AMN2 user/device/access/revoke foundations instead of creating a second provisioning stack. Add an operator-labelled user identity that does not require Telegram, centralize the `NEOBYATNAYA.NET` profile/filename contract, couple operator device creation to Device Passport and lifecycle evidence, and expose one fail-closed admin issuance workflow. Keep Spain access in separate checksum-bound PowerShell/OpenSSH runners with a dedicated key, an independently pinned host key, a private target binding, and read-only inventory before any install gate.

**Tech stack:** Python 3.12, SQLite, FastAPI, aiogram, pytest, PowerShell 7/Windows OpenSSH, Bash read-only remote probes, systemd/Docker deployment tooling already present in the project.

**Global constraints:**

- Never migrate or reuse USA users, devices, peers, configs, database rows, or VPN keys.
- Never delete or reinstall the USA host; it remains a rollback reference until Spain acceptance.
- Never stop, change, restart, inspect secrets from, or reconfigure the unrelated Spain service. Record a privacy-safe fingerprint before and after every later live mutation.
- Never put a VPS password in chat, Git, command arguments, `.env`, logs, or target binding. The operator enters it once interactively only to install the dedicated public key.
- Never inherit a host-key pin from another VPS. Spain gets a separate `known_hosts` file and an independently verified SHA-256 fingerprint.
- Never stop or mutate AWG for a probe. All live gates remain separate and exact.
- Do not touch `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` or unrelated working-tree files.
- Each implementation task follows red -> green -> focused regression -> diff/security review -> intentional commit.

## Gap audit: reuse versus implementation

| Capability | Existing evidence | Decision |
|---|---|---|
| Create live peer and encrypted local device record | `app/services/access.py::AccessService.create_operator_device`; CLI/web tests | Reuse unchanged as the single peer mutation primitive. |
| Build config from encrypted material | `app/services/config_delivery.py::build_device_config_delivery` | Reuse; do not add a second renderer. |
| Disable/enable user and revoke device | `app/services/user_vpn_access.py`, `app/services/device_revoke.py`, web tests | Reuse; add operator-label lookup and acceptance coverage only. |
| Remote-first mutation, partial-failure evidence | existing access/revoke services and `RemoteMutationResult` | Reuse and preserve fail-closed semantics. |
| Device Passport tables/services | `app/db/schema.py`, `app/services/device_passports.py` | Reuse; operator creation currently does not attach a passport, so add the missing coupling. |
| User identity | `users.telegram_id INTEGER NOT NULL UNIQUE` | Real gap: support an operator label without fabricated Telegram IDs. |
| Config naming | current `Neobyatnaya.NET-{device_id}.conf` and numeric prefix | Real gap: exact uppercase brand plus user/device labels and safe normalization. |
| Bot delivery | approval sends secret to `result.user_telegram_id` | Real gap: add an explicit admin-only issuance path; do not change ordinary user self-service behavior. |
| Bounded multiple issuance | no idempotent operator manifest/receipt | Real gap: add a local private manifest executor that stops on first failure and resumes without duplicates. |
| Spain trust/bootstrap | existing generic SSH patterns | Real gap: dedicated Spain key, target binding and host pin; never store password. |

## Task 1: Add operator-labelled recipients without synthetic Telegram IDs

**Files:**

- Modify: `app/db/schema.py`
- Modify: `app/db/repositories.py`
- Modify: `app/web/app.py`
- Modify: `app/web/device_passports.py`
- Modify: `app/bot/ux.py`
- Test: `tests/db/test_repositories.py`
- Test: `tests/web/test_users.py`
- Test: `tests/web/test_device_passport_views.py`

**Step 1: Write failing migration and repository tests.**

Cover a fresh database and a legacy database containing Telegram users and dependent devices. Require:

```python
recipient_id = repo.create_operator_recipient(operator_label="Alice — Pixel 8")
recipient = repo.get_user(recipient_id)
assert recipient["telegram_id"] is None
assert recipient["operator_label"] == "Alice — Pixel 8"
assert repo.get_user_by_operator_label("Alice — Pixel 8")["id"] == recipient_id
```

Also assert blank labels fail, normalized duplicates fail, Telegram upsert behavior remains unchanged, foreign keys are enabled after migration, and all legacy IDs/rows survive.

Run:

```powershell
python -m pytest tests/db/test_repositories.py tests/web/test_users.py tests/web/test_device_passport_views.py -q
```

Expected: failures because the schema and repository do not yet support operator recipients.

**Step 2: Implement a transactional users-table rebuild.**

Change the canonical schema to:

```sql
telegram_id INTEGER UNIQUE,
operator_label TEXT,
CHECK (telegram_id IS NOT NULL OR length(trim(operator_label)) > 0)
```

Add a unique partial index on `lower(trim(operator_label)) WHERE operator_label IS NOT NULL`. Implement `_migrate_users_operator_identity(conn)` using `users_new`, an explicit column list, `PRAGMA foreign_key_check`, and restoration of the original foreign-key setting in `finally`. Do not use negative or fabricated Telegram IDs.

**Step 3: Add repository and presentation helpers.**

Add the exact typed interfaces `create_operator_recipient(*, operator_label: str) -> int`, `get_user_by_operator_label(operator_label: str) -> sqlite3.Row | None`, and `user_display_label(row: Mapping[str, Any]) -> str`.

Keep Telegram-only handlers fail-closed when `telegram_id is None`; update web/passport display code to use the safe display label instead of `int(row["telegram_id"])`.

**Step 4: Verify and commit.**

```powershell
python -m pytest tests/db/test_repositories.py tests/web/test_users.py tests/web/test_device_passport_views.py -q
git diff --check
git add app/db/schema.py app/db/repositories.py app/web/app.py app/web/device_passports.py app/bot/ux.py tests/db/test_repositories.py tests/web/test_users.py tests/web/test_device_passport_views.py
git commit -m "Support operator-labelled recipients"
```

## Task 2: Centralize the exact NEOBYATNAYA.NET naming contract

**Files:**

- Create: `app/services/config_identity.py`
- Modify: `app/bot/delivery.py`
- Modify: `app/services/access.py`
- Test: `tests/services/test_config_identity.py`
- Test: `tests/bot/test_delivery.py`
- Test: `tests/services/test_access_service.py`

**Step 1: Write failing naming tests.**

Use exact expectations:

```python
identity = build_config_identity(user_label="Иван", device_label="Pixel 8")
assert identity.display_name == "NEOBYATNAYA.NET — Иван — Pixel 8"
assert identity.filename == "NEOBYATNAYA.NET-Ivan-Pixel-8.conf"
```

Also cover Cyrillic transliteration/fallback, path separators, control characters, repeated whitespace, reserved Windows names, 96-character filename bound, and collision suffix derived from the immutable local device ID rather than config secret material.

**Step 2: Implement one formatter.**

`ConfigIdentity` contains `display_name` and `filename`. Preserve the exact display punctuation; sanitize only the filesystem filename. Never include Telegram IDs, IPs, public keys, or secret fingerprints in the filename.

**Step 3: Route operator issuance through the formatter.**

Pass the computed display name to `AccessService.create_operator_device`. Change only the new admin issuance attachment naming; retain existing user-delivery behavior until its own compatibility decision.

**Step 4: Verify and commit.**

```powershell
python -m pytest tests/services/test_config_identity.py tests/bot/test_delivery.py tests/services/test_access_service.py -q
git diff --check
git add app/services/config_identity.py app/bot/delivery.py app/services/access.py tests/services/test_config_identity.py tests/bot/test_delivery.py tests/services/test_access_service.py
git commit -m "Add canonical operator config identity"
```

## Task 3: Couple operator creation to Device Passport and lifecycle evidence

**Files:**

- Modify: `app/services/access.py`
- Modify: `app/services/device_passports.py`
- Modify: `app/services/device_lifecycle.py`
- Test: `tests/services/test_access_service.py`
- Test: `tests/services/test_device_passports.py`
- Test: `tests/services/test_device_lifecycle.py`

**Step 1: Write failing tests.**

After a successful mocked live peer apply, require one passport linked to `local_device_id`, with owner/server/config version, declared platform/client/import method, and `sha256(config_text)` fingerprint. Require completed `config_ready` evidence without raw config or keys. On remote or local failure require no false `delivered` event.

**Step 2: Extend the existing operator input.**

Add an immutable context:

```python
@dataclass(frozen=True)
class OperatorDeviceContext:
    platform: str
    official_client_type: str = "amnezia_vpn"
    client_version: str | None = None
    import_method: str = "conf_file"
```

Use the existing passport service/repository. Generate the stable passport ID locally; store only the SHA-256 fingerprint of rendered config, never the config itself in passport evidence.

**Step 3: Preserve partial-failure semantics.**

Passport/lifecycle writes stay inside the local transaction after remote apply. If they fail, surface the existing `RemoteOperationPartialFailure` recovery contract; do not retry peer creation blindly.

**Step 4: Verify and commit.**

```powershell
python -m pytest tests/services/test_access_service.py tests/services/test_device_passports.py tests/services/test_device_lifecycle.py -q
git diff --check
git add app/services/access.py app/services/device_passports.py app/services/device_lifecycle.py tests/services/test_access_service.py tests/services/test_device_passports.py tests/services/test_device_lifecycle.py
git commit -m "Bind operator devices to passports"
```

## Task 4: Implement idempotent admin issuance and bounded manifest receipts

**Files:**

- Modify: `app/db/schema.py`
- Modify: `app/db/repositories.py`
- Create: `app/services/admin_config_issuance.py`
- Modify: `app/cli.py`
- Test: `tests/services/test_admin_config_issuance.py`
- Test: `tests/cli/test_admin_config_issuance.py`
- Create: `docs/examples/spain-config-issuance-manifest.example.json`

**Step 1: Write failing service tests.**

The private input contains labels and non-secret compatibility metadata only:

```json
{
  "request_id": "spain-first-real-001",
  "server": "Spain-Madrid",
  "items": [
    {"recipient_label": "Alice", "device_label": "Pixel 8", "platform": "android"}
  ]
}
```

Require that the same `request_id` plus item index returns the existing receipt and never creates a second peer. A failure at item 2 stops before item 3. The receipt exposes IDs, status and config filename, but not config text, private keys, PSK, token, endpoint IP, or raw SSH data.

**Step 2: Add the issuance receipt table.**

Add `admin_config_issuance_receipts` with unique `(request_id, item_index)`, recipient/user/device/passport IDs, status `started|completed|partial_failure`, safe error code, and timestamps. Do not persist config content in this table.

**Step 3: Implement the service around existing primitives.**

`AdminConfigIssuanceService.issue_manifest()` validates the whole manifest before mutation, resolves/creates operator recipients, calls `AccessService.create_operator_device`, builds the canonical attachment, records a safe audit action, stops on first failure, and supports resume from completed receipts.

**Step 4: Add a local-only CLI surface.**

Add `admin-config issue-manifest --manifest private-artifacts/post-release/spain-migration/issuance.json --server Spain-Madrid --apply`. Dry-run is default. `--apply` requires the existing live mutation admission and explicit configured admin ID. The example manifest contains no real person or target data.

**Step 5: Verify and commit.**

```powershell
python -m pytest tests/services/test_admin_config_issuance.py tests/cli/test_admin_config_issuance.py -q
git diff --check
git add app/db/schema.py app/db/repositories.py app/services/admin_config_issuance.py app/cli.py tests/services/test_admin_config_issuance.py tests/cli/test_admin_config_issuance.py docs/examples/spain-config-issuance-manifest.example.json
git commit -m "Add idempotent admin config issuance"
```

## Task 5: Deliver new operator-issued configs only to the configured admin

**Files:**

- Modify: `app/bot/workflows.py`
- Modify: `app/bot/handlers.py`
- Modify: `app/bot/main.py`
- Modify: `app/bot/ux.py`
- Test: `tests/bot/test_bot_workflows.py`
- Test: `tests/bot/test_handlers.py`
- Test: `tests/bot/test_app_bootstrap.py`

**Step 1: Write failing authorization and delivery tests.**

Require non-admin rejection before parsing/mutation, configured-admin membership, one `.conf` document sent to `admin_telegram_id`, no send to recipient, no QR, no `vpn://`, no secret in text/caption/logs, and `delivered` lifecycle evidence only after Telegram confirms document send.

**Step 2: Add a distinct workflow result.**

```python
@dataclass(frozen=True)
class AdminConfigHandoff:
    recipient_user_id: int
    device_id: int
    passport_device_id: str
    filename: str
    config_bytes: bytes
```

Do not reuse `ApprovalResult.user_telegram_id`; that existing path intentionally targets a Telegram user.

**Step 3: Add the admin command.**

Register the literal command grammar `/admin_issue_config recipient label | device label | platform`. Validate bounded lengths and supported platforms before mutation. The handler calls the issuance service once and sends the document to the invoking configured admin only. On Telegram delivery failure, record a failed `delivered` stage and offer safe resend by device ID without creating another peer.

**Step 4: Verify and commit.**

```powershell
python -m pytest tests/bot/test_bot_workflows.py tests/bot/test_handlers.py tests/bot/test_app_bootstrap.py -q
git diff --check
git add app/bot/workflows.py app/bot/handlers.py app/bot/main.py app/bot/ux.py tests/bot/test_bot_workflows.py tests/bot/test_handlers.py tests/bot/test_app_bootstrap.py
git commit -m "Add admin-only config handoff"
```

## Task 6: Prove disable, revoke and operator UI behavior for labelled recipients

**Files:**

- Modify: `app/web/app.py`
- Modify: `app/web/templates/users.html`
- Modify: `app/web/templates/user_detail.html`
- Modify: `app/web/templates/device_detail.html`
- Test: `tests/web/test_users.py`
- Test: `tests/web/test_operator_device_create.py`
- Test: `tests/services/test_device_revoke.py`

**Step 1: Add acceptance tests.**

Create an operator-labelled user with a passport-backed device. Verify admin pages never cast a missing Telegram ID, show the canonical config identity, disable removes live access through the existing remote-first flow, enable restores only the intended peer, revoke closes passport/lifecycle surfaces, and audit output contains IDs/labels but no config material.

**Step 2: Make presentation-only changes.**

Use `user_display_label`; do not fork disable/revoke implementations. Hide Telegram-specific actions for recipients without Telegram identity.

**Step 3: Verify and commit.**

```powershell
python -m pytest tests/web/test_users.py tests/web/test_operator_device_create.py tests/services/test_device_revoke.py -q
git diff --check
git add app/web/app.py app/web/templates/users.html app/web/templates/user_detail.html app/web/templates/device_detail.html tests/web/test_users.py tests/web/test_operator_device_create.py tests/services/test_device_revoke.py
git commit -m "Expose operator recipients safely"
```

## Task 7: Build dedicated Spain SSH onboarding locally

**Files:**

- Create: `scripts/vps/post_release_spain_ssh_onboarding.ps1`
- Create: `tests/test_post_release_spain_ssh_onboarding.py`
- Modify: `.gitignore`
- Create: `docs/POST_RELEASE_SPAIN_SSH_ONBOARDING.ru.md`

**Step 1: Write failing static/behavior tests.**

Require absolute Windows OpenSSH paths, `-F none`, `BatchMode=yes`, `IdentitiesOnly=yes`, a dedicated Spain key path, a separate known-hosts file, exact `TARGET_HOST`/`TARGET_USER`, and `EXPECTED_HOST_KEY_SHA256`. Reject `password`, `sshpass`, PuTTY password switches, disabled host checking, global `known_hosts`, shell interpolation, and missing ACL hardening.

**Step 2: Implement local modes only.**

Implement `prepare-key`, `write-binding`, `verify-pin`, and `print-public-key`. `prepare-key` calls absolute `ssh-keygen.exe` with Ed25519 and an AMN2 Spain comment. `write-binding` writes only:

The binding contains exactly four assignment lines named `TARGET_HOST`, `TARGET_USER`, `SSH_KEY_PATH`, and `EXPECTED_HOST_KEY_SHA256`; values are supplied interactively or through non-logged secure input and are never echoed.

Place binding, key and known-hosts under `private-artifacts/post-release/spain-migration/{run_id}/`; restrict ACL to the current Windows user. The script never accepts a password parameter and never connects to the VPS.

**Step 3: Document the single interactive operator action.**

The operator uses provider console or interactive OpenSSH once to append the displayed public key to the Spain account. Fingerprint verification is an independent operator/provider check before the runner records the pin.

**Step 4: Verify and commit.**

```powershell
python -m pytest tests/test_post_release_spain_ssh_onboarding.py -q
git diff --check
git add .gitignore scripts/vps/post_release_spain_ssh_onboarding.ps1 tests/test_post_release_spain_ssh_onboarding.py docs/POST_RELEASE_SPAIN_SSH_ONBOARDING.ru.md
git commit -m "Add fail-closed Spain SSH onboarding"
```

## Task 8: Build the checksum-bound read-only Spain preflight

**Files:**

- Create: `scripts/vps/post_release_spain_readonly_preflight_remote.sh`
- Create: `scripts/vps/post_release_spain_readonly_preflight_ssh_runner.ps1`
- Create: `tests/test_post_release_spain_readonly_preflight.py`
- Create: `docs/POST_RELEASE_SPAIN_READONLY_PREFLIGHT_GATE.ru.md`

**Step 1: Write failing safety tests.**

Allow only read-only inventory: OS/kernel, CPU/RAM/disk capacity, listening sockets, Docker/systemd names and states, firewall display, SSH effective-policy display, clock, package presence, and a privacy-safe unrelated-service fingerprint. Ban `systemctl stop|restart|enable|disable`, `docker stop|restart|rm`, package install/update, firewall writes, file writes, redirection, secret/env/config dumps, AWG mutation, and Telegram calls.

**Step 2: Implement the remote probe.**

Emit normalized JSON with no public target address, credentials, environment variables, command lines containing secrets, config bodies, keys, or tokens. The unrelated-service fingerprint is `(kind, stable unit/container name hash, image/unit hash, active state, restart count, bound-port set)`; it is later compared exactly.

**Step 3: Implement the trusted local runner.**

The PowerShell runner verifies its embedded remote-script SHA-256, loads the private binding, verifies the pinned host key into the separate known-hosts file, then calls absolute `ssh.exe` with:

```text
-F none -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes
-o UserKnownHostsFile=private-artifacts/post-release/spain-migration/{run_id}/known_hosts -i private-artifacts/post-release/spain-migration/{run_id}/id_ed25519 -p 22
```

It exposes only `Mode preflight`, cannot install or mutate, and writes redacted evidence beneath the same ignored run directory.

**Step 4: Verify and commit.**

```powershell
python -m pytest tests/test_post_release_spain_readonly_preflight.py -q
git diff --check
git add scripts/vps/post_release_spain_readonly_preflight_remote.sh scripts/vps/post_release_spain_readonly_preflight_ssh_runner.ps1 tests/test_post_release_spain_readonly_preflight.py docs/POST_RELEASE_SPAIN_READONLY_PREFLIGHT_GATE.ru.md
git commit -m "Add Spain read-only preflight gate"
```

## Task 9: Run complete local verification and security review

**Files:**

- Review all files changed in Tasks 1-8
- Update only if required by verified failures: `docs/PROJECT_STATUS_CURRENT.ru.md`

**Step 1: Run AMN2 scoped and full tests.**

```powershell
python -m pytest tests/db/test_repositories.py tests/services/test_config_identity.py tests/services/test_access_service.py tests/services/test_admin_config_issuance.py tests/services/test_device_revoke.py tests/bot/test_bot_workflows.py tests/bot/test_handlers.py tests/web/test_users.py -q
python -m pytest tests -q
```

**Step 2: Run docs/runner tests.**

```powershell
python -m pytest tests/test_post_release_spain_ssh_onboarding.py tests/test_post_release_spain_readonly_preflight.py -q
python -m pytest tests -q
```

Run the two commands in their respective repositories/worktrees.

**Step 3: Review diff and secrets.**

```powershell
git diff --check
git diff --stat origin/codex-vps-test-prep...HEAD
git grep -n -I -E "(BEGIN (RSA|OPENSSH) PRIVATE KEY|BOT_TOKEN=|PASSWORD=|PRESHARED|PrivateKey[[:space:]]*=)" -- . ":(exclude)tests/fixtures/**"
```

Apply the `codex-security:security-diff-scan` skill to both Git-backed change sets. Treat admin-only secret routing, nullable identity, migration integrity, idempotency, subprocess arguments, host-key pinning, path handling and log redaction as mandatory review areas.

**Step 4: Self-review against the approved specification.**

- Re-read `docs/superpowers/specs/2026-07-19-spain-fresh-admin-config-issuance-design.ru.md`.
- Map every requirement to a passing test or a later exact live gate.
- Search changed files for unfinished markers, non-materialized hashes, example IPs in executable defaults, password parameters, and unbound SSH targets; remove every match that can affect execution.
- Confirm Python interfaces use `int | None` consistently for Telegram identity and never cast `None`.
- Confirm the protected monitor baseline and unrelated files are absent from staged changes.

## Task 10: Commit, push, and issue the exact live preflight gate

**Files:**

- Modify: `docs/PROJECT_STATUS_CURRENT.ru.md`
- Create: `docs/POST_RELEASE_SPAIN_IMPLEMENTATION_EVIDENCE.ru.md`
- Modify: active Phase 11/post-release handoff document resolved from current status

**Step 1: Record immutable evidence.**

Record AMN2 source head, docs head, full-test counts, security review result, runner SHA-256, remote-script SHA-256, and the fact that no Spain network connection or mutation has occurred.

**Step 2: Commit and push both trusted branches.**

```powershell
git add docs/PROJECT_STATUS_CURRENT.ru.md docs/POST_RELEASE_SPAIN_IMPLEMENTATION_EVIDENCE.ru.md docs/NEXT_CHAT_AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS.ru.md
git commit -m "Prepare Spain deployment gates"
git push origin codex-spark-phase9-docs-sync
git -C worktrees/amn2-p7-c005-write-install push origin codex-vps-test-prep
git status --short --branch
git -C worktrees/amn2-p7-c005-write-install status --short --branch
```

Verify each local head equals its trusted origin. Do not stage `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` or the unrelated monitoring plan/spec.

**Step 3: Compute the literal approval only after checksums exist.**

The runner constructs the approval from the fixed prefix `APPROVE POST_RELEASE_SPAIN_READ_ONLY_PREFLIGHT`, its actual uppercase SHA-256, the actual remote-script SHA-256, the actual AMN2 source head, and the fixed safety suffix `DEDICATED_ED25519_EXACT_PRIVATE_TARGET_AND_INDEPENDENT_HOST_KEY_PIN_READ_ONLY_OS_CAPACITY_PORT_SERVICE_DOCKER_SYSTEMD_FIREWALL_SSH_CLOCK_AND_UNRELATED_SERVICE_FINGERPRINT_NO_INSTALL_NO_RESTART_NO_STOP_NO_CONFIG_SECRET_TELEGRAM_OR_AWG_MUTATION`. It prints one fully materialized line for the operator and rejects every other string.

Do not connect until the operator repeats that fully materialized literal phrase. A successful read-only preflight prepares, but does not authorize, the clean install gate.

## Execution handoff

This plan is ready for execution. Recommended execution mode: **Subagent-Driven in this task**, one task at a time with spec review and code-quality review after each task. Alternative: **Inline Execution in a separate task** using `superpowers:executing-plans` with the same checkpoints.
