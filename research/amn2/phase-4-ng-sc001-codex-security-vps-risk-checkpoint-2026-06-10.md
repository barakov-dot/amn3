# Phase 4 NG-SC001: Codex Security VPS risk checkpoint 2026-06-10

Дата: 2026-06-10.

Назначение: закрыть `NG-SC001` как AMN3 docs-only/local-only checkpoint, который добавляет `Codex Security` threat-model review перед любым live VPS gate, destructive rebuild gate или public/write/config gate. Этот документ не разрешает SSH, live VPS commands, reinstall/rebuild, package apply, public exposure, config delivery, write API, Local Agent mutations, backup/import/reboot или production peer/user mutation.

## Decision

```text
task_id: NG-SC001
task_name: Codex Security risk checkpoint for VPS live/rebuild gates
tooling: Codex Security threat-model workflow
scope: AMN3 docs-only/local-only
live_vps_commands: no
ssh_commands: no
destructive_rebuild_authorized: no
public_exposure_authorized: no
write_config_authorized: no
go_no_go_decision: defer-live-actions
next_live_gate_candidate: NG-V001 read-only VPS baseline gate
future_destructive_gate_candidate: VPS-REBUILD-001, only after separate explicit approval
```

## Overview

AMN3 is the coordination, evidence and gate-planning repository for AMN2 production work. The security-sensitive runtime is the target VPS running AMN2 web/bot in service-mode, with web/admin bound to `127.0.0.1:3030`, operator access through SSH tunnel only, no public API `3040`, no public direct web/admin `3030`, no TCP `80/443`, no domain/Caddy/HTTPS cutover, and `VPS_APPLY_ENABLED=false`.

The current decision point is whether to move from docs-only planning into a live/read-only gate (`NG-V001`) or a later destructive fresh VPS rebuild gate. `Codex Security` is added as a required risk checkpoint before those gates so the operator decision is explicit, scoped and auditable.

## Threat Model, Trust Boundaries, And Assumptions

Protected assets:

- target VPS identity and SSH trust;
- web/admin auth, session and bot credentials;
- `.env`, `servers.yml`, token hashes, admin password hash and session secret;
- AmneziaWG runtime config, peer private keys, PSK, `.conf`, QR and `vpn://` artifacts;
- current service-mode evidence and approved test peer state;
- AMN2/AMN3 repository history, release packages and operator runbooks;
- operator workstation trust and copied command text.

Trust boundaries:

- local AMN3 docs/repo vs live VPS runtime;
- SSH client/operator shell vs remote host root/user privileges;
- loopback-only web/admin vs public internet;
- safe summary evidence vs secret-bearing logs/configs;
- read-only status checks vs state-write/destructive operations;
- repo-controlled plans vs out-of-band secrets/target aliases.

Assumptions:

- target SSH alias/host is provided by the operator outside repository secrets;
- no raw secrets are pasted into AMN3 evidence or chat output;
- a named gate authorizes only listed actions, not adjacent actions;
- `NG-V001` may only sample read-only state;
- VPS reinstall/rebuild is destructive and must be a separate gate, even if the VPS can be recreated from scratch.

## Attack Surface, Mitigations, And Attacker Stories

Read-only VPS baseline risks:

- wrong target host or stale SSH alias produces misleading evidence;
- host-key mismatch or unverified host identity creates MITM risk;
- a nominally read-only command accidentally prints `.env`, tokens, keys, peer configs or full logs;
- command scope creep turns a status check into restart/apply/edit;
- public listener checks are misunderstood as permission to open ports.

Mitigations:

- require explicit named approval before `NG-V001`;
- require target alias/host outside repository secrets;
- keep allowed actions to service status, loopback `/login`, listener checks and boolean-only `VPS_APPLY_ENABLED=false` proof;
- publish only safe summary fields;
- make `Codex Security` risk result part of the preflight: `security_risk_decision: go | no-go | defer`.

Fresh VPS rebuild risks:

- irreversible data loss if the wrong VPS is rebuilt or if required state was not captured;
- loss of peer configs, keys, test evidence, firewall state, systemd units, Docker volumes or manual fixes;
- temporary public exposure during reinstall/bootstrap;
- supply-chain drift from OS packages, Python dependencies, Docker images or installer artifacts;
- unsafe backup/import path that moves secrets into chat/docs or restores the wrong state;
- reusing old secrets in a new trust context;
- post-install false-positive readiness if only one surface is checked.

Mitigations:

- treat rebuild as `destructive + remote-exec + secret-read + state-write`;
- require a separate `VPS-REBUILD-001` gate with exact target confirmation, data retention decision, snapshot/backup decision, stop criteria, post-install verification and rollback/recovery note;
- do not combine rebuild with public exposure, write API, config delivery or production peer mutation;
- run a read-only baseline first when possible;
- use safe artifact hashes and pinned repository heads for install packages;
- keep secret transfer out of repo evidence.

## Severity Calibration

Critical:

- rebuilding or wiping the wrong VPS;
- publishing `.env`, private keys, PSK, `.conf`, QR, `vpn://`, admin tokens or session secrets;
- opening public admin/API surfaces without a public gate;
- running production peer/user mutations outside a named write gate.

High:

- running package apply, service restart, firewall edit or reverse proxy change during a read-only gate;
- using an unverified SSH host identity;
- restoring/importing state without preview, secret classification and recovery plan;
- combining client creation with config delivery before a config gate.

Medium:

- stale status evidence causing a bad go/no-go decision;
- incomplete listener checks that miss IPv6 or alternate bind paths;
- logs that leak safe-looking but identifying peer/user metadata;
- dependency/version drift between AMN3 package evidence and VPS install state.

Low:

- docs wording drift that labels a gated/destructive action as normal;
- missing evidence links for already closed docs-only tasks;
- cosmetic naming inconsistency that does not affect authorization.

## Gate Integration

`NG-V001` must include:

```text
security_checkpoint: Codex Security risk review
security_risk_decision: go | no-go | defer
security_scope: read-only VPS baseline only
destructive_action_authorized: no
safe_summary_only: yes
```

Allowed `NG-V001` actions remain read-only only:

- SSH transport check to the operator-provided target;
- read-only service status for `amneziya-web` and `amneziya-bot`;
- loopback `/login` check on `127.0.0.1:3030`;
- listener checks for `3030`, `3040`, `80`, `443`;
- boolean-only proof that `VPS_APPLY_ENABLED=false` exists, without printing `.env`.

Future `VPS-REBUILD-001` must not start until it has a separate explicit operator approval and must define:

```text
gate_name:
target_vps:
operation_class: destructive + remote-exec + secret-read + state-write
data_retention_decision:
snapshot_or_backup_decision:
allowed_actions:
blocked_actions:
secret_transfer_policy:
install_source_and_hashes:
post_install_read_only_checks:
rollback_or_recovery:
stop_criteria:
go_no_go_decision:
```

## Plan Effect

`NG-SC001` is closed and removed from the active plan. The active P4-NG plan still contains only `NG-V001` as a possible next live gate, and `NG-V001` remains blocked until explicit named approval.

This checkpoint does not authorize live work. It only makes security risk review mandatory before live/read-only or destructive gate execution.

## Recommendation

If we continue toward VPS work, take `NG-V001` first as read-only baseline with the `Codex Security` checkpoint embedded. Only after that decide whether a separate `VPS-REBUILD-001` destructive rebuild gate is needed.
