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

## Decision matrix

| Gate result | Что делать с branch | Что делать с интеграцией |
| --- | --- | --- |
| `verified-live` | Готовить merge/PR `codex/remote-operation-vps-gate-prep` -> `codex-vps-test-prep` | Разрешить следующий read-only integration slice |
| `dry-run-only-pass` | Не merge как live-verified; оставить branch candidate | Можно продолжать docs/privacy design, но не write/API integration |
| `needs-fix` | Не merge; открыть fix slice поверх candidate или новой ветки | Блокировать KYORESUAS/PRVTPRO integration до повторного gate |

## Merge checklist for `verified-live`

- [ ] AMN3 evidence записана без секретов.
- [ ] `amn2` candidate branch все еще указывает на проверенный head.
- [ ] `codex-vps-test-prep` не ушел вперед с конфликтующими runtime changes.
- [ ] Локально повторен focused remote-operation suite.
- [ ] Локально повторен full suite или явно записана причина, почему повторяется только focused suite.
- [ ] PR/merge description содержит VPS gate result и ссылку на AMN3 evidence.

## Blockers

Merge блокируется, если:

- test peer cleanup не подтвержден;
- вывод содержит raw PSK/private key/full config;
- apply/revoke затронул production peer;
- dry-run и live behavior расходятся по expected side effects;
- recovery note оказался неверным или отсутствующим.

## Next safe slice after merge

После `verified-live` и merge лучше начинать не с write lifecycle API, а с одного из read-only направлений:

1. Aggregate-only read-only metrics/API route shell по `research/amn2/read-only-metrics-privacy-classification.md`.
2. Controller-safe Local Agent runtime summary по `research/amn2/local-agent-runtime-metadata-alignment.md`.
3. Web-panel status UX для уже существующих read-only states.

Write lifecycle, public config links, backup/import/reboot и destructive operations остаются за отдельными gates.
