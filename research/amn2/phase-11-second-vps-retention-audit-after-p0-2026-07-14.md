# Phase 11: second VPS retention audit after P0

Date: 2026-07-14.

Decision: `KEEP TEMPORARILY FOR PHASE11-RESTORE-001A; DO NOT RETAIN AS
PRODUCTION DR OR INDEFINITE FLEET CAPACITY`.

Direct answer: the second VPS is not needed for current production P0 and is
not a production dependency. It is needed temporarily because it is the clean
disposable environment best suited to the canonical full-secret functional
restore rehearsal required before the old recovery bundle/key can be retired.

No provider, billing, firewall, package, service, file, key or listener state
was changed by this audit. No production contact or secret transfer occurred.

## Current read-only state

```text
second_vps_audit=pass
os=ubuntu_24.04
ssh_service=active
ssh_pubkeyauthentication=yes
ssh_passwordauthentication=no
ssh_kbdinteractiveauthentication=no
ssh_permitrootlogin=without-password
ufw=active_default_incoming_deny
external_tcp_ports=22
external_udp_ports=none
amn2_tree=absent
amn2_unit_count=0
container_count=0
recovery_or_amn2_artifact_name_matches=0
failed_systemd_units=0
root_disk_used=40_percent
root_disk_available_kb=5862396
memory_available_kb=647724
memory_total_kb=984568
load1=0.02
production_contact_performed=false
secret_transfer_performed=false
provider_mutation_performed=false
```

The host is clean after the earlier sanitized rehearsal: there is no AMN2
tree, AMN2 unit, container or recovery/AMN2-named artifact in the audited
root/opt/tmp scope. Only SSH is externally listening; password and keyboard-
interactive authentication are disabled, UFW is active with default incoming
deny, and no systemd unit is failed.

## What the VPS is and is not for

Allowed future purpose, only under a new exact gate:

- one trusted disposable `PHASE11-RESTORE-001A` canonical full-secret offline
  restore rehearsal;
- bounded validation and service-start checks required by `RECOVERY-001`;
- complete post-rehearsal secret/runtime cleanup and a repeated clean-host
  audit.

It is not:

- a hot/warm production standby;
- an independent provider disaster-recovery domain;
- a replica that may receive automatic production sync;
- a reason to open public web/API/Telegram or create client configs;
- a justified long-term fleet node before `IPAM-001` and `FLEET-001`.

The staging VPS and production are at the same provider. It therefore helps
prove functional restore mechanics but does not mitigate a provider-wide
incident. Independent recovery remains the encrypted removable-media copy plus
the separately stored private key.

## Retention window and stop rule

Recommended policy:

1. Keep the VPS now in its current clean SSH-only state.
2. Schedule or explicitly decline `PHASE11-RESTORE-001A` before the next
   provider billing renewal/cutoff.
3. If the rehearsal passes, clean and re-audit the VPS, then prepare safe
   provider retirement. Do not retain it merely for possible future fleet work.
4. If the rehearsal is not approved or cannot be scheduled before renewal,
   prepare retirement instead of silently paying another cycle; extend for one
   cycle only by an explicit operator cost/schedule decision.

The exact provider renewal date/cost was not available from the repository or
SSH host and was not guessed. Provider deletion, plan cancellation and local
staging-key removal remain separate destructive actions.

## Safe-retirement gate

The current host already satisfies the technical empty-host preconditions.
Before provider deletion, repeat the clean audit and require:

- AMN2 tree/unit/container counts zero;
- recovery/AMN2 artifact match count zero in the audited scope;
- no required evidence left only on the host;
- no production dependency or DNS/endpoint binding;
- explicit provider instance identity and exact operator approval.

After provider deletion is confirmed, remove the dedicated staging SSH private
key and its known-host binding under the same or a separately named local
cleanup gate. Do not touch the production operator key or known-host binding.

## Next recommendation

The critical next action is a local/product gate review for the restore
rehearsal, not immediate live execution:

```text
GPT-5.6 SOL -> REVIEW_PHASE11_RESTORE_001A_CANONICAL_FULL_SECRET_DISPOSABLE_REHEARSAL_GATE
```

`PHASE11-TELEGRAM-002A` persistent bot admission/unit hardening remains the
parallel product follow-up, but production bot activation stays closed.
