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
current source-overlay transfer head: f7f6131 Update integration status for c92 manual prelaunch
current source-overlay update+smoke kit: dist/amn2-vps-update-and-smoke-kit-f7f6131.zip, read-only-vps-smoke-pass
last VPS-smoked runtime/source: f7f6131 Update integration status for c92 manual prelaunch, run_id=20260607T203730Z, latest_repeat_api_smoke_run_id=20260607T204300Z, checked_routes=6
previous VPS-smoked runtime/source: c92bd1a Bind web admin systemd to loopback, run_id=20260607T182131Z, checked_routes=6
current amn2 git head: f7f6131 Update integration status for c92 manual prelaunch
current amn2 git head status: read-only status visibility, VPS source-overlay-smoked
current app-code read-only smoke slice: 62ff184 Update controlled prod status visibility
git-checkout VPS smoke: /opt/amn2-git, checked_routes=6, status=passed
current source-overlay package: dist/amn2-vps-update-and-smoke-kit-f7f6131.zip
current package sha256: 19BF96A7E1057C042B89630BF80ADC7A9F5A09A62436E33A8555D7E2991AF282
previous c92 source-overlay package: dist/amn2-vps-update-and-smoke-kit-c92bd1a.zip, read-only-vps-smoke-pass
previous c92 package sha256: EC48DBA7C91F189512AB77EB5490432C85DA79F987068A98C1CC7F3082387F12
source-overlay promotion for web-admin loopback systemd: read-only-vps-smoke-pass
manual runtime validation: passed on mirror; web/bot run manually, systemd not used, direct public 3030/3040 exposure no
```

Активная рабочая ветка для установки/API smoke:

```text
branch: codex/read-only-api-route-shell
head: 2010d60 Add API VPS smoke evidence template
status: pushed; full local suite 588 passed; latest real VPS API-only smoke passed 2026-06-03, run_id=20260603T112418Z
working chat: Переводим AMN на API
```

AMN3 evidence: [API VPS smoke evidence 2026-06-03](api-vps-smoke-evidence-2026-06-03.md). Historical first pass: [API VPS smoke evidence 2026-06-02](api-vps-smoke-evidence-2026-06-02.md).

Merge result: read-only API shell fast-forward merged into `codex-vps-test-prep` at production head `5f12736`; API/web-panel finish slice then fast-forward merged into `codex-vps-test-prep` at production head `294803e`; Phase 1 read-only integration closeout then moved stable to `7764ae7`; remote partial-failure contract moved stable to `1a193b9`; controlled-prod integration status update moved stable to `32d01fd` and passed read-only VPS smoke; mapper-only Local Agent runtime summary moved stable to `c8a6363` and passed read-only VPS smoke; controlled-prod status visibility moved stable to `42ffa65` and passed source-overlay VPS smoke; web-admin loopback systemd safety follow-up moved stable to `c92bd1a` and passed source-overlay VPS smoke.

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
- [Integration status controlled prod update 2026-06-06](integration-status-controlled-prod-update-2026-06-06.md) - AMN2 stable `32d01fd`, local tests green, AMN3 update+smoke kit published, read-only VPS smoke passed `run_id=20260606T185114Z`.
- [Local Agent runtime summary package 2026-06-06](local-agent-runtime-summary-vps-package-2026-06-06.md) - AMN2 stable `c8a6363`, package-ready and read-only VPS-smoked.
- [c8a6363 VPS smoke preflight 2026-06-06](c8a6363-vps-smoke-preflight-2026-06-06.md) - local package preflight passed; later superseded by real VPS smoke evidence.
- [c8a6363 VPS smoke evidence 2026-06-06](local-agent-runtime-summary-vps-smoke-evidence-2026-06-06.md) - real VPS read-only update/smoke pass for stable `c8a6363`, `run_id=20260606T202040Z`.
- [Controlled prod readiness 2026-06-06](controlled-prod-readiness-2026-06-06.md) - operator-only prod gate is recorded as `controlled-prod-ready`; historical decision baseline was `c8a6363`, later superseded by VPS-smoked source overlay `42ffa65`.
- [Controlled prod reverse proxy confirmation 2026-06-07](controlled-prod-reverse-proxy-confirmation-2026-06-07.md) - web/admin access is through approved HTTPS reverse proxy; public API port `3040` is not exposed.
- [Controlled prod ready 2026-06-07](controlled-prod-ready-2026-06-07.md) - final operator-only decision `controlled-prod-ready`; recovery path known; continue only read-only next slice.
- [Controlled prod status visibility git-checkout smoke 2026-06-07](controlled-prod-status-visibility-git-checkout-smoke-2026-06-07.md) - AMN2 current git head `42ffa65`, app-code slice `62ff184`, real VPS git-checkout smoke pass on `/opt/amn2-git`; later promoted through source-overlay smoke.
- [Controlled prod status visibility VPS package 2026-06-07](controlled-prod-status-visibility-vps-package-2026-06-07.md) - AMN3 update+smoke kit for `42ffa65`; package prepared for source-overlay gate.
- [Controlled prod status visibility VPS smoke 2026-06-07](controlled-prod-status-visibility-vps-smoke-evidence-2026-06-07.md) - real VPS source-overlay update/smoke pass for `42ffa65`, `run_id=20260607T165625Z`.
- [Controlled prod status visibility repeat VPS smoke 2026-06-07](controlled-prod-status-visibility-vps-repeat-smoke-2026-06-07.md) - repeat read-only API smoke pass for the same `42ffa65` source overlay, `run_id=20260607T165807Z`.
- [Web-admin loopback systemd VPS package 2026-06-07](web-admin-loopback-systemd-vps-package-2026-06-07.md) - AMN2 `c92bd1a`, package prepared and read-only VPS-smoked for promoting loopback web-admin systemd template before controlled production launch.
- [Web-admin loopback systemd VPS smoke 2026-06-07](web-admin-loopback-systemd-vps-smoke-evidence-2026-06-07.md) - real VPS source-overlay update/smoke pass for `c92bd1a`, `run_id=20260607T182131Z`, `checked_routes=6`.
- [c92bd1a manual prelaunch evidence 2026-06-07](c92bd1a-manual-prelaunch-evidence-2026-06-07.md) - validation VPS manual runtime pass: backup, safe preflight, API smoke cycle, manual web `/login=200`, bot process present, loopback-only web/admin, public `3030`/`3040` exposure no; `systemd` not used.
- [Manual prelaunch integration status 2026-06-07](manual-prelaunch-integration-status-2026-06-07.md) - AMN2 `f7f6131` read-only status update for `/api/integration/status` and web `/integration-status`; VPS source-overlay smoke passed.
- [f7f6131 status alignment VPS package 2026-06-07](f7f6131-status-alignment-vps-package-2026-06-07.md) - AMN3 update+smoke kit for `f7f6131`; VPS source-overlay smoke passed.
- [f7f6131 status alignment VPS smoke 2026-06-07](f7f6131-status-alignment-vps-smoke-evidence-2026-06-07.md) - real VPS source-overlay update/smoke pass for `f7f6131`, `run_id=20260607T203730Z`, latest repeat API smoke `20260607T204300Z`, `checked_routes=6`.
- [API/Web panel VPS test runbook](../../docs/AMN2_API_WEB_PANEL_VPS_TEST_RUNBOOK.ru.md) - что делать на VPS при будущей проверке API/web-panel slice через loopback и SSH tunnel.
- [Transfer backlog](transfer-backlog.md) - очередь переноса lab-решений в `amn2`.

## Следующие рабочие шаги

Текущее решение: 2FA для web-admin поставлена на паузу, implementation plan для нее не пишем до отдельного решения.

Текущий фокус после verified VPS cycle, read-only `RemoteOperationRunner` baseline, redaction coverage, state-changing metadata, partial-failure, dry-run/audit metadata, web-panel safety, scoped API token storage local slices и read-only API route shell:

1. Не расширять API за пределы merged read-only aggregate shell до отдельного route/secret/remote-write gate.
2. API/web-panel finish slice реализован, запушен и fast-forward merged: `amn2/codex/api-web-panel-finish`, commit `294803e`, evidence `api-web-panel-finish-implementation.md`.
3. AMN3 VPS update/smoke package rebuilt from current production head `f7f6131`; read-only VPS smoke passed, `run_id=20260607T203730Z`, latest repeat API smoke `20260607T204300Z`, `checked_routes=6`.
4. Real VPS API/web-panel gate для `294803e` пройден: API loopback smoke `run_id=20260604T102355Z`, web-admin `API readiness` и `API tokens` доступны; evidence `api-web-panel-vps-evidence-2026-06-04.md`.
5. VPS update/smoke package `f7f6131` is now the current VPS-smoked runtime/source; `c92bd1a`, `42ffa65`, `c8a6363`, `32d01fd`, `294803e`, `5f12736`, and `7764ae7` remain historical evidence baselines.
5.1. Validation VPS manual runtime passed for `c92bd1a`; web/admin and bot run manually, `systemd` is not used, direct public `3030`/`3040` exposure is not present, and public API port `3040` remains closed.
5.2. Controlled prod decision recorded as `controlled-prod-ready`; recovery path is known. Continue with read-only next slice, not write/config/backup/agent expansion.
5.3. AMN3 package `f7f6131` passed read-only status-alignment source-overlay smoke; write/config/backup/agent/service-mode gates remain closed.
6. Controlled real VPS verification gate Phase 1 для `codex/remote-operation-vps-gate-prep` пройден как `dry-run-only-pass`; evidence `remote-operation-vps-gate-evidence-2026-06-04.md`.
7. Backup/import policy registry, restore-preview contract и machine-checkable secret inventory уже выполнены; web/API full backup, restore apply, import apply, route expansion, secret-bearing output и live VPS write flows остаются закрытыми до отдельных gates.

## Неактуальный риск

Старые формулировки `implemented-needs-live-retest` считаются историческими: базовый live VPS cycle закрыт и помечен тегом `vps-live-cycle-verified`.
