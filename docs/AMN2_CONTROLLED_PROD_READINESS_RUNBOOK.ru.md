# AMN2 Controlled Prod Readiness Runbook

Дата: 2026-06-06.

Назначение: зафиксировать безопасный production-режим для текущего `amn2/codex-vps-test-prep` baseline после real VPS read-only smoke. Первичный source overlay `c8a6363` прошел read-only VPS update/smoke, 2026-06-07 head `42ffa65` прошел safe source-overlay update/smoke на `/opt/amn2`, затем controlled production safety follow-up `c92bd1a` также прошел source-overlay update/read-only smoke.

Актуализация 2026-06-07: operator-only decision recorded as `controlled-prod-ready`; evidence `research/amn2/controlled-prod-ready-2026-06-07.md`.

Post-decision AMN2 update: current `amn2/codex-vps-test-prep` git head is `c92bd1a Bind web admin systemd to loopback`. The app-code read-only slice `62ff184 Update controlled prod status visibility` passed VPS git-checkout smoke on `/opt/amn2-git` with six read-only routes. AMN3 package `42ffa65` then passed source-overlay update+read-only smoke on `/opt/amn2`; AMN3 package `c92bd1a` then passed source-overlay update+read-only smoke on `/opt/amn2`.

AMN3 package for the current source-overlay promotion gate is smoke-passed: `dist/amn2-vps-update-and-smoke-kit-c92bd1a.zip`, sha256 `EC48DBA7C91F189512AB77EB5490432C85DA79F987068A98C1CC7F3082387F12`; source sha256 `272CC013A416937AAA2256A1643B2C77F707874D28FDCB2EA16534E349DD4FC2`; evidence `research/amn2/web-admin-loopback-systemd-vps-smoke-evidence-2026-06-07.md`. Prior `42ffa65` evidence remains `research/amn2/controlled-prod-status-visibility-vps-smoke-evidence-2026-06-07.md`.

Это не разрешение на public web/API exposure, `/api/clients` write CRUD, API `config:read`, public/self-service config delivery, Local Agent mutations, backup/import/reboot routes или новые live peer mutations.

## Текущая production-точка

```text
repo: https://github.com/barakov-dot/amn2.git
branch: codex-vps-test-prep
last VPS-smoked head: c92bd1a Bind web admin systemd to loopback
current amn2 git head: c92bd1a Bind web admin systemd to loopback
current app-code read-only smoke slice: 62ff184 Update controlled prod status visibility
current git-checkout smoke: 62ff184 pass on /opt/amn2-git, checked_routes=6
current source-overlay package: dist/amn2-vps-update-and-smoke-kit-c92bd1a.zip
current source-overlay package status: read-only-vps-smoke-pass
previous VPS-smoked head: 42ffa65 Record git checkout smoke status
current VPS-smoked source-overlay package: dist/amn2-vps-update-and-smoke-kit-c92bd1a.zip
current package sha256: EC48DBA7C91F189512AB77EB5490432C85DA79F987068A98C1CC7F3082387F12
current source sha256: 272CC013A416937AAA2256A1643B2C77F707874D28FDCB2EA16534E349DD4FC2
current package status: read-only-vps-smoke-pass
latest proven VPS read-only smoke: c92bd1a pass, source_update_run_id 20260607T182118Z, api_smoke_run_id 20260607T182131Z
previous VPS read-only smoke: 42ffa65 pass, promotion run_id 20260607T165625Z, repeat run_id 20260607T165807Z
historical VPS read-only smoke: 1a193b9 pass, run_id 20260606T154636Z
VPS smoke evidence: research/amn2/web-admin-loopback-systemd-vps-smoke-evidence-2026-06-07.md
prior VPS smoke evidence: research/amn2/controlled-prod-status-visibility-vps-smoke-evidence-2026-06-07.md
repeat VPS smoke evidence: research/amn2/controlled-prod-status-visibility-vps-repeat-smoke-2026-06-07.md
c8a6363 historical evidence: research/amn2/local-agent-runtime-summary-vps-smoke-evidence-2026-06-06.md
Phase 2 live single disposable peer gate: verified-live on stable line, evidence research/amn2/phase-2-live-vps-gate-evidence-2026-06-05.md
```

## Controlled Prod Mode

Controlled prod means:

- `/opt/amn2` stays on the VPS-smoked `c92bd1a` source overlay unless a later package passes a new read-only update/smoke gate.
- `62ff184`/`42ffa65` git-checkout smoke is now paired with source-overlay smoke evidence for `/opt/amn2`.
- `VPS_APPLY_ENABLED=false` is the default operator shell state.
- Read-only API smoke and web/admin checks use loopback only.
- Web panel access is operator-only through SSH tunnel, private network, or a separately approved reverse-proxy/firewall/TLS gate.
- Existing operator CLI/bot behavior may continue only inside the already verified production contract.
- New live writes require separate operator confirmation and dedicated evidence.
- No secret-bearing output is copied into AMN3, GitHub or chat.

Controlled prod does not mean broad public SaaS mode.

## Allowed Without New Gate

Allowed after this readiness check:

- Keep current VPS-smoked `/opt/amn2` runtime on `c92bd1a`.
- Run read-only API loopback smoke again.
- Run DB-only server config sync used by the smoke script.
- Check web-admin read-only/status pages through loopback or SSH tunnel.
- Inspect safe evidence summaries only.
- Use current verified operator flows according to existing runbooks.
- Record status/evidence updates in AMN3.

## Still Blocked

Blocked until separate explicit gates:

- `VPS_APPLY_ENABLED=true`.
- `apply-peer --apply` and `revoke-peer --apply`.
- Public web/API exposure.
- API `config:read`.
- `/api/clients` write CRUD.
- Public/self-service config delivery.
- Local Agent clients/configs/write mutations.
- Backup/import/reboot routes.
- Full logs, `.env`, `servers.yml`, raw tokens, Authorization headers, token hashes, private keys, PSK, `.conf`, QR and `vpn://` links in evidence.

## Readiness Checklist

Before calling the VPS controlled-prod-ready:

- [ ] Current package checksum is recorded.
- [ ] `.amn2_source_overlay_commit` on VPS is `c92bd1a` after applying the current kit.
- [ ] Latest read-only smoke safe summary is `VPS verdict: pass`.
- [ ] Smoke result has 6 checked routes with `status: passed`.
- [ ] `/api/integration/status` is included in the smoke result and returns `200` with empty forbidden markers.
- [ ] Auth checks show missing bearer `401`, wrong scope `403`, revoked token `401`.
- [ ] Listener and audit checks are `passed`.
- [ ] Operator shell default has `VPS_APPLY_ENABLED=false`.
- [ ] Web/admin access path is loopback, SSH tunnel, private network, or separately approved reverse proxy.
- [ ] Host key prompt did not appear, or host key was verified out-of-band.
- [ ] Recovery path is known before any future write gate.
- [ ] No secret-bearing files or raw logs are pasted into AMN3/GitHub/chat.

## Operator Verification Commands

These commands are safe to publish because they do not contain secret values. Run them on the VPS only when needed.

```bash
cd /opt/amn2
source venv/bin/activate

cat .amn2_source_overlay_commit

export VPS_APPLY_ENABLED=false
export AMN2_RUN_PREFLIGHT=0
export AMN2_SYNC_SERVER_CONFIG=1
export AMN2_REQUIRE_SERVER_DB_SYNC=1
export AMN2_SERVER_NAME=local

bash ./amn2_api_loopback_smoke.sh
```

After the smoke, publish only:

```bash
cat /opt/amn2/vps-smoke/api-loopback-*/api-smoke-safe-summary.txt
cat /opt/amn2/vps-smoke/api-loopback-*/api-smoke-result.json
```

Do not publish `api-server.log` unless manually redacted.

## Stop Conditions

Stop and do not proceed to prod if:

- package checksum does not match;
- source overlay commit is not `c92bd1a` after applying the current kit, or not an explicitly superseding smoke-passed commit;
- any smoke status is not `passed`;
- any route reports forbidden markers;
- auth checks do not return the expected `401/403/401`;
- unexpected host key prompt appears;
- web/API must be exposed publicly to complete the check;
- recovery path is unclear;
- evidence would require pasting secrets or full logs.

## Recovery Boundary

This readiness runbook is read-only and should not require rollback.

For future write gates, recovery must be documented before execution and scoped to the touched object. For peer apply/revoke this means:

- dedicated test peer only;
- public key/PSK/private key kept in operator notes, not AMN3;
- revoke path verified before apply;
- final sync confirms the test peer is removed or restored to the expected state.

## Evidence Template

Record only safe values:

```text
date/time:
operator:
server alias:
source overlay commit:
package:
package sha256:
read-only smoke run_id:
preflight_status:
server_db_sync_status:
api_ready_status:
api_smoke_status:
auth_status:
listener_status:
audit_status:
checked_routes:
forbidden_markers:
web/admin access path:
VPS_APPLY_ENABLED default:
host key prompt:
recovery path known:
decision:
next action:
```

## Decision Rules

For a fresh decision chat, use:

```text
docs/NEXT_CHAT_AMN2_CONTROLLED_PROD_DECISION.ru.md
```

`controlled-prod-ready` is allowed only when the readiness checklist is complete and no stop condition is present.

`needs-fix` is required if smoke, auth, listener, audit, checksum, host key, access-path or evidence hygiene fails.

`defer-prod` is acceptable when the system is healthy but operator recovery/access conditions are not yet ready.

## Next Engineering Slice

After `controlled-prod-ready`, the next safe implementation slice should remain read-only. The earlier controller-safe Local Agent runtime summary candidate is already implemented and read-only VPS-smoked. Prefer read-only controlled-prod status/recovery visibility, operator documentation cleanup, or another read-only status/observability slice.

Do not jump directly to config delivery, public API writes, backup/import or Local Agent mutations.
