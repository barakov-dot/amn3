# Phase 7 Watch-Only Intake Correction

Date: 2026-06-18.

Task: `watch-only intake only`.

Status: `completed-watch-only-correction-no-live-action`.

Gate: `docs-only/watch-only`.

## Correction

This watch-only pass corrects the previous Phase 7 watch/status hygiene note that
treated `amneziawg-android 2.0.0` as the current latest-release endpoint
observation.

Current official GitHub release-page observation:

```text
amnezia-client_latest_observed=4.8.19.0
amneziawg_android_latest_observed=2.0.1
```

The `2.0.0` wording from
`research/amn2/phase-7-watch-only-intake-status-hygiene-2026-06-18.md` is
superseded for current status/navigation by this correction.

## Watch Sources Checked

- `https://github.com/amnezia-vpn/amnezia-client/releases`
- `https://github.com/amnezia-vpn/amneziawg-android/releases`
- `https://github.com/PRVTPRO/Amnezia-Web-Panel`
- `https://github.com/kyoresuas/amnezia-api`

## Boundary

These are watch-only client/upstream signals. They do not enable config
delivery, public exposure, write API, Local Agent mutation, Telegram delivery or
any live VPS mutation.

Local automation configs remain present and unchanged since 2026-06-14:

```text
prvtpro-weekly-upstream-refresh=present
weekly-kyoresuas-upstream-refresh=present
amnezia-weekly-upstream-refresh=present
new_local_automation_output_found=false
```

Current operator policy remains:

```text
selected_default_mode=operator_only_ip_plus_loopback_ssh_tunnel
dns_domain_for_amn2=not_used
trusted_public_tls_cutover=not_planned
public_web_admin_exposure=false
public_api_exposure=false
```

## What Was Not Performed

No live VPS command, SSH command, `.env` mutation, package install, service
restart, reverse proxy apply, TLS certificate issue, firewall change, public
listener change, public web/admin exposure, public API exposure, config delivery,
write API enablement, Local Agent mutation, backup/import/reboot, production
peer/user mutation, destructive action, Telegram action, secret publication or
upstream/GPL code copy was performed.

## Next Recommendation

No new local implementation task is created from this watch-only correction.

Default next step:

```text
watch-only intake only
```
