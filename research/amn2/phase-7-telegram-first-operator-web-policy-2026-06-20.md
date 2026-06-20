# AMN2 Phase 7 Telegram-First / Operator-Web Policy

Date: 2026-06-20.

Status: `completed-docs-only-telegram-first-operator-web-policy`.

Gate: docs-only/local-only.

No live VPS command, SSH command, package apply, service restart, public
exposure, config delivery, write execution, Local Agent mutation, backup
restore/import/reboot, provider mutation, Telegram token use, Telegram API call,
live bot send, Telegram identity/profile/media mutation or secret-bearing
output was performed.

## Decision

For the private/operator RC lane, AMN2 uses a Telegram-first user channel and an
operator-only web/admin channel.

User channel:

- end users should interact through Telegram;
- user-facing status, instructions and future config delivery belong to the
  Telegram/product flow, behind the relevant exact gates;
- public web-admin exposure is not part of the user-facing RC surface.

Operator channel:

- the operator may use the VPS IP and the web/admin panel;
- the web/admin panel remains loopback/operator-only by default;
- the preferred operator access model is VPS IP plus SSH tunnel or equivalent
  private operator access to loopback `127.0.0.1:3030`;
- DNS domain, trusted public TLS and reverse-proxy publication are not required
  for private/operator RC readiness.

## Effect On P7-C002

`P7-C002` public web/admin exposure is deferred and not required for the
private/operator RC lane.

The earlier `P7-C002d` result remains valid: IP-only public exposure was blocked
and not applied. This policy makes that result intentional rather than a release
blocker: AMN2 does not need a public web-admin panel for the current RC target.

Future public exposure would still require a separate exact named gate covering
domain/TLS/reverse proxy/firewall/listener changes, rollback and public
operator risk acceptance.

## Effect On Telegram Work

`P7-C007` Telegram identity/profile/media remains deferred and not required for
private/operator RC readiness.

This policy does not authorize Telegram token use, live bot send, profile/media
mutation or config delivery. It only clarifies product direction: the next
user-facing live validation, if opened, should be a narrow Telegram user-flow
smoke gate rather than public web-panel exposure.

Candidate future gate, not active without operator approval:

```text
P7-C008 Telegram user-flow smoke gate.
Importance: critical/user-facing.
Gate: exact named live Telegram gate.
Scope: verify bot runtime and safe user-facing flow for the RC channel.
Out of scope by default: Telegram identity/profile/media mutation, public web
exposure, write execution, restore/import/reboot, provider mutation and
secret-bearing evidence.
```

## Current RC Posture

```text
AMN2 head: 5501295 Add P7 install write contour
VPS: 89.185.80.166
current runtime: direct clean-installed 5501295
web/admin: loopback-only 127.0.0.1:3030
operator access policy: VPS IP + loopback/SSH tunnel
user channel policy: Telegram-first
public web-admin: not required for private/operator RC
domain/TLS/reverse proxy: not required for private/operator RC
VPS_APPLY_ENABLED=false
```

## Conclusion

The domain/TLS/public web-panel path is no longer a blocker for the private
operator RC lane. AMN2 can proceed as an operator-managed system where users
receive the product experience through Telegram and the operator uses the
web/admin panel privately by IP/loopback access.

The next meaningful release-readiness choice is whether to open a narrow live
Telegram user-flow smoke gate, or to prepare the final RC go/no-go/release
notes package without additional live action.
