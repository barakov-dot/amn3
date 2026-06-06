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
current transfer head: 7764ae7 Cover integration status in API smoke
```

Активная рабочая ветка для установки/API smoke:

```text
branch: codex/read-only-api-route-shell
head: 2010d60 Add API VPS smoke evidence template
status: pushed; full local suite 588 passed; latest real VPS API-only smoke passed 2026-06-03, run_id=20260603T112418Z
working chat: Переводим AMN на API
```

AMN3 evidence: [API VPS smoke evidence 2026-06-03](api-vps-smoke-evidence-2026-06-03.md). Historical first pass: [API VPS smoke evidence 2026-06-02](api-vps-smoke-evidence-2026-06-02.md).

Merge result: read-only API shell fast-forward merged into `codex-vps-test-prep` at production head `5f12736`; API/web-panel finish slice then fast-forward merged into `codex-vps-test-prep` at production head `294803e`; Phase 1 read-only integration closeout then moved stable to `7764ae7`.

Живой VPS-цикл подтвержден: approve, working config, peer sync, disable/enable и выборочное удаление устройства работают на Docker AmneziaWG runtime.

Это значит, что дальнейшие lab-решения должны опираться на уже проверенное поведение `amn2`, а не возвращаться к live retest как к незакрытому риску.

## Артефакты

- [Decision log](decisions.md) - зафиксированные продуктовые решения по `amn2` transfer candidates.
- [Auth/security inventory snapshot](current-auth-security-inventory.md) - первый read-only снимок web-admin auth, CSRF, admin model, secret handling, backup и применимости 2FA.
- [Route/auth surface inventory](route-auth-surface-inventory.md) - первый проход по web routes, public email token endpoints и Telegram bot admin surface.
- [Route/Auth Policy Matrix](route-policy-matrix.md) - конкретная policy matrix для web, bot, public-token и CLI/operator surfaces.
- [Route/Auth machine-checkable tests plan](route-auth-machine-checkable-tests-plan.md) - next-gate plan для binding/drift tests поверх текущего `app/security/surface_policy.py`.
- [Secret surface inventory](secret-surface-inventory.md) - первый проход по secrets, redaction, encrypted backup, email tokens, config delivery и 2FA implications.
- [Secret inventory registry implementation](secret-inventory-registry-implementation.md) - local-only `amn2` branch/commit/test evidence для machine-checkable secret inventory без route expansion.
- [KYORESUAS API integration priority plan](kyoresuas-api-integration-priority-plan.md) - новый приоритет API lane: native read-only aggregate route shell без копирования upstream code.
- `amn2/docs/API_VPS_SMOKE_EVIDENCE.ru.md` - evidence template для текущей ветки `codex/read-only-api-route-shell`.
- [AMN2 VPS Operator API Smoke](../../docs/AMN2_VPS_OPERATOR_API_SMOKE.ru.md) - инструкция и безопасный operator script для запуска VPS loopback API smoke без передачи доступа.
- [AMN2 VPS API Update And Smoke](../../docs/AMN2_VPS_API_UPDATE_AND_SMOKE.ru.md) - update+smoke kit для VPS, где `/opt/amn2` еще не содержит `app/api`.
- [Backup/import dangerous API design](backup-import-dangerous-api-design.md) - policy boundary для metadata/redacted/full backup, restore preview и dangerous import/apply.
- [Backup/import policy contract implementation](backup-import-policy-contract-implementation.md) - local-only `amn2` branch/commit/test evidence для no-route backup/import policy registry and restore/import preview contract.
- [Config delivery inventory](config-delivery-inventory.md) - первый проход по выдаче VPN config через bot, email, QR, `vpn://` link, recovery token и template preview.
- [Manager config export contract](manager-config-export-contract.md) - typed result boundary для `.conf`, QR, `vpn://` и future protocol manager export artifacts.
- [Manager config export contract implementation](manager-config-export-contract-implementation.md) - local-only `amn2` branch/commit/test evidence для no-route typed export adapter.
- [Public/self-service config delivery policy](public-self-service-config-delivery-policy.md) - policy gate для share/self-service delivery без открытия public config routes.
- [Public config delivery policy contract implementation](public-config-delivery-policy-contract-implementation.md) - local-only `amn2` branch/commit/test evidence для no-route share-token/policy contract.
- [Redaction coverage plan](redaction-coverage-plan.md) - P0-план покрытия `.conf`, QR, `vpn://`, tokens, Local Agent headers, command output и diagnostics перед расширением remote operations.
- [Remote operations inventory](remote-operations-inventory.md) - первый проход по SSH/server apply flows, dry-run, health checks, peer apply/revoke, traffic collection, audit, redaction и rollback gaps.
- [Local-only task priority](local-only-task-priority.md) - приоритетный список локально выполняемых задач перед controlled real VPS verification gate.
- [Remote operation VPS gate runbook](vps-gate-remote-operation-dry-run-audit.md) - подготовленный checklist для реального VPS-теста ветки `codex/remote-operation-vps-gate-prep`.
- [Remote operation VPS gate evidence 2026-06-04](remote-operation-vps-gate-evidence-2026-06-04.md) - real VPS Phase 1 read-only/dry-run evidence for `7281254`, decision `dry-run-only-pass`.
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
- [API/Web panel finish plan](../../docs/superpowers/plans/2026-06-04-amn2-api-web-panel-finish.md) - следующий безопасный `amn2` implementation slice: web-admin API readiness/status и API token lifecycle UI.
- [API/Web panel finish implementation](api-web-panel-finish-implementation.md) - pushed `amn2/codex/api-web-panel-finish`, commit `294803e`, merged into stable `codex-vps-test-prep`, local gate evidence.
- [API/Web panel VPS evidence 2026-06-04](api-web-panel-vps-evidence-2026-06-04.md) - real VPS API loopback smoke and web-admin API readiness/API tokens route check for stable head `294803e`.
- [Phase 1 closeout 2026-06-04](phase-1-closeout-2026-06-04.md) - `7764ae7` follow-up: `/api/integration/status` is covered by API smoke and current update+smoke kit is published.
- [Next chat Phase 2 VPS live gate](../../docs/NEXT_CHAT_AMN2_PHASE_2_VPS_LIVE.ru.md) - one-copy handoff for the separate live single test peer apply/revoke chat.
- [Remote partial-failure contract evidence 2026-06-06](remote-partial-failure-contract-2026-06-06.md) - local-only AMN2 branch `codex/remote-partial-failure-contract`, commit `1a193b9`, focused `70 passed`; fast-forward merged into stable.
- [Remote partial-failure contract VPS package 2026-06-06](remote-partial-failure-contract-vps-package-2026-06-06.md) - AMN3 update+smoke kit for stable `1a193b9`; package published and read-only VPS-smoked.
- [Remote partial-failure contract VPS smoke 2026-06-06](remote-partial-failure-contract-vps-smoke-evidence-2026-06-06.md) - real VPS read-only update/smoke pass for stable `1a193b9`, `run_id=20260606T154636Z`.
- [API/Web panel VPS test runbook](../../docs/AMN2_API_WEB_PANEL_VPS_TEST_RUNBOOK.ru.md) - что делать на VPS при будущей проверке API/web-panel slice через loopback и SSH tunnel.
- [Transfer backlog](transfer-backlog.md) - очередь переноса lab-решений в `amn2`.

## Следующие рабочие шаги

Текущее решение: 2FA для web-admin поставлена на паузу, implementation plan для нее не пишем до отдельного решения.

Текущий фокус после verified VPS cycle, read-only `RemoteOperationRunner` baseline, redaction coverage, state-changing metadata, partial-failure, dry-run/audit metadata, web-panel safety, scoped API token storage local slices и read-only API route shell:

1. Не расширять API за пределы merged read-only aggregate shell до отдельного route/secret/remote-write gate.
2. API/web-panel finish slice реализован, запушен и fast-forward merged: `amn2/codex/api-web-panel-finish`, commit `294803e`, evidence `api-web-panel-finish-implementation.md`.
3. AMN3 VPS update/smoke package rebuilt from production head `7764ae7`.
4. Real VPS API/web-panel gate для `294803e` пройден: API loopback smoke `run_id=20260604T102355Z`, web-admin `API readiness` и `API tokens` доступны; evidence `api-web-panel-vps-evidence-2026-06-04.md`.
5. VPS update/smoke package `7764ae7` is the current package; historical `294803e` and `5f12736` remain evidence baselines.
6. Controlled real VPS verification gate Phase 1 для `codex/remote-operation-vps-gate-prep` пройден как `dry-run-only-pass`; evidence `remote-operation-vps-gate-evidence-2026-06-04.md`.
7. Backup/import policy registry, restore-preview contract и machine-checkable secret inventory уже выполнены; web/API full backup, restore apply, import apply, route expansion, secret-bearing output и live VPS write flows остаются закрытыми до отдельных gates.

## Неактуальный риск

Старые формулировки `implemented-needs-live-retest` считаются историческими: базовый live VPS cycle закрыт и помечен тегом `vps-live-cycle-verified`.
