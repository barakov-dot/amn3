# `amn2` Transfer Backlog

Status-visibility update 2026-06-07: `amn2/codex-vps-test-prep` advanced to `42ffa65 Record git checkout smoke status`. The app-code read-only smoke slice is `62ff184 Update controlled prod status visibility`, which passed real VPS git-checkout smoke on `/opt/amn2-git` with `checked_routes=6`; AMN3 package `42ffa65` then passed safe source-overlay update/read-only smoke on `/opt/amn2`. That source overlay is now the previous status-visibility baseline, original `api_smoke_run_id=20260607T165625Z`, latest repeat `api_smoke_run_id=20260607T165807Z`. `c8a6363` is historical prior VPS-smoked runtime/source, `run_id=20260606T202040Z`; `32d01fd` and `1a193b9` are older historical baselines.

Follow-up 2026-06-07: `amn2/codex-vps-test-prep` advanced to `c92bd1a Bind web admin systemd to loopback` and the AMN3 package passed safe source-overlay update/read-only smoke on `/opt/amn2`. This is a controlled production launch safety slice: web/admin systemd template uses `127.0.0.1:3030` by default for the approved HTTPS reverse proxy mode. Package: `dist/amn2-vps-update-and-smoke-kit-c92bd1a.zip`, sha256 `EC48DBA7C91F189512AB77EB5490432C85DA79F987068A98C1CC7F3082387F12`; evidence `research/amn2/web-admin-loopback-systemd-vps-package-2026-06-07.md` and `research/amn2/web-admin-loopback-systemd-vps-smoke-evidence-2026-06-07.md`.

Manual runtime 2026-06-07: validation VPS `mirror` passed backup create/verify, safe preflight, API smoke-cycle summary with six read-only routes, manual web `/login` check on `127.0.0.1:3030`, and manual bot runtime check. `systemd` is not used in the current operator mode; direct public web `3030` and public API `3040` are not exposed. Evidence: `research/amn2/c92bd1a-manual-prelaunch-evidence-2026-06-07.md`.

Neighboring AMN2 status follow-up 2026-06-07: `amn2/codex-vps-test-prep` advanced to `f7f6131 Update integration status for c92 manual prelaunch`. This is a read-only status-visibility update to `/api/integration/status` and web `/integration-status`; it has now passed source-overlay update/read-only smoke on `/opt/amn2`. Evidence: `research/amn2/manual-prelaunch-integration-status-2026-06-07.md` and `research/amn2/f7f6131-status-alignment-vps-smoke-evidence-2026-06-07.md`.

Status-alignment package 2026-06-07: AMN3 update+smoke kit for `f7f6131` passed real VPS read-only smoke. Package: `dist/amn2-vps-update-and-smoke-kit-f7f6131.zip`, sha256 `19BF96A7E1057C042B89630BF80ADC7A9F5A09A62436E33A8555D7E2991AF282`; source sha256 `720B6C9FE3CADDBC65C19BDEC5B0C811D00C94EB0D095D6311DCD90DD77BE4E1`; package evidence `research/amn2/f7f6131-status-alignment-vps-package-2026-06-07.md`; smoke evidence `research/amn2/f7f6131-status-alignment-vps-smoke-evidence-2026-06-07.md`; `source_update_run_id=20260607T203721Z`, `api_smoke_run_id=20260607T203730Z`, `latest_repeat_api_smoke_run_id=20260607T204300Z`, `checked_routes=6`.

Target-server prep 2026-06-08: validation VPS source overlay should remain untouched after `f7f6131` pass. The new rented VPS starts a separate target-server prep gate using `docs/AMN2_TARGET_SERVER_PREP_GATE.ru.md`; detailed runbook `docs/AMN2_TARGET_SERVER_PREP_RUNBOOK.ru.md` is used only after safe precheck review, with evidence note `research/amn2/target-server-prep-gate-2026-06-08.md` and safe evidence template `research/amn2/target-server-prep-evidence-template-2026-06-08.md`. This gate covers bootstrap, read-only preflight, API loopback smoke, manual web/admin check and backup verify; service-mode `systemd`/reverse proxy remains a separate explicit decision.

Target-server bootstrap 2026-06-08: new target VPS partial bootstrap passed. Evidence: `research/amn2/target-server-bootstrap-evidence-2026-06-08.md`. Completed: base packages, Docker runtime installed with no containers, `/opt/amn2` venv, `f7f6131` source overlay, Python dependency install, CLI import, DB schema init, partial loopback API probe for `/api/servers` with token revoke and `forbidden_markers_count=0`, encrypted backup create/verify.

Target-server AWG2 runtime 2026-06-09: new target VPS runtime gate passed. Evidence: `research/amn2/target-server-awg2-runtime-smoke-evidence-2026-06-09.md`. Completed: `amnezia-awg2` Docker runtime built/started, `awg0` up, UDP `30001` listening, self-SSH for AMN2 local Docker operations passed, real target `servers.yml` created on the VPS and accepted by AMN2 loader, full read-only API loopback smoke passed with `run_id=20260609T043158Z`, `checked_routes=6`. Live peer apply/revoke remains a separate explicit gate.

Unified prod gate handoff 2026-06-08: prepare a future single decision chat after the active Phase 2 live gate returns a safe summary. Use `docs/AMN_UNIFIED_PROD_GATE_HANDOFF.ru.md` and evidence note `research/amn2/unified-prod-gate-handoff-2026-06-08.md`. Until then, live VPS commands remain owned by the Phase 2 chat; this AMN2/API chat stays integration dispatcher; PRVTPRO/Web Panel remains a candidate source, not a direct production-change source.

`42ffa65` VPS smoke 2026-06-07: source update preserved `.env`, `data/`, `venv/` and `servers.yml`; read-only API smoke passed with `checked_routes=6`, auth 401/403/401, listener `127.0.0.1:3040` loopback-only, audit safe, server DB sync passed. Repeat read-only smoke for the same source overlay also passed with `run_id=20260607T165807Z`. Evidence: `research/amn2/controlled-prod-status-visibility-vps-smoke-evidence-2026-06-07.md`; repeat evidence: `research/amn2/controlled-prod-status-visibility-vps-repeat-smoke-2026-06-07.md`.

`c8a6363` VPS smoke 2026-06-06: local package SHA/source SHA and source hygiene checks passed, then operator real VPS update/smoke passed with `VPS verdict: pass`. Evidence: `research/amn2/local-agent-runtime-summary-vps-smoke-evidence-2026-06-06.md`. The earlier preflight blocker is preserved as historical context at `research/amn2/c8a6363-vps-smoke-preflight-2026-06-06.md`.

Controlled prod decision 2026-06-07: web/admin access is through an operator-approved HTTPS reverse proxy, public API port `3040` is not exposed, recovery artifacts are present, and the final decision is `controlled-prod-ready`. Evidence: `research/amn2/controlled-prod-ready-2026-06-07.md`; access-path confirmation: `research/amn2/controlled-prod-reverse-proxy-confirmation-2026-06-07.md`.

Read-only integration status update 2026-06-06: `32d01fd` updates `/api/integration/status` to report `read_only_vps_smoked`, Phase 2 `verified_live`, and controlled-prod readiness pending without enabling write routes or write operations. AMN3 evidence is `research/amn2/integration-status-controlled-prod-update-2026-06-06.md`. The previous local-only operation-contract fast-forward remains recorded at `research/amn2/remote-partial-failure-contract-2026-06-06.md`.

```text
AMN3 package: dist/amn2-vps-update-and-smoke-kit-32d01fd.zip
sha256: BE59AF74001AC4F094C753B565A4E672194D823C4F65B6CB476F4FF01B310807
source zip: dist/amn2-codex-vps-test-prep-32d01fd-source.zip
source sha256: 034753DA7EC42ACF869519F43909EEFDC8A392A5665B2A33C935F8A058CCB99B
current source-overlay package: dist/amn2-vps-update-and-smoke-kit-f7f6131.zip
current source-overlay package sha256: 19BF96A7E1057C042B89630BF80ADC7A9F5A09A62436E33A8555D7E2991AF282
current source-overlay source sha256: 720B6C9FE3CADDBC65C19BDEC5B0C811D00C94EB0D095D6311DCD90DD77BE4E1
current source-overlay package status: read-only-vps-smoke-pass
local verification: focused deploy tests 11 passed; package SHA/source SHA/no-BOM/no-CRLF/no-forbidden-source-entry/test-extract checks passed
package evidence: research/amn2/web-admin-loopback-systemd-vps-package-2026-06-07.md
VPS result for c92bd1a: read-only-vps-smoke-pass, run_id 20260607T182131Z, checked_routes=6
VPS smoke evidence: research/amn2/web-admin-loopback-systemd-vps-smoke-evidence-2026-06-07.md
previous VPS-smoked runtime/source: 42ffa65, promotion run_id 20260607T165625Z, repeat run_id 20260607T165807Z, evidence research/amn2/controlled-prod-status-visibility-vps-smoke-evidence-2026-06-07.md
previous VPS-smoked runtime/source: 1a193b9, run_id 20260606T154636Z, evidence research/amn2/remote-partial-failure-contract-vps-smoke-evidence-2026-06-06.md
controlled prod readiness: controlled-prod-ready
manual runtime validation: passed; systemd not-used; web_process present; bot_process present; public 3030/3040 no
current AMN2 git head: f7f6131 Update integration status for c92 manual prelaunch
current AMN2 git head status: read-only status visibility, VPS source-overlay-smoked
current AMN2 git head evidence: research/amn2/manual-prelaunch-integration-status-2026-06-07.md
status-alignment package: dist/amn2-vps-update-and-smoke-kit-f7f6131.zip
status-alignment package sha256: 19BF96A7E1057C042B89630BF80ADC7A9F5A09A62436E33A8555D7E2991AF282
status-alignment source sha256: 720B6C9FE3CADDBC65C19BDEC5B0C811D00C94EB0D095D6311DCD90DD77BE4E1
status-alignment package status: read-only-vps-smoke-pass
status-alignment VPS smoke: passed, run_id 20260607T203730Z, latest_repeat_api_smoke_run_id 20260607T204300Z, checked_routes=6
current app-code read-only smoke slice: 62ff184 Update controlled prod status visibility
current VPS-smoked package/source: f7f6131, run_id 20260607T203730Z, latest_repeat_api_smoke_run_id 20260607T204300Z, checked_routes=6
git-checkout VPS smoke: 62ff184 pass on /opt/amn2-git, checked_routes=6
source-overlay package: dist/amn2-vps-update-and-smoke-kit-f7f6131.zip
source-overlay package sha256: 19BF96A7E1057C042B89630BF80ADC7A9F5A09A62436E33A8555D7E2991AF282
source-overlay source sha256: 720B6C9FE3CADDBC65C19BDEC5B0C811D00C94EB0D095D6311DCD90DD77BE4E1
source-overlay package status: read-only-vps-smoke-pass
controlled prod runbook: docs/AMN2_CONTROLLED_PROD_READINESS_RUNBOOK.ru.md
controlled prod evidence: research/amn2/controlled-prod-readiness-2026-06-06.md
controlled prod next chat: docs/NEXT_CHAT_AMN2_CONTROLLED_PROD_DECISION.ru.md
previous VPS-smoked source: 568c611, run_id 20260605T162742Z, evidence research/amn2/phase-2-post-psk-stdin-vps-smoke-evidence-2026-06-05.md
docs-only cleanup: 6b5b5b7 Document stdin PSK peer apply
local-only contract merge: 1a193b9 Add remote partial failure contract
read-only integration status update: 32d01fd Update integration status for controlled prod
```

Актуализация 2026-06-05: Phase 2 live single disposable test peer apply/revoke gate пройден на current stable `amn2/codex-vps-test-prep` head `7764ae7 Cover integration status in API smoke`.

```text
AMN3 evidence: research/amn2/phase-2-live-vps-gate-evidence-2026-06-05.md
result: verified-live
scope: exactly one disposable test peer apply/revoke, no production peer
```

Актуализация 2026-06-04: Phase 1 read-only/API/web-panel baseline закрыт на `amn2/codex-vps-test-prep` head `7764ae7 Cover integration status in API smoke`.

```text
AMN3 evidence: research/amn2/phase-1-closeout-2026-06-04.md
current update+smoke kit: dist/amn2-vps-update-and-smoke-kit-7764ae7.zip
sha256: 832E1B1F6516A02E0D6AA45672B8FF526DF15D27117D2063CE45F9966825A66A
```

Phase 2 live single test peer apply/revoke now has `verified-live` evidence for exactly one disposable peer. Старые строки `294803e` ниже остаются historical API/web-panel evidence.

Дата: 2026-06-02.

Назначение: единая очередь переноса AMNEZIYA-наработок и upstream-идей из AMN3 в production repo `amn2`.

Правило: AMN3 хранит статус, решение, plan, branch/commit/PR links и test evidence. Production-код остается в `C:\Users\SooL\Documents\Amneziya` / `barakov-dot/amn2`.

## Verified Production Baseline

Verified live `amn2` baseline:

```text
branch: codex-vps-test-prep
latest: 91aeb3e Document VPS verified tag
stable tag: vps-live-cycle-verified -> d6eda20 Document verified VPS live cycle
```

Текущий production head после merged API/VPS evidence transfer:

```text
5f12736 Record VPS API smoke evidence
```

В эту линию уже вошли PR #4/#5 по API token lifecycle и PR #6 по SSH host key verifier. Scoped API token storage `1fdcde5` остается важным baseline, но больше не является текущим production head.

Текущая active implementation branch для установки/API smoke:

```text
branch: codex/read-only-api-route-shell
remote branch: amn2/codex/read-only-api-route-shell
head: 2010d60 Add API VPS smoke evidence template
base: d0939d8 Merge pull request #6 from barakov-dot/codex/ssh-host-key-identity-verifier
status: merged into codex-vps-test-prep at 5f12736 after local tests and real VPS loopback API smoke
working chat: Переводим AMN на API
```

Актуализация 2026-06-03: latest real VPS API-only smoke passed на `/opt/amn2` через AMN3 operator script, `run_id=20260603T112418Z`; DB-only server config sync выполнен, preflight `skipped`, API/auth/scope/revoke/listener/audit `passed`, `VPS_APPLY_ENABLED=false`, raw token/header/hash/config/keys/PSK не публиковались. Evidence: `research/amn2/api-vps-smoke-evidence-2026-06-03.md`.

Live VPS cycle подтвержден на Docker AmneziaWG runtime:

- approve создает рабочий peer;
- config работает;
- `Working configs on server` обновляется сразу;
- `Run peer sync` подтверждает `confirmed live`;
- внешние Amnezia-created peer не удаляются;
- missing local device можно добавить на сервер;
- disable/enable работают;
- выборочное удаление устройства работает.

## Active Items

| Item | Статус | Target repo | Текущий artifact | Следующий шаг |
| --- | --- | --- | --- | --- |
| API readiness after verified live baseline | `implemented-historical-baseline` | AMN3 -> `amn2` | `research/amn2/api-readiness-audit-after-live-baseline.md`; Route/Auth matrix and read-only API shell already implemented | Использовать как historical decision source; VPS loopback API smoke для `codex/read-only-api-route-shell` passed 2026-06-02 |
| Main merge roadmap | `active-roadmap` | AMN3 -> `amn2` later | `docs/AMN2_MAIN_MERGE_ROADMAP.ru.md` | Использовать как порядок слияния API, web panel и operations |
| Local Amnezia Agent first slice | `merged-in-baseline` | `amn2` | merge PR #2, commits `3119ee6`, `ac2baa8` | Использовать как read-only baseline, не расширять до clients/configs без policy gate |
| Local Agent production wiring | `merged-in-baseline` | `amn2` | merge PR #3, head `8697b60` | Использовать как opt-in local runtime adapter boundary |
| VPS retest bundle | `verified-live-baseline` | `amn2` | commit `573c368` | Не трогать без изменения VPS apply/sync логики |
| Config defaults from `.env` | `verified-live-baseline` | `amn2` | commit `8ecb0b4` и последующие fixes | Использовать как текущий config contract |
| Docker runtime peer apply/revoke | `verified-live-baseline` | `amn2` | `codex-vps-test-prep`, tag `vps-live-cycle-verified` | Использовать как behavior contract |
| Redaction coverage | `implemented-pushed-local-gate-complete` | `amn2` | commits `75c235a`..`94ad807` | Использовать как secret-output baseline; VPS gate не нужен |
| Verified config delivery | `implemented-pushed-local-gate-complete` | `amn2` | commits `952cc49`, `4b19cd3`, `fc73929`; verified at `94ad807` | Использовать как artifact integrity baseline; VPS gate не нужен |
| Public-token safety | `implemented-pushed-local-gate-complete` | `amn2` | commit `dfe27ee`; tests `14 passed`, full suite `535 passed` | Использовать как verify/recover token baseline; VPS gate не нужен |
| Local Agent hardening | `implemented-pushed-local-gate-complete` | `amn2` | commit `c5d7eb6`; focused tests `64 passed`, full suite `536 passed` | Использовать как read-only audit/version contract; VPS gate не нужен |
| Remote operation VPS gate candidate | `verified-live-on-current-stable` | `amn2` branch + AMN3 evidence | historical branch `codex/remote-operation-vps-gate-prep`, head `7281254`, is merged into stable via `708c98e` and is ancestor of `7764ae7`; current Phase 2 evidence `research/amn2/phase-2-live-vps-gate-evidence-2026-06-05.md`; read-only baseline package `dist/amn2-vps-update-and-smoke-kit-7764ae7.zip`, sha256 `832E1B1F6516A02E0D6AA45672B8FF526DF15D27117D2063CE45F9966825A66A` | Phase 2 live single disposable peer apply/sync/revoke/sync passed; keep broad write/API/config/backup/agent mutation surfaces behind separate gates |
| VPS gate evidence/merge package | `verified-live-evidence-recorded` | AMN3 | `phase-2-live-vps-gate-evidence-2026-06-05.md`, `remote-operation-vps-gate-evidence-2026-06-04.md`, `vps-gate-evidence-checklist.md`, `post-vps-gate-merge-decision.md`, `neighbor-chat-vps-gate-handoff.md` | Use result `verified-live` for exactly one disposable test peer; broad write integration remains blocked behind route/secret/remote-write gates |
| Post dry-run read-only integration status | `phase-1-closeout-pushed` | `amn2` stable branch + AMN3 evidence | branch `codex/post-dry-run-read-only-integration`, commits `55a7ed6`, `7764ae7`; evidence `research/amn2/post-dry-run-read-only-integration-implementation.md`, `research/amn2/phase-1-closeout-2026-06-04.md`; focused `39 passed`, full `610 passed` | Read-only API/web status surface готов и включен в API smoke; Phase 2 live apply/revoke вынести в отдельный чат/gate |
| VPS install/update package | `read-only-vps-smoke-pass-f7f6131` | AMN3 package for `amn2` | source-overlay update+smoke kit `dist/amn2-vps-update-and-smoke-kit-f7f6131.zip`, sha256 `19BF96A7E1057C042B89630BF80ADC7A9F5A09A62436E33A8555D7E2991AF282`; source `dist/amn2-codex-vps-test-prep-f7f6131-source.zip`, sha256 `720B6C9FE3CADDBC65C19BDEC5B0C811D00C94EB0D095D6311DCD90DD77BE4E1`; package evidence `research/amn2/f7f6131-status-alignment-vps-package-2026-06-07.md`; VPS smoke evidence `research/amn2/f7f6131-status-alignment-vps-smoke-evidence-2026-06-07.md`; previous c92 VPS-smoked kit `dist/amn2-vps-update-and-smoke-kit-c92bd1a.zip`, `run_id=20260607T182131Z` | `f7f6131` is the current VPS-smoked runtime/source baseline. Keep `VPS_APPLY_ENABLED=false`; live write remains a separate gate |
| Controlled prod readiness | `controlled-prod-ready-manual-runtime-pass` | AMN3 operator gate | `docs/AMN2_CONTROLLED_PROD_READINESS_RUNBOOK.ru.md`; handoff `docs/NEXT_CHAT_AMN2_CONTROLLED_PROD_DECISION.ru.md`; readiness evidence `research/amn2/controlled-prod-readiness-2026-06-06.md`; reverse proxy confirmation `research/amn2/controlled-prod-reverse-proxy-confirmation-2026-06-07.md`; final decision `research/amn2/controlled-prod-ready-2026-06-07.md`; current VPS-smoked package/source `f7f6131`, read-only VPS smoke `run_id=20260607T203730Z`, latest repeat API smoke `20260607T204300Z`, `checked_routes=6`; manual runtime evidence `research/amn2/c92bd1a-manual-prelaunch-evidence-2026-06-07.md`; web/admin systemd template confirmed loopback-only at previous c92 baseline and status-aligned at f7 | Validation VPS manual runtime passed: web/admin and bot are operator-started manually, `systemd` is not used, direct public `3030`/`3040` exposure is no. This is not public API `3040`, not broad write/API/config/backup/agent surfaces |
| Controlled prod status visibility | `source-overlay-vps-smoke-pass` | `amn2` stable branch + AMN3 evidence | VPS-smoked AMN2 head `42ffa65`; app-code smoke slice `62ff184`; git-checkout evidence `research/amn2/controlled-prod-status-visibility-git-checkout-smoke-2026-06-07.md`; source-overlay evidence `research/amn2/controlled-prod-status-visibility-vps-smoke-evidence-2026-06-07.md`; AMN2 source docs `docs/API_VPS_SMOKE_EVIDENCE.ru.md` and `docs/AMN2_VPS_SMOKE_62FF184_RUNBOOK.ru.md` | Promotion completed for read-only status visibility. Current git head later advanced to `f7f6131`; no write/config/backup/agent mutation unlock |
| Controlled prod status visibility package | `read-only-vps-smoke-pass` | AMN3 package for `amn2` | `dist/amn2-vps-update-and-smoke-kit-42ffa65.zip`, sha256 `5B43B467E014E87FEC1E49E8D9A8B7A2FBF841541BE88FDC6768097806240E39`; source sha256 `8A5B83D9AB95BE4230AAC221CE0321A37EF37E4E4B6EAB5EDECAE3C98A944829`; package evidence `research/amn2/controlled-prod-status-visibility-vps-package-2026-06-07.md`; smoke evidence `research/amn2/controlled-prod-status-visibility-vps-smoke-evidence-2026-06-07.md` | Operator can rerun read-only smoke with `VPS_APPLY_ENABLED=false`; `/opt/amn2` is promoted to `42ffa65` |
| Web-admin loopback systemd package | `manual-runtime-pass-systemd-not-used` | AMN3 package for `amn2` | AMN2 head `c92bd1a`; `dist/amn2-vps-update-and-smoke-kit-c92bd1a.zip`, sha256 `EC48DBA7C91F189512AB77EB5490432C85DA79F987068A98C1CC7F3082387F12`; source sha256 `272CC013A416937AAA2256A1643B2C77F707874D28FDCB2EA16534E349DD4FC2`; package evidence `research/amn2/web-admin-loopback-systemd-vps-package-2026-06-07.md`; smoke evidence `research/amn2/web-admin-loopback-systemd-vps-smoke-evidence-2026-06-07.md`; manual runtime evidence `research/amn2/c92bd1a-manual-prelaunch-evidence-2026-06-07.md` | Source-overlay update/smoke and manual web/bot runtime checks passed; `systemd` is not used in current operator mode. Keep backend on `127.0.0.1:3030`, API `3040` loopback-only |
| Docker manager safety note | `prepared-local-docs` | AMN3 -> `amn2` later | `research/amn2/docker-manager-design-note.md` | Использовать как вход для будущего implementation plan после VPS evidence |
| SSH host key enrollment design | `design-prepared-local-docs` | AMN3 -> `amn2` later | `research/amn2/ssh-host-key-enrollment-design.md` | Использовать как policy gate перед VPS onboarding, web/API remote operations и app-managed host key pinning |
| SSH host key identity verifier | `implemented-pushed-local-gate-complete` | `amn2` | branch `codex/ssh-host-key-identity-verifier`, commit `dd20364`; evidence `research/amn2/ssh-host-key-verifier-implementation.md`; focused `29 passed`, full `550 passed` | Использовать как merge/cherry-pick candidate перед live VPS gate; следующий шаг - подключать к SSH-backed operations только отдельным gated slice |
| Route/Auth machine-checkable binding tests | `implemented-pushed-local-gate-complete` | `amn2` | branch `codex/route-auth-binding-tests`, commit `f9d2c79`; RED `1 import error as expected`; focused `22 passed`; full suite `549 passed` | Использовать как route/policy drift guard; VPS gate не нужен |
| Secret inventory registry | `implemented-pushed-local-gate-complete` | `amn2` | branch `codex/secret-inventory-registry`, commit `9ce42f4`; evidence `research/amn2/secret-inventory-registry-implementation.md`; RED `1 import error as expected`; focused `64 passed`; full suite `591 passed` | Использовать как machine-checkable secret baseline; route/API secret-bearing output остается отдельным gate |
| Backup/import dangerous API design | `design-prepared-local-docs` | AMN3 -> `amn2` later | `research/amn2/backup-import-dangerous-api-design.md` | Использовать как gate перед backup/import web/API routes, restore preview и full backup dangerous mode |
| Backup/import policy contract | `implemented-pushed-local-gate-complete` | `amn2` | branch `codex/backup-import-policy-contract`, head `afb2702` with foundation commit `d2c160b`; evidence `research/amn2/backup-import-policy-contract-implementation.md`; RED `1 import error as expected`; focused `61 passed`; full suite `584 passed` | Использовать как no-route backup/import policy baseline; web/API full backup, restore apply и import apply остаются отдельными gates |
| Manager config export contract | `implemented-pushed-local-gate-complete` | `amn2` | branch `codex/manager-config-export-contract`, commit `4d4e7a4`; evidence `research/amn2/manager-config-export-contract-implementation.md`; focused `40 passed`, full `560 passed` | Использовать как no-route typed export adapter baseline; public/self-service endpoints, API `config:read` и Local Agent `/configs` остаются отдельными gates |
| Public/self-service config delivery policy | `implemented-pushed-local-gate-complete` | `amn2` | branch `codex/public-config-delivery-policy-contract`, commit `2ef3af7`; evidence `research/amn2/public-config-delivery-policy-contract-implementation.md`; focused `94 passed`, full `577 passed` | Использовать как no-route share-token/policy baseline; public download, self-service download, API `config:read` и Local Agent `/configs` остаются отдельными gates |
| Packaging discovery fix | `implemented-pushed-local-gate-complete` | `amn2` | branch `codex/read-only-api-route-shell`, commit `e99d5f3 Fix editable install package discovery` | Считать install/startup blocker закрытым для API smoke branch; проверять на VPS через editable install |
| KYORESUAS API integration priority | `merged-in-stable-read-only-api` | AMN3 -> `amn2` | `research/amn2/kyoresuas-api-integration-priority-plan.md`; `amn2/codex/read-only-api-route-shell`; latest evidence `research/amn2/api-vps-smoke-evidence-2026-06-03.md`; production head `5f12736` | Использовать как merged read-only API baseline; upstream code не копировать |
| Read-only API route shell | `merged-in-stable` | `amn2` | branch `codex/read-only-api-route-shell`, commits `6534ac4`, `9cccdc2`, `b37103a`, `2010d60`, `5f12736`; full suite `588 passed`; focused merge check `75 passed`; latest real VPS smoke passed `run_id=20260603T112418Z`; operator script `scripts/vps/amn2_api_loopback_smoke.sh`; update+smoke kit `dist/amn2-vps-update-and-smoke-kit-5f12736.zip` | Считать first read-only API baseline merged; дальнейшее route expansion только через отдельные gates |
| API/Web panel finish slice | `verified-real-vps-api-web-panel-read-only` | `amn2` stable branch + AMN3 evidence | branch `codex/api-web-panel-finish`, commit `294803e`; fast-forward merged into `codex-vps-test-prep`; local evidence `research/amn2/api-web-panel-finish-implementation.md`; real VPS evidence `research/amn2/api-web-panel-vps-evidence-2026-06-04.md`; package `dist/amn2-vps-update-and-smoke-kit-294803e.zip`; API loopback smoke `run_id=20260604T102355Z` | Считать API readiness/API tokens web slice verified on real VPS for read-only gate; route/API expansion and remote-write operations remain closed |
| Read-only metrics privacy classification | `classification-used-by-api-shell` | AMN3 -> `amn2` | `research/amn2/read-only-metrics-privacy-classification.md` | Держать как privacy baseline для aggregate-only API; detailed client metrics остаются заблокированы |
| Local Agent runtime metadata alignment | `merged-stable-read-only-vps-smoked` | `amn2` stable branch + AMN3 evidence | `amn2/codex-vps-test-prep` at `c8a6363`; branch `amn2/codex/local-agent-runtime-summary`; `research/amn2/local-agent-runtime-metadata-alignment.md`; `docs/superpowers/specs/2026-06-06-local-agent-runtime-summary-design.md`; `docs/superpowers/plans/2026-06-06-local-agent-runtime-summary.md`; `research/amn2/local-agent-runtime-summary-implementation-2026-06-06.md`; VPS evidence `research/amn2/local-agent-runtime-summary-vps-smoke-evidence-2026-06-06.md` | Mapper-only controller-safe runtime summary merged into stable and read-only VPS-smoked; no clients/configs, no API route, no VPS write command; mutation surfaces remain separate gates |
| API token rotation/revoke policy | `policy-prepared-local-docs` | AMN3 -> `amn2` later | `research/amn2/api-token-rotation-revoke-policy.md` | Policy остается design source для route expansion и Local Agent token separation |
| API token lifecycle gate | `implemented-pushed-local-gate-complete` | `amn2` | branch `codex/api-token-lifecycle-gate`, commit `c2ba646`; stacked branch `codex/api-token-lifecycle-gate-stacked`, commit `256d0c0` поверх `codex/route-auth-binding-tests`; evidence `research/amn2/api-token-lifecycle-gate-implementation.md`; stacked focused `56 passed`, full `555 passed` | Использовать как service/repository lifecycle baseline; `/api/*` routes, `config:read`, write scopes и bearer-token route exposure остаются отдельными gates |
| Web panel safe improvements | `implemented-pushed-local-gate-complete` | `amn2` | commit `22dfc37`; RED `4 failed as expected`; focused `75 passed`; full suite `536 passed` | Использовать как operator safety wording baseline; VPS gate не нужен |
| Scoped API token storage | `implemented-pushed-local-gate-complete` | `amn2` | commit `1fdcde5`; RED `1 import error as expected`; focused `54 passed`; full suite `542 passed` | Использовать как hash-only token baseline; lifecycle gate выполнен отдельным branch `codex/api-token-lifecycle-gate`, а для очереди после route/auth binding есть stacked branch `codex/api-token-lifecycle-gate-stacked`; VPS gate не нужен |
| Public/self-service config delivery | `lab-only-until-policy` | AMN3 -> `amn2` later | `research/amn2/config-delivery-inventory.md` | Не открывать public config links до scoped token/self-service design |

## Local Agent Decision

Решение: переносить как собственную реализацию `amn2`, без копирования внешнего `kyoresuas/amnezia-api`.

Причина:

- задача совпадает с целевым продуктом: API-first управление пользователями Amnezia;
- текущий first slice уже защищен route policy, hash-only token auth, typed auth errors и no-write boundary;
- ближайший production gain - получить opt-in local runtime adapter на сервере, который controller сможет опрашивать безопасно; safety boundary для этого зафиксирован в `research/amn2/local-agent-runtime-metadata-alignment.md`;
- verified VPS baseline теперь дает реальный behavior contract для будущих write операций.

## Transfer Gates

Любая новая функция из AMN3 переходит в `amn2` только если есть:

- source/license verdict;
- current `amn2` inventory;
- risk class;
- route/auth policy;
- secret and audit decision;
- tests;
- rollback/recovery note for state-write or remote operations;
- AMN3 return note after branch/commit/PR.

## Current Priority Order

1. Считать first read-only API shell merged в stable `codex-vps-test-prep` at `5f12736`.
2. API/web-panel finish slice реализован, fast-forward merged в stable `codex-vps-test-prep` at `294803e`; Phase 1 read-only integration status follow-up pushed at `7764ae7`; local full suite `610 passed`.
3. Не расширять API route surface в этом slice: `/api/clients` write CRUD, API `config:read`, public config delivery, backup/import/reboot, public docs/metrics и detailed client metrics остаются заблокированы до отдельного решения.
4. VPS API/web-panel gate для production head `294803e` пройден: API loopback smoke `run_id=20260604T102355Z`, web-admin route check passed; evidence `research/amn2/api-web-panel-vps-evidence-2026-06-04.md`.
5. Controlled real VPS verification gate Phase 2 пройден на current stable `7764ae7` как `verified-live` для ровно одного disposable test peer apply/sync/revoke/sync; API/web/agent routes, которые вызывают SSH, sync peers, emit config или меняют runtime state, все равно остаются отдельными gated slices.
6. Post dry-run read-only integration status реализован в `amn2/codex/post-dry-run-read-only-integration` at `55a7ed6`, затем закрыт follow-up `7764ae7`, который добавляет `/api/integration/status` в API smoke; это только API/web visibility, без live writes. Phase 2 live apply/revoke вынести в отдельный чат/gate.
7. Route/Auth binding tests, scoped API token lifecycle, secret inventory, public config policy and backup/import policy остаются обязательными baselines перед route expansion.
8. Domain exclusions и 2FA держать отложенными до закрытия текущих safety gates.

## Neighbor Chat Decision

`VPS OPS LAB - PRVTPRO-Amnezia-Web-Panel`:

- broad research paused;
- keep as targeted input for web-panel UX, route taxonomy, config delivery integrity and dangerous-action UX;
- no code/UI/templates/managers/scripts copied because GPL-3.0.

`VPN Ops Lab — KYORESUAS-API`:

- теперь является источником product direction для собственной `amn2` API lane;
- активная реализация идет в `amn2/codex/read-only-api-route-shell`, не через копирование upstream code;
- no broad CRUD/write API, no `config:read`, no backup/import/reboot before policy/secret/remote-write gates.

## Когда нужен новый live retest

Новый live retest обязателен, если меняется хотя бы одно из:

- peer apply/revoke;
- config template/defaults;
- IP allocation;
- peer sync classification;
- disable/enable/delete device flows;
- Docker runtime write/restart behavior.

## Route/Auth/Operation Policy Matrix Plan

Статус: `implemented-in-amn2-local-commit`.

Plan artifact:

```text
docs/superpowers/plans/2026-05-31-amn2-route-auth-operation-policy-matrix.md
```

Production branch:

```text
codex-vps-test-prep
```

Production commit:

```text
d1d9690 Add route auth operation policy matrix
```

Created in `amn2`:

- `app/security/surface_policy.py`
- `tests/security/test_surface_policy.py`
- `docs/ROUTE_AUTH_OPERATION_POLICY.ru.md`

Verification:

```text
tests/security/test_surface_policy.py tests/agent/test_policy.py tests/server/test_operation_runner.py tests/server/test_checks.py -v
result: 46 passed

tests/web/test_app.py tests/web/test_users.py tests/web/test_servers.py tests/web/test_email_delivery.py tests/bot/test_bot_workflows.py -v
result: 85 passed, 1 StarletteDeprecationWarning
```

Note: pytest emitted the known Windows temp cleanup `PermissionError` after successful sessions; both commands returned exit code 0.

Границы slice:

- live VPS не трогать;
- новых endpoints не добавлять;
- config/self-service API не добавлять;
- Local Agent clients/configs/backup/restore/reboot не включать;
- upstream code не копировать.

## Local Gate / Live VPS Gate

Все следующие transfer items делятся на два контура.

### Local gate

Можно выполнять и коммитить после локальных тестов:

- policy/inventory-only registry;
- redaction coverage;
- config delivery artifact tests;
- web/bot TestClient smoke;
- Local Agent read-only/auth/token hardening на fake/local runtime;
- remote operation contract tests на fake SSH/client;
- docs/status/backlog updates.

### Live VPS gate

Отдельная проверка на реальном VPS нужна только после local green, если item меняет:

- peer apply/revoke;
- disable/enable/delete;
- add missing local device to server;
- remove unknown remote peer;
- peer sync classification;
- config templates/defaults, которые попадут в рабочий client config;
- Docker AmneziaWG write/reload/restart behavior;
- real Local Agent deployment или controller-to-agent calls.

Policy matrix commit `d1d9690` остается `local-gate-complete`; live VPS gate для него не нужен.

Redaction coverage commits `75c235a`..`94ad807` также остаются `local-gate-complete`: они усиливают sanitizer, тесты и docs, но не меняют live apply/revoke/config/sync behavior.

Config delivery integrity на head `94ad807` также остается `local-gate-complete`: `.conf` UTF-8 bytes, QR payload, `vpn://` round-trip, non-ASCII fixture и secret metadata подтверждены локальными тестами; live VPS gate не нужен, пока не меняются реальные templates/defaults или apply/sync behavior.

Public-token safety commit `dfe27ee` также остается `local-gate-complete`: TTL guard, hash-only token contract, verify/recover purpose separation, expired-code rejection, generic denial/no raw token echo и no-consume failure behavior подтверждены локальными тестами. Live VPS gate не нужен, потому что slice не меняет peer apply/revoke/config/sync/runtime behavior.

Local Agent hardening commit `c5d7eb6` также остается `local-gate-complete`: `agent serve` подключает repository-backed audit sink для allowed read routes, `/agent/version` публикует runtime contract metadata, а tests подтверждают отсутствие raw bearer token в audit. Live VPS gate не нужен, потому что slice не делает real agent deployment, controller-to-agent calls, peer apply/revoke/config/sync/runtime writes.

Remote operation VPS gate branch `codex/remote-operation-vps-gate-prep` обновлена поверх stable head `294803e` и запушена как `7281254`: dry-run metadata, Runtime Registry, SSH host key verifier baseline и API/web-panel baseline подтверждены локально. Real VPS Phase 1 read-only/dry-run verification пройден 2026-06-04 как `dry-run-only-pass`; Phase 2 live single disposable peer apply/revoke пройден 2026-06-05 на current stable `7764ae7` как `verified-live`.

Web panel safe-improvements commit `22dfc37` также остается `local-gate-complete`: это wording/UI-test слой без изменения apply/revoke/config/sync/runtime behavior. Live VPS gate не нужен.

Scoped API token storage commit `1fdcde5` также остается `local-gate-complete`: добавлены `api_tokens` table, hash-only service contract, one-time raw token issue metadata, expiry/revoke/last-used fields, allowed first-slice scopes `server:read` и `metrics:read`, а `/api/*` routes не добавлены. Live VPS gate не нужен, потому что slice не меняет live apply/revoke/config/sync/runtime behavior.

Route/Auth binding tests commit `f9d2c79` также остается `local-gate-complete`: добавлены inventory-only route bindings, web runtime route drift tests, Local Agent blocked-future assertions и test-ref integrity check. Slice не добавляет endpoints, не меняет web/bot/agent/CLI behavior и не трогает live VPS.

Manager config export contract commit `4d4e7a4` также остается `local-gate-complete`: добавлен no-route typed export adapter для существующего `DeviceConfigDelivery`/`ConfigDeliveryPackage`, safe metadata и stable error categories. Slice не добавляет public/self-service endpoint, API `config:read`, Local Agent `/configs`, новый QR/import behavior или live VPS calls.

Public/self-service config delivery policy commit `2ef3af7` также остается `local-gate-complete`: добавлен no-route hash-only share-token/policy contract, `config_share_tokens` storage, blocked future policy entries and safe audit/backup metadata. Slice не добавляет public download route, self-service download route, API `config:read`, Local Agent `/configs`, generated config persistence, новый QR/import behavior или live VPS calls.

Backup/import policy contract head `afb2702` (foundation commit `d2c160b`) также остается `local-gate-complete`: добавлен no-route backup mode registry, secret field policy, safe manifests, restore/import preview-only contracts and blocked future `SurfacePolicy` entries. Slice не добавляет `/api/*`, web/Local Agent backup routes, restore apply, import apply или live VPS calls.

Secret inventory registry commit `9ce42f4` также остается `local-gate-complete`: добавлен machine-checkable `app.security.secret_inventory`, safe manifest, lookup/filter helpers and backup policy cross-checks. Slice не читает `.env`, не подключается к БД, не добавляет routes, secret-bearing output или live VPS calls.

## Post Dry-Run Read-Only Integration Status

Статус: `implemented-pushed-local-gate-complete`.

Plan artifact:

```text
docs/superpowers/plans/2026-06-04-amn2-post-dry-run-read-only-integration.md
```

Implementation:

```text
branch: codex/post-dry-run-read-only-integration
commit: 55a7ed6 Add post dry-run integration status
follow-up: 7764ae7 Cover integration status in API smoke
evidence: research/amn2/post-dry-run-read-only-integration-implementation.md
focused: 39 passed
full: 610 passed
```

Решение: после real VPS Phase 1 `dry-run-only-pass` не переходить к Phase 2 live apply/revoke по умолчанию. Реализован local-only read-only integration status surface: web-admin `/integration-status`, API `GET /api/integration/status`, общий local `integration_status` service, route policy/binding tests и AMN3 evidence. Slice не добавляет `/api/clients`, `config:read`, public/self-service config delivery, Local Agent mutations, SSH writes, Docker writes, peer apply/revoke, backup/import/reboot routes или detailed per-peer metrics.
