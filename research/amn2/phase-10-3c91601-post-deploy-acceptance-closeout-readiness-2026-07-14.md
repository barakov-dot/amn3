# Phase 10 3c91601 post-deploy acceptance and closeout readiness review

Date: 2026-07-14.

Decision: `TECHNICAL-CLOSEOUT-READY-CLIENT-ACCEPTANCE-PENDING`.

Reviewed command:

```text
GPT-5.6 SOL -> REVIEW_PHASE10_3C91601_POST_DEPLOY_ACCEPTANCE_AND_CLOSEOUT_READINESS
```

The review used the published source, rollout evidence and read-only VPS
observations. It did not stop, restart or reconfigure AWG or web, mutate the
database, create or remove a peer, generate or deliver a config, call Telegram
or expose a public management listener.

## Authoritative state

```text
source_branch=codex-vps-test-prep
source_head=3c91601
source_origin_match=true
source_worktree=clean
status_branch=codex-spark-phase9-docs-sync
rollout_overlay=3c91601
rollout_run=20260714T101632Z
```

The implemented Phase 10 source includes read-only drift diagnostics, Device
Passport and Enrollment Ticket service contracts, lifecycle evidence, admin
web diagnostics and cascade physical-device revoke. Enrollment remains
non-launch-blocking while self-service onboarding is outside the initial launch
scope. Live drift remediation remains closed.

## Read-only runtime verification

The previously reviewed final verifier was streamed to `bash` over pinned-key
SSH. Its relevant result was:

```text
source_overlay=3c91601
marker=0640_root_amneziya|service_readable
web=active_enabled|restart_count_0|login_200|protected_303|plans_303
listeners=127.0.0.1_3030_only|api_3040_0|public_3030_3040_0
bot=inactive_disabled|process_0
write_gates=false_false
awg=running|restart_count_0|container_id_match|peer_count_12|peer_set_match
rollback=0700_root_root|required_files_present|hashes_verified
temporary_clone_count=0
clone_safe_evidence_secret_scan=passed
db_integrity=ok|foreign_key_issues_0
db_logical_sha256=C54309D1C82E006C1F59AF1BB9A792B05C020B1DF9AE0D6C26BACD3907B78C5D
db_file_sha256=888AB7E6479354B7E354CD5262FA28D42D1A35CD29907A81A827E9821CFEF611
schema=3_new_tables|5_named_indexes|new_rows_0_0_0
existing_counts=users_6|orders_8|devices_8|admin_actions_45|plans_8|api_tokens_12
```

This matches the successful rollout result. The VPN service was not stopped or
restarted during this review and remains available.

## Bounded client observation

A separate aggregate-only runner was syntax-checked locally and streamed over
SSH. It did not emit peer keys or endpoints.

```text
runner_sha256=A5E521FEF0F08EFC6D5DEBF3B8E5AFC38EB47899DA5EBF115B95066C028CA410
observation_started_utc=2026-07-14T11:18:03Z
observation_finished_utc=2026-07-14T11:19:04Z
peer_count=12_stable
latest_handshake_epoch=1783979070
latest_handshake_utc=2026-07-13T21:44:30Z
final_handshake_age_seconds=48874
rx_delta=0
tx_delta=0
```

No client was active during the bounded observation. This is not evidence of a
server defect: overlay, web, AWG, peer set, database and rollback invariants all
passed, and the rollout did not mutate AWG, peers or published configs. It is
also not sufficient to claim a fresh post-rollout physical-client acceptance.

## Closeout decision

Phase 10 remains active with exactly one external acceptance remainder:

```text
remainder=one_existing_client_connect_and_generate_traffic
verification=read_only_new_handshake_and_positive_rx_tx_delta
product_code_remainder=none_identified
package_or_schema_remainder=none_identified
new_config_required=false
peer_mutation_required=false
```

If the fresh observation passes, the next work is the Phase 10 final closeout
packet, final status sync and Phase 11 handoff. If it fails while the client is
actively attempting to connect, Phase 10 remains open for a focused incident
diagnosis; no speculative rebuild or config regeneration is authorized.

The exact next command is:

```text
GPT-5.6 SOL -> VERIFY_ONE_EXISTING_CLIENT_POST_3C91601_HANDSHAKE_AND_TRAFFIC_READ_ONLY
```

## Deferred without launch expansion

Dynamic subnet source-of-truth remains post-launch. Android TV reacceptance is
triggered only by a new published Amnezia Client release. Restore
single-flight/idempotency returns when restore apply is opened. WARP, NGINX,
marketplace, public tunnels and broad multi-protocol parity remain outside the
launch scope. Enrollment Ticket does not delay launch while self-service
onboarding is not mandatory.

## Local verification after status sync

```text
phase9_progress_harness=passed
next_command=GPT-5.6 SOL -> VERIFY_ONE_EXISTING_CLIENT_POST_3C91601_HANDSHAKE_AND_TRAFFIC_READ_ONLY
stop_lines=execution_go_false|config_generation_false|config_delivery_false|peer_creation_false|live_vps_ssh_telegram_public_false
scoped_harness_and_markdown_tests=20_passed
canonical_root_tests=43_passed
git_diff_check=passed
new_evidence_secret_value_scan=0_findings
```
