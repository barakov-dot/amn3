# `amn2`: remote operations inventory

## Паспорт

- Production repo: `C:\Users\SooL\Documents\Amneziya`
- Дата снимка: 2026-05-30
- Режим: read-only inventory, без изменений в `amn2`.
- Секреты: `.env` намеренно не читался.
- Цель: описать SSH/VPS/server apply flows, dry-run, audit, redaction и rollback gaps перед переносом идей из lab в production-направление.

## Краткий вывод

В `amn2` уже есть осторожная основа для remote operations:

- live apply выключен по умолчанию через `VPS_APPLY_ENABLED=false`;
- CLI `apply-peer` и `revoke-peer` требуют явный выбор `--dry-run` или `--apply`;
- read-only server checks проходят через allowlist команд;
- Docker runtime намеренно заблокирован для live `apply-peer`, `revoke-peer` и `collect-traffic`;
- peer preshared key не вставляется в remote command string, а передается через stdin;
- ошибки и diagnostic output проходят через redaction.

Главный gap: state-changing remote operations пока не оформлены как единый contract. Для production-доработок нужен слой, который заранее описывает risk class, inputs, remote side effects, local side effects, idempotency, audit, rollback note и test double.

## Обновление 2026-05-31: verified runner baseline

Read-only health slice `RemoteOperationRunner` уже присутствует в текущем `amn2` baseline:

- `app/server/operations.py` задает typed operation contract;
- `app/server/operation_runner.py` выполняет только `read-only-remote` operation через существующий read-only command policy;
- `app/server/checks.py` строит `server.health.check` operation и запускает health checks через runner;
- web health audit получает `operation_id`, `risk_class` и `consistency_status`;
- `docs/RUNTIME_REGISTRY.ru.md` и `docs/RUNTIME_REGISTRY.en.md` фиксируют границы первого slice.

Проверено в isolated worktree `codex/remote-operation-runner-first-slice`:

- focused verification: `75 passed`;
- full suite: `508 passed`;
- hygiene/redaction checks: `6 passed`;
- предупреждение: один внешний `StarletteDeprecationWarning` из `fastapi.testclient`.

Итог: read-only remote health baseline считается закрытым. Следующие remote work items не должны расширять runner на state-changing операции без отдельного partial-failure/rollback design.

## Обновление 2026-05-31: local/VPS verification split

Следующий remote safety блок делится на две фазы:

1. `Local-only gate` - проектирование и тестирование state-changing contract без реального VPS:
   - fake SSH/operation runner;
   - DB transaction simulations;
   - dry-run previews;
   - audit metadata;
   - rollback/resume notes;
   - redaction checks;
   - full `pytest tests -v`.
2. `Real VPS verification gate` - отдельная controlled проверка после локального зеленого suite:
   - read-only health baseline;
   - dry-run apply/revoke preview;
   - single test peer apply/revoke;
   - diagnostic snapshot;
   - lab result note.

Подробный handoff-план: [AMN2 Remote Operations Local/VPS Split Implementation Plan](../../docs/superpowers/plans/2026-05-31-amn2-remote-ops-local-vps-split.md).

Решение: реальные VPS-mutation проверки не запускаются, пока локально не закрыты contract, fake-runner tests, redaction, audit и rollback note. Первый live probe выполняется только на тестовом device/peer, с backup/recovery window и явной командой оператора.

## Карта remote surfaces

| Surface | Actor / gate | Remote command class | Local side effect | Current controls |
| --- | --- | --- | --- | --- |
| CLI `server check --dry-run` | operator shell | none, preview only | none | lists planned read-only commands |
| CLI `server check` | operator shell | `read-only-remote` | none | `ensure_read_only_command()` allowlist |
| Web `/servers/{id}/health/run` | web admin session + CSRF | `read-only-remote` | records server health + admin action | session, CSRF, redacted health errors |
| CLI `server preflight` | operator shell | none, dry-run bundle only | syncs server row in local DB | validates fixed VPN port and server public key |
| CLI `server collect-traffic` | operator shell | `read-only-remote-telemetry` | writes local traffic snapshots | Docker blocked, remote command is `awg show ... dump` |
| Bot approval with `VPS_APPLY_ENABLED=true` | Telegram admin | `remote-state-write` | creates device, fulfills order, audit action | DB transaction, peer apply before fulfill, failure rollback for remote apply error |
| CLI `server apply-peer --apply` | operator shell | `remote-state-write` | none | explicit apply flag, PSK via stdin, Docker blocked |
| Bot user revoke/reset with `VPS_APPLY_ENABLED=true` | Telegram user ownership gate | `remote-state-write` | marks device(s) revoked | remote remove before local revoke |
| CLI `server revoke-peer --apply` | operator shell | `remote-state-write` | none | explicit apply flag, Docker blocked |
| Runtime scripts | operator shell | read-only diagnostics | none | tests assert no install/restart/remove/firewall mutation commands |

## SSH execution model

`app/server/ssh.py::SystemSshClient` executes commands through system `ssh`:

- uses `ssh -p <port>`;
- enables `BatchMode=yes`;
- sets `ConnectTimeout`;
- optionally passes `-i <private_key_path>`;
- returns structured `CommandResult(exit_code, stdout, stderr)`;
- maps missing `ssh` binary to exit code `127`;
- maps timeout to exit code `124`;
- returns exit code `125` for password auth because non-interactive password backend is not enabled.

Current limitations:

- no explicit host key enrollment/pinning model was found in this pass;
- no dedicated sudo policy layer was found;
- command execution assumes the configured SSH user can run the needed commands directly;
- timeout is per command, but there is no operation-level cancellation/rollback contract.

## Read-only checks

`app/server/checks.py` defines `READ_ONLY_CHECK_COMMANDS` and `DOCKER_READ_ONLY_CHECK_COMMANDS`.

Before execution, `_run()` calls `ensure_read_only_command()`:

- exact allowlist for simple commands like `cat /etc/os-release`, `command -v awg`, `ss -lun`;
- regex allowlist for `systemctl is-active awg-quick@...`;
- regex allowlist for Docker diagnostics like `docker exec <container> awg show <interface>`;
- rejects shell control tokens such as pipes, redirection, command substitution and newlines;
- rejects common mutating words such as package install, file writes, service start/stop, firewall changes and destructive file operations.

This is strong and should become the baseline for future read-only remote operations.

## Peer apply

`app/server/peer_apply.py::apply_peer()` applies one peer for `host_systemd` runtime:

1. Builds a shell command with `shlex.quote()` for interface, public key, allowed IPs and service name.
2. Creates a temporary remote PSK file with `mktemp`.
3. Writes PSK from stdin into that file.
4. Runs `awg set <interface> peer <public-key> preshared-key "$psk_file" allowed-ips <ip>/32`.
5. Runs `systemctl reload <service_name>`.
6. Deletes the temporary PSK file through shell trap.

Controls:

- PSK is not embedded in the command string.
- Dry-run output uses `<redacted-psk-file>`.
- Errors replace the raw PSK and then pass through `redact()`.
- Docker runtime raises `PeerApplyError` until persistent container config path is known.

Open questions:

- persistent server config update was not found in the code path;
- server config backup after live apply was not found in the code path;
- if remote apply succeeds but a later local DB/audit step fails, there is no remote rollback contract visible in this pass;
- CLI `--preshared-key` is a secret-bearing argument and can leak through shell history or process inspection.

## Peer revoke/reset

`revoke_peer()` removes one peer for `host_systemd` runtime:

- runs `awg set <interface> peer <public-key> remove`;
- reloads systemd service;
- redacts failure output;
- blocks Docker runtime.

Bot user flows call remote remove before local DB revoke:

- `revoke_user_device()` verifies Telegram ownership, removes the remote peer if remover is configured, then marks the device revoked.
- `reset_user_devices()` lists owned devices, removes each remote peer, then marks all user devices revoked.

This prevents local revoke when a single remote remove fails before DB mutation. The reset flow still needs a partial-failure plan: if one remote remove succeeds and a later one fails, some remote peers may already be removed while local DB still shows devices active.

## Traffic collection

`AwgDumpTrafficCollector` runs `awg show <interface> dump` and parses counters into local traffic snapshots.

Risk class: `read-only-remote-telemetry + local-state-write`.

Controls:

- command is read-only by design;
- interface name is quoted with `shlex.quote()`;
- failed stdout/stderr are summarized as present/empty instead of being copied into the error;
- Docker traffic collection is blocked until persistent config path is known.

Gap: traffic collection does not currently reuse `ensure_read_only_command()`. It should either reuse the command policy or define an equivalent allowlist for telemetry commands.

## Web health

`POST /servers/{server_id}/health/run`:

- requires web admin session;
- requires CSRF token;
- loads server by DB id;
- resolves server name through `SERVER_CONFIG_PATH`;
- runs live read-only checks through `run_server_health_check()`;
- stores `server_health_checks`;
- records `web_server_health_run` admin action with status and error.

This is a good model for read-only remote operations exposed through web UI: route auth, CSRF, redacted errors, local audit and stored result.

## Runtime diagnostics

`deploy/runtime/check_vps.sh` and `deploy/runtime/collect_debug_snapshot.sh` are operational scripts, not app routes, but they matter for production readiness.

Current posture:

- `check_vps.sh` is read-only: checks commands, directories, ports, systemd/Docker status and AWG visibility.
- `collect_debug_snapshot.sh` gathers app, system, runtime and log context.
- Tests assert diagnostic scripts avoid package install, service restart, container removal, firewall mutation and file deletion patterns.
- Snapshot redacts key environment names, Telegram token patterns, private key path, `PrivateKey`, `PresharedKey` and `preshared-key` values.

## Existing tests that protect this area

- `tests/server/test_command_policy.py` checks read-only allowlist and mutating command rejection.
- `tests/server/test_peer_apply.py` checks dry-run output, PSK handling, redacted errors, Docker blocking, apply and revoke commands.
- `tests/server/test_system_ssh.py` checks missing binary, timeout and password backend behavior.
- `tests/server/test_checks.py` checks host and Docker read-only server reports.
- `tests/server/test_cli_server_check.py` checks CLI dry-run/apply flag behavior, traffic dry-run and preflight.
- `tests/services/test_access_service.py` checks local rollback when peer apply fails.
- `tests/bot/test_bot_workflows.py` checks user revoke/reset ownership and remote remove ordering.
- `tests/web/test_servers.py` checks web health session/CSRF and health action recording.
- `tests/deploy/test_runtime_registry.py` checks runtime manifest/scripts/docs stay read-only and redacted.

## Gaps before production changes

- Нет единого `RemoteOperationRunner`/contract layer для state-changing SSH operations.
- Нет host key enrollment/pinning flow.
- Нет sudo/privilege policy: кто и какие команды может выполнять без interactive password.
- Не найден явный persistent config update и backup после `awg set`.
- Нет operation id / before-after audit для live apply/revoke.
- Нет rollback note/resume strategy для частично успешных remote operations.
- Нет shared command policy for traffic telemetry.
- CLI `apply-peer --preshared-key` принимает secret через аргумент командной строки.
- Docker live operations правильно заблокированы, но будущий Docker manager еще не описан до уровня persistent config path, backup и reload/apply semantics.

## Transfer gate для идей из lab

Любая идея про install, uninstall, clear server, save raw config, firewall changes, Docker management, peer lifecycle или remote diagnostics должна пройти:

- License gate: переносим только подход, без копирования GPL/AGPL кода.
- Value gate: зачем operation нужна оператору и почему текущего CLI/web/bot flow недостаточно.
- Risk gate: `read-only-remote`, `read-only-remote-telemetry`, `remote-state-write` или `destructive-remote`.
- Architecture fit: operation идет через единый runner/contract, а не через ad hoc SSH строку.
- Test plan: dry-run, command allowlist, secret redaction, fake runner, remote failure, local failure after remote success, audit payload, rollback note.

## Решение для lab

Статус: `remote-operations-read-only-runner-verified`.

Не переносим новые remote-state-write функции в `amn2` как code edit, пока не описан и не утвержден policy/design для partial failure, rollback/resume и audit before/after.

Первый безопасный read-only slice `RemoteOperationRunner` уже есть в baseline и проверен. Дальше работаем не над повторным вводом runner-а, а над его расширением только через отдельные gates.

## Следующие рабочие шаги

1. Исполнить local-only phase из плана `remote-ops-local-vps-split`: contract, fake runner, partial-failure simulations, dry-run/audit metadata и full local suite.
2. Только после этого провести controlled real VPS verification gate на тестовом peer/device.
3. До live Docker apply/revoke отдельно описать Docker manager: persistent config path, backup, reload/apply semantics и rollback note.
