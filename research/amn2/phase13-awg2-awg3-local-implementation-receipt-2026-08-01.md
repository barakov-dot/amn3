# AMN2 Phase 13 — AWG2/AWG3 local-only implementation receipt

Дата: 2026-08-01
Статус: `local_implementation_reviewed_not_package_or_live_authorized`

## Принятое основание и границы

Оператор утвердил Phase 13 AWG2/AWG3 version-admission и isolated-runtime TDD
implementation plan и разрешил выполнить Tasks 1–10 только в новом
изолированном AMN2 worktree, task-by-task commits и без любых live mutations.

- authoritative base: `55dc243b8e6c6bdb57f8301b56326e4cd4072d19`;
- reviewed head: `ff115b63ca1329640ca13ae0a502d155f99b456b`;
- implementation scope: `local_only`;
- package build, SSH, Spain/USA preflight, config/peer issuance, reboot,
  rollback rehearsal и USA retirement: `not_authorized_and_not_performed`.

Spain AWG2 baseline d1–d7, USA rollback contour и посторонний Spain-сервис
этим local-only slice не изменялись.

## Task-by-task source commits

1. `107cb3c` — canonical AWG2/AWG3 protocol versions;
2. `3da5c91` — protocol compatibility and runtime identities;
3. `913cb0a` — isolated VPN runtime planner;
4. `e3eb19d` — fail-closed client protocol admission;
5. `7e46227` — isolated typed AWG3 renderer;
6. `ac710f0` — issuance bound to exact protocol admission;
7. `3ae644b` — protocol evidence in Passport and Drift;
8. `c058c56` — backup/restore validation for additive Phase 13 state;
9. `3f3abd0` — advisory-only USA retirement readiness evaluator;
10. `ff115b6` — AWG3 removed from legacy issuance surfaces.

## Verification

- focused Phase 13 suite: `129 passed`;
- authoritative full Python 3.12 suite: `1108 passed, 1 skipped, 1 warning`;
- exact diff check: passed;
- all secret-pattern matches were reviewed; no raw secret, token, private key,
  PSK or usable config was recorded in this receipt.

## Sealed security diff review

- scan target: exact `55dc243…ff115b63` diff;
- scan status: `completed`, sealed;
- reportable findings: `0`;
- coverage: `partial`, because one bounded future follow-up remains;
- deferred follow-up: reopen Drift handling only if a future normal
  lifecycle/import writer can persist non-positive compatibility evidence on an
  active device;
- report SHA-256:
  `150E7DADEB1C6156777C9E8203B1FE6EB09E09667C48187FAE633FB31774D52B`.

The deferred follow-up is not a current reportable security finding and does
not authorize any remediation or live action.

## Remaining gated work

The next separate approval may authorize only preparation/design of a
checksum-bound isolated-runtime package and read-only Spain conflict/equality
preflight. It must not authorize deploy, peer/config issuance, reboot,
rollback rehearsal, AWG2 alteration, USA shutdown/cleanup/reuse, or any other
Spain/USA live mutation.

USA retirement readiness remains advisory-only and always retains
`live_action_authorized=false`; USA may be disabled or repurposed only after
the separate full readiness evidence and a later exact live approval.
