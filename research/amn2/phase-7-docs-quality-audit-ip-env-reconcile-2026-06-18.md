# Phase 7 Docs Quality Audit And IP-Only Env Reconcile Planning

Date: 2026-06-18.

Task: `P7-S005 + P7-I012 docs quality audit / IP-only env reconciliation plan`.

Status: `completed-docs-only-audit-with-inactive-reconcile-gate`.

Gate: `docs-only/status`.

## Audit Trigger

The operator requested a review of the recent Phase 7 modifications made under
a lower reasoning setting, with weak or inaccurate implementation details to be
added to the correction plan.

## Finding 1: Workspace / Source Branch Ambiguity

The current local workspace is the AMN3 documentation/evidence repository:

```text
workspace_repo=barakov-dot/amn3
workspace_branch=master
workspace_head=ec811cf Prepare Phase 7 transition
```

AMN2 remains the package/source truth for the released overlay:

```text
amn2_source_repo=barakov-dot/amn2
amn2_source_branch=codex-vps-test-prep
amn2_source_head=b121865 Add multi instance conflict model
```

Risk if left unclear: a future operator could confuse the AMN3 evidence branch
with the AMN2 source branch and run branch-sensitive commands in the wrong
repository.

Correction: status/handoff docs must describe this as AMN3 workspace/evidence
context plus AMN2 package/source context, not as one local git branch.

## Finding 2: IP-Only Policy Versus Existing Public URL Env Fields

`P7-C002a` intentionally added admin/public URL prerequisite fields to the live
`.env` before the later `P7-I011` no-domain policy decision.

After `P7-I011`, current policy is:

```text
selected_default_mode=operator_only_ip_plus_loopback_ssh_tunnel
dns_domain_for_amn2=not_used
trusted_public_tls_cutover=not_planned
public_web_admin_exposure=false
public_api_exposure=false
```

The existing public URL fields are not public exposure by themselves, but they
are a future confusion point. They should be treated as inert historical
prerequisite residue until a separate exact gate decides whether to clear,
normalize or explicitly retain them.

New inactive proposal:

```text
P7-C002e Public URL env reconciliation gate.
Importance: important gated.
Gate: live .env mutation / public exposure prerequisite hygiene.
Purpose: decide whether to clear, normalize or explicitly retain
PUBLIC_BASE_URL, PUBLIC_DOMAIN and WEB_PUBLIC_BASE_URL after the operator chose
IP-only loopback/SSH-tunnel operation. Must create a rollback copy and must not
open public listeners, reverse proxy, TLS, firewall or config delivery.
```

This proposal is not active and must not be executed without an exact named
gate.

## Corrections Applied

The Phase 7 plan/status/handoff docs are updated so:

- AMN3 workspace context and AMN2 source/package context are separate;
- `P7-C002c` remains closed by the operator no-domain policy;
- `P7-C002d` remains the only public exposure risk proposal;
- `P7-C002e` is added as a narrower env reconciliation proposal;
- no DNS/domain/TLS branch is recommended as the default next path.

## What Was Not Performed

No live VPS command, SSH command, `.env` mutation, package install, service
restart, reverse proxy apply, TLS certificate issue, firewall change, public
listener change, public web/admin exposure, public API exposure, config delivery,
write API enablement, Local Agent mutation, backup/import/reboot, production
peer/user mutation, destructive action, Telegram action, secret publication or
upstream/GPL code copy was performed.

## Next Recommendation After Audit

Default safe next step:

```text
watch-only intake only
```

If the operator wants to resolve the env residue before any future public work,
open a separate exact named gate:

```text
Открываю P7-C002e Public URL env reconciliation gate для b121865 на текущем disposable VPS 89.185.80.166.
```
