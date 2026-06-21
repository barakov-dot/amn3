# Phase 8 P8-C003 destructive gate proposal

Date: 2026-06-21.

Status: `proposed-not-opened-destructive-gate-docs-only-no-live-action`.

Scope: proposal for the future exact named `P8-C003 fresh-from-zero VPS
rehearsal gate`. No live VPS/SSH command, package upload, destructive clean
install, source apply, service restart, public exposure, config delivery,
Telegram API call/live send, write/install execution, backup restore/import/
reboot, provider mutation, production peer/user mutation or secret-bearing
output was performed by this proposal.

## Proposed Exact Gate

Gate name:

```text
P8-C003 fresh-from-zero VPS rehearsal gate
```

Target:

```text
target_vps=89.185.80.166
target_role=disposable
amn2_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
package=dist/amn2-vps-update-and-smoke-kit-187949b.zip
package_sha256=7FA073E4C66C0981673061D167D525BB9BCD6DFDDAA075E15701F0C2608E2E82
```

Goal:

```text
prove fresh-from-zero private/operator RC reproducibility using current AMN2
187949b package/runtime path, Telegram-first delivery posture, fresh Android
per-device config acceptance, backup evidence and closed public exposure.
```

## Readiness Confirmation

Readiness confirmation was completed after this proposal was drafted. Evidence:
`research/amn2/phase-8-p8-c003-readiness-confirmation-2026-06-21.md`.

```text
telegram_token_available_privately=yes
web_admin_credentials_strategy=new_private_credentials
safe_env_strategy=generate_fresh_plus_private_inputs
private_handoff_destination_outside_workspace=yes
private_handoff_path=C:\Users\SooL\Documents\AMN2-PRIVATE-HANDOFF
android_phone_available=no
android_projector_available=yes
android_projector_telegram_available=no
android_projector_telegram_required=false
android_projector_can_generate_browser_or_app_traffic=yes
android_test_device_available=yes-with-limitation
android_test_device_type=android_projector
limitation_accepted=yes
p8_c003_readiness_status=go-with-limitation
```

If the Android projector is used during `P8-C003`, the final evidence and
`P8-SFINAL` freeze must state that fresh-from-zero Android acceptance used an
Android projector with browser/app traffic, while prior Android phone
acceptance remains the separate `P8-C001` evidence.

## Copy/Paste Operator Gate Text

The operator can open the gate in a future chat or prompt with this exact
message:

```text
Open exact gate P8-C003 fresh-from-zero VPS rehearsal.

Target VPS: 89.185.80.166.
I confirm this VPS is disposable and destructive clean/fresh install is allowed
inside this gate only.

Use AMN2 head:
187949bffb927a0a6d6c1f260fc0bb9ebb972447

Use package:
dist/amn2-vps-update-and-smoke-kit-187949b.zip

Expected package SHA256:
7FA073E4C66C0981673061D167D525BB9BCD6DFDDAA075E15701F0C2608E2E82

Private inputs readiness:
- Telegram token available privately.
- Web admin credentials strategy: new private credentials.
- Safe env strategy: generate fresh plus private inputs.
- Private handoff path: C:\Users\SooL\Documents\AMN2-PRIVATE-HANDOFF.

Android acceptance limitation:
- Android phone is not available for this gate.
- Android projector is available.
- Android projector has no Telegram, and Telegram on-device is not required.
- Browser/app traffic on Android projector is available and accepted for the
  fresh Android traffic observation.

No public exposure, no Telegram live send/profile/media mutation, no restore/
import, no config payload output, no QR/vpn:// output, no private key/PSK/token
output.

Stop at first failed gate and report the exact blocker.
```

Recommended confirmation strings for any future helper:

```text
P8_C003_FRESH_FROM_ZERO_DESTRUCTIVE_REHEARSAL_CONFIRMED
TARGET_89_185_80_166_DISPOSABLE_WIPE_ALLOWED
APPLY_AMN2_187949B_PACKAGE_AND_SMOKE
NO_PUBLIC_EXPOSURE_NO_PAYLOAD_OUTPUT_CONFIRMED
STOP_AT_FIRST_FAILED_GATE_CONFIRMED
ANDROID_PROJECTOR_LIMITATION_ACCEPTED
```

If a private destination is needed for a fresh Android `.conf`, use a local
absolute path outside `C:\Users\SooL\Documents\VPS-OPS-LAB`, for example:

```text
C:\Users\SooL\Documents\AMN2-PRIVATE-HANDOFF
```

Do not paste file contents, QR, `vpn://`, keys, PSK, tokens or screenshots
containing payload into chat/evidence.

## Allowed Inside P8-C003

Only after the exact gate is opened, the following actions are allowed:

- destructive clean/fresh install on target VPS `89.185.80.166`;
- package upload and SHA verification for `187949b`;
- source overlay apply to the fresh AMN2 runtime;
- fresh safe `.env` and DB initialization using private operator inputs;
- loopback web runtime start/restart as needed;
- loopback web login smoke;
- loopback API smoke;
- Telegram `getMe` and non-polling dispatcher/user-flow smoke;
- create exactly one fresh Android per-device config through the normal AMN2
  access/dataplane path;
- private `.conf` handoff to an operator-controlled local directory outside
  the workspace;
- read-only server-side AWG observation of the fresh peer fingerprint,
  handshake and transfer counters;
- use the Android projector for acceptance if an Android phone remains
  unavailable, with browser/app traffic as the traffic generator and the
  limitation recorded in evidence;
- backup create and verify;
- public external probes confirming `3030`, `3040`, `80` and `443` remain
  closed;
- safe evidence updates with no secret-bearing payload.

## Not Allowed Inside P8-C003

These remain out of scope unless a separate exact gate is opened:

- public web/admin exposure;
- public API exposure;
- Cloudflare, ngrok, reverse proxy, TLS, DNS or firewall/listener opening;
- Telegram live send, bot polling, profile/media mutation or media upload;
- outputting `.conf`, QR, `vpn://`, private key, PSK, token or secret-bearing
  screenshots;
- backup restore/import;
- archive import/apply;
- provider actions beyond the explicitly confirmed disposable VPS destructive
  rehearsal target;
- production user/peer mutation beyond the one fresh Android test peer created
  for acceptance;
- upstream/GPL code/template/workflow copying.

If a reboot becomes necessary, stop and request an explicit sub-confirmation
before rebooting.

## Proposed Execution Order

1. **Boundary print**

   Record the opened gate, target VPS, AMN2 head, package SHA, forbidden
   outputs/actions and stop-lines before doing any live command.

2. **Pre-destructive snapshot**

   Record safe current-state facts only: reachable SSH target, OS identity,
   existing `/opt/amn2` presence if any, public probes closed, and no payload.

3. **Destructive fresh install**

   Clean the disposable target into a fresh AMN2-ready state. Do not restore old
   archives or import old configs.

4. **Fresh safe env/DB initialization**

   Initialize `.env`, `servers.yml`, DB and admin/runtime settings using private
   operator inputs. Do not print secret values.

5. **Package verify/apply**

   Upload the `187949b` package, verify SHA, extract, apply tracked source
   overlay and confirm `source_overlay_match=yes`.

6. **Runtime smoke**

   Run loopback web login and loopback API smoke. Confirm no public listener is
   opened.

7. **Telegram smoke**

   Run Telegram `getMe` and non-polling dispatcher/user-flow smoke only. Do not
   start polling or live-send messages.

8. **Fresh Android acceptance**

   Create exactly one fresh Android peer/config through AMN2. Copy exactly one
   `.conf` privately outside the workspace. Android operator imports it into
   AmneziaWG, connects and generates traffic. Server-side observation records
   only peer fingerprint, handshake age and counter growth.

9. **Backup evidence**

   Create and verify a backup artifact. Record basename, bytes, SHA and mode
   `600`; do not download or print archive contents.

10. **Closed exposure proof**

    Probe public `3030`, `3040`, `80` and `443`; expected result is `000` for
    each.

11. **Final guard and evidence**

    Record pass/fail status, exact blocker if failed, or move to `P8-SFINAL` if
    passed.

## Failure Classes

Use exactly one primary class if the gate fails:

```text
target_not_confirmed_disposable
ssh_or_reachability_failed
destructive_clean_install_failed
safe_env_db_init_failed
package_sha_mismatch
source_overlay_mismatch
loopback_web_failed
loopback_api_failed
telegram_getme_failed
telegram_polling_or_live_send_unexpected
fresh_android_peer_create_failed
fresh_android_private_handoff_failed
fresh_android_import_failed
fresh_android_connect_failed
fresh_android_traffic_or_counter_failed
fresh_android_projector_limitation_not_recorded
backup_create_failed
backup_verify_failed
backup_mode_failed
public_probe_open_unexpectedly
secret_payload_output_risk
operator_android_device_unavailable
```

## Pass Result Contract

If `P8-C003` passes, evidence should end with:

```text
p8_c003_status=passed-fresh-from-zero-vps-rehearsal
phase8_launch_gate_status=fresh-from-zero-rehearsal-passed-awaiting-final-freeze
private_operator_rc_distance_to_launch=97_percent
fresh_android_acceptance_device=android_projector
fresh_android_phone_available=false
fresh_android_traffic_source=browser_or_app
fresh_android_projector_limitation_recorded=true
recommended_next_gate=P8-SFINAL launch readiness freeze
```

## Fail Result Contract

If `P8-C003` fails, evidence should end with:

```text
p8_c003_status=failed
phase8_launch_gate_status=blocked-until-p8-c003-failure-class-resolved
primary_failure_class=<one class from Failure Classes>
recommended_next_gate=<exact blocker-specific gate>
```

## Result

This proposal is ready for operator review. It does not open the destructive
gate. The launch status remains:

```text
phase8_launch_gate_status=blocked-until-fresh-from-zero-vps-rehearsal
```
