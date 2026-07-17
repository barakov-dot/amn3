# Phase 11 `0b858c5` combined private overlay rollout

Date: 2026-07-17.

Decision: `ROLLOUT-PASS`.

The exact trusted-transport approval was received and consumed once. The
bounded transaction changed only the AMN2 tracked source overlay and private
web runtime. Regular bot remained inactive/disabled, Telegram profile media
was unchanged, the production database was unchanged and AWG was never
stopped, restarted, recreated, reconfigured or mutated.

## Bound inputs

```text
docs_branch=codex-spark-phase9-docs-sync
docs_gate_commit=4c5e9be
source_branch=codex-vps-test-prep
source_commit=0b858c5cdbc5b565cc265966a2edfe2d339d65e0
production_before=801f8c3
production_after=0b858c5
package_sha256=7866BDD9FEBE1D6EEA701B37A6E4206A8267766A56993F3C02A0C7B30C394B54
source_zip_sha256=E03F13FD6A7BB5CBC5FCEE7179F395EA8C2864EBCEAB01BC351C5904F3CFF975
remote_executor_sha256=A41C000C8C15E0A4D4E2DE0CC35CB84A27EF73CCA00B69EB04FD4971FC64EF72
ssh_runner_sha256=654154AFF81425DE610817C9FF05FB2D976B2EA3A7843C9FC8F566269C94A6BE
approval=received_consumed
run_id=20260717T081340Z
```

## Preflight

The new SSH session passed all admission checks before upload:

```text
overlay=801f8c3
web=active_enabled_http_ok_loopback_only
bot=inactive_disabled_process_0_unit_env_bound
write_gates=false_false
database=integrity_ok|foreign_key_issues_0|tables_15|rows_88
database_file_sha256=888AB7E6479354B7E354CD5262FA28D42D1A35CD29907A81A827E9821CFEF611
database_logical_sha256=C54309D1C82E006C1F59AF1BB9A792B05C020B1DF9AE0D6C26BACD3907B78C5D
database_counts_sha256=FEDD60460F70DB5DE23EB0566A68AF772C0351242A8712B37C3F19A1C53CADF1
awg=running|restart_0|peers_12
awg_container_sha256=267BD715ED6B788FFAE1E59B3E7741ED6932756D25A00C5B7AAAC7492796C79B
awg_peer_set_sha256=E42E1176843B82A748081EDDB8E45A9852C1627A13BC08B9F69A4E4C70B81BB5
disk_sufficient=true
```

## Upload and apply

Only `amn2-combined-overlay-0b858c5.zip` and its checksum receipt were
uploaded. Both remote files were mode `0600`; the package SHA check passed.
One manually composed receipt command initially failed locally before SSH
handshake because its target argument was split. The corrected read-only
receipt passed. Raw diagnostic/environment output is intentionally excluded.

The remote executor repeated preflight and package/source/helper/runbook
bindings before stopping web. It created and verified a root-only rollback
bundle, applied the source offline, removed only the tracked obsolete JPG,
started only web and verified both canonical image contracts.

```text
package_contract=pass
source_delta_exact=true
rollout=pass
source_overlay=0b858c5
assets=canonical_square_and_wide_language_header_verified
telegram_profile_photo=unchanged
database=unchanged_integrity_ok_fk_0
bot=inactive_disabled_process_0_unit_env_unchanged
awg=running_restart_peer_set_unchanged
rollback_bundle=retained_verified
```

Early loopback health attempts observed bounded connection refusals while web
was starting; the executor continued its existing retry loop and the final
health contract passed. Automatic rollback was not needed.

## Independent postflight

A separate SSH session repeated the full read-only check after apply:

```text
overlay=0b858c5
web=active_enabled_http_ok_loopback_only
bot=inactive_disabled_process_0_unit_env_bound
write_gates=false_false
database_file_sha256=888AB7E6479354B7E354CD5262FA28D42D1A35CD29907A81A827E9821CFEF611
database_logical_sha256=C54309D1C82E006C1F59AF1BB9A792B05C020B1DF9AE0D6C26BACD3907B78C5D
database_counts_sha256=FEDD60460F70DB5DE23EB0566A68AF772C0351242A8712B37C3F19A1C53CADF1
database=integrity_ok|foreign_key_issues_0|tables_15|rows_88
awg=running|restart_0|peers_12
awg_container_sha256=267BD715ED6B788FFAE1E59B3E7741ED6932756D25A00C5B7AAAC7492796C79B
awg_peer_set_sha256=E42E1176843B82A748081EDDB8E45A9852C1627A13BC08B9F69A4E4C70B81BB5
postflight=pass
```

No token, key, private target, raw Telegram response or unsanitized production
log is stored in this evidence.

## Next gate

`PHASE11-TELEGRAM-002B` may now be reviewed as a separate persistent-bot
activation gate. This rollout approval does not authorize bot installation,
enable/start, Telegram API calls, provider actions, recovery deletion, peer or
config mutation, or any AWG action.
