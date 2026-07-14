# Phase 10 3c91601 private VPS rollout

Date: 2026-07-14.

Status: `completed-pass-with-verified-automatic-rollback`.

The exact approval was received and consumed:

```text
APPROVE PHASE10_3C91601_PRIVATE_VPS_SOURCE_OVERLAY_UPLOAD_SNAPSHOT_CLONE_DB_MIGRATION_AND_WEB_ACTIVATION_WITH_ROLLBACK
```

The operation advanced the private production source overlay from `1c7fb78`
to `3c91601`. The AWG container was never stopped, restarted, recreated or
reconfigured. Only the private web service was stopped during the verified
snapshot, clone rehearsal and schema checkpoint.

## Bound artifacts

```text
source_commit=3c916015c10add37886370d04af70f0343f7f691
package_sha256=12E90EB54FCC374C84B6AA987C65E5644C4BD1B974089E81E16D00780389FB6E
source_sha256=5AD92A3A9D944825FEFDFEB4D56BDDBBB05390036E19E5AD197288C73812B0CB
apply_sha256=578A145E2AFE5BCC69B3730CE8C12BCE1BE368EC3B6DDD4847E94DD428D90DDA
smoke_sha256=4E49B183825603168108B227978F488A68EF31BC8BD11E2A839135CDE70E4106
preflight_sha256=920E9F9ECA78006745D8B54D978D4503666BAAD446CDC0EABCE11F8FA78BAEF7
successful_orchestrator_sha256=92BD2675CE5FC926E4C411C290B4F3B3E6298AB1488E523B7371AA3086F1816E
final_verifier_sha256=6B03D317BEF37C9A41D3FC69B439F973B850813BD4C283A6A8C3BE467894E1EB
package_mode=0600_root_root
```

All package and source checksums were reverified locally and remotely before
the web maintenance window. The private runners were sent through SSH stdin
and were not installed as persistent VPS tooling.

## Read-only preflight

```text
source_overlay=1c7fb78
web=active_enabled_http_200_loopback_only
bot=inactive_disabled_process_0
write_gates=VPS_APPLY_ENABLED_false|OPERATOR_DEVICE_CREATE_ENABLED_false
api_3040_listener=0
db=integrity_ok|foreign_key_issues_0|12_user_tables|new_tables_0|new_indexes_0
db_counts=users_6|orders_8|devices_8|admin_actions_45|plans_8|api_tokens_12
awg=running|restart_count_0|peers_12
awg_container_id_sha256=7AEEB324C889FF49CDF512CFE0537067836E5354E9A7DFA47AC17FDDEFAA6B0B
awg_peer_set_sha256=F8385507DA15E44E93AB1DB325E02A59FCFEC23E8E8433C55C5D1E18153D6303
```

## Verified rollback exercise

The first attempt, run `20260714T101311Z`, reached source apply, exact clone
schema migration and clone API smoke. An additional evidence scan rejected the
safe metadata field `raw_token_display` because its initial pattern was too
broad. Production migration had not started.

The automatic rollback removed the exact ten candidate tracked roots, restored
the source snapshot and overlay marker, restarted the web service and proved
the AWG state unchanged. Independent preflight then matched the original
production DB file and logical hashes exactly:

```text
rollback_run=20260714T101311Z
rollback_reason=overbroad_safe_metadata_marker_match
production_schema_checkpoint_crossed=false
source_overlay_restored=1c7fb78
db_file_sha256_restored=6F02F930CCC99A6C5F6754809119264BCD1ED1F9D36E44A6E3BE55AF14C4ABD9
db_logical_sha256_restored=6456C589EF1FF60707D3612F03023CF03D4B79736BD662D96874A460DFDEE599
web_restored=active_http_200
awg_unchanged=true|running|restart_count_0|peer_set_match
```

The scan was narrowed to actual secret-bearing JSON keys and assignments. A
focused regression proved that `raw_token_display` is allowed while an actual
`raw_token` key remains blocked.

## Successful rollout

Run `20260714T101632Z` completed the full reviewed sequence:

```text
rollback_path=/root/amn2-rollbacks/3c91601-20260714T101632Z
rollback_state=0700_root_root
rollback_hashes_verified=true
source_snapshot=verified
sqlite_backup=verified_logical_match
source_apply=passed
clone_schema_migration=passed_exact
clone_api_smoke=passed_loopback_only
clone_safe_evidence_secret_scan=passed
production_db_unchanged_before_migration=true
production_schema_migration=passed_exact
production_api_smoke=false
web_activation=passed
web_downtime_seconds=55
```

The clone API smoke created and revoked temporary credentials and wrote audit
evidence only inside the disposable clone. The clone was removed after success.
No production API token, server-sync or read-audit smoke write occurred.

## Production schema result

```text
new_tables=device_passports|device_enrollment_tickets|device_lifecycle_events
new_named_indexes=5
new_table_rows=0|0|0
existing_table_rows_unchanged=true
db_integrity=ok
db_foreign_key_issues=0
users_count=6
orders_count=8
devices_count=8
admin_actions_count=45
plans_count=8
api_tokens_count=12
```

The rollout did not issue an enrollment ticket, create a passport, write a
lifecycle event, update a plan quota, revoke a device or seed production data.

## Runtime result

```text
source_overlay=3c91601
marker=0640_root_amneziya|service_readable
web=active_enabled|restart_count_0|login_200|protected_303|plans_303
listeners=127.0.0.1_3030_only|api_3040_0|public_3030_3040_0
bot=inactive_disabled|process_0
write_gates=false_false
awg=running|restart_count_0|container_id_match|peer_count_12|peer_set_match
temporary_clone_count=0
```

A five-second post-rollout traffic observation kept all 12 peers but recorded
zero byte delta. The latest non-zero handshake timestamp was
`2026-07-13T21:44:30Z`. This is valid runtime continuity evidence, not a fresh
physical-client acceptance. Existing-client handshake and traffic after the
rollout remain an operator-triggered read-only observation.

## Excluded actions

No AWG/peer/config mutation, config generation or delivery, Telegram API or
polling, production API smoke, enrollment/ticket/passport action, cascade
revoke, public exposure, firewall/TLS/reverse-proxy change, reboot or provider
action occurred.

## Local verification after status sync

```text
phase9_progress_harness=passed
next_command=GPT-5.6 SOL -> REVIEW_PHASE10_3C91601_POST_DEPLOY_ACCEPTANCE_AND_CLOSEOUT_READINESS
stop_lines=execution_go_false|config_generation_false|config_delivery_false|peer_creation_false|live_vps_ssh_telegram_public_false
scoped_harness_and_markdown_tests=20_passed
canonical_root_tests=43_passed
git_diff_check=passed
new_evidence_secret_value_scan=0_findings
```

## Next

The source/schema rollout gate is closed. Post-deploy closeout-readiness review
passed all technical invariants, but a bounded client observation produced no
fresh handshake or traffic. Phase 10 therefore remains open for exactly one
existing-client connection followed by read-only handshake/traffic
verification; no new config or peer mutation is required. Review evidence:
`research/amn2/phase-10-3c91601-post-deploy-acceptance-closeout-readiness-2026-07-14.md`.
