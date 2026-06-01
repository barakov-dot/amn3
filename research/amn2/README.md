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
current transfer head: 1fdcde5 Add scoped API token storage contract
```

Живой VPS-цикл подтвержден: approve, working config, peer sync, disable/enable и выборочное удаление устройства работают на Docker AmneziaWG runtime.

Это значит, что дальнейшие lab-решения должны опираться на уже проверенное поведение `amn2`, а не возвращаться к live retest как к незакрытому риску.

## Артефакты

- [Decision log](decisions.md) - зафиксированные продуктовые решения по `amn2` transfer candidates.
- [Auth/security inventory snapshot](current-auth-security-inventory.md) - первый read-only снимок web-admin auth, CSRF, admin model, secret handling, backup и применимости 2FA.
- [Route/auth surface inventory](route-auth-surface-inventory.md) - первый проход по web routes, public email token endpoints и Telegram bot admin surface.
- [Route/Auth Policy Matrix](route-policy-matrix.md) - конкретная policy matrix для web, bot, public-token и CLI/operator surfaces.
- [Route/Auth machine-checkable tests plan](route-auth-machine-checkable-tests-plan.md) - next-gate plan для binding/drift tests поверх текущего `app/security/surface_policy.py`.
- [Secret surface inventory](secret-surface-inventory.md) - первый проход по secrets, redaction, encrypted backup, email tokens, config delivery и 2FA implications.
- [Backup/import dangerous API design](backup-import-dangerous-api-design.md) - policy boundary для metadata/redacted/full backup, restore preview и dangerous import/apply.
- [Config delivery inventory](config-delivery-inventory.md) - первый проход по выдаче VPN config через bot, email, QR, `vpn://` link, recovery token и template preview.
- [Manager config export contract](manager-config-export-contract.md) - typed result boundary для `.conf`, QR, `vpn://` и future protocol manager export artifacts.
- [Manager config export contract implementation](manager-config-export-contract-implementation.md) - local-only `amn2` branch/commit/test evidence для no-route typed export adapter.
- [Public/self-service config delivery policy](public-self-service-config-delivery-policy.md) - policy gate для share/self-service delivery без открытия public config routes.
- [Public/self-service config delivery policy implementation](public-self-service-config-delivery-policy-implementation.md) - local-only `amn2` branch/commit/test evidence для no-route share-token/policy contract.
- [Public config delivery policy contract implementation](public-config-delivery-policy-contract-implementation.md) - local-only `amn2` branch/commit/test evidence для no-route share-token/policy contract.
- [Redaction coverage plan](redaction-coverage-plan.md) - P0-план покрытия `.conf`, QR, `vpn://`, tokens, Local Agent headers, command output и diagnostics перед расширением remote operations.
- [Remote operations inventory](remote-operations-inventory.md) - первый проход по SSH/server apply flows, dry-run, health checks, peer apply/revoke, traffic collection, audit, redaction и rollback gaps.
- [Local-only task priority](local-only-task-priority.md) - приоритетный список локально выполняемых задач перед controlled real VPS verification gate.
- [Remote operation VPS gate runbook](vps-gate-remote-operation-dry-run-audit.md) - подготовленный checklist для реального VPS-теста ветки `codex/remote-operation-vps-gate-prep`.
- [VPS gate evidence checklist](vps-gate-evidence-checklist.md) - короткая форма фиксации pass/fail результата после реального VPS gate.
- [Post-VPS gate merge decision](post-vps-gate-merge-decision.md) - правила merge/PR после `verified-live`, `dry-run-only-pass` или `needs-fix`.
- [Docker manager design note](docker-manager-design-note.md) - минимальный safety contract для будущего Docker AmneziaWG manager.
- [SSH host key enrollment design](ssh-host-key-enrollment-design.md) - explicit enrollment/pinning policy перед VPS onboarding и remote-operation expansion.
- [SSH host key verifier implementation](ssh-host-key-verifier-implementation.md) - local-only `amn2` verifier branch/commit/test evidence для host key fingerprint/pin проверки.
- [Neighbor chat VPS gate handoff](neighbor-chat-vps-gate-handoff.md) - что ждут KYORESUAS/PRVTPRO направления перед интеграцией.
- [Read-only metrics privacy classification](read-only-metrics-privacy-classification.md) - privacy gate для будущего aggregate-only metrics/API route shell.
- [Local Agent runtime metadata alignment](local-agent-runtime-metadata-alignment.md) - safety boundary для будущего controller-safe Local Agent runtime summary.
- [API token rotation/revoke policy](api-token-rotation-revoke-policy.md) - lifecycle gate для scoped API tokens и Local Agent tokens перед route expansion.
- [API token lifecycle gate implementation](api-token-lifecycle-gate-implementation.md) - local-only `amn2` branch/commit/test evidence для expiry, revoke, rotation и owner inheritance.
- [Transfer backlog](transfer-backlog.md) - очередь переноса lab-решений в `amn2`.

## Следующие рабочие шаги

Текущее решение: 2FA для web-admin поставлена на паузу, implementation plan для нее не пишем до отдельного решения.

Текущий фокус после verified VPS cycle, read-only `RemoteOperationRunner` baseline, redaction coverage, state-changing metadata, partial-failure, dry-run/audit metadata, web-panel safety и scoped API token storage local slices:

1. Выполнить controlled real VPS verification gate по `vps-gate-remote-operation-dry-run-audit.md` на ветке `codex/remote-operation-vps-gate-prep`.
2. Начать VPS gate с read-only check и dry-run apply/revoke preview; single apply/revoke выполнять только после отдельного подтверждения оператора.
3. Зафиксировать VPS evidence через `vps-gate-evidence-checklist.md`.
4. Принять merge/PR решение по `post-vps-gate-merge-decision.md`.
5. Пока VPS не готов, следующий local-only кандидат - backup/import policy registry and restore-preview contract; web/API full backup, restore apply и import apply не открывать.

## Неактуальный риск

Старые формулировки `implemented-needs-live-retest` считаются историческими: базовый live VPS cycle закрыт и помечен тегом `vps-live-cycle-verified`.
