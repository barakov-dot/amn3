# Phase 7 Watch-Only Intake And Status Hygiene

Date: 2026-06-18.

Task: `watch-only intake + status hygiene`.

Status: `completed-watch-only-status-hygiene-no-live-action`.

Gate: `docs-only/watch-only`.

## Scope

The operator requested a paired watch-only intake plus status hygiene pass after
the `P7-I011` IP-only exposure policy decision.

This pass does not open, imply or prepare a live mutation gate.

## Watch Sources Checked

Official GitHub release/source pages checked:

- `https://github.com/amnezia-vpn/amnezia-client/releases`
- `https://github.com/amnezia-vpn/amneziawg-android/releases/latest`
- `https://github.com/PRVTPRO/Amnezia-Web-Panel`
- `https://github.com/kyoresuas/amnezia-api`

Observed watch-only signals:

```text
amnezia-client_latest_observed=4.8.19.0
superseded_amneziawg_android_release_endpoint_observation=2.0.0
prvtpro_amnezia_web_panel_treatment=upstream_idea_source_only_no_gpl_code_copy
kyoresuas_amnezia_api_treatment=api_taxonomy_signal_only
config_delivery_enabled=false
public_exposure_enabled=false
write_api_enabled=false
```

This `amneziawg-android 2.0.0` observation was later corrected by
`research/amn2/phase-7-watch-only-intake-correction-2026-06-18.md`: current
status/navigation must treat `amneziawg-android 2.0.1` as the latest observed
watch-only signal. This file is retained as historical evidence of the earlier
status hygiene pass.

## Automation Intake

Configured local automations remain the expected watch-only intake chain:

```text
prvtpro-weekly-upstream-refresh=present
weekly-kyoresuas-upstream-refresh=present
amnezia-weekly-upstream-refresh=present
```

No new automation-generated output newer than the 2026-06-14 Phase 7 intake
evidence was found in the local workspace. The 2026-06-18 watch files are manual
Phase 7 intake/status evidence, not automation permission to open live work.

## Status Hygiene Result

Current canonical public exposure policy remains:

```text
selected_default_mode=operator_only_ip_plus_loopback_ssh_tunnel
dns_domain_for_amn2=not_used
trusted_public_tls_cutover=not_planned
public_web_admin_exposure=false
public_api_exposure=false
```

The docs/status/handoff set should now treat `P7-C002c` as closed by the
operator no-domain decision and should not recommend DNS/domain/TLS as the next
default path.

Only inactive structural proposal left from this area:

```text
P7-C002d IP-only public exposure risk gate
```

It remains inactive and requires an exact named risk-acceptance gate.

## What Was Not Performed

No live VPS command, SSH command, `.env` mutation, package install, service
restart, reverse proxy apply, TLS certificate issue, firewall change, public
listener change, public web/admin exposure, public API exposure, config delivery,
write API enablement, Local Agent mutation, backup/import/reboot, production
peer/user mutation, destructive action, Telegram action, secret publication or
upstream/GPL code copy was performed.

## Next Recommendation

Default next step:

```text
watch-only intake only
```

Exact named gates still available if the operator intentionally opens one:

```text
P7-C003 config delivery
P7-C004 destructive clean installer execution
P7-C005 write API / install mutation
P7-C006 backup/restore/import
P7-C007 Telegram identity/profile/media
```

Risky live proposal, not recommended by default:

```text
P7-C002d IP-only public exposure risk gate
```
