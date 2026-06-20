# AMN2 Phase 7 DNS/Domain/TLS Prerequisite + Watch-Only Intake

Дата: 2026-06-18.

Requested bundle: `P7-C002c + watch-only intake`.

Статус: `watch-only-intake-complete-p7-c002c-input-required`.

Gate:

- `watch-only/docs` for automation/client/upstream intake;
- `P7-C002c` remains a future exact named live `.env` DNS/domain/TLS
  prerequisite gate and was not executed in this slice.

## Scope

This slice followed the operator request to start the paired option after
`P7-C002` public cutover guard stopped on IP-based `PUBLIC_BASE_URL` /
`PUBLIC_DOMAIN`.

Superseding update on 2026-06-18: `P7-I011` recorded the operator decision not
to use a DNS domain for AMN2. The DNS/domain/trusted TLS branch is now closed as
`operator_declined_dns_domain`, and the selected default mode is VPS IP +
loopback web/admin over SSH tunnel.

Performed:

- inspected local Phase 7 automation configuration;
- inspected local upstream/watch evidence;
- checked current upstream/client release surfaces through official GitHub
  pages;
- recorded the required `P7-C002c` inputs and stop lines.

Not performed:

- live VPS command;
- SSH command;
- `.env` mutation;
- DNS/provider mutation;
- reverse proxy install/apply;
- TLS/certbot issue;
- firewall/listener change;
- service restart/deploy;
- public web/API exposure;
- direct public `3030` / `3040`;
- config delivery;
- write API / install mutation;
- Local Agent mutation;
- backup/import/reboot;
- destructive action;
- Telegram action;
- secret publication;
- upstream/GPL code copy.

## P7-C002c Status

`P7-C002c` was not executed live.

Later `P7-I011` changed this from `input-required` to
`operator_declined_dns_domain`.

Required operator inputs before any live prerequisite mutation:

```text
exact gate phrase:
Открываю P7-C002c DNS/domain/TLS prerequisite gate для b121865 на текущем disposable VPS 89.185.80.166.

required values:
- DNS FQDN, not an IP address;
- PUBLIC_BASE_URL, expected form https://<dns-fqdn>;
- PUBLIC_DOMAIN, expected same DNS FQDN;
- TLS mode decision;
- reverse proxy kind decision;
- rollback target: loopback-only web on 127.0.0.1:3030.
```

Stop lines:

```text
no raw IP as trusted TLS public domain
no reverse_proxy_apply
no tls_certificate_issue
no firewall_apply
no public_listener_change
no direct_public_3030
no direct_public_api_3040
```

Next allowed `P7-C002` step at the time of this evidence:

```text
exact named P7-C002c DNS/domain/TLS prerequisite gate with operator-provided DNS FQDN,
or watch-only intake only.
```

Current superseding policy after `P7-I011`:

```text
stay operator-only with VPS IP + SSH tunnel to loopback web/admin,
or use a separate exact IP-only public exposure risk gate if the operator later
accepts that risk.
```

## Automation Config Intake

Local automation configs are present and active:

```text
prvtpro-weekly-upstream-refresh: ACTIVE, Sunday 10:00
weekly-kyoresuas-upstream-refresh: ACTIVE, Sunday 11:00
amnezia-weekly-upstream-refresh: ACTIVE, Sunday 12:00
```

Local automation files under `C:\Users\SooL\.codex\automations` were last
updated on 2026-06-14. No new local automation output file newer than the
2026-06-14 Phase 7 intake evidence was found.

Latest local watch/intake evidence remains:

```text
research/amn2/phase-7-automation-client-watch-copy-polish-2026-06-14.md
research/amn2/phase-7-evidence-watch-drycheck-rcnotes-2026-06-14.md
research/amn2/phase-7-final-freeze-watch-menu-2026-06-14.md
research/upstreams/prvtpro-amnezia-web-panel-upstream-refresh-2026-06-14.md
research/upstreams/kyoresuas-amnezia-api-github-watch-2026-06-14.md
research/upstreams/amnezia-vpn-client-defaultvpn-refresh-2026-06-14.md
```

## Current Watch-Only Signals

Official GitHub sources checked on 2026-06-18:

- `amnezia-vpn/amnezia-client` releases:
  <https://github.com/amnezia-vpn/amnezia-client/releases>
- `amnezia-vpn/amneziawg-android` releases:
  <https://github.com/amnezia-vpn/amneziawg-android/releases>
- `PRVTPRO/Amnezia-Web-Panel` repository:
  <https://github.com/PRVTPRO/Amnezia-Web-Panel>
- `kyoresuas/amnezia-api` repository:
  <https://github.com/kyoresuas/amnezia-api>

Observed:

- `amnezia-vpn/amnezia-client` latest release is `4.8.19.0`, published
  2026-06-15, after the previous Phase 7 watch evidence. The page marks it
  latest and describes general stability improvements. It also keeps platform
  constraints relevant to AMN2 client guidance: Android 9+ uses
  `AmneziaVPN_4.8.19.0_android9+`, Android 7/8 is temporarily unavailable,
  macOS 13+ uses the package zip, macOS 10.15-12 is temporarily unavailable,
  and Debian 12 / Ubuntu 22.04.x app version is temporarily unavailable.
- `amnezia-vpn/amneziawg-android` latest release remains `2.0.1`, published
  2026-06-12, with version-bump changes only.
- `PRVTPRO/Amnezia-Web-Panel` remains a GPL-3.0 upstream idea source. Its
  README still emphasizes multi-protocol/service management, including
  AmneziaWG, WireGuard, Xray, MTProxy, AmneziaDNS, AdGuard Home and SOCKS5.
  This remains signals-only for AMN2; no GPL code/templates/managers/scripts
  are copied.
- `kyoresuas/amnezia-api` remains a MIT-licensed upstream API idea source. Its
  README describes a typed HTTP interface for Amnezia server management,
  including client/peer operations and ready import config output. For AMN2 RC,
  this remains watch-only/API-taxonomy signal because public write/config
  surfaces remain gated.

## AMN2 Impact

Immediate plan change:

```text
none
```

Recommended local-only follow-up proposal at the time of this evidence,
later activated and completed in
`research/amn2/phase-7-client-compatibility-watch-refresh-4-8-19-2026-06-18.md`:

```text
P7-N005 Client compatibility watch refresh for Amnezia client 4.8.19.0.
Importance: normal.
Gate: local-only/docs/tests/watch-only.
Purpose: update AMN2 client compatibility watch docs/status to mention
4.8.19.0 platform availability constraints, without config delivery.
```

`P7-C002c` was later closed by `P7-I011` as
`operator_declined_dns_domain`. It should not run for AMN2 unless the operator
reverses the no-domain policy in a new explicit decision.
