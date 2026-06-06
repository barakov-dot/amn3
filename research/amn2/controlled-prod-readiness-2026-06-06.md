# Controlled Prod Readiness 2026-06-06

Purpose: record the next safe stage after `c8a6363` passed real VPS read-only update/smoke.

This document contains no secrets, no full logs and no live write evidence.

## Decision

```text
status: controlled-prod-ready
target mode: operator-only controlled prod
amn2 branch at evidence capture: codex-vps-test-prep
amn2 head at evidence capture: c8a6363 Add Local Agent runtime summary mapper
AMN3 package at evidence capture: dist/amn2-vps-update-and-smoke-kit-c8a6363.zip
package sha256: 027ECC1BAD7321FCCD61A4CCCA3AC9F06AAA9AC6A3D7115B4813253D19C2CFBF
source sha256: E1E198979D988B3A5AA038CF732B8DCDBE854C48A6D381FADBA05BFDEE0251C6
latest VPS smoke: c8a6363 read-only-vps-smoke-pass, run_id 20260606T202040Z
previous VPS smoke: 32d01fd read-only-vps-smoke-pass, run_id 20260606T185114Z
runbook: docs/AMN2_CONTROLLED_PROD_READINESS_RUNBOOK.ru.md
next chat handoff: docs/NEXT_CHAT_AMN2_CONTROLLED_PROD_DECISION.ru.md
reverse proxy confirmation: research/amn2/controlled-prod-reverse-proxy-confirmation-2026-06-07.md
controlled prod ready evidence: research/amn2/controlled-prod-ready-2026-06-07.md
```

## Scope

Controlled prod readiness covers:

- confirming the current VPS-smoked baseline;
- preserving read-only loopback/API/web-admin boundaries;
- keeping operator write flows behind explicit gates;
- documenting stop conditions and safe evidence format;
- defining what must remain blocked.

It does not enable:

- public web/API exposure;
- broad API write surfaces;
- config delivery;
- Local Agent clients/configs/mutations;
- backup/import/reboot;
- new live peer mutations.

## Why This Stage

The previous stage proved:

- `1a193b9` package passed real VPS read-only smoke;
- `32d01fd` updates only the read-only integration status contract and passed real VPS read-only smoke;
- `c8a6363` adds the mapper-only Local Agent runtime summary and passed real VPS read-only smoke;
- the API smoke covered five read-only routes;
- auth/listener/audit checks passed;
- Phase 2 single disposable peer apply/revoke was previously verified on the stable line;
- PSK stdin handling was added before repeated live peer work.

The remaining risk before first controlled prod is operational, not feature implementation: access path, rollback awareness, evidence hygiene and stop/go criteria.

## Readiness Prefill

Known from safe evidence already returned:

```text
package checksum recorded in AMN3: yes
latest read-only smoke safe summary: VPS verdict pass
read-only smoke run_id: 20260606T202040Z
preflight_status: skipped
server_db_sync_status: passed
api_ready_status: passed
api_smoke_status: passed
auth_status: passed
missing_bearer_http: 401
wrong_scope_http: 403
revoked_token_http: 401
listener_status: passed
audit_status: passed
checked_routes: 5
route result status: passed
forbidden_markers: none in all returned routes
secret-bearing evidence pasted: no
source overlay commit confirmed: c8a6363
VPS_APPLY_ENABLED shell: false
VPS_APPLY_ENABLED .env: false
web/admin access path: approved-reverse-proxy over HTTPS
public API 3040 exposed: no
web listener: 127.0.0.1:3030
login_http: 200
rollback/current kits and data/.env/servers.yml: present
recovery path known: yes
decision: controlled-prod-ready
```

Closed operator-only confirmations:

```text
integration status body: confirm safe fields if required by the readiness checklist
host key prompt: not applicable for web/admin reverse-proxy access, unless SSH is used for operations
recovery path known: yes
decision: controlled-prod-ready
```

Do not use this prefill as authorization for public exposure or new write operations.

Next-chat handoff for the final operator decision:

```text
docs/NEXT_CHAT_AMN2_CONTROLLED_PROD_DECISION.ru.md
```

## Operator Result

Recorded result:

```text
c8a6363 read-only-vps-smoke-pass; controlled-prod-ready
```

## Next Implementation Candidate

After readiness is recorded, the next code slice should stay read-only. The previous candidate, controller-safe Local Agent runtime summary, is already implemented and read-only VPS-smoked. Prefer another read-only/status/operator-safety slice before any write expansion.

```text
read-only controlled-prod status/recovery visibility
operator documentation cleanup
another read-only status/observability slice
```

Blocked until separate gates:

- `/agent/clients`;
- `/agent/configs`;
- API `config:read`;
- public/self-service config delivery;
- backup/import/reboot;
- write lifecycle.
