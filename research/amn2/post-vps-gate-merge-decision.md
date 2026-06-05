# Post-VPS Gate Merge Decision

Дата: 2026-06-01.

Назначение: заранее зафиксировать, что делать после реального VPS gate ветки `codex/remote-operation-vps-gate-prep`.

## Inputs

Перед решением нужны:

- заполненный `research/amn2/vps-gate-evidence-checklist.md`;
- redacted output read-only/dry-run команд;
- если Phase 2 запускалась, redacted output apply/sync/revoke/sync;
- финальный статус test peer;
- явное решение: `verified-live`, `needs-fix` или `dry-run-only-pass`.

Статус 2026-06-04: Phase 1 evidence recorded as `dry-run-only-pass` in `research/amn2/remote-operation-vps-gate-evidence-2026-06-04.md`; Phase 2 live single peer apply/revoke was not run.

Статус 2026-06-05: Phase 2 live single disposable test peer apply/revoke passed on current stable `7764ae7`; evidence recorded in `research/amn2/phase-2-live-vps-gate-evidence-2026-06-05.md`. The historical `7281254` candidate is already merged into stable via `708c98e` and is an ancestor of `7764ae7`, so there is no separate old-branch merge to perform for the tested code path.

## Decision matrix

| Gate result | Что делать с branch | Что делать с интеграцией |
| --- | --- | --- |
| `verified-live` | Готовить merge/PR `codex/remote-operation-vps-gate-prep` -> `codex-vps-test-prep` | Разрешить следующий read-only integration slice |
| `dry-run-only-pass` | Не merge как live-verified; оставить branch candidate | Можно продолжать docs/privacy design, но не write/API integration |
| `needs-fix` | Не merge; открыть fix slice поверх candidate или новой ветки | Блокировать KYORESUAS/PRVTPRO integration до повторного gate |

## Merge checklist for `verified-live`

- [x] AMN3 evidence записана без секретов.
- [x] `amn2` candidate branch все еще указывает на проверенный head.
- [x] `codex-vps-test-prep` не ушел вперед с конфликтующими runtime changes.
- [x] Локально повторен focused remote-operation suite.
- [x] Локально повторен full suite или явно записана причина, почему повторяется только focused suite.
- [ ] PR/merge description содержит VPS gate result и ссылку на AMN3 evidence.

Local verification after Phase 2:

```text
focused remote-operation suite: 71 passed
full suite: not rerun, because this turn changed AMN3 evidence/status documentation only and did not modify `amn2` production code
```

## Blockers

Merge блокируется, если:

- test peer cleanup не подтвержден;
- вывод содержит raw PSK/private key/full config;
- apply/revoke затронул production peer;
- dry-run planned command preview содержит secret-bearing args/output;
- dry-run и live behavior расходятся по expected side effects;
- recovery note оказался неверным или отсутствующим.

## Next safe slice after merge

API integration из `VPN Ops Lab — KYORESUAS-API` является приоритетной product lane, но начинать нужно не с write lifecycle API, а с read-only направления:

1. Aggregate-only read-only metrics/API route shell по `research/amn2/read-only-metrics-privacy-classification.md` and `research/amn2/kyoresuas-api-integration-priority-plan.md`.
2. Controller-safe Local Agent runtime summary по `research/amn2/local-agent-runtime-metadata-alignment.md`.
3. Route-connected scoped API token lifecycle gate по `research/amn2/api-token-rotation-revoke-policy.md`, если read-only API route shell требует bearer-token доступа.
4. Web-panel status UX для уже существующих read-only states.

Write lifecycle, public config links, backup/import/reboot и destructive operations остаются за отдельными gates.
