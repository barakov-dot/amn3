# AMN2: ожидание точного именованного gate

Дата: 2026-06-22.

Статус:

```text
wait_exact_named_gate_status=active-docs-only
ready_hold_status=active-docs-only
phase8_final_status=launch-ready-with-explicit-limitations
private_operator_rc_launch_ready=true
public_launch_status=not-approved
blocked_with_exact_remaining_blockers=false
remaining_blockers_inside_listed_limitations=none
```

Этот документ фиксирует русскоязычную рабочую команду ожидания: использовать
только существующие Phase 8 evidence и не открывать live/destructive/config/
Telegram send/public exposure gates до явного запроса конкретного
именованного gate.

## Операторская формулировка

```text
ОЖИДАНИЕ_ТОЧНОГО_ИМЕНОВАННОГО_GATE

Использовать только существующие Phase 8 evidence.
Не открывать live/destructive/config/Telegram send/public exposure gates.
Держать AMN2 в статусе private/operator RC launch-ready-with-explicit-limitations
до тех пор, пока оператор явно не запросит конкретный именованный gate.
```

## Head на момент фиксации ожидания

```text
amn3_evidence_head_before_wait_exact_gate=17988d7 Record private operator RC ready hold
amn2_current_fixes_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447 Persist Android-compatible AWG defaults
latest_vps_applied_package_smoked_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
package_name=dist/amn2-vps-update-and-smoke-kit-187949b.zip
package_sha256=7FA073E4C66C0981673061D167D525BB9BCD6DFDDAA075E15701F0C2608E2E82
```

## Что разрешено

Разрешено:

- читать существующие Phase 8 evidence;
- вести docs-only/status-only синхронизацию;
- планировать следующий exact named gate без его открытия;
- отвечать оператору русскоязычными командами и подсказками.

## Что запрещено без нового gate

Без явного нового exact named gate нельзя:

- выполнять live VPS/SSH command;
- выполнять destructive VPS/provider action;
- загружать или применять package;
- перезапускать сервисы;
- открывать public exposure;
- менять firewall/listener/TLS/reverse proxy/Cloudflare/ngrok;
- выполнять config delivery;
- выводить `.conf`, QR, `vpn://`, private key, PSK, token или password;
- выполнять Telegram live send;
- запускать bot polling;
- менять Telegram profile/media;
- выполнять backup restore/import/reboot;
- выполнять provider rebuild;
- менять production peer/user;
- начинать broader rollout.

## Какие gate могут вывести из ожидания

Выход из ожидания возможен только новым явным заданием, например:

```text
PRIVATE-RC-OPERATOR-RUN-GATE
CONFIG-DELIVERY-GATE
TELEGRAM-LIVE-DELIVERY-GATE
PUBLIC-EXPOSURE-GATE
RESTORE-IMPORT-DR-GATE
PROVIDER-REBUILD-GATE
PRODUCTION-ROLLOUT-GATE
FRESH-ANDROID-PHONE-POST-RC-RECHECK-GATE
```

## Текущая рекомендация

```text
current_recommendation=ожидать_явный_именованный_gate
next_action=ничего_не_открывать_без_запроса_оператора
```
