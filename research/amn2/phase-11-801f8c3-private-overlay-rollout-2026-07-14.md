# Phase 11: 801f8c3 private overlay rollout

Date: 2026-07-14.

Decision: `COMPLETED-PASS`.

The exact approved private source-overlay rollout moved production from
`3c91601` to `801f8c3`. The web service was the only production service
briefly stopped. The AWG container remained running and was never stopped,
restarted, recreated or reconfigured. No Telegram API, API smoke, schema,
peer, config, public-listener, provider or reboot action was performed.

## Bound approval and artifacts

```text
approval=APPROVE PHASE11_801F8C3_PRIVATE_VPS_SOURCE_OVERLAY_UPLOAD_WEB_FREEZE_SNAPSHOT_OFFLINE_APPLY_VERIFY_AND_ROLLBACK_WITH_AWG_UNTOUCHED
approval_status=received_consumed
candidate_source=801f8c3406121549eb6a19150be009cfc0ea88d0
package_sha256=693DF74192E55A2231F45C0ADF153B745C7D2AF8EDEDA67830D02CB620A4C3FF
source_sha256=B332CB1DCFB85768ACE0DF78E038B955F7C853989CF1C67CDE0233FA51EBD6C3
apply_sha256=85AE2C0E5A1E949529342AF2939A577AE23B3924653A344E1E77465B898E56AF
runbook_sha256=923DBB704BDDF464DEB1D3037703B58AF8B102CFCC3A174509A05FB3FB4B42CC
successful_run_id=20260714T165948Z
```

The uploaded package was verified before extraction. Its exact four-entry
contract, source commit binding and bound artifact digests passed. The
successful run removed the disposable candidate and uploaded copies and
retained its rollback material under the unique root-only rollback path.

## Preflight baseline

```text
overlay=3c91601
web=active_enabled_http_ok_loopback_only
bot=inactive_disabled_process_0
write_gates=false_false
database_integrity=ok
database_foreign_key_issues=0
database_file_sha256=888AB7E6479354B7E354CD5262FA28D42D1A35CD29907A81A827E9821CFEF611
database_logical_sha256=C54309D1C82E006C1F59AF1BB9A792B05C020B1DF9AE0D6C26BACD3907B78C5D
database_counts_sha256=FEDD60460F70DB5DE23EB0566A68AF772C0351242A8712B37C3F19A1C53CADF1
database_tables=15
database_total_rows=88
awg_container_sha256=267BD715ED6B788FFAE1E59B3E7741ED6932756D25A00C5B7AAAC7492796C79B
awg_restart_count=0
awg_running=true
awg_peer_count=12
awg_peer_set_sha256=E42E1176843B82A748081EDDB8E45A9852C1627A13BC08B9F69A4E4C70B81BB5
disk_sufficient=true
```

## Controlled retry and rollback evidence

The first apply run `20260714T165601Z` reached the web restart check before
the service was ready within a fixed two-second delay. Its automatic rollback
completed with `rollout=rollback-pass`. A separate read-only preflight then
proved the exact `3c91601` baseline was restored: all database and AWG values
above matched, web was healthy and the bot remained inactive and disabled.

The local executor was corrected to use a bounded 30-second web readiness
loop. Its Bash and PowerShell syntax checks and secret-pattern scan passed. A
subsequent local client-timeout produced no accepted result; before retrying,
another independent preflight again proved the exact baseline and invariants.
No unknown intermediate state was treated as success.

## Successful offline apply

Run `20260714T165948Z` passed all of the following:

1. Repeated the full read-only preflight on overlay `3c91601`.
2. Froze only `amneziya-web.service` and created source, overlay-marker and
   SQLite snapshots in a unique root-only rollback directory.
3. Applied the bound source ZIP offline with both product write gates false
   and package-index access disabled.
4. Proved the exact functional source delta was only
   `app/bot/controlled_smoke.py` and
   `tests/bot/test_controlled_smoke.py`.
5. Proved production SQLite was byte/logically unchanged, with identical
   counts, integrity `ok` and zero foreign-key issues.
6. Started the web service through the bounded readiness loop and verified
   login HTTP, protected-route redirect and loopback-only listener state.
7. Proved the bot stayed inactive/disabled and AWG retained the same container
   identity, restart count, peer count and peer-set digest.

## Independent postflight

```text
postflight=pass
overlay=801f8c3
web=active_enabled_http_ok_loopback_only
bot=inactive_disabled_process_0
write_gates=false_false
database_integrity=ok
database_foreign_key_issues=0
database_file_logical_counts_hashes=unchanged
database_tables=15
database_total_rows=88
awg_restart_count=0
awg_running=true
awg_peer_count=12
awg_peer_set=unchanged
api_3040_listener=0
```

The production prerequisite for the corrected transient Telegram smoke is now
complete. The smoke itself was not started and remains a separate exact live
gate. Next command:

```text
GPT-5.6 SOL -> REVIEW_PHASE11_801F8C3_PRIVATE_TELEGRAM_SINGLE_ADMIN_TRANSIENT_SMOKE_GATE
```
