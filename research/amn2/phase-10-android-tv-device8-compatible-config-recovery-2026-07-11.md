# Phase 10 Android TV device 8 compatible config recovery

Date: 2026-07-11.

Status: `working-standard-conf-pass-android-tv-ios-windows`.

The operator imported the first device 8 config into the official AmneziaVPN
Android TV application. Import succeeded, but the application remained in the
connecting state. Read-only runtime observation showed that the device 8 peer
was present and active, but had no endpoint, handshake or traffic. After the 11
AWG compatibility fields were restored, the standard `.conf` connected and
passed traffic on Android TV, iOS DefaultVPN and Windows 11 AmneziaVPN.

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

## Physical Cross-Client Acceptance

The corrected standard `.conf` was tested sequentially against the existing
device 8 peer. Each observation was read-only and showed a fresh handshake plus
growing traffic counters:

```text
android_tv_client=official_amneziavpn
android_tv_import=passed_standard_conf
android_tv_connect_and_traffic=passed
android_tv_handshake_age_s=93
android_tv_rx_bytes=3382412
android_tv_tx_bytes=134118669

ios_client=defaultvpn
ios_import=passed_standard_conf
ios_connect_and_traffic=passed
ios_handshake_age_s=9
ios_rx_bytes=4169240
ios_tx_bytes=149555536

windows_client=official_amneziavpn_windows_11
windows_import=passed_standard_conf
windows_connect_and_traffic=passed
windows_handshake_age_s=46
windows_rx_bytes=4478716
windows_tx_bytes=153445786

cross_client_counter_growth=passed
device8_peer_identity_unchanged=true
server_mutation=false
```

Android TV and iOS were also observed working with the same owner config during
an overlapping interval. That is evidence that shared-owner use can work, not a
guarantee of stable concurrent endpoint handling at arbitrary scale.

The native named `.vpn` JSON experiment imported into Android TV but remained
in the connecting state without an error. It is therefore not an accepted
delivery artifact. The standard `.conf` is the recommended cross-client path.

Real-device Android TV and Windows 11 UI observations also confirmed that the
standard `.conf` filename stem is used as the displayed profile name. The
working profile displayed `Neobyatnaya-AMNZ-N-android-tv-01`; the canonical
future basename is `Neobyatnaya.NET`.

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
compatibility_recovery_commit=60d8cc9
assignment_policy_commit=1c7fb78
assignment_policy_branch=codex-vps-test-prep
assignment_policy_push=completed
assignment_policy=dedicated_device_default|owner_shared_admin_only
client_plan_quota=min_global_and_plan_max_devices
dedicated_delivery_filename=Neobyatnaya.NET-device_id.conf
owner_shared_delivery_filename=Neobyatnaya.NET.conf
scoped_tests=128_passed_1_skipped_1_warning
full_tests=823_passed_1_skipped_1_warning
final_web_scope=7_passed_1_warning
diff_check=passed
diff_review=passed_quota_seed_preservation_and_owner_admin_guard_added
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
canonical_cross_client_alias=private-artifacts/phase10/cross-client-acceptance/20260711T134917Z/Neobyatnaya.NET.conf
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

## Remaining Work

Physical first-connect and traffic acceptance is complete. The remaining work
is product rollout and lifecycle hardening, not another copy of the same
device 8 connection test.

```text
android_tv_acceptance=passed
ios_defaultvpn_first_connect_acceptance=passed
windows_11_amneziavpn_acceptance=passed
ios_reconnect_and_long_session_soak=pending_separate_slice
native_vpn_delivery=disabled_unreliable
current_vps_source_overlay=1c7fb78_smoke_pass
latest_product_head=1c7fb78_active_private_vps
device8_assignment_reconciliation=passed_owner_shared_existing_admin_owner_no_reassignment
next_step=START_PHASE10_PLAN_DEVICE_QUOTA_ADMIN_UI_SLICE
```
