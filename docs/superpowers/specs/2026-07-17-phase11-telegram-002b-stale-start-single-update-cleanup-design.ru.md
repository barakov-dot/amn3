# Phase 11 TELEGRAM-002B stale first-admin `/start` single-update cleanup

Дата: 2026-07-17.

Статус: DESIGN-APPROVED; IMPLEMENTATION-NOT-AUTHORIZED; LIVE-CLEANUP-NOT-AUTHORIZED.

Design approval:

```text
APPROVE_PHASE11_TELEGRAM_002B_STALE_FIRST_ADMIN_START_SINGLE_UPDATE_CLEANUP_DESIGN
```

Это approval разрешает записать и проверить дизайн. Оно не разрешает SSH/VPS
contact, Telegram acknowledgement, очистку очереди, запуск или enable bot,
изменение production database, web, Telegram profile, AWG или provider state.

## Context and decision / Контекст и решение

Exact `2FDB...` activation preflight 2026-07-17 остановился fail-closed:

```text
telegram_preflight=failed reason=pending_updates_nonzero
stage=false
regular_bot=inactive_disabled_process_0
database=integrity_ok|foreign_key_issues_0|tables_15|rows_88
web=active_enabled_http_ok_loopback_only
awg=running|restart_0|peers_12|baseline_unchanged
```

The activation stage did not run, so its local single-use stage receipt was not
created and the exact `2FDB...` stage authority remains unconsumed. A normal
persistent stage cannot start while the Telegram backlog is nonzero.

Решение: добавить отдельный одноразовый fail-closed cleanup executor. Он может
acknowledge только один уже ожидающий exact private `/start` от первого
configured administrator. Он не отвечает в Telegram, не создаёт workflow, не
открывает production SQLite для записи и не меняет existing activation
executor or runner bytes.

## Considered approaches / Рассмотренные варианты

### A. Separate exact-one-update cleanup — selected

A dedicated remote executor plus a checksum-bound local SSH runner performs a
fresh full preflight, inspects at most two queued updates without acknowledging
them, validates exactly one private first-admin `/start`, revalidates the same
update immediately before acknowledgement, acknowledges only that update and
requires final backlog zero.

Преимущества: минимальная authority, отсутствие лишнего bot response и DB
write, preservation of the existing `2FDB...` activation bytes and approval.
Недостаток: Telegram acknowledgement необратим, поэтому нужен отдельный exact
live approval и строгая single-use receipt.

### B. Repeat controlled transient smoke — rejected

The Phase 11 transient smoke could send the language header using a clone DB
and acknowledge the update. This would repeat an already accepted smoke,
produce an unexpected extra user response and widen the operation beyond queue
recovery.

### C. Blind queue reset — prohibited

`deleteWebhook(drop_pending_updates=true)`, an arbitrary high offset, repeated
draining, or acknowledgement without inspecting actor and message are not
allowed. These methods can delete unrelated operator or user traffic and may
change the Telegram webhook/profile contract.

## Components / Компоненты

Implementation will add three isolated files and will not edit the current
`phase11_telegram_002b_persistent_*` pair:

1. `scripts/vps/phase11_telegram_002b_stale_start_cleanup_remote.sh` — remote
   preflight and exact-one acknowledgement executor;
2. `scripts/vps/phase11_telegram_002b_stale_start_cleanup_ssh_runner.ps1` —
   checksum-bound same-byte transport over trusted absolute OpenSSH;
3. `tests/test_phase11_telegram_002b_stale_start_cleanup_executor.py` — static
   safety, ordering, output-redaction and approval-consumption contracts.

The runner supports `preflight` and `cleanup` modes. `preflight` never advances
an update offset. `cleanup` creates an exclusive local receipt before remote
contact so the exact mutation approval cannot be consumed twice.

## Bound inputs and trust / Привязка входов и доверия

The future executor must bind all of the following before Telegram access:

```text
source_overlay=0b858c5
source_commit=0b858c5cdbc5b565cc265966a2edfe2d339d65e0
expected_bot_username=NeobyatnayaAMNZ_bot
write_gates=false_false
regular_bot=inactive_disabled_process_0
web=active_enabled_http_ok_loopback_only
database=integrity_ok|foreign_key_issues_0
awg=running|restart_0|known_container_and_peer_set
```

The token, proxy and ordered administrator list are loaded from the exact
production environment without printing their values. The selected actor is
only `settings.admin_ids[0]`; an absent, duplicate, invalid or unordered
administrator binding fails closed. Environment, source and unit inputs must
be non-symlink regular files with the existing owner/mode contracts. A Python
virtual-environment symlink is accepted only after `readlink -f` resolves it to
an executable regular target.

The local runner must use the absolute Windows OpenSSH binary, one pinned
known-host entry, `-F none`, isolated global/user host sources and exact
SHA-256 verification of the bytes sent through stdin. Neither target nor
private identifiers may appear in output.

## Inspection contract / Контракт проверки update

The Telegram client runs as the existing bot service user and performs only
bounded Bot API reads before acknowledgement:

1. require exact bot identity;
2. require an empty webhook URL;
3. require `pending_update_count == 1`;
4. call `getUpdates` with `limit=2`, `timeout=0` and without an advancing
   offset, so zero or multiple returned updates fail;
5. require exactly one update with a non-negative integer `update_id`;
6. require a message update only, a private chat, sender ID equal to the first
   configured administrator, chat ID equal to sender ID and text exactly
   `/start` after the same normalization used by the accepted handler;
7. reject callbacks, edited/channel/business updates, attachments, another
   actor, `/start` payloads, addressed commands, another text or invalid
   structure without acknowledgement;
8. re-read webhook/backlog and the first two updates immediately before the
   mutation; require backlog exactly one and the same canonical update ID,
   actor, private-chat binding and exact command.

The executor never emits update ID, administrator ID, chat ID, message text,
timestamps, names, usernames, webhook data or raw Telegram exceptions.

## Acknowledgement transaction / Точная очистка

Only `cleanup` under a future exact live approval may call:

```text
getUpdates(offset=validated_update_id + 1, limit=1, timeout=0)
```

This advances the acknowledgement boundary only past the validated update.
If a concurrent higher-ID update arrives, it may be returned by this call but
is not acknowledged by any further offset. The executor must then stop with a
sanitized `concurrent_update_detected` result and preserve that new update for
manual review.

Success requires all of the following after the single offset advance:

```text
webhook_configured=false
pending_update_count=0
regular_bot=inactive_disabled_process_0
production_database=unchanged_integrity_ok_fk_0
web=active_enabled_http_ok_loopback_only
awg=running_restart_0_peer_set_unchanged
acknowledged_update=first_configured_admin_exact_private_start_only
```

No Telegram response is sent. The executor does not import or call bot
handlers, workflow/bootstrap code, dispatcher polling or callback routes.

## Failure and rollback policy / Отказы и rollback

Before acknowledgement, every mismatch exits without queue mutation. After
acknowledgement, Telegram state cannot be rolled back. Therefore the operation
must not perform an automatic second acknowledgement, blind queue restore or
webhook reset. It reports only one fixed safe category and preserves any
concurrent update.

Allowed safe categories are closed and enumerated, for example:

```text
identity_mismatch
webhook_configured
pending_count_not_one
update_count_not_one
actor_mismatch
chat_not_private
command_mismatch
update_shape_invalid
update_changed_before_ack
concurrent_update_detected
network_failure
cleanup_timeout
cleanup_rejected
```

Unknown exceptions map to `cleanup_rejected`. Raw exception strings are never
printed. The production database is never automatically restored because the
executor has no authority to write it; an unexpected DB digest change is a
hard stop requiring separate investigation.

## Verification / Проверка реализации

TDD must first prove red failures for:

- missing or inexact design/live approval;
- reuse of a consumed cleanup approval;
- missing source/SHA/known-host binding;
- active or enabled regular bot;
- use of `setWebhook`, `deleteWebhook`, `drop_pending_updates`, unbounded loops
  or a second advancing offset;
- zero, two, malformed, callback, wrong-admin, non-private or non-exact-start
  updates;
- acknowledgement before the second identity/backlog/update recheck;
- output containing private IDs, raw update data, token-like values or raw
  exception text;
- database, web or AWG mutation commands.

Green verification requires focused tests, the canonical docs/ops test suite,
`bash -n`, PowerShell parser validation, `git diff --check`, high-confidence
secret scanning and a fresh security diff scan with zero unresolved reportable
findings. Then status docs are synchronized, committed, pushed and read back
from trusted origin before any live phrase is issued.

## Live gates and continuation / Дальнейшая последовательность

The design approval recorded in this document is not a live approval. After
implementation verification and origin synchronization, Codex will issue a
new literal phrase bound to the cleanup remote SHA, source overlay and exact
one-update scope.

After that phrase is separately received:

```text
cleanup preflight
-> single-use exact cleanup
-> independent backlog/web/DB/AWG postflight
-> reuse unconsumed 2FDB activation preflight
-> 2FDB disabled-first stage with autorollback240
-> prompt the first admin to send one fresh /start
-> exact wide-header confirmation
-> accept, enable and independent postflight
```

The user must not send another `/start` until the new activation stage reports
`awaiting_admin_start=true`. Production AWG remains untouched throughout.
