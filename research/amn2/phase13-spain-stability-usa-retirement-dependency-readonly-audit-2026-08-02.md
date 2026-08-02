# AMN2 Phase 13: Spain stability / USA retirement dependency read-only audit

Date: 2026-08-02.

## Scope

- root head: `b58738b8a8b7562c86dfc237b00669b004058ffe`;
- one read-only SSH process for Spain and one for USA;
- no package build, deploy, issuance, reboot, service/container/network action,
  config/peer mutation, USA shutdown, cleanup or reuse;
- no target, user, key path, fingerprint, peer identifier, endpoint, traffic
  bytes, raw stdout/stderr or system error persisted.

## Sanitized result

```text
spain_transport=ssh_client_failure
spain_awg2_equality=unverified
spain_foreign_equality=unverified
usa_transport=success
usa_overlay_equal=true
usa_awg_running=true
usa_peer_count=12
usa_recent_handshake_24h_count=2
usa_recent_handshake_7d_count=4
usa_recent_handshake_30d_count=4
usa_bot_active=true
usa_web_active=true
usa_db_integrity_ok=true
usa_db_foreign_key_issues=0
usa_dependency_audit_clear=false
live_mutation_attempted=false
```

## Decision

`go_no_go_decision=stop` for USA shutdown/cleanup/reuse.

Current USA cannot be classified as dependency-free: twelve configured peers
remain, two have a recent handshake within 24 hours and four within 7/30 days;
the bot and web runtime are active. Spain equality could not be refreshed
because the pinned read-only SSH attempt failed in the coarse
`ssh_client_failure` class. No raw transport output was inspected or retained,
so auth, host-key and connection causes are intentionally not claimed.

The result does not authorize migration, peer/config changes, service action,
shutdown or reuse. Finishing USA retirement now requires an explicit operator
decision about the observed active USA dependencies and a later separate exact
live approval.
