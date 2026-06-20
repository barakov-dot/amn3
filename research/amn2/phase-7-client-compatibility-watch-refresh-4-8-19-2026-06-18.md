# Phase 7 P7-N005 Client Compatibility Watch Refresh

Date: 2026-06-18.

Requested bundle: `P7-C002c + P7-N005`.

Status: `p7-n005-complete-p7-c002c-input-required`.

## Boundary

This was a local-only/docs/tests/watch-only pass.

`P7-C002c` was not executed live because the operator did not provide both:

- the exact named live gate phrase for `P7-C002c`;
- a DNS FQDN for `PUBLIC_BASE_URL` / `PUBLIC_DOMAIN`.

Later on 2026-06-18, `P7-I011` superseded the input-required state by recording
the operator decision not to use a DNS domain for AMN2. The DNS/domain/trusted
TLS branch is now closed as `operator_declined_dns_domain`.

No SSH command, live VPS command, `.env` mutation, reverse proxy apply, TLS
certificate issue, firewall apply, public listener change, public exposure,
config delivery, write API enablement, Local Agent mutation, backup/import/
reboot, destructive action, Telegram action, secret publication or upstream/GPL
code copy was performed.

## P7-C002c Required Inputs

Future live prerequisite gate phrase:

```text
Открываю P7-C002c DNS/domain/TLS prerequisite gate для b121865 на текущем disposable VPS 89.185.80.166.
```

Required operator inputs:

```text
DNS_FQDN=<operator-provided-dns-name>
PUBLIC_BASE_URL=https://<DNS_FQDN>
PUBLIC_DOMAIN=<DNS_FQDN>
TLS_MODE=<trusted-certificate-mode>
REVERSE_PROXY_KIND=<nginx|caddy|other explicit operator choice>
ROLLBACK_TARGET=loopback-only 127.0.0.1:3030
```

Stop lines remain:

```text
no raw-IP trusted TLS public domain
no reverse_proxy_apply without exact gate
no tls_certificate_issue without exact gate
no firewall_apply without exact gate
no public_listener_change without exact gate
no direct_public_3030
no direct_public_api_3040
```

## Watch-Only Inputs

Official GitHub sources checked on 2026-06-18:

- `amnezia-vpn/amnezia-client` releases:
  <https://github.com/amnezia-vpn/amnezia-client/releases>
- `amnezia-vpn/amneziawg-android` releases:
  <https://github.com/amnezia-vpn/amneziawg-android/releases>
- `PRVTPRO/Amnezia-Web-Panel` repository:
  <https://github.com/PRVTPRO/Amnezia-Web-Panel>
- `kyoresuas/amnezia-api` repository:
  <https://github.com/kyoresuas/amnezia-api>

Local automation configs remain active:

```text
prvtpro-weekly-upstream-refresh: ACTIVE, Sunday 10:00
weekly-kyoresuas-upstream-refresh: ACTIVE, Sunday 11:00
amnezia-weekly-upstream-refresh: ACTIVE, Sunday 12:00
```

No new local automation output newer than the 2026-06-14 Phase 7 intake
evidence was found.

## Observed Client Compatibility Signals

- `amnezia-vpn/amnezia-client` latest observed release: `4.8.19.0`, published
  2026-06-15. Treat as a compatibility guidance signal only.
- Platform availability constraints to carry into AMN2 operator docs/watch
  status: Android 9+ uses the `4.8.19.0` Android 9+ asset; Android 7/8 is
  temporarily unavailable; macOS 13+ uses the package zip; macOS 10.15-12 is
  temporarily unavailable; Debian 12 / Ubuntu 22.04.x app version is
  temporarily unavailable.
- `amnezia-vpn/amneziawg-android` latest observed release remains `2.0.1`,
  published 2026-06-12, with version-bump changes only.
- `PRVTPRO/Amnezia-Web-Panel` remains a GPL-3.0 upstream idea source only.
- `kyoresuas/amnezia-api` remains a MIT-licensed API taxonomy idea source only.

## AMN2 Impact

`P7-N005` is complete as watch-only documentation/status intake.

No config artifact, QR, `vpn://`, SMTP delivery, public redeem route,
client-secret output or Telegram config send was enabled. `P7-C003` remains a
separate exact named config delivery gate.

No public write/config surface was opened. `P7-C005` remains a separate exact
named write/install mutation gate, and the RC policy remains
`keep_public_api_read_only_for_rc`.

## Plan Update

Remove `P7-N005` from inactive structural proposals and record it as completed
watch-only work.

At the time of this evidence, `P7-C002` remained blocked by DNS/TLS
prerequisite:

```text
P7-C002c input_required=yes
dns_fqdn_required=yes
public_cutover_apply_allowed=false
```

Superseding status after `P7-I011`:

```text
P7-C002c_status=operator_declined_dns_domain
selected_default_mode=operator_only_ip_plus_loopback_ssh_tunnel
```

## Next Recommendation

Historical live prerequisite path at the time, only with exact gate and DNS
FQDN:

```text
P7-C002c DNS/domain/TLS prerequisite gate.
```

Current safe non-live alternative after `P7-I011`:

```text
watch-only intake only.
```
