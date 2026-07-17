# Phase 11 TELEGRAM-002B: staged persistent activation design

Дата: 2026-07-17.

Статус: approved for local design, TDD planning and implementation by the
operator command
`APPROVE_PHASE11_TELEGRAM_002B_STAGED_PERSISTENT_ACTIVATION_DESIGN`.

Это approval не разрешает SSH/VPS contact, Telegram API calls, unit/env write,
`systemctl start/enable`, production database write или любое AWG action.
Отдельная exact live-фраза выпускается только после tests, security review,
commit, push и origin verification.

## Цель

Перевести уже развернутый source overlay `0b858c5` из состояния
`regular_bot=inactive_disabled` в один контролируемый persistent bot runtime.
Live transaction должна сначала установить exact hardened unit/env contract,
запустить unit при `disabled-at-boot`, доказать fail-closed Telegram admission,
systemd readiness/watchdog и один реальный `/start` первого настроенного
администратора, а затем — и только затем — включить автозапуск.

Web остаётся активным и loopback-only. Product write gates остаются
`false/false`. Telegram profile photo, provider, peer/config и AWG не входят в
gate.

## Bilingual design summary (EN)

This local slice defines a staged, fail-closed activation executor for the
already deployed `0b858c5` source overlay. It is design/implementation
approval only: it does not authorize SSH, VPS, Telegram API, systemd, database,
provider, or AWG actions. The runtime starts the bot active but disabled at
boot, arms a 240-second rollback before any unit/env mutation, and keeps signal
traps (`ERR`, `HUP`, `INT`, `TERM`) until the stage is safely recorded. The
accept path verifies the exact first-admin database delta and wide-header
confirmation, keeps a compensation rollback trap through `enable`, and clears
it only after the accepted state is committed.

The trusted runner accepts one literal ordinal approval, consumes a local
exclusive `CreateNew` stage receipt, requires that receipt for `accept`, and
transports the space-bearing confirmation as canonical UTF-8 Base64. The
remote side decodes and re-encodes the token before comparing the exact phrase.
OpenSSH is bound to the absolute Windows installation with `-F none`,
`GlobalKnownHostsFile=none`, `KnownHostsCommand=none`, and the dedicated pinned
known-host file. No regular bot, Telegram profile, production DB restore,
provider mutation, or AWG action is performed in this local slice.

## Bound production source

```text
source_overlay=0b858c5
source_commit=0b858c5cdbc5b565cc265966a2edfe2d339d65e0
unit_source_sha256=E0C6706B030775C9731CF3FC3A055CAE88512CF470BF2D6BFABDACD7F2F5F694
persistent_runtime_sha256=F400FE8FDA673CA6976B698365A591CEC3A373C4284721A39AEF935DF16C5A31
app_main_sha256=C34A0F457B2242EDE138DD0B6DC1B08B860515F7BD2FADB7DF8F2B86A3F5ED31
systemd_notify_sha256=649EA2EABBD6B18C5E489D2059D08020D64914C47B15E50EA2873AEEFA99A8A3
settings_sha256=1DB81553DBCBF4DAFC710EFDD69C2DB0CC1A869F0754D7BB67C7ADFA3DCAC631
expected_bot_identity=@NeobyatnayaAMNZ_bot|prior_sanitized_getMe_binding
allowed_updates=message,callback_query
tasks_concurrency_limit=8
```

Source rollout не устанавливал production unit и не менял `.env`, поэтому
live executor обязан отдельно привязать и применить эти два runtime inputs.

## Рассмотренные варианты

### A. Disabled-first start, bounded acceptance, then enable — выбран

Одна exact transaction ставит unit/env, оставляет unit disabled, запускает его,
ждёт readiness/watchdog, затем в ограниченном окне принимает ровно один
`/start` первого configured admin. После exact DB delta, wide-header response,
single-instance и health proof выполняется `systemctl enable`.

Плюсы: boot persistence появляется только после фактического acceptance;
failure автоматически возвращает service в inactive/disabled; оператору нужна
одна live approval-фраза и одно действие в Telegram.

### B. Два отдельных live gate: start-disabled и later-enable — отложен

Это ещё сильнее разделяет authority, но оставляет промежуточный active/disabled
runtime между двумя операторскими решениями и добавляет лишнюю незавершённую
production state. Вариант остаётся fallback, если bounded acceptance нельзя
закрыть в одной SSH transaction.

### C. `enable --now` до acceptance — отклонён

Immediate boot persistence до identity/backlog/readiness/watchdog и real
response proof расширяет blast radius и усложняет rollback после reboot или
restart loop.

## Локальные компоненты

### PowerShell trusted runner

`scripts/vps/phase11_telegram_002b_persistent_ssh_runner.ps1`:

- требует literal ordinal equality с отдельной exact live-фразой до чтения SSH
  bindings или target resolution;
- использует только absolute `%WINDIR%\System32\OpenSSH\ssh.exe`;
- изолирует ambient OpenSSH configuration через `-F none`,
  `GlobalKnownHostsFile=none` и `KnownHostsCommand=none`, оставляя только
  dedicated pinned known-host file;
- проверяет dedicated production key и pinned known-host file;
- читает remote executor один раз как `byte[]`, сверяет exact SHA-256 и
  передаёт в `bash -s` тот же массив;
- поддерживает только `preflight`, `stage`, `accept`, `postflight`;
- redacts target и не выводит environment, token, admin IDs или raw Telegram
  payload.

Никакой package upload не нужен: exact unit и application source уже находятся
в production overlay `0b858c5`.

### Remote fail-closed executor

`scripts/vps/phase11_telegram_002b_persistent_remote.sh`:

- выполняет read-only preflight;
- создаёт unique mode-0700 rollback root;
- сохраняет root-only unit/env/DB/runtime/AWG receipts;
- атомарно ставит exact unit и четыре explicit env settings;
- запускает unit disabled-first;
- arm-ит 240-second automatic rollback watchdog и возвращает sanitized run id;
- в отдельном `accept <run-id>` проверяет bounded acceptance и визуальное
  подтверждение оператора; пробелосодержащая exact confirmation передаётся
  как canonical UTF-8 Base64 token и декодируется/проверяется удалённой частью;
- отменяет rollback watchdog и включает unit только после полного PASS;
- arm-ит rollback до первой unit/env mutation; signal traps (`ERR`, `HUP`,
  `INT`, `TERM`) закрывают потерю SSH-сессии; после отмены timer accept держит
  compensation rollback до фиксации `accepted`;
- на любой ошибке stop/disable и восстанавливает прежние unit/env;
- никогда не выполняет AWG/Docker/peer/config mutation.

## Preflight contract

До первой mutation обязательны:

1. overlay marker и пять exact source hashes совпадают с design binding;
2. web active/enabled, HTTP healthy и listener loopback-only;
3. regular bot inactive/disabled/process zero;
4. write gates `VPS_APPLY_ENABLED=false` и
   `OPERATOR_DEVICE_CREATE_ENABLED=false`;
5. production DB integrity `ok`, foreign keys `0`, online backup возможен;
6. installed bot unit/env существуют, не symlink и snapshot-readable;
7. service user, runtime/data/log/backup/template directories и unit source
   имеют ожидаемые ownership/access properties;
8. Telegram expected identity совпадает с prior sanitized binding, webhook URL
   пуст, pending backlog `0`, non-acknowledging zero-time ownership probe пуст;
9. AWG running/restart count/peer count/peer-set snapshot снимается read-only;
10. disk space достаточен для rollback material.

Preflight Telegram calls ограничены `getMe`, `getWebhookInfo` и zero-time
`getUpdates` без offset. Они не удаляют webhook и не очищают backlog.

## Unit and environment transaction

Rollback root сохраняет:

- installed unit fragment и `systemctl cat` hash;
- complete `.env` copy, metadata и hash без публикации содержимого;
- SQLite online backup плюс application-row snapshot;
- bot service active/enabled/process state;
- web and AWG snapshots;
- exact source/input receipts.

Executor rejects duplicate env keys and atomically binds:

```text
TELEGRAM_EXPECTED_BOT_USERNAME=NeobyatnayaAMNZ_bot
TELEGRAM_ADMISSION_TIMEOUT_SECONDS=30
TELEGRAM_POLLING_TIMEOUT_SECONDS=20
TELEGRAM_RUNTIME_LOCK_PATH=/run/amn2-bot/polling.lock
```

Existing token, proxy, admin IDs, database path and product write gates are not
changed or printed. Exact source unit is installed root-owned mode `0644`, then
`systemctl daemon-reload` runs. Unit must remain disabled before the first
`systemctl start`.

## Disabled-first acceptance

После `stage` executor требует:

1. `ActiveState=active`, `SubState=running`, `Type=notify`, main PID present;
2. `NRestarts=0`, start-limit contract and one process/cgroup owner;
3. sanitized admission receipt exactly once with expected identity, webhook
   absent, pending count `0`, allowed updates `message,callback_query`;
4. nonzero systemd watchdog timestamp within the bounded observation window;
5. local second-lock probe fails before any duplicate network/DB access;
6. application-table rows remain unchanged before the operator update;
7. executor возвращает `awaiting_admin_start=true` и оставляет bot active but
   disabled максимум на 240 секунд под automatic rollback watchdog;
8. first configured administrator sends exactly one `/start`, видит ровно один
   новый wide language-selection header response и передаёт Codex exact local
   confirmation `CONFIRM PHASE11_TELEGRAM_002B_FIRST_ADMIN_WIDE_HEADER_RESPONSE`;
9. DB changes only in that existing administrator's `users` row fields
   `username`, `first_name`, `last_name`, `updated_at`; row/table counts and all
   other application rows remain unchanged;
10. service remains active with zero restarts and no conflict/traceback/error
    marker after the response.

The preflight interpreter binding accepts a standard virtual-environment
symlink only after `readlink -f` resolves it to a regular executable target;
all source/unit/env files remain non-symlink regular-file bindings.

Только runner mode `accept`, получивший exact confirmation и matching run id,
может отменить rollback watchdog, выполнить `systemctl enable` и report
`activation=pass`. Если `accept` не завершён за 240 секунд, root-only rollback
helper автоматически stop/disable bot и восстанавливает прежние unit/env.

## Rollback and failure policy

Before Telegram polling is admitted, any failure restores unit/env. An
unexpected initialization write stops activation and preserves the verified DB
backup plus before/after evidence for manual review; the executor never
overwrites the live production DB automatically while web may hold it open.

After any Telegram update could have been acknowledged, the same no-automatic-
restore rule applies. Executor stops and disables only the bot, restores
unit/env, preserves before/after DB evidence root-only and reports manual
database review required. The known first-admin `/start` row delta is retained
as legitimate acceptance state.

Rollback always requires:

- bot inactive/disabled/process zero;
- old unit/env hashes restored and daemon reloaded;
- web still active/enabled/private;
- DB integrity/FK zero;
- AWG snapshot exactly unchanged.

Rollback never stops/restarts/recreates/reconfigures AWG.

## Postflight

Independent mode requires overlay/source hashes unchanged, exact installed
unit and env contract, bot active/enabled, main PID/cgroup one, readiness
receipt, watchdog timestamp, `NRestarts=0`, webhook absent and backlog `0`
without a competing `getUpdates` call. It repeats web, DB integrity and AWG
read-only checks.

`postflight` does not send Telegram messages, change profile media or mutate
provider/peer/config state.

The local runner also records a one-time stage approval receipt with exclusive
file creation. A replayed stage phrase fails closed, while `accept` cannot run
without the matching local receipt; this receipt contains only mode and remote
script SHA, never secrets or Telegram payloads.

## TDD and security strategy

Static contract tests first fail for absent files. GREEN implementation must
prove:

- exact source/unit/env/identity bindings;
- ordinal approval before target/SSH;
- same-byte remote executor hash/transport;
- absolute trusted OpenSSH path;
- preflight-before-mutation ordering;
- disabled-first `stage`, exact-confirmed `accept` and 240-second automatic
  rollback ordering;
- exact single-admin DB delta checks;
- rollback split before/after possible acknowledgement;
- no secret/raw-output paths;
- no Docker/AWG/peer/config mutation;
- bounded waits and retained rollback evidence.

Then run focused tests, full repository tests, Bash/PowerShell syntax,
`git diff --check`, high-confidence secret scan and Codex Security diff review.

## Acceptance criteria

- Local executor and tests are committed and origin-synced before live phrase.
- Exact live phrase binds the finalized remote executor SHA-256.
- No live action occurs under design/local implementation approval.
- Success means one active/enabled persistent bot, real first-admin wide-header
  `/start` response, zero restarts, healthy watchdog/web/DB and unchanged AWG.
- Failure means bot inactive/disabled, unit/env restored, DB not blindly
  overwritten after acknowledgement, web healthy and AWG unchanged.

## Вне scope

Telegram profile photo, arbitrary bot workflow acceptance, callback mutation,
VPS apply enablement, SSH-key relocation for future bot VPS-write mode, schema
migration, public listener, provider action, second-VPS mutation, recovery
artifact deletion, AWG action и
`docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md`.
