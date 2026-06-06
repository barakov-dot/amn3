# AMN2 Controlled Prod Readiness Runbook

Дата: 2026-06-06.

Назначение: зафиксировать первый безопасный production-режим для текущего `amn2/codex-vps-test-prep` baseline после real VPS read-only smoke. Текущий GitHub head `32d01fd` прошел read-only VPS smoke; следующий шаг - operator-only controlled prod readiness decision.

Это не разрешение на public web/API exposure, `/api/clients` write CRUD, API `config:read`, public/self-service config delivery, Local Agent mutations, backup/import/reboot routes или новые live peer mutations.

## Текущая production-точка

```text
repo: https://github.com/barakov-dot/amn2.git
branch: codex-vps-test-prep
head: 32d01fd Update integration status for controlled prod
AMN3 package: dist/amn2-vps-update-and-smoke-kit-32d01fd.zip
package sha256: BE59AF74001AC4F094C753B565A4E672194D823C4F65B6CB476F4FF01B310807
source sha256: 034753DA7EC42ACF869519F43909EEFDC8A392A5665B2A33C935F8A058CCB99B
latest proven VPS read-only smoke: 32d01fd pass, run_id 20260606T185114Z
previous VPS read-only smoke: 1a193b9 pass, run_id 20260606T154636Z
VPS smoke evidence: research/amn2/integration-status-controlled-prod-update-2026-06-06.md
32d01fd package evidence: research/amn2/integration-status-controlled-prod-update-2026-06-06.md
Phase 2 live single disposable peer gate: verified-live on stable line, evidence research/amn2/phase-2-live-vps-gate-evidence-2026-06-05.md
```

## Controlled Prod Mode

Controlled prod means:

- `/opt/amn2` stays on the VPS-smoked `32d01fd` source overlay unless a new package and smoke gate supersede it.
- `VPS_APPLY_ENABLED=false` is the default operator shell state.
- Read-only API smoke and web/admin checks use loopback only.
- Web panel access is operator-only through SSH tunnel, private network, or a separately approved reverse-proxy/firewall/TLS gate.
- Existing operator CLI/bot behavior may continue only inside the already verified production contract.
- New live writes require separate operator confirmation and dedicated evidence.
- No secret-bearing output is copied into AMN3, GitHub or chat.

Controlled prod does not mean broad public SaaS mode.

## Allowed Without New Gate

Allowed after this readiness check:

- Keep current `/opt/amn2` runtime on `32d01fd`.
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
- [ ] `.amn2_source_overlay_commit` on VPS is `32d01fd` after applying the current kit.
- [ ] Latest read-only smoke safe summary is `VPS verdict: pass`.
- [ ] Smoke result has 5 checked routes with `status: passed`.
- [ ] `/api/integration/status` reports `read_only_vps_smoked`, `phase_2=verified_live`, `controlled_prod_readiness.decision=pending_operator_evidence`, `write_routes_enabled=false` and `write_operations_enabled=false`.
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
- source overlay commit is not `32d01fd` after applying the current kit, or not an explicitly superseding smoke-passed commit;
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

After `controlled-prod-ready`, the next safe implementation slice should remain read-only. The recommended first candidate is controller-safe Local Agent runtime summary from `research/amn2/local-agent-runtime-metadata-alignment.md`.

Do not jump directly to config delivery, public API writes, backup/import or Local Agent mutations.
