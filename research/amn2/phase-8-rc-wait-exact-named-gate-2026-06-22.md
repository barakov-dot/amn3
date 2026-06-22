# Phase 8: ожидание точного именованного gate

Дата: 2026-06-22.

Статус: `active-wait-exact-named-gate-docs-only`.

Scope: AMN2 удерживается в `private/operator RC
launch-ready-with-explicit-limitations` на основе существующих Phase 8 evidence.
Live VPS/SSH command, destructive action, package upload/apply, service
restart, public exposure, config delivery, Telegram live send, bot polling,
Telegram profile/media mutation, backup restore/import/reboot, provider
mutation, production peer/user mutation и secret-bearing output не выполнялись.

## Созданный документ

```text
docs/AMN2_PRIVATE_OPERATOR_RC_WAIT_EXACT_GATE.ru.md
```

## Зафиксированная команда

```text
ОЖИДАНИЕ_ТОЧНОГО_ИМЕНОВАННОГО_GATE

Использовать только существующие Phase 8 evidence.
Не открывать live/destructive/config/Telegram send/public exposure gates.
Держать AMN2 в статусе private/operator RC launch-ready-with-explicit-limitations
до тех пор, пока оператор явно не запросит конкретный именованный gate.
```

## Статус

```text
wait_exact_named_gate_status=active-docs-only
ready_hold_status=active-docs-only
phase8_final_status=launch-ready-with-explicit-limitations
private_operator_rc_launch_ready=true
public_launch_status=not-approved
blocked_with_exact_remaining_blockers=false
remaining_blockers_inside_listed_limitations=none
```

## Head на старте

```text
amn3_evidence_head_before_wait_exact_gate=17988d7 Record private operator RC ready hold
amn2_current_fixes_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447 Persist Android-compatible AWG defaults
latest_vps_applied_package_smoked_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
package_name=dist/amn2-vps-update-and-smoke-kit-187949b.zip
package_sha256=7FA073E4C66C0981673061D167D525BB9BCD6DFDDAA075E15701F0C2608E2E82
```

## Условие выхода

Выход из ожидания разрешен только через новый exact named gate, явно
запрошенный оператором.
