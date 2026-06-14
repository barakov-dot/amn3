# AMN2 Phase 7 transition packet

Дата: 2026-06-14.

Статус: `phase-7-transition-prepared`.

Phase 7 name: `Release Candidate Readiness / Clean Installer RC`.

Phase 7 status: `pre-release / release-candidate readiness`.

Default lane: `local-only/docs/tests/security/package-preflight`.

## Prepared artifacts

- `docs/NEXT_CHAT_AMN2_PHASE_7_RELEASE_CANDIDATE.ru.md`;
- `docs/PHASE_7_RELEASE_CANDIDATE_PLAN.ru.md`;
- updated project status/context/transfer backlog;
- weekly upstream-refresh automations updated to Phase 7 context.

## Current source of truth

```text
AMN2 current head: b121865 Add multi instance conflict model
AMN2 latest VPS-smoked/package head: 0de7a77 Polish fresh installer preflight planning
Current disposable VPS: 89.185.80.166
Known-good evidence: research/amn2/phase-6-live-update-smoke-0de7a77-2026-06-14.md
```

## Access decision

No VPS/SSH/PowerShell/provider/Telegram/payment access is required for this
transition packet or default Phase 7 work.

Future live work requires separate named gates and operator-provided access at
the moment of execution.

## Carry-forward summary

Critical gated/deferred items carried into Phase 7:

- public exposure: `P7-C002`;
- config delivery: `P7-C003`;
- write API / install mutation / Local Agent mutation / production peer-user
  mutation: `P7-C005`;
- backup/restore/import: `P7-C006`;
- destructive clean installer execution / rebuild: `P7-C004`;
- live package/apply/smoke for post-`0de7a77` heads: `P7-C001`;
- Telegram identity/profile/media mutation: `P7-C007`.

Default first recommendation:

```text
P7-I001 + P7-M001 together as local-only package/test readiness.
```

## Negative controls

No live VPS command, SSH command, package rebuild/apply on VPS, service
restart/deploy, public exposure, public OpenAPI publication, config delivery,
write API, Local Agent mutation, backup/import/reboot, production peer/user
mutation, destructive action, Telegram action, secret publication or
upstream/GPL code copy was performed.
