# Phase 7 P7-C002e Public URL Env Reconciliation

Date: 2026-06-19.

Task: `P7-C002e Public URL env reconciliation gate`.

Status: `completed-live-env-reconcile-not-exposed`.

Target: current disposable VPS `89.185.80.166`.

AMN2 source overlay commit:

```text
b121865f488821f6fc471c9529fb26e5d7992515
```

## Gate Phrase

The operator opened the exact named gate:

```text
Открываю P7-C002e Public URL env reconciliation gate для b121865 на текущем disposable VPS 89.185.80.166.
```

## Scope

Allowed scope:

- live `.env` reconciliation for `PUBLIC_BASE_URL`, `PUBLIC_DOMAIN`,
  `WEB_PUBLIC_BASE_URL`;
- rollback copy on VPS;
- safe evidence collection;
- watch-only intake.

Explicitly out of scope:

- service restart;
- reverse proxy, TLS, firewall or public listener changes;
- public web/admin or public API exposure;
- config delivery;
- write API / install mutation;
- Local Agent mutation;
- backup/import/reboot;
- destructive action;
- Telegram action.

## Mutation Result

The live `.env` was reconciled by removing the IP-based public URL residue left
from `P7-C002a` after the later `P7-I011` IP-only policy decision.

Downloaded safe report:

```text
P7-C002e downloaded safe report
target=166780.ip-ptr.tech
utc=2026-06-19T04:22:40Z
source_overlay_commit=b121865f488821f6fc471c9529fb26e5d7992515
secret_values_printed=false

[post_env_flags]
APP_SECRET_KEY=present
WEB_ADMIN_USERNAME=present
WEB_ADMIN_PASSWORD_HASH=present
WEB_ADMIN_SESSION_SECRET=present
PUBLIC_BASE_URL=missing
PUBLIC_DOMAIN=missing
WEB_PUBLIC_BASE_URL=missing
VPS_APPLY_ENABLED=false
LOCAL_AGENT_ENABLED=false

[latest_safe_summary]
latest_safe_evidence_dir=vps-smoke/p7-c002e-public-url-env-reconcile-20260619T041402Z
P7-C002e public URL env reconciliation
run_id=20260619T041402Z
env_mutation_status=passed
secret_values_printed=false
rollback_copy_created_on_vps=true
rollback_copy_contains_secrets=true
rollback_copy_send_to_chat=false
removed_PUBLIC_BASE_URL=1
removed_PUBLIC_DOMAIN=1
removed_WEB_PUBLIC_BASE_URL=1
service_restart_performed=false
reverse_proxy_apply_performed=false
firewall_apply_performed=false
tls_apply_performed=false
public_listener_change_performed=false
config_delivery_performed=false
write_api_enabled=false

[runtime_probe_summary]
loopback_login_http=200
loopback_root_http=303
local_80_http=000
local_443_http=000
local_3040_http=000
listener_3030=LISTEN 0 2048 127.0.0.1:3030 0.0.0.0:* users:(("python",pid=166198,fd=6))
listener_3040=missing

[verification_mutation_status]
env_mutation_performed=false
service_restart_performed=false
reverse_proxy_apply_performed=false
firewall_apply_performed=false
tls_apply_performed=false
public_listener_change_performed=false
config_delivery_performed=false
write_api_enabled=false
```

Local external probes after reconciliation:

```text
http://89.185.80.166:3030/login 000
http://89.185.80.166:3040/api/servers 000
http://89.185.80.166:80/ 000
https://89.185.80.166:443/ 000
```

## Settings Probe Note

An initial verifier attempted to import `app.settings.get_settings`; the remote
package does not expose `app.settings`, so that verifier returned:

```text
settings_load_status=failed
settings_error_type=ModuleNotFoundError
settings_error=No module named 'app.settings'
```

This is a verifier path issue, not evidence of a runtime failure. Runtime web
checks after reconciliation returned loopback `/login=200` and root `/=303`,
with external probes still closed.

## Evidence Files

Local transcripts / safe reports:

```text
tmp/p7-c002e-public-url-env-reconcile-20260619T041402Z.log
tmp/p7-c002e-public-url-env-reconcile-verify-20260619T041643Z.log
tmp/p7-c002e-public-url-env-reconcile-compact-verify-20260619T041828Z.log
tmp/p7-c002e-public-url-env-reconcile-scp-verify-20260619T042009Z.log
tmp/p7-c002e-public-url-env-reconcile-report-verify-20260619T042214Z.log
tmp/p7-c002e-public-url-env-reconcile-safe-report-20260619T042214Z.txt
tmp/p7-c002e-settings-report-probe-20260619T042537Z.log
tmp/p7-c002e-settings-safe-report-20260619T042537Z.txt
```

Remote safe evidence:

```text
/opt/amn2/vps-smoke/p7-c002e-public-url-env-reconcile-20260619T041402Z
```

The rollback copy remains on the VPS and must not be posted because it contains
secrets.

## Watch-Only Pair Result

The paired watch-only state remains unchanged from the latest current-signal
intake:

```text
amnezia_client_latest_observed=4.8.19.0
amneziawg_android_latest_observed=2.0.1
prvtpro_treatment=upstream_idea_source_only_no_gpl_code_copy
kyoresuas_treatment=api_taxonomy_signal_only
```

## Final Boundary

No service restart, reverse proxy apply, TLS certificate issue, firewall change,
public listener change, public web/admin exposure, public API exposure, config
delivery, write API enablement, Local Agent mutation, backup/import/reboot,
production peer/user mutation, destructive action, Telegram action, secret
publication or upstream/GPL code copy was performed.

## Next Recommendation

Default next step:

```text
watch-only intake only
```

Remaining exact named gates:

```text
P7-C002d IP-only public exposure risk gate
P7-C003 config delivery gate
P7-C004 destructive clean installer execution gate
P7-C005 write API / install mutation gate
P7-C006 backup/restore/import gate
P7-C007 Telegram identity/profile/media gate
```
