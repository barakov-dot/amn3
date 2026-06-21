# Phase 7 Android acceptance contract after upstream-refresh

Date: 2026-06-21.

Status: `completed-local-android-acceptance-contract-no-live-action`.

AMN2 worktree:
`C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-phase7-current`.

AMN2 base/head:
`471bca8 Downgrade DefaultVPN iOS compatibility`.

Scope: local-only code/tests after manual upstream-refresh and mobile VPN
acceptance debugging. No live VPS/SSH command, package upload/apply, service
restart, public exposure, config delivery, Telegram action, restore/import/
reboot, provider mutation, write execution or secret-bearing output was
performed.

## Reason

After real-device testing, QR and full `vpn://` import-link UX cannot be
release-primary for mobile. DefaultVPN iOS is already experimental/unreliable.
Android AmneziaWG remains the intended mobile candidate, but it is not accepted
until a real device passes `.conf` import, tunnel connect and traffic checks.

## AMN2 Changes

Changed:

- `app/vpn/client_compatibility.py`
- `app/services/integration_status.py`
- `tests/vpn/test_client_compatibility.py`
- `tests/services/test_phase7_client_compatibility_boundary.py`

The compatibility matrix now exposes:

```text
android.amneziawg.acceptance_status=pending_real_device_acceptance
android.amneziawg.release_primary_allowed=false
desktop.windows.acceptance_status=operator_observed_passed
desktop.windows.release_primary_allowed=true
qr_release_primary_allowed=false
vpn_import_link_release_primary_allowed=false
phase8_mobile_gate_status=blocked_android_real_device_acceptance_pending
```

Android AmneziaWG remains a supported candidate, but `.conf` is the only
recommended artifact. QR and `vpn://` are not release-primary and must remain
diagnostic/fallback until proven on the target client.

## Verification

Focused tests:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-runtime-toolchain-standardization\.venv\Scripts\python.exe -m pytest tests\services\test_phase7_client_compatibility_boundary.py tests\vpn\test_client_compatibility.py -q
result: 9 passed in 0.09s
```

Syntax verification:

```text
python -m py_compile app\vpn\client_compatibility.py app\services\integration_status.py tests\vpn\test_client_compatibility.py tests\services\test_phase7_client_compatibility_boundary.py
result: passed
```

The current default `python` and the bundled Codex runtime did not contain
`pytest`; the focused pytest verification used an existing AMN2 virtualenv from
the local workspace.

## Release Posture

Phase 8 remains blocked for mobile launch until Android AmneziaWG real-device
acceptance passes or the operator explicitly narrows the launch policy to a
desktop-first/private lane.

Recommended next exact gate, if live diagnostics are needed:

```text
P7-C011f live AWG handshake observation
```

This gate is read-only and should be used to distinguish "server sees the
client handshake" from "device/UDP/client never reaches the live peer".
