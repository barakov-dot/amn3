# NEXT CHAT: AMN2 Phase 4 Unified Product Gate

Дата: 2026-06-09.

Рабочая папка нового основного чата:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB
```

Назначение: перевести основной coordination-чат в Phase 4 после закрытого Phase 3 service-mode baseline. Phase 4 не является новым live-write gate. Это единый контур для продукта, API, web-panel UX, PRVTPRO/KYORESUAS intake и подготовки следующих безопасных `amn2` slices.

## Current Truth

```text
AMN3 repo: C:\Users\SooL\Documents\VPS-OPS-LAB
AMN3 remote: https://github.com/barakov-dot/amn3.git
AMN3 branch: master
AMN3 checkpoint before this Phase 4 packet: a205daa Record web panel UX review evidence

AMN2 repo: C:\Users\SooL\Documents\Amneziya
AMN2 remote: https://github.com/barakov-dot/amn2.git
AMN2 branch: codex-vps-test-prep
AMN2 source-overlay/package head: f7f6131 Update integration status for c92 manual prelaunch

target VPS mode: service-mode web/bot active, loopback-only
operator access: SSH local port forward to 127.0.0.1:3030, external browser only
web/admin bind: 127.0.0.1:3030
amneziya-web: active/enabled
amneziya-bot: active/enabled
loopback login: 200
public/direct 3030: closed by loopback bind
public API 3040: absent/closed
TCP 80/443: absent
domain/Caddy/HTTPS public cutover: deferred, no domain planned
VPS_APPLY_ENABLED: false
peer scope: two remaining approved test peers
revoked peers: Neobyatnaya-AMNZ-3, Neobyatnaya-AMNZ-4
```

Phase 3 service-mode loopback is considered closed as a baseline. Do not reopen manual-vs-service-mode as an unresolved question unless new evidence contradicts this state.

## What Phase 4 Is

Phase 4 is the unified product/planning gate after the service-mode loopback pass:

- consolidate AMN2/API, target VPS, PRVTPRO/Web Panel and KYORESUAS/API work into one decision map;
- convert external-project ideas into candidate rows before any `amn2` implementation;
- prepare local/read-only `amn2` slices first;
- keep live mutations and public exposure behind separate named gates;
- keep the main chat from issuing ad hoc commands against the VPS.

## What Phase 4 Is Not

Phase 4 does not authorize:

- `VPS_APPLY_ENABLED=true`;
- public API `3040`;
- direct public web/admin `3030`;
- Caddy/nginx/HTTPS public cutover;
- production peer/user mutation beyond the two approved test peers;
- API `config:read`;
- `/api/clients` write CRUD;
- public/self-service config delivery;
- Local Agent write/config mutations;
- backup/import/reboot routes;
- secret-bearing evidence publication.

Any item above requires a separate explicit gate, safe summary and rollback/recovery note.

## Required Reading

Start with:

```text
docs/NEXT_CHAT_AMN2_PHASE_4_UNIFIED_PRODUCT_GATE.ru.md
docs/PROJECT_STATUS_CURRENT.ru.md
docs/PROJECT_CONTEXT_IMPORT.ru.md
docs/AMN_UNIFIED_PROD_GATE_HANDOFF.ru.md
docs/NEXT_CHAT_AMN2_PHASE_3_SERVICE_MODE.ru.md
research/amn2/phase-4-unified-product-gate-handoff-2026-06-09.md
research/amn2/transfer-backlog.md
research/amn2/service-mode-web-panel-read-only-ux-review-evidence-2026-06-09.md
```

Historical Phase 3 evidence is linked from `docs/NEXT_CHAT_AMN2_PHASE_3_SERVICE_MODE.ru.md`; do not paste full logs or secret-bearing runtime files into the new chat.

## Phase 4 Work Lanes

### Lane A. Status And Handoff Consolidation

Allowed:

- docs/status/backlog updates in AMN3;
- safe summaries only;
- one-copy context packet for the main chat;
- cross-linking PRVTPRO/KYORESUAS/AMN2 evidence.

Blocked:

- live VPS commands;
- new package apply;
- new peer write operation;
- secret-bearing artifacts.

### Lane B. Web Panel UX/Product Review

Allowed:

- read-only review through SSH tunnel;
- page labels, navigation, empty states, warnings and safety copy;
- candidate rows for local UI wording/navigation improvements;
- local tests and docs for safe read-only improvements.

Current evidence:

```text
review_status: ok
routes_reviewed: ok
authenticated_overview_ok: ok
write_actions_called: no
config_delivery_requested: no
api_token_issue_revoke_called: no
sync_or_health_actions_called: no
backup_import_reboot_called: no
secrets_published: no
result: passed-minimal-safe-summary
```

Important limitation: detailed page-by-page UX findings were not returned. If concrete UX tasks are needed, run a second read-only UX pass using `docs/AMN2_WEB_PANEL_READ_ONLY_UX_REVIEW_EVIDENCE_TEMPLATE.ru.md`.

### Lane C. PRVTPRO And KYORESUAS Candidate Intake

Use this row format before any `amn2` work:

```text
candidate_id:
source:
feature_area:
user_value:
AMN2_fit:
license_boundary:
risk_class:
secret_surface:
remote_write_surface:
test_plan:
required_gate:
recommendation: accept | defer | reject | research
```

Default boundaries:

- PRVTPRO/Amnezia-Web-Panel is GPL-3.0: research-only, no code/UI/templates/scripts/managers copied.
- KYORESUAS/API is used as product/architecture signal: own AMN2 implementation, no direct production install.
- Any secret-bearing config delivery, write API or remote mutation candidate stays blocked until a named gate exists.

### Lane D. AMN2 Local Read-Only Slice Prep

Good next local candidates:

- detailed web-panel UX backlog from a second read-only pass;
- status/readiness wording cleanup;
- candidate registry for PRVTPRO/KYORESUAS ideas;
- route/auth/secret policy checks before future route expansion;
- tests for read-only UI/status surfaces.

Do not start live operations from this lane. If an `amn2` code change is selected, create a separate branch/plan in the `amn2` repo and keep the first slice local/read-only unless explicitly approved otherwise.

### Lane E. Future Live Gates

Open a separate named gate only when Phase 4 selects a live operation. The gate must include:

```text
gate_name:
target_vps:
operation_class:
allowed_actions:
blocked_actions:
preflight:
rollback:
safe_summary_fields:
secrets_policy:
go_no_go_decision:
```

Examples that require a separate gate:

- production peer apply/revoke;
- public HTTPS reverse proxy;
- public API exposure;
- config delivery expansion;
- Local Agent deployment/mutations;
- backup/import/reboot.

## Phase 4 First Recommended Steps

1. Confirm this Phase 4 handoff is the main chat entry point.
2. Keep target VPS unchanged: web/bot active, web/admin loopback-only, SSH tunnel access only.
3. Treat `P4-C009` web-panel user/config visibility as the completed first local-only slice; evidence: `research/amn2/phase-4-web-panel-user-config-visibility-implementation-2026-06-09.md`.
4. Continue with `P4-I002`: AMN2 service-mode/read-only status wording.
5. If a live action is proposed, stop and create a separate gate first.

## One-Copy Message For Main Chat

```text
Работаем в C:\Users\SooL\Documents\VPS-OPS-LAB.

Новый этап: AMN2 Phase 4 Unified Product Gate.

Сначала прочитай:
- docs/NEXT_CHAT_AMN2_PHASE_4_UNIFIED_PRODUCT_GATE.ru.md
- docs/PROJECT_STATUS_CURRENT.ru.md
- docs/PROJECT_CONTEXT_IMPORT.ru.md
- docs/AMN_UNIFIED_PROD_GATE_HANDOFF.ru.md
- docs/NEXT_CHAT_AMN2_PHASE_3_SERVICE_MODE.ru.md
- research/amn2/phase-4-unified-product-gate-handoff-2026-06-09.md
- research/amn2/transfer-backlog.md
- research/amn2/service-mode-web-panel-read-only-ux-review-evidence-2026-06-09.md

Текущая точка:
- AMN2 source-overlay/package head: f7f6131
- AMN3 checkpoint before Phase 4 packet: a205daa
- target VPS: service-mode web/bot active, web/admin 127.0.0.1:3030 only
- operator access: SSH tunnel + external browser
- public/direct 3030: closed by loopback bind
- public API 3040: absent/closed
- TCP 80/443: absent
- no domain/Caddy/HTTPS public cutover
- VPS_APPLY_ENABLED=false
- remaining approved test peers: Neobyatnaya-AMNZ-1 and Neobyatnaya-AMNZ-2
- Neobyatnaya-AMNZ-3 and Neobyatnaya-AMNZ-4 revoked

Задача Phase 4:
1. Не повторять Phase 3 как незакрытый вопрос.
2. Свести AMN2/API, target VPS, PRVTPRO/Web Panel и KYORESUAS/API в одну decision map.
3. Готовить только local/read-only slices по умолчанию.
4. PRVTPRO/KYORESUAS идеи заносить как candidate rows, не переносить код напрямую.
5. Любой public API, direct public web/admin, HTTPS reverse proxy, config delivery, write CRUD, Local Agent mutation, backup/import/reboot или production peer mutation запускать только отдельным named gate.

Не публиковать:
.env, servers.yml, raw tokens, Authorization headers, token hashes, web password hash, session secret, private keys, PSK, peer public keys, .conf, QR, vpn://, backup contents, session cookies, public endpoint values или full logs.

Закрытый первый slice:
- P4-C009 web-panel user/config visibility, local-only.

Следующий рекомендуемый slice:
- P4-I002 service-mode/read-only status wording.
```
