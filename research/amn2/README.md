# `amn2`: текущий production-контекст

Этот раздел хранит read-only inventory текущего `amn2`, чтобы идеи из `vpn-ops-lab` сравнивались с реальной архитектурой, а не переносились по впечатлению от upstream-проектов.

## Правила

- Production-код `amn2` из этого раздела не меняется.
- `.env` и другие файлы с возможными секретами не читаются и не переносятся в заметки.
- В заметках фиксируются только пути, имена настроек, классы риска, найденные patterns и test surfaces.
- Любая функция из lab переходит к implementation plan только после license gate, value gate, risk gate, architecture fit и test plan.

## Артефакты

- [Auth/security inventory snapshot](current-auth-security-inventory.md) - первый read-only снимок web-admin auth, CSRF, admin model, secret handling, backup и применимости 2FA.
- [Route/auth surface inventory](route-auth-surface-inventory.md) - первый проход по web routes, public email token endpoints и Telegram bot admin surface.
- [Secret surface inventory](secret-surface-inventory.md) - первый проход по secrets, redaction, encrypted backup, email tokens, config delivery и 2FA implications.

## Следующие рабочие шаги

1. Config delivery inventory: все места, где config создается, отображается, отправляется, скачивается или восстанавливается.
2. Remote operations inventory: SSH/sudo/server apply flows, dry-run, audit, redaction и rollback notes.
3. Только после этих шагов - отдельный implementation plan для первой безопасной доработки в `amn2`.
