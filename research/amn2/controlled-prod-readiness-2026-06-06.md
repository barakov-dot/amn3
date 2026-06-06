# Controlled Prod Readiness 2026-06-06

Purpose: record the next safe stage after `1a193b9` passed real VPS read-only update/smoke.

This document contains no secrets, no full logs and no live write evidence.

## Decision

```text
status: readiness-runbook-published
target mode: operator-only controlled prod
current amn2 branch: codex-vps-test-prep
current amn2 head: 1a193b9 Add remote partial failure contract
current AMN3 package: dist/amn2-vps-update-and-smoke-kit-1a193b9.zip
package sha256: 48530E59618C413BF8B298CD01801D28DD1AA6E144EAD946EF5BCF303BE56533
source sha256: 8FA2E86FF056A4BA0DE5BC3F913EF33DFC2CC9EF34DDCDC03B0EA09FAD655AEC
latest VPS smoke: read-only-vps-smoke-pass, run_id 20260606T154636Z
runbook: docs/AMN2_CONTROLLED_PROD_READINESS_RUNBOOK.ru.md
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
- the API smoke covered five read-only routes;
- auth/listener/audit checks passed;
- Phase 2 single disposable peer apply/revoke was previously verified on the stable line;
- PSK stdin handling was added before repeated live peer work.

The remaining risk before first controlled prod is operational, not feature implementation: access path, rollback awareness, evidence hygiene and stop/go criteria.

## Required Operator Result

The next operator evidence should use the runbook template and end in one of:

```text
controlled-prod-ready
needs-fix
defer-prod
```

Until `controlled-prod-ready` is recorded, treat the current state as:

```text
read-only-vps-smoke-pass; controlled-prod-readiness-pending
```

## Next Implementation Candidate

After readiness is recorded, the next code slice should stay read-only:

```text
controller-safe Local Agent runtime summary
```

Design source:

```text
research/amn2/local-agent-runtime-metadata-alignment.md
```

Blocked until separate gates:

- `/agent/clients`;
- `/agent/configs`;
- API `config:read`;
- public/self-service config delivery;
- backup/import/reboot;
- write lifecycle.
