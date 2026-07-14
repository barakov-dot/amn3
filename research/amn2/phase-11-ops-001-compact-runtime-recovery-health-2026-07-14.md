# Phase 11 OPS-001: compact runtime/recovery health evidence

Date: 2026-07-14.

Decision: `HEALTHY; CONTINUE CONTROLLED OPERATIONS`.

This is one bounded read-only observation, not a permanent telemetry agent.
It did not restart or change a service, call Telegram, write SQLite, expose a
listener, create/deliver a config, change a peer, or stop/restart/recreate AWG.
Raw journal rows, target address and secret-bearing material were not emitted.

## Observation receipt

```text
observation_utc=2026-07-14T18:02:04Z
production_overlay=801f8c3
web=active_enabled|result_success|restarts_0
regular_bot=inactive_disabled_process_0
listener_3030=loopback_only
listener_3040=absent
listener_80=absent
listener_443=absent
failed_systemd_units=0
ntp_synchronized=yes
root_and_amn2_disk_used=71_percent
root_and_amn2_disk_available_kb=2888376
memory_available_kb=505188
memory_total_kb=984560
load1=0.07
uptime_seconds=182601
```

Disk utilization is an observation, not a current incident. The filesystem
still has about 2.75 GiB available. Recheck at the next bounded operations
snapshot; investigate growth at 80% and require cleanup/capacity action before
85%. Memory has roughly half of its total available and load is low.

## Application and journal boundary

The last 24 hours contained 32 `err..alert` journal rows. Safe aggregation,
without message text, classified them as:

```text
journal_source_amn2_24h=0
journal_source_docker_24h=0
journal_source_ssh_24h=30
journal_source_other_24h=2
journal_category_auth_failure_24h=0
journal_category_permission_denied_24h=0
journal_category_transport_close_24h=11
journal_category_missing_path_24h=0
journal_category_unit_start_failure_24h=0
journal_category_resource_exhaustion_24h=0
journal_category_network_24h=2
journal_category_other_24h=19
```

There is no AMN2 or Docker error row in this window, no failed systemd unit,
no resource-exhaustion marker and no classified authentication failure. The
SSH-heavy transport-close/noise count is retained as an operations observation
but does not alter the healthy application verdict.

## Data and AWG invariants

```text
database_integrity=ok
database_foreign_key_issues=0
database_file_sha256=888AB7E6479354B7E354CD5262FA28D42D1A35CD29907A81A827E9821CFEF611
database_logical_sha256=C54309D1C82E006C1F59AF1BB9A792B05C020B1DF9AE0D6C26BACD3907B78C5D
database_counts_sha256=FEDD60460F70DB5DE23EB0566A68AF772C0351242A8712B37C3F19A1C53CADF1
database_tables=15
database_total_rows=88
awg_running=true
awg_restart_count=0
awg_peer_count=12
awg_peer_set_sha256=E42E1176843B82A748081EDDB8E45A9852C1627A13BC08B9F69A4E4C70B81BB5
```

The database matches the accepted post-Telegram-smoke baseline exactly. AWG
was never stopped, restarted or recreated and retains the accepted peer set.

## Recovery health

The retained successful `801f8c3` production rollback directory exists with
mode `0700`. All seven required source/marker/SQLite/AWG snapshot and manifest
items are present; its SQLite snapshot has integrity `ok` and zero foreign-key
issues.

The canonical external hybrid recovery copy was rechecked read-only:

```text
canonical_external_copy=present
canonical_external_file_count=3
canonical_external_missing=0
canonical_external_extras=0
canonical_external_sha256=2c618fa52aed038eb494a892480970795c554bddd6649156e1fe5a9c00e52280
canonical_external_private_key_like_files=0
```

It contains exactly ciphertext plus checksum and recovery-info receipts. The
known ciphertext hash matches and no private-key-like file is present on that
external copy. This recheck does not supersede the separate old bundle/key
retention decision and does not authorize restore apply.

## Security and operational conclusion

The accepted private boundary is unchanged: web is loopback-only, public API
and ports 80/443 are absent, the persistent bot is disabled, and product write
gates remain false. No target, token, administrator ID, private key, PSK,
config/import payload or raw log is included here.

Next ordered action: `DECIDE_PHASE11_RECOVERY_001_OLD_BUNDLE_KEY_RETENTION`.
