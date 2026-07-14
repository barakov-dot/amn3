# Phase 11: 801f8c3 private Telegram transient smoke

Date: 2026-07-14.

Decision: `COMPLETED-PASS`.

The separately approved single-admin transient smoke ran against production
overlay `801f8c3`. It accepted exact `/start` from the first configured
administrator, sent one response, acknowledged only that accepted update and
proved the Telegram backlog transition `0 → 1 → 0`.

The regular bot service remained inactive and disabled. Production SQLite was
opened read-only by the controlled runner and remained unchanged. The AWG
container was never stopped, restarted, recreated or reconfigured.

## Approval and bound scope

```text
approval=APPROVE PHASE11_801F8C3_PRIVATE_TELEGRAM_FIRST_CONFIGURED_ADMIN_TRANSIENT_START_SMOKE_AND_ONE_RESPONSE_ON_CLONE_DB_TTL120_WATCHDOG180_BACKLOG_0_1_0_CLEANUP_WITH_REGULAR_BOT_DISABLED_AND_AWG_UNTOUCHED
approval_status=received_consumed
source_commit=801f8c3406121549eb6a19150be009cfc0ea88d0
production_overlay=801f8c3
successful_run_id=20260714T174239Z
internal_ttl_seconds=120
outer_watchdog_seconds=180
restart=no
timeout_stop_seconds=15
kill_mode=control-group
```

## Final preflight

The complete read-only preflight was repeated immediately before execution:

```text
preflight=pass
source_hash_binding=controlled_smoke_and_test_match
web=active_enabled_http_ok_loopback_only
api_3040_listener=0
regular_bot=inactive_disabled_process_0
write_gates=false_false
token_configured_shape_valid=true
configured_admin_count=2
selected_admin_binding=first_configured_private
proxy_configured=false
service_user_binding=valid_private
systemd_run_available=true
database_integrity=ok
database_foreign_key_issues=0
database_file_sha256=888AB7E6479354B7E354CD5262FA28D42D1A35CD29907A81A827E9821CFEF611
database_logical_sha256=C54309D1C82E006C1F59AF1BB9A792B05C020B1DF9AE0D6C26BACD3907B78C5D
database_counts_sha256=FEDD60460F70DB5DE23EB0566A68AF772C0351242A8712B37C3F19A1C53CADF1
database_tables=15
database_total_rows=88
awg_container_sha256=267BD715ED6B788FFAE1E59B3E7741ED6932756D25A00C5B7AAAC7492796C79B
awg_restart_count=0
awg_peer_count=12
awg_peer_set_sha256=E42E1176843B82A748081EDDB8E45A9852C1627A13BC08B9F69A4E4C70B81BB5
run_directory_required_kb=10888
run_directory_available_kb=97328
telegram_api_called=false
```

No Telegram method was called during this preflight.

## Controlled prepare retry

The first prepare attempt created no active smoke because `/run` refused direct
execution of the private helper file. `systemd-run` returned permission denied
before the controlled command could call Telegram. The fail-closed prepare
cleanup removed its state, clone and runtime directory.

A separate read-only audit then proved:

```text
post_failure_audit=pass
active_state=absent
private_clone_run_directory=absent
telegram_api_called=false
production_runtime=baseline_unchanged
awg=running_restart_0_peer_set_unchanged
```

The helper invocation was corrected to use `/bin/bash` while preserving the
same private file ownership, systemd sandbox, TTL and watchdog contract. This
is the expected execution method on a `/run` mount that does not allow direct
file execution.

## Successful transient run

The retry created a consistent mode `0600` SQLite online-backup clone in a
private mode `0700` runtime directory, proved production SQLite and AWG were
unchanged during clone creation, and started one unique transient systemd unit
as the existing bot service user.

The controlled runner then proved:

```text
transient_smoke=pass
run_id=20260714T174239Z
bot_identity_match=true
accepted_update=first_configured_admin_exact_start
one_response_sent=true
backlog_transition=0_1_0
production_database=unchanged_integrity_ok_fk_0
regular_bot=inactive_disabled_process_0
web=active_enabled_http_ok_loopback_only
awg=running_restart_0_peer_set_unchanged
transient_unit=stopped_collected
private_clone=removed
```

The output did not contain the bot token, administrator ID, message body,
webhook URL, config material, peer keys or private target.

## Postflight and boundaries

The transient control group was absent before private material was removed.
Production database file/logical/count digests match the preflight exactly;
integrity remains `ok` with zero foreign-key issues. Web remains healthy and
loopback-only. AWG retains restart count zero, 12 peers and the same peer-set
digest.

This smoke does not authorize persistent bot enablement. It did not process
callbacks, generate or deliver configs, mutate peers or production lifecycle
state, run schema/API smoke, expose a public listener, reboot or perform a
provider action.

Next command:

```text
GPT-5.6 SOL -> REVIEW_PHASE11_TELEGRAM_002_PERSISTENT_PRIVATE_BOT_SERVICE_DECISION
```
