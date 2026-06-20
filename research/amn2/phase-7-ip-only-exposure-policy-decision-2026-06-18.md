# Phase 7 P7-I011 IP-Only Exposure Policy Decision

Date: 2026-06-18.

Task: `P7-I011 IP-only exposure policy decision`.

Status: `completed-local-only-operator-declined-dns-domain`.

## Operator Decision

The operator explicitly decided not to use a DNS domain for AMN2:

```text
я не буду для амнезии использовать домен, только айпи
```

This means the `P7-C002c` DNS/domain/trusted TLS prerequisite path is closed as:

```text
P7-C002c_status=operator_declined_dns_domain
trusted_public_tls_with_dns_domain=not_a_goal_for_amn2
```

## Selected Access Policy

AMN2 remains an operator-only system.

Selected default access path:

```text
web_admin_bind=127.0.0.1:3030
operator_access=VPS_IP + SSH tunnel to loopback web/admin
public_domain=not_used
trusted_public_tls_cutover=not_planned
direct_public_3030=false
direct_public_3040=false
public_80_443=false_until_separate_gate
```

The VPS IP remains useful for SSH and operator targeting. It is not treated as a
DNS FQDN, and it is not a trusted public TLS identity.

## Impact On P7-C002

`P7-C002` no longer waits for a DNS FQDN by default. The DNS/domain/TLS
prerequisite branch is closed by operator policy.

Current `P7-C002` status:

```text
public_exposure_applied=false
domain_tls_branch=closed_operator_declined_dns_domain
selected_default_mode=operator_only_ip_plus_loopback_ssh_tunnel
```

Any future IP-only public web/admin exposure is not part of the current RC
readiness path. It would need a separate exact named gate with explicit risk
acceptance because it would not be a normal trusted-domain HTTPS cutover.

Candidate future gate, not active:

```text
P7-C002d IP-only public exposure risk gate.
Importance: critical gated.
Gate: public exposure / IP-only risk acceptance.
Purpose: decide whether to expose AMN2 web/admin on IP-only HTTP or self-signed
HTTPS, with explicit browser warning, firewall, rollback and audit criteria.
```

## What Was Not Performed

No live VPS command, SSH command, `.env` mutation, package install, service
restart, reverse proxy apply, TLS certificate issue, firewall change, public
listener change, public web/admin exposure, public API exposure, config
delivery, write API enablement, Local Agent mutation, backup/import/reboot,
production peer/user mutation, destructive action, Telegram action, secret
publication or upstream/GPL code copy was performed.

The temporary local helper `tmp/p7_c002c_dns_domain_tls_prereq.ps1`, created
before the operator declined domain use, should be removed so it cannot be run
by accident.

## Next Recommendation

Single safe next step:

```text
watch-only intake only.
```

Single risky/live next step, only if the operator intentionally wants public
IP-only exposure later:

```text
P7-C002d IP-only public exposure risk gate.
```

Recommended default:

```text
stay_operator_only_ip_plus_ssh_tunnel=yes
```
