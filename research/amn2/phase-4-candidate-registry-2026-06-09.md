# Phase 4 Candidate Registry 2026-06-09

Дата: 2026-06-09.

Назначение: единый local/read-only candidate registry для AMN2/API, target VPS Phase 3 evidence, PRVTPRO/Web Panel ideas и KYORESUAS/API ideas. Этот файл не открывает live gate и не разрешает public/write/config operations.

## Current Boundary

Accepted baseline:

- Phase 3 service-mode loopback baseline is closed.
- Web/bot service-mode is enabled and active on target VPS.
- Web/admin listens only on `127.0.0.1:3030`.
- Operator access is SSH tunnel only.
- No domain is planned; Caddy/HTTPS public cutover is deferred indefinitely.
- Public/direct `3030` is closed by loopback bind.
- Public API `3040` is absent/closed.
- TCP `80/443` are absent.
- `VPS_APPLY_ENABLED=false`.
- Current approved test peers: `Neobyatnaya-AMNZ-1`, `Neobyatnaya-AMNZ-2`.
- Revoked test peers: `Neobyatnaya-AMNZ-3`, `Neobyatnaya-AMNZ-4`.
- Web-panel unauth/authenticated read-only navigation passed, but detailed page-by-page UX findings were not returned.
- `P4-C009` local investigation clarified that `/users` shows local AMN2 DB users/devices only; live VPS peers created outside AMN2 belong to server peer-sync/read-only inventory unless a separate write/backfill gate is opened.

Still blocked without a separate named gate:

- live VPS commands;
- public API `3040`;
- direct public web/admin `3030`;
- Caddy/HTTPS/domain cutover;
- config delivery, `.conf`, QR, `vpn://`;
- `/api/clients` write CRUD;
- Local Agent mutations;
- backup/import/reboot;
- production peer/user mutation;
- copying GPL/upstream code.

## Priority And Gate Definitions

Priorities:

- `critical`: prevents unsafe transfer, secret leakage, public exposure, or write-route drift.
- `important`: gives direct product value or prepares a likely safe AMN2 slice.
- `normal`: useful product polish, planning, docs or future design, but not blocking Phase 4.
- `cosmetic`: naming/docs/grouping polish with low runtime risk.

Gate classes:

- `local-only`: can be done in AMN3 docs or AMN2 local tests/docs/templates without live VPS commands, route expansion, config output, token issue/revoke, or runtime mutation.
- `requires VPS gate`: may be safe after a named preflight, but needs real target VPS evidence because it reads live runtime, polls real services, deploys agent/service code, or changes server-observed behavior.
- `blocked until separate write/config/public gate`: must not be implemented in Phase 4 default mode because it exposes public surfaces, returns secret-bearing config, mutates peers/users/runtime, or performs destructive operations.

## Registry Matrix

| Priority | Local-only | Requires VPS gate | Blocked until separate write/config/public gate |
| --- | --- | --- | --- |
| `critical` | `P4-C001`, `P4-C002`, `P4-C003`, `P4-C009` | `P4-C004` | `P4-C005`, `P4-C006`, `P4-C007`, `P4-C008` |
| `important` | `P4-I001`, `P4-I002`, `P4-I003`, `P4-I005` | `P4-I006`, `P4-I007` | `P4-I008`, `P4-I009` |
| `normal` | `P4-I004`, `P4-N001`, `P4-N002`, `P4-N003`, `P4-N004` | `P4-N005`, `P4-N006` | `P4-N007` |
| `cosmetic` | `P4-X001`, `P4-X002`, `P4-X003` | - | `P4-X004` |

## Candidate Rows

### Critical

```text
candidate_id: P4-C001
priority: critical
source: Phase 4 handoff; transfer-backlog; PRVTPRO/KYORESUAS intake boundary
feature_area: candidate registry / gate classification
user_value: prevents ad hoc transfer of upstream ideas into AMN2 without priority, risk and gate labels
AMN2_fit: yes, as AMN3 planning source before any AMN2 branch
license_boundary: no upstream code copied; PRVTPRO GPL remains research-only; KYORESUAS used as idea/reference only
risk_class: docs-only governance
secret_surface: none
remote_write_surface: none
test_plan: review registry rows against active handoff and transfer-backlog before selecting a slice
required_gate: local-only
recommendation: accept
```

```text
candidate_id: P4-C002
priority: critical
source: AMN2 route/auth policy matrix; PRVTPRO API surface; KYORESUAS API surface
feature_area: route/auth/secret policy drift guard before any new route
user_value: avoids accidental privilege escalation when API, web, bot or Local Agent surfaces change
AMN2_fit: strong; existing AMN2 policy/binding tests are the baseline
license_boundary: independent AMN2 implementation only
risk_class: read-only guardrail
secret_surface: route metadata only; no secret output
remote_write_surface: none
test_plan: add/maintain local tests that fail when a runtime route/action lacks policy, auth, risk and audit binding
required_gate: local-only
planning_status: route/secret gate plan created 2026-06-09; see research/amn2/phase-4-route-secret-gate-plan-2026-06-09.md
recommendation: accept
```

```text
candidate_id: P4-C003
priority: critical
source: AMN2 secret inventory; config delivery inventory; PRVTPRO config delivery integrity; KYORESUAS config/QR signal
feature_area: secret-bearing artifact classification
user_value: keeps `.conf`, QR, `vpn://`, token hashes, private keys and PSK out of logs, docs, backup metadata and API responses
AMN2_fit: strong; existing secret inventory/redaction/config delivery contracts are baseline
license_boundary: independent AMN2 tests and docs only
risk_class: secret-read guardrail
secret_surface: secret metadata only, no raw payloads
remote_write_surface: none
test_plan: maintain local redaction/manifest tests; any new config output must prove no secret leakage in safe metadata
required_gate: local-only
planning_status: route/secret gate plan created 2026-06-09; see research/amn2/phase-4-route-secret-gate-plan-2026-06-09.md
recommendation: accept
```

```text
candidate_id: P4-C004
priority: critical
source: Phase 3 target VPS evidence; service-mode final safety snapshot
feature_area: target VPS baseline recheck before any future live gate
user_value: confirms web/bot, loopback bind, public ports and `VPS_APPLY_ENABLED=false` before a named live/public/write operation
AMN2_fit: yes, but only as gate evidence, not as default Phase 4 work
license_boundary: not applicable
risk_class: read-only live environment check
secret_surface: safe summary only; no `.env` values, tokens, peer keys, configs or full logs
remote_write_surface: read-only VPS commands
test_plan: named gate preflight with explicit allowed commands, safe fields and no secret publication
required_gate: requires VPS gate
recommendation: defer
```

```text
candidate_id: P4-C005
priority: critical
source: Phase 4 boundary; PRVTPRO public panel ideas; KYORESUAS nginx/API exposure signal
feature_area: public exposure: API 3040, direct web/admin 3030, HTTPS reverse proxy/domain cutover
user_value: could improve access convenience later, but currently contradicts no-domain loopback-only decision
AMN2_fit: not for Phase 4 default mode
license_boundary: no upstream code/config copied
risk_class: public-exposure
secret_surface: session cookies, admin auth, bearer tokens and panel data become internet-facing if exposed
remote_write_surface: firewall/reverse proxy/service changes
test_plan: separate public-cutover gate with DNS, TLS, auth, rollback, firewall and `VPS_APPLY_ENABLED=false` proof
required_gate: blocked until separate write/config/public gate
recommendation: defer
```

```text
candidate_id: P4-C006
priority: critical
source: KYORESUAS `/clients`; PRVTPRO connections API; AMN2 remote operation evidence
feature_area: `/api/clients` write CRUD and peer lifecycle mutations
user_value: API-first client lifecycle is core product direction, but unsafe without write gate
AMN2_fit: future fit after route/auth, partial-failure, audit, locking and real VPS gate
license_boundary: own AMN2 implementation; no KYORESUAS/PRVTPRO code copied
risk_class: state-write + remote-exec + secret-read
secret_surface: generated configs, QR, `vpn://`, PSK/private keys, peer identifiers
remote_write_surface: peer apply/revoke/sync, Docker/AWG restart/reload, local DB changes
test_plan: local fake-runner tests first; then named single-test-peer VPS gate before broad lifecycle
required_gate: blocked until separate write/config/public gate
recommendation: defer
```

```text
candidate_id: P4-C007
priority: critical
source: AMN2 config delivery policy; PRVTPRO share/self-service; KYORESUAS create-client returns config signal
feature_area: API `config:read`, public/self-service config delivery, QR and `vpn://` delivery routes
user_value: high user value for onboarding, but high secret leakage risk
AMN2_fit: future fit after ownership, scoped token, expiry/revoke, rate limit, redaction and audit gates
license_boundary: own AMN2 implementation; no upstream templates/scripts copied
risk_class: secret-read + public-exposure
secret_surface: `.conf`, QR payload/PNG, `vpn://`, private key, PSK, endpoint values
remote_write_surface: none for read delivery, but may couple to peer creation if combined with CRUD
test_plan: route-level tests for ownership, one-time/expiry, no raw token in audit/logs, no config in safe metadata
required_gate: blocked until separate write/config/public gate
recommendation: defer
```

```text
candidate_id: P4-C008
priority: critical
source: PRVTPRO settings backup/restore; KYORESUAS backup/import/reboot; AMN2 backup/import policy contract
feature_area: backup/import/reboot/destructive server operations
user_value: useful for operations and recovery, dangerous for runtime integrity
AMN2_fit: only after separate dangerous-operation design and gate
license_boundary: own AMN2 implementation only
risk_class: destructive + secret-read + state-write
secret_surface: full backup can contain tokens, private keys, PSK, configs, server state and user state
remote_write_surface: restore/import apply, reboot, service restart, filesystem and Docker mutations
test_plan: preview-only local tests already baseline; route exposure requires confirmation, backup-before-write, rollback and VPS gate
required_gate: blocked until separate write/config/public gate
recommendation: defer
```

```text
candidate_id: P4-C009
priority: critical
source: operator web-panel observation during Phase 3 service-mode read-only navigation
feature_area: web-panel user/config visibility gap
user_value: operator must see whether approved test peers/configurations are represented in the panel, or the panel must clearly explain why live peers are not shown there
AMN2_fit: strong; this is directly about the current private web/admin product surface
license_boundary: not applicable
risk_class: read-only data consistency / operator trust
secret_surface: may involve client config identities, peer names and live/server metadata; no `.conf`, QR, `vpn://`, private key, PSK or raw endpoint values should be printed
remote_write_surface: none for investigation; no sync/apply/import/backfill mutation without a separate gate
test_plan: first reproduce locally or with safe read-only evidence; compare web users/config list, local DB records, API/server summaries and live peer inventory using safe counts/names only; then add local regression tests for the chosen display/empty-state behavior
required_gate: local-only for code/tests/docs; requires VPS gate only for a fresh live read-only evidence sample
implementation_status: local-only implemented 2026-06-09 in AMN2 branch codex/phase-4-web-panel-user-config-visibility; see research/amn2/phase-4-web-panel-user-config-visibility-implementation-2026-06-09.md
recommendation: completed; use as local visibility baseline
```

### Important

```text
candidate_id: P4-I001
priority: important
source: service-mode web-panel UX evidence; Phase 4 handoff; PRVTPRO web-panel UX signal
feature_area: detailed read-only web-panel UX backlog
user_value: turns the minimal `ok` review into concrete page/action wording tasks without touching live state
AMN2_fit: strong; private operator panel is the current product surface
license_boundary: PRVTPRO used only as UX/product reference; no GPL UI/templates copied
risk_class: read-only product review
secret_surface: no secrets; safe notes only
remote_write_surface: none
test_plan: second SSH-tunnel read-only pass using the evidence template; return only safe page-by-page findings
required_gate: local-only
recommendation: accept
```

```text
candidate_id: P4-I002
priority: important
source: Phase 3 service-mode evidence; AMN2 web panel safe improvements; integration status pages
feature_area: service-mode/read-only status and safety wording
user_value: operator sees that access is tunnel-only, public ports are closed, write/config actions are gated, and `VPS_APPLY_ENABLED=false`
AMN2_fit: strong local-only template/test slice
license_boundary: independent AMN2 wording
risk_class: read-only UI/status
secret_surface: safe status labels only
remote_write_surface: none
test_plan: focused web tests for integration/status/settings/templates pages; no POST route behavior changes
required_gate: local-only
implementation_status: local-only implemented 2026-06-09 in AMN2 branch codex/phase-4-service-mode-status-wording, commit 83f6d28; see research/amn2/phase-4-service-mode-status-wording-implementation-2026-06-09.md
recommendation: completed; use as service-mode status baseline
```

```text
candidate_id: P4-I003
priority: important
source: KYORESUAS API-first model; AMN2 read-only API route shell
feature_area: read-only API status/schema maturity
user_value: gives controller/integration users stable aggregate status without exposing configs or writes
AMN2_fit: already baseline; future work should refine docs/tests, not open CRUD
license_boundary: own AMN2 API contract; no KYORESUAS code copied
risk_class: read-only API
secret_surface: aggregate metadata only
remote_write_surface: none
test_plan: local API tests for `server:read`/`metrics:read`, safe audit and no secret-bearing fields
required_gate: local-only
design_status: candidate-specific design prepared 2026-06-09; see research/amn2/phase-4-read-only-api-status-design-2026-06-09.md
implementation_plan_status: prepared 2026-06-09; see docs/superpowers/plans/2026-06-09-amn2-p4-i003-read-only-api-status-schema.md
implementation_status: local-only implemented 2026-06-09 in AMN2 branch codex/phase-4-read-only-api-status-schema, commit b71b8f4; see research/amn2/phase-4-read-only-api-status-schema-implementation-2026-06-09.md
recommendation: completed; use as read-only API/status schema contract baseline
```

```text
candidate_id: P4-I005
priority: important
source: AMN2 current auth/security inventory; PRVTPRO/KYORESUAS token signals
feature_area: scoped API token lifecycle docs/tests before route exposure
user_value: prevents broad admin-equivalent tokens when API grows
AMN2_fit: strong; storage/lifecycle local slices already exist
license_boundary: independent AMN2 implementation
risk_class: auth guardrail
secret_surface: token hashes and one-time raw token issue boundary, no raw token in evidence
remote_write_surface: none
test_plan: local tests for expiry, revoke, owner inheritance, scope denial and no raw token in audit
required_gate: local-only
recommendation: accept
```

```text
candidate_id: P4-I006
priority: important
source: KYORESUAS local API agent; AMN2 Local Agent runtime summary/hardening
feature_area: real Local Agent deployment/read-only controller calls
user_value: would reduce dependence on external SSH for future controller integrations
AMN2_fit: future fit; current safe baseline is metadata/read-only only
license_boundary: own AMN2 agent; no KYORESUAS code copied
risk_class: read-only live service deployment now, future remote-exec risk
secret_surface: agent token, runtime metadata, possible Docker/config adjacency
remote_write_surface: deployment/service start and controller-to-agent network path
test_plan: local agent tests first; named VPS gate before deployment or controller-to-agent calls
required_gate: requires VPS gate
recommendation: defer
```

```text
candidate_id: P4-I007
priority: important
source: PRVTPRO status polling; KYORESUAS `/server/load`; AMN2 metrics privacy classification
feature_area: health/status polling against real target services
user_value: better operator dashboards and troubleshooting
AMN2_fit: local aggregate status exists; real polling needs gate discipline
license_boundary: idea only
risk_class: read-only live telemetry
secret_surface: peer names, IPs, endpoints and activity metadata can leak if too detailed
remote_write_surface: none if read-only, but can load SSH/API services
test_plan: local fake telemetry tests; VPS gate only for real service polling/sampling
required_gate: requires VPS gate
recommendation: research
```

```text
candidate_id: P4-I008
priority: important
source: PRVTPRO raw config editing; manager architecture
feature_area: raw server config edit/save
user_value: advanced operator escape hatch
AMN2_fit: poor for Phase 4; too risky without parser, diff, rollback and audit
license_boundary: no GPL code/flows copied
risk_class: secret-read + state-write + destructive
secret_surface: raw server configs, private keys, PSK, endpoint values
remote_write_surface: config file writes, service reload/restart
test_plan: separate design only; parser/schema/diff/rollback tests before any implementation
required_gate: blocked until separate write/config/public gate
recommendation: reject
```

```text
candidate_id: P4-I009
priority: important
source: PRVTPRO configurable subnet/IPAM; AMN2 target peer evidence
feature_area: configurable VPN subnet/IPAM migration
user_value: useful for avoiding conflicts and supporting varied deployments
AMN2_fit: future fit after read-only conflict report; live migration is not Phase 4 default
license_boundary: idea only
risk_class: state-write + runtime migration
secret_surface: configs and peer addressing metadata
remote_write_surface: server config, peer configs, Docker/AWG reload/restart
test_plan: local CIDR/reserved/conflict tests first; migration requires named VPS gate
required_gate: blocked until separate write/config/public gate
recommendation: research
```

### Normal

```text
candidate_id: P4-I004
priority: normal
source: PRVTPRO API taxonomy; KYORESUAS `/clients` and `/server`; AMN2 route policy matrix
feature_area: endpoint taxonomy and OpenAPI/domain grouping
user_value: keeps product/API docs understandable before more endpoints exist
AMN2_fit: good as docs/test alignment, not public docs exposure
license_boundary: idea only; no upstream OpenAPI copied
risk_class: docs-only + read-only API
secret_surface: none
remote_write_surface: none
test_plan: local docs/tests that route groups match current implemented routes and policy entries
required_gate: local-only
implementation_status: local-only implemented 2026-06-09 in AMN2 branch codex/phase-4-endpoint-taxonomy-route-policy-docs, commit acf39f8; see research/amn2/phase-4-endpoint-taxonomy-route-policy-docs-implementation-2026-06-09.md
recommendation: completed; use as private/local endpoint taxonomy baseline, not public OpenAPI/docs exposure
```

```text
candidate_id: P4-N001
priority: normal
source: AMN2 transfer-backlog; docs/status drift after Phase 3
feature_area: AMN3/AMN2 roadmap and evidence synchronization
user_value: keeps future chats from reopening closed Phase 3 questions or selecting unsafe slices
AMN2_fit: AMN3 docs first; AMN2 docs only when a code branch is selected
license_boundary: not applicable
risk_class: docs-only
secret_surface: none
remote_write_surface: none
test_plan: markdown/link review and `rg` checks for stale baseline claims
required_gate: local-only
recommendation: accept
```

```text
candidate_id: P4-N002
priority: normal
source: PRVTPRO manager architecture; AMN2 remote operation contracts
feature_area: protocol manager interface checklist
user_value: helps future manager/plugin work stay capability-based and testable
AMN2_fit: planning/docs fit; no new manager implementation now
license_boundary: no GPL code/commands/templates copied
risk_class: design-only
secret_surface: none
remote_write_surface: none
test_plan: checklist against existing AMN2 manager/export/remote-operation contracts
required_gate: local-only
recommendation: research
```

```text
candidate_id: P4-N003
priority: normal
source: KYORESUAS metrics; wg-easy metrics privacy research; AMN2 read-only metrics classification
feature_area: aggregate metrics privacy docs/tests
user_value: preserves useful aggregate monitoring while preventing detailed client leakage by default
AMN2_fit: good as local tests/docs; detailed/public metrics stay blocked
license_boundary: independent AMN2 classification
risk_class: read-only telemetry
secret_surface: avoid peer names, IPs, endpoints and per-user activity labels
remote_write_surface: none
test_plan: local tests for aggregate-only response shape and scope separation
required_gate: local-only
implementation_status: local-only implemented 2026-06-09 in AMN2 branch codex/phase-4-aggregate-metrics-privacy-boundary, commit 8b6aef8; see research/amn2/phase-4-aggregate-metrics-privacy-boundary-implementation-2026-06-09.md
recommendation: completed; use as aggregate metrics privacy boundary baseline
```

```text
candidate_id: P4-N004
priority: normal
source: web-panel UX evidence; AMN2 bot/web safety wording
feature_area: bot/admin read-only navigation labels and empty states
user_value: reduces operator mistakes by marking gated write/config actions clearly
AMN2_fit: good local-only template/test slice after concrete UX notes
license_boundary: independent wording
risk_class: read-only UI
secret_surface: none
remote_write_surface: none
test_plan: local web/bot rendering tests; no POST/action behavior changes
required_gate: local-only
recommendation: accept
```

```text
candidate_id: P4-N005
priority: normal
source: PRVTPRO attach-existing-server idea; AMN2 target VPS prep evidence
feature_area: attach existing server reconciliation
user_value: could onboard an existing VPS safely if read-only detection is reliable
AMN2_fit: future fit, but real detection touches live target state
license_boundary: idea only
risk_class: read-only live inventory, future state-write
secret_surface: server config/topology metadata
remote_write_surface: none for detection; future attach may write local DB/server records
test_plan: local fake inventory first; named VPS read-only gate for real detection
required_gate: requires VPS gate
recommendation: research
```

```text
candidate_id: P4-N006
priority: normal
source: PRVTPRO/KYORESUAS long-running remote operations
feature_area: background jobs, cancellation and operation queue
user_value: better UX for slow remote operations later
AMN2_fit: useful after write operations are selected; not first Phase 4 implementation
license_boundary: idea only
risk_class: orchestration for state-write/remote-exec
secret_surface: job logs and operation metadata must be redacted
remote_write_surface: future operation runner calls
test_plan: local fake-job tests before any live runner integration; VPS gate for real operations
required_gate: requires VPS gate
recommendation: defer
```

```text
candidate_id: P4-N007
priority: normal
source: PRVTPRO external sync; future hybrid backlog
feature_area: external sync/integration delete flows
user_value: may help future billing/support integrations
AMN2_fit: not Phase 4 AMN2; too broad and destructive
license_boundary: no upstream code copied
risk_class: state-write + destructive integration
secret_surface: external tokens, user identifiers, config state
remote_write_surface: sync delete, local DB mutation, possible peer mutation
test_plan: separate integration threat model and destructive-operation gate
required_gate: blocked until separate write/config/public gate
recommendation: defer
```

### Cosmetic

```text
candidate_id: P4-X001
priority: cosmetic
source: ideas/priority-backlog; KYORESUAS API docs signal
feature_area: OpenAPI/docs grouping polish for existing read-only routes
user_value: easier API navigation for operators/integrators
AMN2_fit: good after route policy docs are stable
license_boundary: no upstream docs copied
risk_class: docs-only
secret_surface: none
remote_write_surface: none
test_plan: docs/link check; confirm no public docs exposure decision is implied
required_gate: local-only
recommendation: accept
```

```text
candidate_id: P4-X002
priority: cosmetic
source: AMN2 backlog
feature_area: naming cleanup for API/status/gate terms
user_value: fewer misunderstandings between manual/service-mode/read-only/live-write states
AMN2_fit: good only if scoped to visible wording and docs
license_boundary: not applicable
risk_class: docs/UI wording
secret_surface: none
remote_write_surface: none
test_plan: focused string/template tests if AMN2 code changes; no behavior changes
required_gate: local-only
recommendation: accept
```

```text
candidate_id: P4-X003
priority: cosmetic
source: AMN3 docs practice
feature_area: Russian-first operator docs polish
user_value: smoother handoff and safer operator execution
AMN2_fit: docs-only unless tied to selected implementation slice
license_boundary: not applicable
risk_class: docs-only
secret_surface: none
remote_write_surface: none
test_plan: link/path review and stale baseline scan
required_gate: local-only
recommendation: accept
```

```text
candidate_id: P4-X004
priority: cosmetic
source: PRVTPRO i18n/RTL signal
feature_area: i18n/RTL expansion
user_value: broader UI accessibility later
AMN2_fit: not near-term while safety/product gates are unsettled
license_boundary: no upstream translation/UI copied
risk_class: UI-only but broad surface
secret_surface: none
remote_write_surface: none
test_plan: separate UI strategy/design decision
required_gate: blocked until separate write/config/public gate
recommendation: defer
```

## Completed AMN2 Local-only Slices

Completed: `P4-C009`, then `P4-I002`, then route/secret gate planning, then `P4-I003` candidate-specific read-only API/status design, then `P4-I003` AMN2 local implementation plan, then `P4-I003` AMN2 local implementation, then `P4-I004` endpoint taxonomy / route-policy docs alignment, then `P4-N003` aggregate metrics privacy boundary visibility.

Completed slice name:

```text
AMN2 web-panel user/config visibility investigation
```

Why this slice was selected:

- It is directly supported by accepted Phase 3 evidence.
- It has immediate operator value in the current private SSH-tunnel panel.
- It addresses a concrete operator observation: created test accounts/configurations were not visible under web-panel users/configurations.
- It does not need live VPS commands.
- It does not open public API, direct public web/admin, config delivery, `/api/clients`, Local Agent mutations, backup/import/reboot or token issue/revoke.
- It can start with local web/API/repository tests and safe evidence review only.

Implemented safe scope:

- Root cause confirmed: expected separation between live peer inventory and local web users/config records.
- Added local tests for the chosen read-only display/empty-state behavior.
- Implemented only local read-only navigation/empty-state clarification.
- No DB/live backfill, sync, apply/revoke, config delivery or token work was performed.
- `P4-I002` implemented the service-mode/read-only status wording on `/integration-status`.
- Route/secret gate planning consolidated existing route/auth, secret inventory, token lifecycle, config delivery policy, manager export and backup/import policy baselines into `research/amn2/phase-4-route-secret-gate-plan-2026-06-09.md`.
- `P4-I003` prepared a candidate-specific read-only API/status schema maturity design in `research/amn2/phase-4-read-only-api-status-design-2026-06-09.md`; no AMN2 code or runtime route changed.
- `P4-I003` AMN2 local implementation plan was prepared in `docs/superpowers/plans/2026-06-09-amn2-p4-i003-read-only-api-status-schema.md`; it limits execution to API route binding tests, schema/status contract tests and docs updates.
- `P4-I003` AMN2 local implementation was completed in branch `codex/phase-4-read-only-api-status-schema`, commit `b71b8f4`; it adds API runtime route bindings, route drift tests, read-only API/status contract tests and policy docs without new routes.
- `P4-I004` endpoint taxonomy / route-policy docs alignment was completed in branch `codex/phase-4-endpoint-taxonomy-route-policy-docs`, commit `acf39f8`; it adds private/local taxonomy docs for the same six read-only routes and links policy docs without public OpenAPI/docs exposure or runtime changes.
- `P4-N003` aggregate metrics privacy boundary visibility was completed in branch `codex/phase-4-aggregate-metrics-privacy-boundary`, commit `8b6aef8`; it adds an additive safe `privacy` marker to `/api/metrics/summary` and locks the response boundary in local API tests/docs without changing route count or exposure.

Next decision: continue `P4-I005` scoped API token lifecycle boundary, or run `P4-I001` only if more private-panel UX evidence is needed first.

## Source Notes

Primary AMN3 sources:

- `docs/NEXT_CHAT_AMN2_PHASE_4_UNIFIED_PRODUCT_GATE.ru.md`
- `docs/PROJECT_STATUS_CURRENT.ru.md`
- `research/amn2/transfer-backlog.md`
- `research/amn2/service-mode-web-panel-read-only-ux-review-evidence-2026-06-09.md`
- `research/amn2/phase-4-unified-product-gate-handoff-2026-06-09.md`

Upstream/reference sources:

- `research/upstreams/prvtpro-amnezia-web-panel-feature-gap.md`
- `research/upstreams/prvtpro-amnezia-web-panel-api-surface.md`
- `research/upstreams/prvtpro-amnezia-web-panel-auth-secrets.md`
- `research/upstreams/prvtpro-amnezia-web-panel-config-delivery-integrity.md`
- `research/upstreams/prvtpro-amnezia-web-panel-manager-architecture.md`
- `research/upstreams/kyoresuas-amnezia-api.md`
- `research/amn2/kyoresuas-api-integration-priority-plan.md`
- `ideas/candidates-for-amn2.md`
- `ideas/priority-backlog.md`
