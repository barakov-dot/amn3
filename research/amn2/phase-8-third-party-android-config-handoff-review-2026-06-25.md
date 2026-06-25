# Phase 8 third-party Android config handoff review

Date: 2026-06-25.

Status: `completed-docs-only`.

No live VPS/SSH/config/Telegram/public gate was opened.

## Inputs

- Existing Phase 8 evidence.
- `PRIVATE_RC_SSH_TRANSPORT_DIAGNOSTIC_GATE` result.
- `PRIVATE_RC_DB_RUNTIME_OBSERVATION_GATE_RETRY` result.
- Operator statement: a third party with Android phone can receive/test a
  config, but phone access may not be immediate.

## Decision

```text
review_go=true
gate_open_go=conditional-go-when-third-party-android-phone-is-available
gate_name=THIRD_PARTY_ANDROID_CONFIG_HANDOFF_GATE
target_vps=89.185.80.166
expected_amn2_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
handoff_model=recommended_operator_mediated_private_conf_handoff
third_party_telegram_id_required=no_for_handoff_yes_only_if_order_identity_is_required_by_execution_helper
fresh_peer_limit=1
```

## Boundary

Third-party Android test is limited to one fresh per-device `.conf` handoff.
The third party is not an admin/operator and receives no admin credentials,
Telegram token, runtime secrets, QR, `vpn://`, private key, PSK, or secret
payload in evidence.

The preferred model is operator-mediated private file handoff:

```text
private_handoff_dir=C:\Users\SooL\Documents\AMN2-PRIVATE-HANDOFF
artifact_type=.conf
artifact_count=1
artifact_location=outside_workspace
```

Telegram ID for the third party is not required for file handoff. It is only
needed if the execution helper must create an AMN2 order tied to a Telegram
identity. Unrelated old user IDs must not be reused.

## Pass criteria

Android-side safe criteria:

```text
android_import_status=passed
android_connect_status=passed
android_traffic_attempted=true
android_traffic_source=browser_or_app
payload_screenshot_shared=false
```

Server-side safe criteria:

```text
fresh_peer_found=yes
fresh_peer_limit=1
fresh_peer_expected_count_delta=1
latest_handshake_after=true
endpoint_observed_after=yes
transfer_rx_delta_bytes_gt_0=true
transfer_tx_delta_bytes_gt_0=true
public_closed_probes_after_status=passed
secret_values_printed=false
```

## Stop-lines

Stop if target/source mismatch, public probes are not closed, more than one peer
would be created, any secret-bearing config payload would be printed, unrelated
Telegram ID is used, phone is unavailable, Android import/connect/traffic fails,
or the scenario expands into Telegram live send, public exposure, service
restart, package apply, restore/import/reboot, provider rebuild or production
rollout.

## Artifacts

Review:

```text
docs/AMN2_THIRD_PARTY_ANDROID_CONFIG_HANDOFF_GATE_REVIEW.ru.md
```

Future exact gate:

```text
THIRD_PARTY_ANDROID_CONFIG_HANDOFF_GATE
```
