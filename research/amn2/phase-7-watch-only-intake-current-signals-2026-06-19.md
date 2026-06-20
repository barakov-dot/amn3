# AMN2 Phase 7 Watch-Only Intake Current Signals

Дата: 2026-06-19.

Статус: `completed-watch-only-intake-current-signals-no-live-action`.

Gate: docs-only/watch-only.

## Scope

Обновить текущий watch-only срез после `P7-C002e`, не открывая live/public/config/write контур.

Проверенные источники:

- https://github.com/amnezia-vpn/amnezia-client/releases
- https://github.com/amnezia-vpn/amneziawg-android/releases
- https://github.com/PRVTPRO/Amnezia-Web-Panel
- https://github.com/kyoresuas/amnezia-api

## Current Signals

```text
amnezia_client_latest_observed=4.8.19.0
amneziawg_android_latest_observed=2.0.1
prvtpro_treatment=upstream_idea_source_only_no_gpl_code_copy
kyoresuas_treatment=api_taxonomy_signal_only
new_amn2_implementation_task_created=false
```

`amnezia-vpn/amnezia-client` remains a client-compatibility signal only. The
current observed release is `4.8.19.0`.

`amnezia-vpn/amneziawg-android` remains a client-compatibility signal only. The
current observed release is `2.0.1`.

PRVTPRO remains an upstream idea source only. GPL/upstream code copying into AMN2
is still forbidden.

KYORESUAS remains an API taxonomy signal only. No AMN2 implementation task was
created from this intake.

## Automation Config Check

Local automation config timestamps remain unchanged from the prior Phase 7 intake
context:

```text
prvtpro-weekly-upstream-refresh=present-unchanged-since-2026-06-14
weekly-kyoresuas-upstream-refresh=present-unchanged-since-2026-06-14
amnezia-weekly-upstream-refresh=present-unchanged-since-2026-06-14
new_local_automation_output_found=false
```

Automation output remains intake-only. It does not authorize live/public/config/
write changes.

## Operator Policy

The active public exposure policy remains:

```text
public_exposure_mode=operator-only-ip-loopback-ssh-tunnel
dns_domain_planned=false
trusted_tls_public_cutover_planned=false
public_web_or_api_exposure_planned=false
```

`P7-C002e` already reconciled the previous public URL residue. No new public URL,
DNS, TLS, reverse proxy, firewall or listener action is requested by this intake.

## Hard Boundary

This pass performed no live VPS command, SSH command, `.env` mutation, package
install, service restart, reverse proxy/TLS/firewall apply, public listener
change, public exposure, config delivery, write API, Local Agent mutation,
backup/import/reboot, destructive action, Telegram action, secret publication or
upstream/GPL code copy.

## Next Default

If no exact named gate is opened, continue with watch-only intake only.
