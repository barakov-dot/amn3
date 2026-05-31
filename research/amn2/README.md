# `amn2`: текущий production-контекст

Этот раздел хранит read-only inventory текущего `amn2`, чтобы идеи из `VPS-OPS-LAB` сравнивались с реальной архитектурой, а не переносились по впечатлению от upstream-проектов.

## Правила

- Production-код `amn2` из этого раздела не меняется.
- `.env` и другие файлы с возможными секретами не читаются и не переносятся в заметки.
- В заметках фиксируются только пути, имена настроек, классы риска, найденные patterns и test surfaces.
- Любая функция из lab переходит к implementation plan только после license gate, value gate, risk gate, architecture fit и test plan.

## Текущий verified baseline

Актуальная production-точка:

```text
repo: C:\Users\SooL\Documents\Amneziya
branch: codex-vps-test-prep
latest: 91aeb3e Document VPS verified tag
stable tag: vps-live-cycle-verified -> d6eda20 Document verified VPS live cycle
handoff: docs/NEXT_CHAT_HANDOFF.ru.md
```

Живой VPS-цикл подтвержден: approve, working config, peer sync, disable/enable и выборочное удаление устройства работают на Docker AmneziaWG runtime.

Это значит, что дальнейшие lab-решения должны опираться на уже проверенное поведение `amn2`, а не возвращаться к live retest как к незакрытому риску.

## Артефакты

- [Decision log](decisions.md) - зафиксированные продуктовые решения по `amn2` transfer candidates.
- [Auth/security inventory snapshot](current-auth-security-inventory.md) - первый read-only снимок web-admin auth, CSRF, admin model, secret handling, backup и применимости 2FA.
- [Route/auth surface inventory](route-auth-surface-inventory.md) - первый проход по web routes, public email token endpoints и Telegram bot admin surface.
- [Route/Auth Policy Matrix](route-policy-matrix.md) - конкретная policy matrix для web, bot, public-token и CLI/operator surfaces.
- [Secret surface inventory](secret-surface-inventory.md) - первый проход по secrets, redaction, encrypted backup, email tokens, config delivery и 2FA implications.
- [Config delivery inventory](config-delivery-inventory.md) - первый проход по выдаче VPN config через bot, email, QR, `vpn://` link, recovery token и template preview.
- [Redaction coverage plan](redaction-coverage-plan.md) - P0-план покрытия `.conf`, QR, `vpn://`, tokens, Local Agent headers, command output и diagnostics перед расширением remote operations.
- [Remote operations inventory](remote-operations-inventory.md) - первый проход по SSH/server apply flows, dry-run, health checks, peer apply/revoke, traffic collection, audit, redaction и rollback gaps.
- [Local-only task priority](local-only-task-priority.md) - приоритетный список локально выполняемых задач перед controlled real VPS verification gate.
- [Transfer backlog](transfer-backlog.md) - очередь переноса lab-решений в `amn2`.

## Следующие рабочие шаги

Текущее решение: 2FA для web-admin поставлена на паузу, implementation plan для нее не пишем до отдельного решения.

Текущий фокус после verified VPS cycle, read-only `RemoteOperationRunner` baseline и verified redaction coverage first slice:

1. Исполнить local-only phase для partial-failure/rollback contract: typed contract, fake runner, DB simulations, dry-run/audit metadata, redaction и full local suite.
2. Только после local green suite провести controlled real VPS verification gate на тестовом peer/device.
3. До live Docker apply/revoke описать Docker manager: persistent config path, backup, reload/apply semantics и rollback note.
4. Затем вернуться к route policy coverage tests.

## Неактуальный риск

Старые формулировки `implemented-needs-live-retest` считаются историческими: базовый live VPS cycle закрыт и помечен тегом `vps-live-cycle-verified`.
