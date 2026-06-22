# Phase 8 private/operator RC handoff

Date: 2026-06-22.

Status: `completed-private-operator-rc-handoff-docs-only`.

Scope: operator-facing RC handoff prepared from existing Phase 8 evidence only.
No live VPS/SSH command, destructive action, package upload/apply, service
restart, public exposure, config delivery, Telegram live send, bot polling,
Telegram profile/media mutation, backup restore/import/reboot, provider
mutation, production peer/user mutation or secret-bearing output was performed.

## Produced Artifact

Operator-facing handoff:

```text
docs/AMN2_PRIVATE_OPERATOR_RC_HANDOFF.ru.md
```

The handoff records:

- final Phase 8 status;
- allowed private/operator RC scope;
- exact limitations;
- stop-lines;
- future exact gates required for broader launch or live actions.

## Final Status Carried Forward

```text
phase8_final_status=launch-ready-with-explicit-limitations
private_operator_rc_launch_ready=true
public_launch_status=not-approved
blocked_with_exact_remaining_blockers=false
```

## Evidence Used

```text
research/amn2/phase-8-p8-c001-fresh-android-config-acceptance-2026-06-21.md
research/amn2/phase-8-p8-c002-187949b-package-apply-smoke-2026-06-21.md
research/amn2/phase-8-p8-c003-fresh-zero-rehearsal-2026-06-22.md
research/amn2/phase-8-sfinal-launch-readiness-freeze-2026-06-22.md
```

No new evidence was generated from live systems in this handoff step.

## Allowed RC Scope

The private/operator RC lane is ready for:

- Telegram-first product operation as the user-facing lane;
- private operator web/admin access only;
- `.conf`-first private handoff;
- Android AmneziaWG as the primary mobile candidate;
- AMN2 `187949b` as the current RC runtime/package line;
- backup create+verify evidence as the current backup proof.

## Limitations Preserved

```text
public_launch_status=not-approved
public_exposure_status=closed-by-default
telegram_live_send_status=not-performed
telegram_bot_polling_status=not-performed
fresh_android_phone_acceptance_source=P8-C001
fresh_zero_android_acceptance_device=P8-C003_android_projector
qr_release_primary=false
full_vpn_uri_release_primary=false
ios_defaultvpn_status=experimental_unreliable
restore_import_status=not-proven
secret_payload_output_status=not-performed
```

## Stop Lines

Without a new exact named gate, do not perform:

- destructive VPS/provider action;
- public exposure or listener/firewall changes;
- Telegram live send/profile/media mutation or bot polling;
- config delivery or config payload output;
- backup restore/import/reboot;
- production peer/user mutation;
- provider rebuild or broader rollout.

## Next Recommended Gate

The next recommended step is docs-only unless the operator explicitly requests
broader live action:

```text
P8-RC-OPERATOR-RUN-CHECKLIST
```

If broader launch is requested, open the relevant exact named gate first:

- public exposure gate;
- Telegram live delivery gate;
- config delivery gate;
- restore/import DR gate;
- production rollout gate.
