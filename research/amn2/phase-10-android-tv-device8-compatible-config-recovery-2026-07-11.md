# Phase 10 Android TV device 8 compatible config recovery

Date: 2026-07-11.

Status: `corrected-config-generated-pending-physical-android-tv-retest`.

The operator imported the first device 8 config into the official AmneziaVPN
Android TV application. Import succeeded, but the application remained in the
connecting state. Read-only runtime observation showed that the device 8 peer
was present and active, but had no endpoint, handshake or traffic.

No new peer or device was created during this recovery. The production
database, runtime peer, server config and Docker container were not changed or
restarted.

## Read-Only Diagnosis

```text
android_client=official_amneziavpn
initial_import=passed
initial_connect=failed_connecting_without_connected_state
device_id=8
device_status=active
runtime=amnezia-awg2_running
runtime_peer_present=true
runtime_endpoint_present=false
runtime_handshake_present=false
runtime_rx_bytes=0
runtime_tx_bytes=0
other_existing_profiles_reported_working=true
```

Immediately after the operator's control connection, a read-only runtime
observation identified device 1 as the active previous profile:

```text
control_device_id=1
control_device_endpoint_present=true
control_device_handshake_age_s=90
control_device_rx_positive=true
control_device_tx_positive=true
device8_endpoint_present=false
device8_handshake=never
device8_rx_positive=false
device8_tx_positive=false
control_comparison=confirmed_client_network_server_dataplane_healthy
```

This A/B observation confirms that the failure is specific to the first device
8 client config rather than the official application, Android TV network path,
VPS endpoint or AWG runtime.

Secret-safe comparison confirmed:

```text
client_private_key_derives_expected_device8_peer=true
client_preshared_key_matches_runtime_peer=true
client_address_matches_runtime_allowed_ip=true
client_server_public_key_matches_verified_runtime_server_key=true
client_endpoint_and_server_key_match_known_working_profiles=true
secret_values_printed=false
```

The first TV config differed from the Phase 8 Android-accepted profile in
exactly 11 AWG fields: `Jc`, `Jmin`, `Jmax`, `S1` through `S4`, and `H1`
through `H4`. This is the same failure signature recorded by the Phase 8
Android acceptance: import succeeds, but the runtime never observes a valid
endpoint or handshake until the compatible AWG profile is used.

## Branch Regression

The active Phase 10 line started from `4326cae`. The previously tested AMN2
commit `187949b Persist Android-compatible AWG defaults` was not an ancestor of
that line, so the active product branch had silently returned to the
incompatible `4/40/70/0...` defaults.

The verified fix was restored on the active branch as:

```text
commit=60d8cc9 Persist Android-compatible AWG defaults
branch=codex-vps-test-prep
push=completed
```

The product default, `.env` examples and operator documentation now use the
Android-accepted profile consistently. Explicit environment overrides remain
supported.

## Product And Test Evidence

```text
scoped_tests=87_passed_1_skipped_1_warning
full_tests=811_passed_1_skipped_1_warning
diff_check=passed
diff_review=passed_no_unrelated_changes
phase9_progress_harness=14_passed|stop_lines_passed|docs_only_status_sync_scope_passed
```

## Corrected Private Artifact

The existing device 8 material was re-rendered locally using the known-good
profile. Identity and peer fields were preserved byte-for-byte; only the 11
incompatible AWG fields changed.

```text
run_id=20260711T125600Z
original_private_config=private-artifacts/phase10/android-tv-single/20260707T200605Z/Neobyatnaya-AMNZ-N-android-tv-01.conf
corrected_private_config=private-artifacts/phase10/android-tv-corrected/20260711T125600Z/Neobyatnaya-AMNZ-N-android-tv-01-compatible.conf
corrected_sha256=916B08317819CE4C147B39C91C513F6DCF8DB59A1850EEA0774BFDB91CA193BD
identity_and_peer_fields_preserved=true
changed_field_count=11
peer_created=false
peer_mutated=false
server_mutated=false
container_restarted=false
secret_values_printed=false
```

The private file remains excluded from Git and was not printed to chat or
evidence.

## Remaining Acceptance

The operator must replace the failed profile on Android TV with the corrected
private config and start a connection. Final acceptance requires a read-only
observation of a fresh device 8 handshake, endpoint and traffic growth.

```text
next_step=ANDROID_TV_IMPORT_CONNECT_CORRECTED_DEVICE8_CONFIG
final_acceptance=pending_physical_device
```
