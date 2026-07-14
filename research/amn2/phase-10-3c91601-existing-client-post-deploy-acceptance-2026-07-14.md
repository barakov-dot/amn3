# Phase 10 3c91601 existing-client post-deploy acceptance

Date: 2026-07-14.

Status: `PASSED-FRESH-HANDSHAKE-AND-TRAFFIC`.

Executed command:

```text
GPT-5.6 SOL -> VERIFY_ONE_EXISTING_CLIENT_POST_3C91601_HANDSHAKE_AND_TRAFFIC_READ_ONLY
```

The verification observed aggregate AWG counters only. It did not emit peer
keys or endpoints, identify the physical client, stop or restart a service,
mutate a peer or config, write the database, call Telegram or expose a public
management listener.

## Acceptance observation

```text
observation_started_utc=2026-07-14T11:30:40Z
observation_finished_utc=2026-07-14T11:31:40Z
peer_count_start=12
peer_count_end=12
fresh_handshake_epoch=1784028593
fresh_handshake_utc=2026-07-14T11:29:53Z
rx_delta_bytes=205184
tx_delta_bytes=7176839
```

All six ten-second samples retained 12 peers. Traffic increased during the
window, including another increase in the final sample. The handshake is newer
than the successful `3c91601` rollout and therefore closes the exact
post-deploy physical-client acceptance remainder.

## Final runtime verification

The full read-only verifier ran after the accepted traffic window:

```text
source_overlay=3c91601
web=active_enabled|restart_count_0|login_200|protected_303|plans_303
listeners=127.0.0.1_3030_only|api_3040_0|public_3030_3040_0
bot=inactive_disabled|process_0
write_gates=false_false
awg=running|restart_count_0|container_id_match|peer_count_12|peer_set_match
latest_handshake_epoch=1784029146
latest_handshake_utc=2026-07-14T11:39:06Z
rollback=present|0700_root_root|hashes_verified
temporary_clone_count=0
db_integrity=ok|foreign_key_issues_0
db_logical_sha256=C54309D1C82E006C1F59AF1BB9A792B05C020B1DF9AE0D6C26BACD3907B78C5D
db_file_sha256=888AB7E6479354B7E354CD5262FA28D42D1A35CD29907A81A827E9821CFEF611
schema=3_new_tables|5_named_indexes|new_rows_0_0_0
existing_counts=users_6|orders_8|devices_8|admin_actions_45|plans_8|api_tokens_12
```

The later handshake independently confirms continued client reachability after
the traffic window. A subsequent five-second sample was idle, which does not
invalidate the earlier positive acceptance deltas.

## Decision

```text
post_deploy_client_acceptance=passed
exact_external_acceptance_remainder=closed
product_code_remainder=none_identified
package_or_schema_remainder=none_identified
new_config_required=false
peer_mutation_required=false
phase10_closeout_readiness=ready_for_final_packet
phase10_formally_closed=false_until_closeout_packet
```

The next command is:

```text
GPT-5.6 SOL -> PREPARE_PHASE10_FINAL_CLOSEOUT_PACKET_AND_PHASE11_HANDOFF
```

## Local verification after status sync

```text
phase9_progress_harness=passed
next_command=GPT-5.6 SOL -> PREPARE_PHASE10_FINAL_CLOSEOUT_PACKET_AND_PHASE11_HANDOFF
stop_lines=execution_go_false|config_generation_false|config_delivery_false|peer_creation_false|live_vps_ssh_telegram_public_false
scoped_harness_and_markdown_tests=20_passed
canonical_root_tests=43_passed
git_diff_check=passed
new_evidence_secret_value_scan=0_findings
```
