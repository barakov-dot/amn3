# POST-RELEASE-API-001 live acceptance evidence — 2026-07-19

## Decision

The separately approved single-use API-001 acceptance gate passed against the
production source overlay while all smoke mutations remained confined to a
private disposable SQLite clone and a transient IPv4-loopback listener.

```text
post_release_api_001=live_acceptance_pass
approval=exact_literal_match|single_use_consumed
remote_sha256=6D4F801D7A0235C62E8F558B9D9F82DF676F672C0F7972A30F4362BCA12C9526
source_overlay=0b858c5cdbc5b565cc265966a2edfe2d339d65e0
write_gates=false_false
production_api_3040_before=absent
transient_api=127.0.0.1:3040|clone_db_only
production_api_3040_after=absent
production_database=unchanged
production_bot_web=unchanged
production_awg=untouched|observed_unchanged
```

## Fresh preflight

The checksum-bound runner first executed only `Mode preflight` and returned:

```text
source_contract=pass
write_gates=false_false
post_release_api_001_preflight=pass
production_api_3040=absent
production_db_bot_web_awg=observed_unchanged
```

No approval was supplied to preflight and no state was created.

## Single-use run

The exact user approval was compared ordinally to the literal in committed
runner bytes. The local `CreateNew` receipt exists and binds the consumed run
authority to the remote SHA. The runner streamed those exact Bash bytes through
trusted OpenSSH once.

```text
source_contract=pass
write_gates=false_false
transient_api=ipv4_loopback_only
missing_bearer=401
invalid_bearer=401
server_scope_metrics=403
metrics_scope_server=403
checked_routes=6
api_read_count=6
api_write_count=0
last_used_at=present
revoked_at=present
post_release_api_001_run=pass
```

The bearer value, Authorization header, token hash, SSH target, private key,
PSK, and clone contents were not printed or written to evidence.

## Cleanup and independent postflight

The bounded run completed through mandatory cleanup:

```text
cleanup=listener_0_process_0_clone_0_state_0
production_db_bot_web_awg=unchanged
```

After the run returned PASS, a separate read-only `Mode preflight` was executed
without approval and independently returned:

```text
source_contract=pass
write_gates=false_false
post_release_api_001_preflight=pass
production_api_3040=absent
production_db_bot_web_awg=observed_unchanged
```

No retry, repeated run, blind DB restore, service restart, Telegram action,
Docker lifecycle operation, AWG mutation, or Phase 10/11 rollout action was
performed.

## Release boundary

API-001 validates the existing private scoped read-only API contract. It does
not authorize public exposure, write/config/peer/self-service routes, permanent
port `3040`, or a persistent API service. Phase 11 remains closed as
`completed-controlled-private-release`.
