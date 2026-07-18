# TELEGRAM-GROUP-ICON-001: bilingual TDD implementation and runbook plan

Дата: `2026-07-18`.

## Authority and boundary / Полномочия и граница

Canonical design: AMN2 commit `57efe86`, file
`docs/superpowers/specs/2026-07-18-post-release-device-001-and-telegram-group-icon-design.ru.md`.

Approved written spec:

```text
APPROVE_WRITTEN_DEVICE_001_AND_TELEGRAM_GROUP_ICON_001_SPEC_57EFE86
```

This approval authorizes only the written plan, local executor, tests, diff
and security review, documentation, commit and push. It does **not** authorize
`setChatPhoto`, `deleteChatPhoto`, Telegram messages, polling/update
consumption, bot restart, DB/web/VPS mutation or any AWG action.

Утверждение разрешает только план, локальную реализацию и проверки. Живое
изменение фото группы требует отдельной literal approval после origin sync.

## Fixed target and asset contract / Контракт цели и asset

Canonical asset:

```text
path=/opt/amn2/app/bot/assets/NEOBYATNAYA-AMNZ-BOT.png
sha256=40ACD9465DC9FDA06644D2D829DA996E1D9BF6C856E95298B624B31154FEC791
dimensions=1254x1254
format=PNG
source_overlay=0b858c5cdbc5b565cc265966a2edfe2d339d65e0
```

The exact group target is never committed. Production receives one root-only,
regular, non-symlink `0600` JSON file:

```text
/root/.config/amn2/telegram-group-icon-001/target.json
```

It contains exactly `chat_id`, `expected_title`, and `expected_type`; type is
`group` or `supergroup`. The executor emits only an uppercase namespaced
SHA-256 fingerprint of the canonical JSON, never the raw ID or title.

Exact target хранится только в private runtime input. В evidence, approval и
выводе допускается только fingerprint.

## Files / Файлы

- Create: `scripts/vps/post_release_telegram_group_icon_001_remote.sh`
- Create: `scripts/vps/post_release_telegram_group_icon_001_ssh_runner.ps1`
- Create: `tests/test_post_release_telegram_group_icon_001_executor.py`
- Create after verification:
  `research/amn2/post-release-telegram-group-icon-001-local-gate-2026-07-18.md`
- Update after verification: `docs/PROJECT_STATUS_CURRENT.ru.md`

## Executor modes / Режимы

Only three public modes are admitted:

1. `fingerprint` — checksum-bound SSH transport reads the private target file,
   validates its shape/permissions, performs no Telegram API call and prints
   only `target_chat_fingerprint=<SHA256>`.
2. `preflight` — requires exact target fingerprint plus exact literal live
   approval; runs read-only identity/chat/title/type/member/permission,
   webhook/backlog, asset, bot/web/DB/AWG checks.
3. `apply` — requires the same bindings and a single-use local receipt;
   snapshots the current chat photo, arms bounded rollback before exactly one
   `setChatPhoto`, verifies changed postflight photo, cancels rollback only
   after success, proves invariants and cleans private state.

`rollback` is internal only and cannot be selected from the local runner.

## Mandatory fail-closed controls / Обязательные controls

- source marker and imported runtime-file SHA checks;
- asset regular-file, SHA, PNG signature and IHDR dimension checks;
- root-owned `0600` target JSON with exact keys and strict types;
- `getMe` username `NeobyatnayaAMNZ_bot`;
- empty webhook and backlog `0` without `getUpdates`;
- `getChat` exact ID/title/type match;
- `getChatMember` proves the bot is administrator and
  `can_change_info=true`;
- current photo is downloaded to root-only state, or an explicit
  `no_existing_photo` receipt is written;
- DB logical snapshot, web health, bot service identity/restart state and AWG
  container/restart/peer-set snapshots are equal before and after;
- rollback timer is armed before mutation and signal/error traps invoke the
  same reviewed helper;
- previous photo is restored on failure; if there was none,
  `deleteChatPhoto` is used only by rollback;
- raw bot token, chat ID, title, Telegram file path and token-bearing URL are
  never printed;
- exact safe error categories only;
- success removes the private photo/metadata/helper/state and verifies the
  directory no longer exists.

## Forbidden operations / Запрещённые операции

The executor must contain no `sendMessage`, `sendPhoto`, `sendDocument`,
`getUpdates`, webhook mutation, bot profile mutation, bot service
start/stop/restart/enable/disable, web service mutation, DB restore/write,
VPS overlay/package operation, Docker mutation, `awg set` or `wg set`.

Messages sent must remain `0`; the regular bot stays active/enabled and is not
restarted. AWG is observation-only and never mutated.

## TDD tasks / TDD-задачи

### Task 1 — RED: static contract tests

Create `tests/test_post_release_telegram_group_icon_001_executor.py` first.
The initial test run must fail because both executors are absent.

```powershell
python -m pytest tests/test_post_release_telegram_group_icon_001_executor.py -q
```

Tests must bind:

- exact modes and no public rollback;
- source/asset/runtime SHA constants;
- target file ownership/mode/schema/fingerprint validation;
- Telegram identity/chat/member/permission checks;
- zero queue consumption and zero messages;
- exactly one `set_chat_photo` in the apply path;
- previous-photo/no-photo rollback branches;
- timer-before-mutation and cancel-after-postflight ordering;
- DB/web/bot/AWG before/after invariants;
- closed safe output/error categories;
- trusted absolute OpenSSH, isolated config/known-host sources, byte-exact
  transport, target-bound exact approval and single-use apply receipt.

### Task 2 — GREEN: remote executor

Implement the Bash executor and inline Python Telegram operations. Prefer
small named functions for source, asset, target, service, DB, AWG, Telegram
and cleanup contracts. Run the focused test until green.

### Task 3 — GREEN: checksum-bound local runner

Implement the PowerShell runner. Compute the final remote SHA, bind it in the
runner, use an absolute Windows OpenSSH path, pass the exact same byte array to
stdin, and validate a dynamic exact approval of the form:

```text
APPROVE POST_RELEASE_TELEGRAM_GROUP_ICON_001_REMOTE_SHA_<REMOTE_SHA>_SOURCE_0B858C5_TARGET_SHA256_<TARGET_FINGERPRINT>_EXACT_GROUP_PHOTO_SINGLE_SETCHATPHOTO_POSTFLIGHT_OR_ROLLBACK_NO_MESSAGES_BOT_DB_WEB_AND_AWG_UNTOUCHED
```

Only `apply` consumes a local `CreateNew` receipt. `fingerprint` accepts no
approval and makes no Telegram API call. Do not execute any mode in this task.

### Task 4 — scoped and full verification

```powershell
python -m pytest tests/test_post_release_telegram_group_icon_001_executor.py -q
python -m pytest tests -q
git diff --check
```

Run forbidden-operation, secret and exact-call-count scans over the new
executor/runner. Verify existing Phase 11 executor byte hashes remain intact.

### Task 5 — diff/security review and evidence

Perform a Git-backed security diff review over the new plan, tests and
executors. Report complete coverage, findings and deferred candidates. Add a
local-readiness evidence record and a top status override that explicitly says
`live_group_icon_unchanged=true`, `telegram_api_called=false` and
`production_awg=untouched`.

### Task 6 — commit, push, origin readback, live stop line

Commit intentionally, push `codex-spark-phase9-docs-sync`, fetch and prove
local/origin equality. Also push the AMN2 written-spec status update and prove
`codex-vps-test-prep` equality.

Only after both origins are verified may the main agent run `fingerprint` and
prepare the exact literal live approval. No `preflight` or `apply` occurs
without that new approval.

## Success receipt / Итог локального gate

```text
local_executor=implemented_and_tested
remote_script_sha256=<BOUND_SHA>
source_overlay=0b858c5
canonical_asset_sha256=40ACD9465DC9FDA06644D2D829DA996E1D9BF6C856E95298B624B31154FEC791
live_group_icon_unchanged=true
telegram_api_called=false
messages_sent=0
bot_service=unchanged
database=unchanged
web=unchanged
awg=untouched
exact_live_approval=withheld_until_target_fingerprint_and_origin_sync
```

## English normative summary

Build and verify a checksum-bound, target-bound, fail-closed group chat photo
executor without running it. The live mutation is exactly one
`setChatPhoto`, with a private previous-photo snapshot and bounded automatic
rollback. It must not alter the bot avatar, send messages, consume updates,
restart services, mutate DB/web/VPS state, or touch AWG. A separate exact live
approval is mandatory after local/origin verification.
