# `amn2` Transfer Backlog

Phase 3 service-mode target VPS update 2026-06-09: AMN3 commit `bc00b77 Record Phase 3 service mode evidence` is the current evidence/runbook checkpoint. Target VPS web/bot service-mode is enabled and active, but only loopback/tunnel: web/admin binds `127.0.0.1:3030`, operator access is SSH tunnel only, no domain is planned, Caddy/HTTPS public cutover is deferred indefinitely, public/direct `3030` is closed by loopback bind, public API `3040` is absent/closed, TCP `80/443` are absent, and `.env` explicitly keeps `VPS_APPLY_ENABLED=false`. Current peer scope is `live_peer_count=2`: `Neobyatnaya-AMNZ-1` and `-2` remain approved test peers; `-3` and `-4` are revoked. Web-panel unauth smoke and authenticated read-only smoke passed. This does not unlock API route expansion, API `config:read`, `/api/clients` write CRUD, public config delivery, Local Agent mutations, backup/import/reboot, public API `3040`, Caddy/HTTPS or production peer writes.

Phase 4 unified product gate 2026-06-09: main-chat entrypoint prepared at `docs/NEXT_CHAT_AMN2_PHASE_4_UNIFIED_PRODUCT_GATE.ru.md`; research note `research/amn2/phase-4-unified-product-gate-handoff-2026-06-09.md`. Phase 4 accepts Phase 3 service-mode loopback as closed baseline and starts as local/read-only product/API coordination for AMN2, target VPS, PRVTPRO/Web Panel and KYORESUAS/API work. The default local-only implementation queue is now closed after `P4-I001` closure; minimal docs/status/registry maintenance remains. Live commands, public exposure, config delivery, write CRUD, Local Agent mutations, backup/import/reboot and production peer/user mutation still require separate named gates.

KYORESUAS upstream refresh 2026-06-10: GitHub `main` was rechecked at `ffdc78c` / tree `ffdc78cf4e6f653322c6df251df10a7d7274a887`; note `research/upstreams/kyoresuas-amnezia-api-github-watch-2026-06-10.md`. Useful new signals are operation serialization, safer config writes, client lifecycle wording, QR/`vpn://` import compatibility, rate-limit/hardening and setup resilience. Decision remains unchanged: no upstream code/service copy, no public API `3040`, no `/api/clients` write CRUD, no config delivery, no backup/import/reboot. These signals were used as docs-only inputs for `WAPI-V001`, `WAPI-V002`, `WAPI-V003`, `WAPI-V004` and `WAPI-V005`; next safe use is docs-only `WAPI-I004` operation status model with `live_write_authorized: no`.

PRVTPRO upstream refresh 2026-06-10: GitHub `main` was rechecked at `7f062abc2c76bbe19eb7daafdf1191d6c26ff19a`; note `research/upstreams/prvtpro-amnezia-web-panel-upstream-refresh-2026-06-10.md`. Useful AMN2 Phase 4 signals are expiration/lifecycle contract tests, read-only About/Version/Build status, read-only server status/latency UX after design boundary and API taxonomy/OpenAPI grouping as docs/policy support. Hybrid-only signals are AdGuard Home integration, SOCKS5 service manager, Xray migration/attach existing install and multi-protocol capability registry. Decision remains unchanged: PRVTPRO is GPL-3.0 research-only; no code, templates, UI, manager implementations or workflows are copied; no admin-equivalent Bearer token model, public panel, config delivery, reboot, backup, import or server cleanup is opened without a separate named gate. `P4-PRVTPRO-REFRESH-002` expiration-field contract tests and `P4-PRVTPRO-REFRESH-001` read-only About/Version/Build status are completed as AMN2 local-only and merged into `amn2/codex-vps-test-prep` at `1508e3c4a100b76815b29f91757290f1266f813d`; evidence: `research/amn2/phase-4-prvtpro-local-slices-merge-2026-06-10.md`. `P4-PRVTPRO-REFRESH-004` API taxonomy/OpenAPI grouping was completed as AMN3 docs-only policy support; evidence: `research/amn2/phase-4-prvtpro-api-taxonomy-openapi-grouping-2026-06-10.md`. Remaining PRVTPRO-derived safe item is `P4-PRVTPRO-REFRESH-003`, but it needs a design boundary first.

Phase 4 candidate registry 2026-06-09: created `research/amn2/phase-4-candidate-registry-2026-06-09.md`. It classifies AMN2/API, target VPS, PRVTPRO/Web Panel and KYORESUAS/API candidates by priority (`critical`, `important`, `normal`, `cosmetic`) and gate class (`local-only`, `requires VPS gate`, `blocked until separate write/config/public gate`). The registry was updated with `P4-C009` after the operator reported that created test accounts/configurations were not visible in the web-panel users/configurations area. The initial local-only/default sequence now has `P4-C009`, `P4-I002`, route/secret gate planning, `P4-I003` design/implementation, `P4-I004` endpoint taxonomy docs, `P4-N003` aggregate metrics privacy boundary, `P4-I005` API token lifecycle boundary, `P4-N004` bot/admin read-only labels, `P4-N001` docs/status drift synchronization, `P4-N002` protocol manager interface checklist, `P4-X003` Russian-first operator docs polish, `P4-X002` API/status/gate naming cleanup, `P4-X001` read-only API docs grouping polish and `P4-I001` second read-only UX pass closure completed. Remaining default-mode work is minimal docs/status/registry maintenance only; any VPS/live/public/write/config work needs a separate named gate/decision.

Phase 4 start plan 2026-06-09: created `docs/superpowers/plans/2026-06-09-amn2-phase-4-start.md`. It records current GitHub/AMN2 checkout access checks, defines the `P4-VPS-ACCESS-READONLY-2026-06-09` gate shape for future SSH access verification, and breaks Phase 4 startup into critical, important, medium, minimal and cosmetic tasks. The plan was updated so the first AMN2 local-only slice investigates the web-panel user/config visibility gap before wording polish. GitHub connector currently shows `pull=true`, `push=false` for `barakov-dot/amn3` and `barakov-dot/amn2`, while local `git fetch --dry-run` and `git push --dry-run` passed for both active remotes. VPS login was not run because the target host/alias is intentionally not stored in the repo.

Phase 4 P4-C009 web-panel user/config visibility 2026-06-09: implemented locally in AMN2 branch `codex/phase-4-web-panel-user-config-visibility`; evidence `research/amn2/phase-4-web-panel-user-config-visibility-implementation-2026-06-09.md`. Root cause: `/users` lists local AMN2 database users/devices only, while live VPS peers created outside AMN2 are visible through server peer-sync/read-only inventory, not automatic user/config backfill. AMN2 change clarifies this boundary in `users.html` and adds a regression test. Verification: RED test failed as expected before the template change; focused verification passed with `26 passed, 1 warning`; `git diff --check` passed. No live VPS commands, write/config/token/sync/apply/revoke/backup/import/reboot or public exposure changes were performed. Next recommended local-only slice is `P4-I002` service-mode/read-only status wording.

Phase 4 P4-I002 service-mode/read-only status wording 2026-06-09: implemented locally in AMN2 branch `codex/phase-4-service-mode-status-wording`, commit `83f6d28 Show service mode status boundary`, stacked on `a73e845` from P4-C009. Evidence: `research/amn2/phase-4-service-mode-status-wording-implementation-2026-06-09.md`. AMN2 `/integration-status` now reports `service_mode_loopback_ready`, shows a `Service-mode boundary` panel, and makes loopback-only web/admin `127.0.0.1:3030`, SSH-tunnel-only operator access, absent/closed public API `3040`, absent TCP `80/443`, deferred domain/HTTPS cutover and `VPS_APPLY_ENABLED=false` visible. Verification: RED showed stale manual-prelaunch wording and missing boundary; focused verification passed with `7 passed, 1 warning`; `git diff --check` passed. No live VPS commands, write/config/token/sync/apply/revoke/backup/import/reboot or public exposure changes were performed. Historical next-step note was superseded by later route/secret work and `P4-I001` closure.

Phase 4 route/secret gate planning 2026-06-09: completed as AMN3 docs-only gate plan `research/amn2/phase-4-route-secret-gate-plan-2026-06-09.md`; execution plan `docs/superpowers/plans/2026-06-09-amn2-route-secret-gate-planning.md`. It consolidates existing AMN2 local-gate baselines (`f9d2c79`, `9ce42f4`, `256d0c0`, `2ef3af7`, `4d4e7a4`, `afb2702`, `83f6d28`) into a mandatory proposal/checklist before future route expansion. It classifies read-only aggregate/status, write peer/user lifecycle, secret-read config delivery, public/self-service delivery, Local Agent configs/mutations, backup/import/reboot and public exposure/cutover. This does not authorize AMN2 code changes, new routes, public API `3040`, direct public web/admin `3030`, config delivery, `/api/clients` CRUD, Local Agent mutations, backup/import/reboot or live VPS commands.

Phase 4 P4-I003 read-only API/status design 2026-06-09: completed as AMN3 docs-only candidate-specific design `research/amn2/phase-4-read-only-api-status-design-2026-06-09.md`; execution plan `docs/superpowers/plans/2026-06-09-amn2-read-only-api-status-design.md`. It binds the next safe AMN2 local slice to the existing six read-only API routes (`/api/servers`, `/api/servers/{server_name}/summary`, `/api/integration/status`, `/api/local-agent/runtime/summary`, `/api/metrics/summary`, `/api/users/summary`) and scopes future work to schema/docs/tests, safe audit assertions, forbidden-marker checks and `checked_routes=6`. No AMN2 code, live VPS command, public listener, config delivery, `/api/clients` CRUD, Local Agent mutation, token lifecycle action, backup/import/reboot or production peer/user mutation was performed.

Phase 4 P4-I003 AMN2 implementation plan 2026-06-09: completed as AMN3 docs-only execution plan `docs/superpowers/plans/2026-06-09-amn2-p4-i003-read-only-api-status-schema.md`. The plan defines AMN2 branch `codex/phase-4-read-only-api-status-schema` and limits execution to `API_RUNTIME_ROUTE_BINDINGS`, runtime route drift tests, read-only API/status contract tests, safe audit assertions and AMN2 policy docs. It does not authorize AMN2 implementation by itself, live VPS commands, new routes, public API `3040`, direct public web/admin `3030`, config delivery, `/api/clients` CRUD, Local Agent mutations, token lifecycle actions, backup/import/reboot or production peer/user mutation.

Phase 4 P4-I003 read-only API/status schema implementation 2026-06-09: completed locally in AMN2 branch `codex/phase-4-read-only-api-status-schema`, commit `b71b8f4 Lock read-only API status contract`; evidence `research/amn2/phase-4-read-only-api-status-schema-implementation-2026-06-09.md`. The slice adds `API_RUNTIME_ROUTE_BINDINGS`, runtime route drift coverage, read-only API/status contract tests, updated service-mode API status expectations and AMN2 policy docs. Verification: RED failed as expected on missing `API_RUNTIME_ROUTE_BINDINGS`; focused final verification passed with `56 passed, 1 warning`; `git diff --check` passed. No live VPS commands, new routes, public exposure, config delivery, `/api/clients` CRUD, Local Agent mutations, token lifecycle actions, backup/import/reboot or production peer/user mutation were performed.

Phase 4 P4-I004 endpoint taxonomy / route-policy docs alignment 2026-06-09: completed locally in AMN2 branch `codex/phase-4-endpoint-taxonomy-route-policy-docs`, commit `acf39f8 Add API endpoint taxonomy docs`; evidence `research/amn2/phase-4-endpoint-taxonomy-route-policy-docs-implementation-2026-06-09.md`. The slice adds private/local taxonomy docs for the current six read-only `/api/*` routes, links route/auth and token policy docs, and keeps public OpenAPI/docs exposure gated. Verification: `git diff --check` passed, forbidden enabled-marker scan passed with no matches, focused policy/contract regression passed with `33 passed, 1 warning`. No live VPS commands, runtime route changes, public exposure, config delivery, `/api/clients` CRUD, Local Agent mutations, token lifecycle actions, backup/import/reboot or production peer/user mutation were performed.

Phase 4 P4-N003 aggregate metrics privacy boundary 2026-06-09: completed locally in AMN2 branch `codex/phase-4-aggregate-metrics-privacy-boundary`, commit `8b6aef8 Show aggregate metrics privacy boundary`; evidence `research/amn2/phase-4-aggregate-metrics-privacy-boundary-implementation-2026-06-09.md`. The slice adds an additive safe `privacy` marker to `GET /api/metrics/summary` (`aggregate_only=true`, no per-peer fields, no per-user fields, no public exposure) and updates local tests/docs. Verification: RED failed on the missing privacy marker as expected; final extended verification passed with `50 passed, 1 warning`; `git diff --check` and marker scan passed. No live VPS commands, route count changes, public exposure, config delivery, `/api/clients` CRUD, Local Agent mutations, token lifecycle actions, backup/import/reboot or production peer/user mutation were performed.

Phase 4 P4-I005 API token lifecycle boundary 2026-06-09: completed locally in AMN2 branch `codex/phase-4-api-token-lifecycle-boundary`, commit `22061ea Show API token lifecycle boundary`; evidence `research/amn2/phase-4-api-token-lifecycle-boundary-implementation-2026-06-09.md`. The slice adds an additive safe `api_token_lifecycle_boundary` marker to `GET /api/integration/status` and updates local tests/docs. Verification: RED failed on the missing lifecycle marker as expected; final extended focused regression passed with `59 passed, 1 warning`; `git diff --check` and marker scan passed. No live VPS commands, route count changes, token issue/revoke/rotate API routes, production token mutation, public exposure, config delivery, `/api/clients` CRUD, Local Agent mutations, backup/import/reboot or production peer/user mutation were performed.

Phase 4 P4-N004 bot/admin read-only labels 2026-06-09: completed locally in AMN2 branch `codex/phase-4-bot-admin-read-only-labels`, commit `c9829b7 Clarify bot admin read-only labels`; evidence `research/amn2/phase-4-bot-admin-read-only-labels-implementation-2026-06-09.md`. The slice adds service-mode/gated boundary labels to web admin navigation, local/live inventory wording to users/servers empty states, and aggregate/local labels to bot admin list views. Verification: RED failed on missing labels as expected; final extended regression passed with `238 passed, 1 warning`; `git diff --check` and marker scan passed. No live VPS commands, route changes, callback changes, POST behavior changes, public exposure, config delivery, `/api/clients` CRUD, Local Agent mutations, backup/import/reboot, token issue/revoke/rotate API routes or production peer/user mutation were performed.

Phase 4 P4-N001 docs/status drift synchronization 2026-06-09: completed as AMN3 docs-only/local-only evidence `research/amn2/phase-4-docs-status-drift-sync-2026-06-09.md`. The sync aligned the active candidate registry, transfer backlog, current status, next-chat packet, Phase 4 handoff, active plan and context import after `P4-N004`; older next-step notes in prior evidence files were retained as historical chronology instead of being rewritten. No AMN2 code, live VPS commands, public exposure, config delivery, `/api/clients` CRUD, Local Agent mutations, backup/import/reboot, token lifecycle API operations or production peer/user mutation were performed. Next recommended local-only slice is `P4-N002` protocol manager interface checklist.

Phase 4 P4-N002 protocol manager interface checklist 2026-06-09: completed as AMN3 docs-only/local-only evidence `research/amn2/phase-4-protocol-manager-interface-checklist-2026-06-09.md`. The checklist maps PRVTPRO manager-architecture ideas onto existing AMN2 `RemoteOperation`/`OperationPlan`, partial-failure and `ConfigExportResult` baselines, with explicit capability, gate, test, license and non-action boundaries. No AMN2 code, live VPS commands, manager implementation, route expansion, public exposure, config delivery, `/api/clients` CRUD, Local Agent mutations, backup/import/reboot, token lifecycle API operations or production peer/user mutation were performed. Historical next-step note was superseded by later `P4-X003`, `P4-X002`, `P4-X001` and `P4-I001` closure.

Phase 4 P4-X003 Russian-first operator docs polish 2026-06-09: completed as AMN3 docs-only/local-only evidence `research/amn2/phase-4-russian-first-operator-docs-polish-2026-06-09.md`. The polish updates active Phase 4 operator-facing handoff/status/plan headings and copy-paste next-chat wording to Russian-first style while preserving technical IDs, route names, gates, file paths and safety boundaries. No AMN2 code, live VPS commands, route expansion, public exposure, config delivery, `/api/clients` CRUD, Local Agent mutations, backup/import/reboot, token lifecycle API operations or production peer/user mutation were performed. Historical next-step note was superseded by later `P4-X002`, `P4-X001` and `P4-I001` closure.

Phase 4 P4-X002 API/status/gate naming cleanup 2026-06-09: completed as AMN3 docs-only/local-only evidence `research/amn2/phase-4-api-status-gate-naming-cleanup-2026-06-09.md`. The cleanup defines active meanings for `service-mode`, `loopback-only`, `SSH tunnel`, `local-only`, `read-only`, `requires VPS gate`, `blocked`, `deferred`, `public exposure` and `config delivery` while preserving technical IDs, route names, gates, file paths and safety boundaries. No AMN2 code, live VPS commands, route expansion, public exposure, config delivery, `/api/clients` CRUD, Local Agent mutations, backup/import/reboot, token lifecycle API operations or production peer/user mutation were performed. Follow-up `P4-X001` was selected and completed next.

Phase 4 P4-X001 read-only API docs grouping polish 2026-06-09: completed as AMN3 docs-only/local-only evidence `research/amn2/phase-4-read-only-api-docs-grouping-polish-2026-06-09.md`. The polish groups the existing six private/local read-only routes into server inventory/status (`GET /api/servers`, `GET /api/servers/{server_name}/summary`), integration/service boundary (`GET /api/integration/status`), Local Agent runtime summary (`GET /api/local-agent/runtime/summary`) and aggregate metrics (`GET /api/metrics/summary`, `GET /api/users/summary`). It does not authorize public OpenAPI/docs exposure, route expansion, public API `3040`, direct public web/admin `3030`, config delivery, write routes, Local Agent mutations or live VPS work. Follow-up `P4-I001` closure was selected and completed next.

Phase 4 P4-I001 second read-only UX pass closure 2026-06-10: completed as AMN3 docs-only decision evidence `research/amn2/phase-4-p4-i001-read-only-ux-pass-closure-2026-06-10.md`. The second private-panel UX pass was not run, and no new page-level findings were collected; the operator chose to close it as not needed now so Phase 4 does not keep returning to the optional fallback. Existing service-mode UX evidence plus `P4-C009`, `P4-I002`, `P4-N004`, `P4-X003`, `P4-X002` and `P4-X001` are sufficient for the current boundary. No AMN2 code, live VPS commands, SSH-tunnel browser review, public exposure, config delivery, write CRUD, Local Agent mutations, backup/import/reboot, token issue/revoke/rotate API routes or production peer/user mutation were performed. Default local-only implementation queue is now closed except minimal maintenance.

Phase 4 P4-NG named gate / write API readiness 2026-06-10: started as AMN3 docs-only planning. Plan: `docs/superpowers/plans/2026-06-10-p4-ng-named-gate-write-api-readiness.md`; charter/evidence: `research/amn2/phase-4-ng-gate-charter-and-plan-2026-06-10.md`. Closed and removed from the active plan: `NG-C001` named gate charter and `NG-C002` safety boundary restatement. Follow-up `NG-C003` and `NG-C004` were selected and completed next. No AMN2 code, live VPS command, SSH command, route expansion, public exposure, config delivery, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot, token issue/revoke/rotate API route or production peer/user mutation was performed. `NG-V001` read-only VPS baseline gate still requires explicit operator approval and target SSH alias/host outside repo secrets; write API live work remains blocked until a separate `P4-WRITE-API-LIVE-GATE`.

Phase 4 NG-C003/NG-C004 secrets policy and go/no-go format 2026-06-10: completed as AMN3 docs-only evidence `research/amn2/phase-4-ng-secrets-policy-go-no-go-format-2026-06-10.md`. Reusable template: `research/amn2/phase-4-ng-named-gate-evidence-template-2026-06-10.md`. `NG-S003` was also closed because creating the reusable named-gate evidence template is required for `NG-C003` and `NG-C004`. Gate evidence is now limited to boolean/status summaries and safe aggregate counts; forbidden fields include `.env`, raw `servers.yml`, raw tokens, Authorization headers, token hashes, password/session secrets, keys, PSK, peer public keys, `.conf`, QR, `vpn://`, backup contents, endpoint values, cookies, full logs and secret-bearing command output. Every gate must end with `go_no_go_decision: go | no-go | defer`. No AMN2 code, live VPS command, SSH command, public exposure, config delivery, write CRUD, Local Agent mutation, backup/import/reboot or production peer/user mutation was performed. Follow-up `NG-C005` was selected and completed next.

Phase 4 NG-C005 write API live-block assertion 2026-06-10: completed as AMN3 docs-only evidence `research/amn2/phase-4-ng-write-api-live-block-assertion-2026-06-10.md`. It records `live_write_authorized: no`, keeps `/api/clients` write CRUD, peer apply/revoke/sync, config delivery, token issue/revoke/rotate routes, Local Agent mutations, backup/import/reboot, public exposure and production peer/user mutation blocked, and requires every future write API slice to state its live-write status explicitly. The selected next docs-only task was `WAPI-V001` write API threat model with `live_write_authorized: no`. No AMN2 code, live VPS command, SSH command, route expansion, public exposure, config delivery, write CRUD, Local Agent mutation, backup/import/reboot or production peer/user mutation was performed.

Phase 4 WAPI-V001 write API threat model 2026-06-10: completed as AMN3 docs-only evidence `research/amn2/phase-4-wapi-v001-write-api-threat-model-2026-06-10.md`. It defines protected assets, trust boundaries, threat classes and required tests before any future write API implementation. Key risk areas are accidental live mutation, scope escalation, config secret leakage, token lifecycle bypass, replay/duplicates, concurrent operations, local/remote partial failure, audit/log leakage, public exposure creep, Local Agent confused-deputy behavior, destructive operation smuggling, operation status leakage and upstream license boundary drift. The KYORESUAS refresh signals are explicitly carried as operation lock/serialization, atomic config write, `active|disabled` plus `expiresAt` lifecycle wording, QR/`vpn://` secret-read tests, rate-limit/Helmet-style public hardening and setup resilience, with no upstream code copied. `live_write_authorized: no` remains in force. Follow-up `WAPI-V002` was selected and completed next. No AMN2 code, live VPS command, SSH command, route expansion, public exposure, config delivery, write CRUD, Local Agent mutation, backup/import/reboot or production peer/user mutation was performed.

Phase 4 WAPI-V002 write API route taxonomy 2026-06-10: completed as AMN3 docs-only evidence `research/amn2/phase-4-wapi-v002-write-api-route-taxonomy-2026-06-10.md`. It classifies future route groups, candidate route names, route classes, minimal scopes, side effects, named gates and required tests before any AMN2 implementation planning. Candidate names are planning placeholders only; no runtime route, OpenAPI artifact, public exposure, config delivery, `/api/clients` CRUD, Local Agent mutation, live VPS command or production mutation was added. Follow-up `WAPI-V003` was selected and completed next.

Phase 4 WAPI-V003 local fake-runner contract 2026-06-10: completed as AMN3 docs-only evidence `research/amn2/phase-4-wapi-v003-local-fake-runner-contract-2026-06-10.md`. It defines future fake-runner inputs, outputs, operation intents, deterministic failure modes, audit-safe metadata and RED test requirements without adding runner code, runtime routes, live VPS commands, config delivery, `/api/clients` CRUD or production mutation. Follow-up `WAPI-V004` was selected and completed next.

Phase 4 WAPI-V004 idempotency, locking and partial-failure model 2026-06-10: completed as AMN3 docs-only evidence `research/amn2/phase-4-wapi-v004-idempotency-locking-partial-failure-model-2026-06-10.md`. It defines required idempotency keys, safe request fingerprints, per-target lock scopes, retry behavior, conflict statuses and partial-failure vocabulary for future write API/fake-runner work. Historical VPS evidence is used only as status vocabulary input: Phase 1 `dry-run-only-pass`, Phase 2 single disposable peer `verified-live`, and Phase 3 service-mode loopback baseline do not authorize new live/write actions. No AMN2 code, runner code, runtime route, live VPS command, config delivery, `/api/clients` CRUD or production mutation was added. Follow-up `WAPI-V005` was selected and completed next.

Phase 4 WAPI-V005 write API audit/redaction requirements 2026-06-10: completed as AMN3 docs-only evidence `research/amn2/phase-4-wapi-v005-write-api-audit-redaction-requirements-2026-06-10.md`. It defines required safe audit fields, forbidden secret-bearing fields, redaction rules, event types, audit failure behavior and RED test requirements before any write API route, fake-runner or audit schema implementation. Historical VPS evidence may be referenced only as safe labels/status vocabulary, not as command output, endpoint data, full logs or current live permission. No AMN2 code, audit schema implementation, runner code, runtime route, live VPS command, config delivery, `/api/clients` CRUD or production mutation was added. Next recommended docs-only task is `WAPI-I004` operation status model with `live_write_authorized: no`.

Phase 4 P4-PRVTPRO-REFRESH-004 API taxonomy/OpenAPI grouping policy support 2026-06-10: completed as AMN3 docs-only evidence `research/amn2/phase-4-prvtpro-api-taxonomy-openapi-grouping-2026-06-10.md`. It records the PRVTPRO grouping signal as taxonomy policy support while keeping the active private/local read-only API surface exactly six routes, with no generated OpenAPI artifact, public docs exposure, route expansion, config delivery, write API, Local Agent mutation or live VPS work. `WAPI-V002` later used this policy baseline and was also closed; the remaining PRVTPRO-derived item `P4-PRVTPRO-REFRESH-003` requires a design boundary first.

Service-mode web-panel read-only UX review prep 2026-06-09: next safe local/operator task is a private-panel UX/product review through SSH tunnel using `docs/AMN2_WEB_PANEL_READ_ONLY_UX_REVIEW_CHECKLIST.ru.md`, safe return template `docs/AMN2_WEB_PANEL_READ_ONLY_UX_REVIEW_EVIDENCE_TEMPLATE.ru.md`, evidence note `research/amn2/service-mode-web-panel-read-only-ux-review-2026-06-09.md` and template note `research/amn2/service-mode-web-panel-read-only-ux-review-evidence-template-2026-06-09.md`. Scope is GET/navigation/labels/empty states/warnings only; no POST/write/config delivery/API token issue/revoke/sync/health/backup/import/reboot/public exposure.

Service-mode web-panel read-only UX review evidence 2026-06-09: passed as `passed-minimal-safe-summary`. Evidence: `research/amn2/service-mode-web-panel-read-only-ux-review-evidence-2026-06-09.md`. Operator confirmed baseline (`amneziya-web=active`, `amneziya-bot=active`, loopback `/login=200`, TCP `3030` loopback-only, TCP `3040`/`80`/`443` absent, `VPS_APPLY_ENABLED=false`), then reported authenticated overview review `ok` with no write/config delivery/API token issue-revoke/sync-health/backup-import-reboot actions and no secrets published. Detailed page-by-page UX findings were not returned; collect them in a second pass only if needed.

Status-visibility update 2026-06-07: `amn2/codex-vps-test-prep` advanced to `42ffa65 Record git checkout smoke status`. The app-code read-only smoke slice is `62ff184 Update controlled prod status visibility`, which passed real VPS git-checkout smoke on `/opt/amn2-git` with `checked_routes=6`; AMN3 package `42ffa65` then passed safe source-overlay update/read-only smoke on `/opt/amn2`. That source overlay is now the previous status-visibility baseline, original `api_smoke_run_id=20260607T165625Z`, latest repeat `api_smoke_run_id=20260607T165807Z`. `c8a6363` is historical prior VPS-smoked runtime/source, `run_id=20260606T202040Z`; `32d01fd` and `1a193b9` are older historical baselines.

Follow-up 2026-06-07: `amn2/codex-vps-test-prep` advanced to `c92bd1a Bind web admin systemd to loopback` and the AMN3 package passed safe source-overlay update/read-only smoke on `/opt/amn2`. This is a controlled production launch safety slice: web/admin systemd template uses `127.0.0.1:3030` by default for the approved HTTPS reverse proxy mode. Package: `dist/amn2-vps-update-and-smoke-kit-c92bd1a.zip`, sha256 `EC48DBA7C91F189512AB77EB5490432C85DA79F987068A98C1CC7F3082387F12`; evidence `research/amn2/web-admin-loopback-systemd-vps-package-2026-06-07.md` and `research/amn2/web-admin-loopback-systemd-vps-smoke-evidence-2026-06-07.md`.

Manual runtime 2026-06-07: validation VPS `mirror` passed backup create/verify, safe preflight, API smoke-cycle summary with six read-only routes, manual web `/login` check on `127.0.0.1:3030`, and manual bot runtime check. `systemd` is not used in the current operator mode; direct public web `3030` and public API `3040` are not exposed. Evidence: `research/amn2/c92bd1a-manual-prelaunch-evidence-2026-06-07.md`.

Neighboring AMN2 status follow-up 2026-06-07: `amn2/codex-vps-test-prep` advanced to `f7f6131 Update integration status for c92 manual prelaunch`. This is a read-only status-visibility update to `/api/integration/status` and web `/integration-status`; it has now passed source-overlay update/read-only smoke on `/opt/amn2`. Evidence: `research/amn2/manual-prelaunch-integration-status-2026-06-07.md` and `research/amn2/f7f6131-status-alignment-vps-smoke-evidence-2026-06-07.md`.

Status-alignment package 2026-06-07: AMN3 update+smoke kit for `f7f6131` passed real VPS read-only smoke. Package: `dist/amn2-vps-update-and-smoke-kit-f7f6131.zip`, sha256 `19BF96A7E1057C042B89630BF80ADC7A9F5A09A62436E33A8555D7E2991AF282`; source sha256 `720B6C9FE3CADDBC65C19BDEC5B0C811D00C94EB0D095D6311DCD90DD77BE4E1`; package evidence `research/amn2/f7f6131-status-alignment-vps-package-2026-06-07.md`; smoke evidence `research/amn2/f7f6131-status-alignment-vps-smoke-evidence-2026-06-07.md`; `source_update_run_id=20260607T203721Z`, `api_smoke_run_id=20260607T203730Z`, `latest_repeat_api_smoke_run_id=20260607T204300Z`, `checked_routes=6`.

Target-server prep 2026-06-08: validation VPS source overlay should remain untouched after `f7f6131` pass. The new rented VPS starts a separate target-server prep gate using `docs/AMN2_TARGET_SERVER_PREP_GATE.ru.md`; detailed runbook `docs/AMN2_TARGET_SERVER_PREP_RUNBOOK.ru.md` is used only after safe precheck review, with evidence note `research/amn2/target-server-prep-gate-2026-06-08.md` and safe evidence template `research/amn2/target-server-prep-evidence-template-2026-06-08.md`. This gate covers bootstrap, read-only preflight, API loopback smoke, manual web/admin check and backup verify. Historical note: at this prep stage, service-mode `systemd`/reverse proxy was still a separate explicit decision; Phase 3 later enabled only loopback web/bot service-mode, while reverse proxy/public cutover remains separate.

Target-server bootstrap 2026-06-08: new target VPS partial bootstrap passed. Evidence: `research/amn2/target-server-bootstrap-evidence-2026-06-08.md`. Completed: base packages, Docker runtime installed with no containers, `/opt/amn2` venv, `f7f6131` source overlay, Python dependency install, CLI import, DB schema init, partial loopback API probe for `/api/servers` with token revoke and `forbidden_markers_count=0`, encrypted backup create/verify.

Target-server AWG2 runtime 2026-06-09: new target VPS runtime gate passed. Evidence: `research/amn2/target-server-awg2-runtime-smoke-evidence-2026-06-09.md`. Completed: `amnezia-awg2` Docker runtime built/started, `awg0` up, UDP `30001` listening, self-SSH for AMN2 local Docker operations passed, real target `servers.yml` created on the VPS and accepted by AMN2 loader, full read-only API loopback smoke passed with `run_id=20260609T043158Z`, `checked_routes=6`. Live peer apply/revoke remains a separate explicit gate.

Target-server live peer gate 2026-06-09: new target VPS is now `verified-live` for the remote peer apply/revoke primitive. Evidence: `research/amn2/target-server-live-peer-gate-evidence-2026-06-09.md`. Completed: exactly one disposable test peer, `--preshared-key-stdin`, dry-run apply/revoke, live apply/sync/revoke/sync, final peer count `0`, post-gate read-only API smoke `run_id=20260609T045546Z`, `checked_routes=6`. Production peer mutation, public API, config delivery and broader write surfaces remain closed.

Target-server manual web/bot gate 2026-06-09: new target VPS passed manual readiness for bot and web/admin without service-mode. Evidence: `research/amn2/target-server-manual-web-bot-evidence-2026-06-09.md`. Completed: Telegram bot token present on VPS, `bot check-network` passed for `@NeobyatnayaAMNZ_bot`, web admin password hash and session secret present, temporary manual web/admin `/login` returned `200` on `127.0.0.1:3030`, cleanup left TCP `3030`/`3040` absent, AWG2 running and peer count `0`. Service-mode, reverse proxy/public HTTPS cutover, public API, config delivery and broader write surfaces remain closed.

Phase 3A.1 phone live test peer gate 2026-06-09: new target VPS now has one operator-approved phone/desktop test peer left enabled. Evidence: `research/amn2/target-server-phone-live-test-peer-evidence-2026-06-09.md`. Completed: initial failed apply left no remote mutation, free VPN IP was selected without publishing it, repeat dry-run apply/revoke passed, live apply passed, client config was regenerated from live AWG2 parameters with absent `I1`-`I5` fields removed, handshake/RX/TX passed, final peer count is `1`, TCP `3030`/`3040` remain absent, and `VPS_APPLY_ENABLED=false`. Service-mode, reverse proxy/public HTTPS cutover, public API, public/self-service config delivery and production peer/user mutation beyond this single test peer remain closed.

Phase 3A.2 test peers batch gate 2026-06-09: three additional operator-approved test-zone peers were created and left enabled. Evidence: `research/amn2/target-server-test-peers-batch-evidence-2026-06-09.md`. Completed: secret-bearing configs/QRs were generated and downloaded through a private operator channel, final peer count is `4`, TCP `3030`/`3040` remain absent, and `VPS_APPLY_ENABLED=false`. Per-client handshake for those three additional users remains a manual follow-up if needed. Service-mode, reverse proxy/public HTTPS cutover, public API, public/self-service config delivery and production peer/user mutation beyond the four approved test peers remain closed.

Phase 3B.0 service-mode read-only precheck 2026-06-09: target VPS is ready for an explicit service-mode decision but service-mode remains disabled. Evidence: `research/amn2/target-server-service-mode-precheck-evidence-2026-06-09.md`. Completed: source overlay `f7f6131` confirmed, Docker runtime running, peer count `4`, TCP `3030`/`3040` absent, `VPS_APPLY_ENABLED=false`, web/bot systemd templates present with web loopback bind, required bot/web secrets present as markers only, and no `amneziya-web`/`amneziya-bot` systemd unit installed/enabled/active. A named peer activity sample for `Neobyatnaya-AMNZ-1..4` returned `not-yet` at that moment. Next action requires an explicit operator choice: stay in manual runtime mode or open a separate service-mode gate for systemd plus HTTPS reverse proxy.

Phase 3A critical manual-mode cleanup 2026-06-09: secret-bearing delivery artifacts were removed after the four test configs had been downloaded privately. Evidence: `research/amn2/target-server-manual-mode-critical-cleanup-evidence-2026-06-09.md`. Completed: pre-cleanup baseline confirmed peer count `4`, TCP `3030`/`3040` absent and `VPS_APPLY_ENABLED=false`; `.conf`, QR/PNG and delivery archive files were removed from the checked gate locations; post-cleanup control confirmed delivery artifacts `0`, peer count `4`, TCP `3030`/`3040` absent and `VPS_APPLY_ENABLED=false`. Monitoring key files were retained for numbered peer checks without printing keys.

Phase 3A protocol identity and numbered peer check 2026-06-09: after the operator reported that imported configs did not visibly advertise "Amnezia 2.0", the downloaded config metadata and live server config metadata were checked without publishing secret values. Evidence: `research/amn2/target-server-protocol-identity-and-numbered-peer-evidence-2026-06-09.md`. Completed: all four downloaded config metadata samples show 11 core AmneziaWG fields and `0` `I1`-`I5` fields; live server metadata matches 11 core AmneziaWG fields and `0` `I1`-`I5` fields; numbered peer status showed `Neobyatnaya-AMNZ-2=connected-with-traffic`, while `1`, `3` and `4` were `not-yet`. Current conclusion: UI/label ambiguity rather than a wrong plain-WireGuard or Amnezia 1/1.5 export. No regenerate/re-delivery gate is required on this evidence alone.

Phase 3A manual-runtime field test 2026-06-09: read-only numbered live snapshot reached `partial-pass` with three of four approved test peers connected with traffic. Evidence: `research/amn2/target-server-manual-mode-field-test-evidence-2026-06-09.md`. Completed: peer count remained `4`, TCP `3030`/`3040` absent, `VPS_APPLY_ENABLED=false`; `Neobyatnaya-AMNZ-1`, `-2` and `-3` were `connected-with-traffic`, while `-4` remained `not-yet`. This proves real manual-runtime field connectivity for three numbered profiles. Remaining A follow-up: resample `-4` when online and prepare revoke-by-number before expanding the test group.

Phase 3A revoke-by-number runbook 2026-06-09: prepared but not executed. Runbook: `docs/AMN2_MANUAL_MODE_REVOKE_BY_NUMBER_RUNBOOK.ru.md`. It covers safe dry-run and explicit-confirmation live revoke for exactly one `Neobyatnaya-AMNZ-N` test peer, with numbered key resolution, target-present checks, dry-run metadata markers, post-revoke persistent/live absence checks, peer count delta, `3030`/`3040` checks and `VPS_APPLY_ENABLED=false` reset. It does not authorize a revoke by default.

Phase 3A revoke-by-number gate for `Neobyatnaya-AMNZ-3` 2026-06-09: passed. Evidence: `research/amn2/target-server-revoke-by-number-3-evidence-2026-06-09.md`. Completed: dry-run confirmed target present in persistent and live state with `connected-with-traffic`; live revoke removed the target from both persistent config and live interface; live peer count changed from `4` to `3`; TCP `3030`/`3040` remained absent; `VPS_APPLY_ENABLED` was reset to `false`. Immediate post-revoke sample showed remaining peers as `not-yet`, expected after Docker container restart until clients reconnect.

Post-revoke numbered snapshots 2026-06-09: safe state remained stable after the revoke gate. Initial snapshot: peer count `3`, TCP `3030`/`3040` absent, `VPS_APPLY_ENABLED=false`, `Neobyatnaya-AMNZ-3=not-found-on-server`, remaining peers `1`, `2`, `4` still `not-yet` pending fresh reconnect. Later reconnect snapshot after user activity: `Neobyatnaya-AMNZ-1=traffic-seen`, `Neobyatnaya-AMNZ-2=traffic-seen`, `Neobyatnaya-AMNZ-3=not-found-on-server`, `Neobyatnaya-AMNZ-4=not-yet`, with peer count still `3` and TCP `3030`/`3040` absent. This proves manual reconnect/traffic for two remaining peers after the #3 revoke; automatic reconnect remains unproven unless a separate disruption test is approved.

Phase 3 revoke-by-number gate for unused `Neobyatnaya-AMNZ-4` 2026-06-09: passed. Evidence: `research/amn2/target-server-revoke-by-number-4-evidence-2026-06-09.md`. Completed: dry-run confirmed #4 present in persistent/live state with `target_status_before=not-yet`; live revoke removed #4 from both persistent config and live interface; live peer count changed from `3` to `2`; web/bot remained active; loopback `/login` returned `200`; TCP `3030` remained loopback-only; TCP `80/443/3040` absent; `VPS_APPLY_ENABLED` reset false and explicit `.env` false confirmed. Remaining approved test peers are now #1 and #2.

Post-revoke #4 numbered snapshot 2026-06-09: passed. Evidence is included in `research/amn2/target-server-revoke-by-number-4-evidence-2026-06-09.md`. Peer count remained `2`, #3/#4 were `not-found-on-server`, #1/#2 were `not-yet` pending reconnect after the Docker/AWG restart, web/bot active, `/login` loopback `200`, TCP `3030` loopback-only, TCP `80/443/3040` absent and explicit `.env` `VPS_APPLY_ENABLED=false`.

Phase 3B0 service-mode preflight 2026-06-09: completed read-only as `needs-fix-before-B1`. Evidence: `research/amn2/target-server-service-mode-b0-preflight-evidence-2026-06-09.md`. Completed: source overlay `f7f6131`, Docker runtime running, peer count `3`, TCP `3030`/`3040` absent, `VPS_APPLY_ENABLED=false`, web/bot templates present, web template loopback-only, no systemd units installed/enabled/active, web/bot imports pass, no writes performed. Blockers before B1: service user/group `amneziya` missing while templates use `User=amneziya`; effective settings show `WEB_ADMIN_ENABLED=False`; `ADMIN_TELEGRAM_IDS` absent; reverse proxy choice undecided for any later HTTPS cutover.

Phase 3B0.1 service-mode prep and B0 repeat 2026-06-09: completed as `ready-for-B1-loopback-systemd`. Evidence: `research/amn2/target-server-service-mode-b0-1-prep-and-repeat-evidence-2026-06-09.md`. Completed: private admin Telegram ID was supplied on the VPS after one blocked attempt; service user `amneziya` was created; `.env` group/mode set for that service group; web/admin effective settings enabled on loopback; `VPS_APPLY_ENABLED=false` preserved; `/opt/amn2` group permissions fixed so the service user can read app/venv/env and write data/logs. No systemd unit installed or started; reverse proxy unchanged. Repeated B0 shows peer count `3`, TCP `3030`/`3040` absent, templates good, no units installed/active, settings as `amneziya` pass, imports pass. Next action requires separate B1 approval for loopback-only systemd.

Phase 3B1 loopback-only systemd gate 2026-06-09: passed after bounded readiness investigation. Evidence: `research/amn2/target-server-service-mode-b1-loopback-systemd-evidence-2026-06-09.md`. Completed: `amneziya-web` and `amneziya-bot` unit files installed, enabled and active; initial immediate probe saw `curl_rc_7` and absent `3030`, so B1 was held as `needs-investigation`; follow-up diagnostics showed both units active with `Result=success`, `NRestarts=0`, web listening on `127.0.0.1:3030`, `/login` returning `200`, TCP `3040` absent, reverse proxy unchanged and `VPS_APPLY_ENABLED=false`. HTTPS reverse proxy/public cutover remains a separate B2 gate.

Phase 3B2.0 reverse proxy preflight 2026-06-09: completed read-only as `passed-ready-for-choice`. Evidence: `research/amn2/target-server-service-mode-b2-0-reverse-proxy-preflight-evidence-2026-06-09.md`. Completed: web/bot systemd still enabled/active, loopback `/login` `200`, TCP `3030` loopback-only, TCP `3040` absent, TCP `80/443` absent, nginx/Caddy/certbot not installed, no Docker proxy candidate running, UFW inactive, no writes performed. Next B2 step requires domain/package readiness and explicit proxy path selection.

Phase 3B2.1 reverse proxy readiness 2026-06-09: completed read-only as `blocked-before-public-cutover`. Evidence: `research/amn2/target-server-service-mode-b2-1-reverse-proxy-readiness-evidence-2026-06-09.md`. Completed: web/bot systemd remained enabled/active, loopback `/login` `200`, TCP `3030` loopback-only, TCP `3040`, `80` and `443` absent, package candidates for Caddy/nginx/certbot available, and no writes performed. Blockers: selected public host did not resolve from the VPS (`dns_a_count=0`, `dns_aaaa_count=0`) and `.env` did not prove an explicit `VPS_APPLY_ENABLED=false` line. Next step is a small baseline/DNS fix gate, then repeat B2.1 before any Caddy/HTTPS cutover.

No-domain service-mode access decision 2026-06-09: selected SSH local port forwarding instead of public HTTPS cutover because no domain is available. Evidence: `research/amn2/target-server-service-mode-no-domain-ssh-tunnel-decision-2026-06-09.md`; runbook: `docs/AMN2_SERVICE_MODE_SSH_TUNNEL_ACCESS_RUNBOOK.ru.md`. The panel remains loopback-only on the VPS and should be opened from the operator workstation through an SSH tunnel in an external browser, not Codex preview. Reverse proxy/public HTTPS remains deferred until a domain exists and B2.1 is green.

No-domain SSH tunnel access 2026-06-09: passed. Evidence: `research/amn2/target-server-service-mode-ssh-tunnel-access-evidence-2026-06-09.md`. The operator opened the web/admin panel through an SSH local port forward in an external browser; post-open control confirmed web/bot active, loopback `/login` `200`, remote `3030` loopback-only, remote `3040` absent and explicit `.env` `VPS_APPLY_ENABLED=false`. Public HTTPS/reverse proxy remains deferred.

Web-panel tunnel smoke 2026-06-09: passed read-only. Evidence: `research/amn2/target-server-service-mode-web-panel-tunnel-smoke-evidence-2026-06-09.md`. Through the SSH local port forward, `/login` returned `200`, `/` redirected to `/login`, sampled protected GET routes redirected to `/login`, local `127.0.0.1:3040` did not connect, and no POST/write/config delivery was performed. Public HTTPS/reverse proxy remains deferred until a domain exists and B2.1 is green.

Second Telegram admin ID add 2026-06-09: passed. Evidence: `research/amn2/target-server-service-mode-admin-telegram-id-add-evidence-2026-06-09.md`. One additional Telegram admin ID was added privately on the VPS; configured admin count is now `2`, raw IDs were not recorded, `VPS_APPLY_ENABLED=false` remained explicit, bot/web are active, TCP `3030` loopback-only and TCP `3040` absent. Web `/login` returned `200` after a short restart readiness window.

Second admin bot read-only check 2026-06-09: skipped by operator decision to save time. Evidence: `research/amn2/target-server-service-mode-second-admin-bot-check-decision-2026-06-09.md`. The configured admin count remains `2`, but this record does not independently prove the second admin Telegram UI path.

Authenticated web-panel tunnel smoke 2026-06-09: passed read-only. Evidence: `research/amn2/target-server-service-mode-authenticated-web-panel-smoke-evidence-2026-06-09.md`. After login through the SSH local port forward, sampled overview GET pages returned HTTP `200` without redirect. No POST/write/token issue/revoke/sync/health/config-delivery operation was performed. Public HTTPS/reverse proxy remains deferred until a domain exists and B2.1 is green.

Read-only web-panel UX review checklist 2026-06-09: prepared as a docs-only next slice. Checklist: `docs/AMN2_WEB_PANEL_READ_ONLY_UX_REVIEW_CHECKLIST.ru.md`; planning note: `research/amn2/service-mode-web-panel-read-only-ux-review-2026-06-09.md`; result evidence: `research/amn2/service-mode-web-panel-read-only-ux-review-evidence-2026-06-09.md`. Scope is private operator panel UX/product review through SSH tunnel only: overview pages, navigation, empty states, labels, warnings and copy. POST/write actions, token issue/revoke, sync/health operations, config delivery, backup/import/reboot, public `3030/3040`, reverse proxy and production peer/user mutation remain closed.

Phase 3 final safety snapshot 2026-06-09: passed with source-overlay git metadata unavailable in that specific check. Evidence: `research/amn2/target-server-phase3-final-safety-snapshot-evidence-2026-06-09.md`. Runtime Docker remained running with peer count `3`; numbered status was `Neobyatnaya-AMNZ-1/-2=traffic-seen`, `-3=not-found-on-server`, `-4=not-yet`; web/bot units enabled/active; `/login` loopback `200`; TCP `3030` loopback-only; TCP `80/443/3040` absent; explicit `.env` `VPS_APPLY_ENABLED=false`; production write surfaces/config delivery not opened; reverse proxy/public HTTPS not enabled. Follow-up after this snapshot: bot admin read-only check was skipped by operator, and #4 was later revoked as unused.

Phase 3 handoff 2026-06-09: new chat packet prepared at `docs/NEXT_CHAT_AMN2_PHASE_3_SERVICE_MODE.ru.md`. Next decision: remain in manual runtime mode or run a separate service-mode gate for web/bot `systemd` plus HTTPS reverse proxy. This handoff does not unlock public API `3040`, direct public web/admin `3030`, production peer mutations, config delivery, Local Agent mutations or backup/import/reboot.

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
