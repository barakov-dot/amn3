# AMN2: ждать запроса оператора

Дата: 2026-06-22.

Статус:

```text
wait_operator_request_status=active-docs-only
wait_exact_named_gate_status=active-docs-only
ready_hold_status=active-docs-only
phase8_final_status=launch-ready-with-explicit-limitations
private_operator_rc_launch_ready=true
public_launch_status=not-approved
blocked_with_exact_remaining_blockers=false
remaining_blockers_inside_listed_limitations=none
```

Этот документ фиксирует финальную русскоязычную рабочую паузу после Phase 8:
ждать запроса оператора и ничего live/destructive/config/Telegram/public не
открывать без явного именованного gate.

## Операторская формулировка

```text
ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА

Использовать только существующие Phase 8 evidence.
Ничего live/destructive/config/Telegram/public не открывать.
Следующее действие выполнять только после явного именованного gate от оператора.
```

## Head на момент фиксации

```text
amn3_evidence_head_before_wait_operator_request=951deb4 Record wait for exact named gate
amn2_current_fixes_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447 Persist Android-compatible AWG defaults
latest_vps_applied_package_smoked_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
package_name=dist/amn2-vps-update-and-smoke-kit-187949b.zip
package_sha256=7FA073E4C66C0981673061D167D525BB9BCD6DFDDAA075E15701F0C2608E2E82
```

## Правило поведения

Пока оператор не дал новый явный gate:

- не выполнять live VPS/SSH command;
- не выполнять destructive VPS/provider action;
- не загружать и не применять package;
- не перезапускать сервисы;
- не открывать public exposure;
- не менять firewall/listener/TLS/reverse proxy/Cloudflare/ngrok;
- не выполнять config delivery;
- не выводить `.conf`, QR, `vpn://`, private key, PSK, token или password;
- не выполнять Telegram live send;
- не запускать bot polling;
- не менять Telegram profile/media;
- не выполнять backup restore/import/reboot;
- не выполнять provider rebuild;
- не менять production peer/user;
- не начинать broader rollout.

## Что можно делать без gate

Можно:

- читать существующие Phase 8 evidence;
- отвечать оператору на русском;
- готовить docs-only/status-only пояснения;
- формировать будущую рекомендацию, но не открывать gate без явного запроса.

## Текущая рекомендация

```text
current_recommendation=ждать_запроса_оператора
next_action=не_открывать_ничего_без_явного_именованного_gate
```
