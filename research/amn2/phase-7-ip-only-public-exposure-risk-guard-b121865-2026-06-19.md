# AMN2 Phase 7 P7-C002d IP-Only Public Exposure Risk Guard

Дата: 2026-06-19.

Статус: `blocked-pending-design-or-explicit-risk-acceptance-not-exposed`.

Gate: `P7-C002d IP-only public exposure risk gate`, explicitly opened by the
operator for AMN2 `b121865` on disposable VPS `89.185.80.166`.

## Evidence Inputs

Local transcripts:

- `tmp/p7-c002d-ip-only-public-exposure-guard-bashs-20260619T045641Z.log` -
  final full read-only guard snapshot.
- `tmp/p7-c002d-source-binding-check-20260619T045804Z.log` - corrected
  source-overlay marker check.

Earlier diagnostic retries in `tmp/p7-c002d-*` are superseded by the two files
above. They performed no public exposure apply.

## Source Binding

The corrected source-overlay marker check read `/opt/amn2/.amn2_source_overlay_commit`:

```text
source_overlay_commit=b121865f488821f6fc471c9529fb26e5d7992515
```

The first full guard looked for the obsolete dashed marker path and therefore
printed `source_overlay_commit_file=missing`; this was a verifier path issue, not
a source rollback signal.

## Runtime Snapshot

```text
web_runtime=166198 /opt/amn2/venv/bin/python -m app.cli web serve --host 127.0.0.1 --port 3030
bot_runtime=166199 /opt/amn2/venv/bin/python -m app.main
web_listener=127.0.0.1:3030
api_public_3040_listener=missing
public_80_listener=missing
public_443_listener=missing
ssh_listener=0.0.0.0:22,[::]:22
```

Loopback web stayed healthy:

```text
http://127.0.0.1:3030/login 200
http://127.0.0.1:3030/ 303
```

Local external probes from the operator workstation returned `000` for public
`3030`, `3040`, `80` and `443`. Curl reported empty-reply/TLS-handshake errors,
but no HTTP success code or public web/API exposure was observed.

## Env And Service Summary

```text
APP_SECRET_KEY=present
WEB_ADMIN_USERNAME=present
WEB_ADMIN_PASSWORD_HASH=present
WEB_ADMIN_SESSION_SECRET=present
PUBLIC_BASE_URL=missing
PUBLIC_DOMAIN=missing
WEB_PUBLIC_BASE_URL=missing
VPS_APPLY_ENABLED=false
LOCAL_AGENT_ENABLED=false
```

Reverse proxy/service inventory:

```text
nginx_active=inactive
caddy_active=inactive
apache2_active=inactive
traefik_active=inactive
nginx_binary=missing
caddy_binary=missing
apache2_binary=missing
traefik_binary=missing
certbot_binary=missing
openssl_binary=present
ufw_binary=present
iptables_binary=present
```

Firewall snapshot:

```text
ufw_status=inactive
iptables_input_policy=ACCEPT
```

## Guard Verdict

The guard found four blockers:

```text
blocker=ufw_inactive_for_public_exposure
blocker=no_reverse_proxy_binary_for_admin_exposure
blocker=ip_only_public_admin_has_no_trusted_dns_tls
blocker=public_admin_over_ip_requires_explicit_risk_acceptance
blocker_count=4
p7_c002d_guard_status=blocked_pending_design_or_explicit_risk_acceptance
ip_only_public_apply_allowed=false
```

Conclusion: `P7-C002d` does not authorize IP-only public exposure. Current
selected mode remains operator-only VPS IP + SSH tunnel to loopback web/admin.

## Mutation Status

```text
service_restart_performed=false
env_mutation_performed=false
package_install_performed=false
reverse_proxy_apply_performed=false
firewall_apply_performed=false
tls_apply_performed=false
public_listener_change_performed=false
public_api_3040_exposed=false
config_delivery_performed=false
write_api_performed=false
telegram_action_performed=false
secret_values_printed=false
```

No live public exposure, reverse proxy/TLS/firewall/listener apply, config
delivery, write API, Local Agent mutation, backup/import/reboot, destructive
action, Telegram action, secret publication or upstream/GPL code copy was
performed.

## Next Decision

Default: keep `P7-C002` closed as not exposed and continue to the next ordered
gate, `P7-C003 Config delivery`, only if the operator opens the exact named
config-delivery gate.

Any future attempt to expose web/admin by IP must be a separate explicit
risk-acceptance/design gate. It must not be bundled with config delivery or write
API.
