# Следующий чат: AMN2 Phase 8 Prep

Дата: 2026-06-21.

## Короткий старт

```text
Продолжаем AMN2 после Phase 7 closeout.

Phase 7 status: phase8-prep-ready.
Phase 8 final status:
launch-ready-with-explicit-limitations.

Default lane: local-only/docs/tests/package-preflight unless an exact named
Phase 8 live/destructive/config gate is opened.

Do not use historical shared .conf files as release delivery artifacts.
They are diagnostic proof only.
```

## Update 2026-06-22: P8-SFINAL launch readiness freeze

`P8-SFINAL` launch readiness freeze completed on 2026-06-22. Evidence:
`research/amn2/phase-8-sfinal-launch-readiness-freeze-2026-06-22.md`.

Final safe result:

```text
phase8_final_status=launch-ready-with-explicit-limitations
private_operator_rc_launch_ready=true
phase8_launch_gate_status=closed-for-private-operator-rc-with-limitations
public_launch_status=not-approved
blocked_with_exact_remaining_blockers=false
fresh_android_phone_acceptance_source=P8-C001
fresh_zero_android_acceptance_device=P8-C003_android_projector
telegram_first_runtime_status=server-side-getme-and-non-polling-smoke-passed
telegram_live_send_status=not-performed
public_exposure_status=closed-by-default
backup_evidence_status=create-and-verify-passed
restore_import_status=not-proven
secret_payload_output_status=not-performed
```

The project is ready for a private/operator RC handoff with explicit
limitations. It is not approved for public launch.

## Update 2026-06-22: P8-C003 fresh-from-zero rehearsal passed

`P8-C003` fresh-from-zero VPS rehearsal passed on 2026-06-22. Evidence:
`research/amn2/phase-8-p8-c003-fresh-zero-rehearsal-2026-06-22.md`.

Key safe result:

```text
target_vps=89.185.80.166
amn2_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
package_sha256=7FA073E4C66C0981673061D167D525BB9BCD6DFDDAA075E15701F0C2608E2E82
fresh_install_status=passed
source_overlay_match=yes
fresh_env_db_init_status=passed
admin_telegram_ids_count_actual=2
operator_admin_pair_present=yes
loopback_web_status=passed
loopback_api_smoke_status=passed
telegram_get_me_status=passed
telegram_polling_started=false
telegram_live_send_performed=false
backup_create_status=passed
backup_verify_status=passed
backup_artifact_mode_600_verified=true
fresh_peer_public_key_fp=d0ab128d6801
fresh_android_acceptance_device=android_projector
fresh_android_phone_available=false
fresh_android_traffic_source=browser_or_app
endpoint_observed_after=yes
transfer_rx_delta_bytes=622084
transfer_tx_delta_bytes=9004751
public_3030_probe=000
public_3040_probe=000
public_80_probe=000
public_443_probe=000
secret_values_printed=false
phase8_launch_gate_status=fresh-from-zero-rehearsal-passed-awaiting-final-freeze
recommended_next_gate=P8-SFINAL launch readiness freeze
```

Important limitation: `P8-C003` Android acceptance used an Android projector
with browser/app traffic and no on-device Telegram. Android phone acceptance
remains the separate `P8-C001` evidence. The final freeze must state this
limitation explicitly.

## Update 2026-06-21: P8-S002 + P8-C003 proposal prepared

`P8-S002` fresh-from-zero preflight ledger is complete as docs-only evidence.
`P8-C003` destructive gate proposal is prepared but not opened. `P8-C003`
readiness confirmation is now `go-with-limitation`. Evidence:

- `research/amn2/phase-8-p8-s002-fresh-from-zero-preflight-ledger-2026-06-21.md`
- `research/amn2/phase-8-p8-c003-destructive-gate-proposal-2026-06-21.md`
- `research/amn2/phase-8-p8-c003-readiness-confirmation-2026-06-21.md`

Current status remains:

```text
phase8_launch_gate_status=blocked-until-fresh-from-zero-vps-rehearsal
operator_explicit_destructive_gate_opened=false
p8_c003_readiness_status=go-with-limitation
telegram_token_available_privately=yes
web_admin_credentials_strategy=new_private_credentials
safe_env_strategy=generate_fresh_plus_private_inputs
android_test_device_type=android_projector
android_phone_available=no
android_projector_can_generate_browser_or_app_traffic=yes
next_action=operator_review_or_open_exact_P8_C003_gate
```

If the operator chooses to open `P8-C003`, use the copy/paste gate text from
the proposal. Do not treat this handoff, readiness confirmation or proposal as
permission to wipe or install.

## Update 2026-06-21: P8-C002 passed for AMN2 187949b

`P8-C002` package/current-head smoke and compatible AWG defaults persistence
passed on 2026-06-21. Evidence:
`research/amn2/phase-8-p8-c002-187949b-package-apply-smoke-2026-06-21.md`.

Key safe result:

```text
amn2_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
package_sha256=7FA073E4C66C0981673061D167D525BB9BCD6DFDDAA075E15701F0C2608E2E82
source_overlay_match=yes
settings_client_awg_compatible=yes
loopback_web_runtime_status=passed
api_smoke_status=passed
telegram_get_me_status=passed
telegram_live_send_performed=false
backup_create_status=passed
backup_verify_status=passed
backup_artifact_mode=600
public_3030_probe=000
public_3040_probe=000
public_80_probe=000
public_443_probe=000
secret_values_printed=false
```

Latest VPS-applied/package-smoked AMN2 head is now `187949b`. The remaining
launch blocker is fresh-from-zero reproducibility, not Android acceptance or
current-head package smoke.

## Update 2026-06-21: P8-C001 passed with reconnect sanity

`P8-C001` fresh per-device Android config acceptance passed functionally on
2026-06-21. Evidence:
`research/amn2/phase-8-p8-c001-fresh-android-config-acceptance-2026-06-21.md`.

Key safe result:

```text
fresh_peer_public_key_fp=594ba96e4f90
android_import_status=passed
android_connect_status=passed
android_traffic_status=passed
endpoint_observed=yes
latest_handshake_age_s=45
transfer_rx_bytes_before=191124
transfer_tx_bytes_before=1487651
transfer_rx_bytes_after=520504
transfer_tx_bytes_after=4609467
reconnect_sanity_status=passed
reconnect_latest_handshake_age_s=18
reconnect_transfer_rx_bytes_before=5136612
reconnect_transfer_tx_bytes_before=229495265
reconnect_transfer_rx_bytes_after=5318584
reconnect_transfer_tx_bytes_after=230151167
payload_output_status=not_performed
public_exposure_status=not_performed
telegram_live_send_status=not_performed
```

Important limitation: the successful file used live-compatible AWG client
parameters rendered for existing fresh device `2`; the normal package/runtime
delivery path later persisted those compatible defaults in `P8-C002`.

## Источник правды

- AMN3/evidence workspace:
  `C:\Users\SooL\Documents\VPS-OPS-LAB`, branch `master`, verify with
  `git log -1`.
- AMN2 current-fixes worktree:
  `C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-phase7-current`,
  branch `codex/phase7-current-fixes`.
- AMN2 source head for current local policy:
  `187949b Persist Android-compatible AWG defaults`.
- AMN2 latest VPS-applied/package-smoked head:
  `187949b Persist Android-compatible AWG defaults`.
- Current disposable VPS:
  `89.185.80.166`.

## Последняя важная правда Phase 7

- `P7-C011f2` confirmed the live dataplane is working:
  - `awg0` listens on UDP `30001`;
  - live server public key fingerprint is `0bdc326c396a`;
  - live peers are present;
  - matched old peer `a6a551084fad` showed fresh handshake and growing transfer
    counters;
  - operator observed Android connecting instantly.
- Old matched configs from `C:\temp` are diagnostic proof only:
  - `Neobyatnaya-AMNZ.conf` matched peer `a6a551084fad`;
  - `Neobyatnaya-AMNZ-2.conf` matched peer `2ed2b69a2f79`.
- Do not paste or publish `.conf`, QR, `vpn://`, private keys, PSK, tokens or
  screenshots containing payloads.
- Android AmneziaWG is the intended mobile candidate. `P8-C001` now provides
  functional fresh per-device Android acceptance, and `P8-C002` persisted the
  compatible AWG defaults in the normal package/runtime delivery path.
- QR and full `vpn://` are not release-primary mobile delivery paths.
- iOS DefaultVPN is experimental/unreliable.
- Windows desktop is accepted by operator observation, but this does not close
  mobile launch acceptance.

## Главный Phase 8 выбор

Phase 8 freeze is complete. The next recommended step is docs/operator handoff,
not another live gate:

```text
private/operator RC handoff with explicit limitations
```

Already prepared/completed docs:

- `P8-S002` preflight ledger with criticality/size grouping, package inputs,
  readiness checklist, pass criteria and stop-lines;
- `P8-C003` destructive gate proposal with copy/paste operator text and
  confirmation strings;
- `P8-C003` readiness confirmation with Android projector limitation accepted.
- `P8-C003` fresh-from-zero rehearsal evidence with projector acceptance and
  closed public probes.

`P8-SFINAL` decided:

```text
phase8_final_status=launch-ready-with-explicit-limitations
```

If the operator wants actual production sends, public exposure, restore/import,
or broader rollout, open a new exact named gate for that action.

## Stop lines

Do not open without exact named gate:

- destructive VPS/provider actions;
- public exposure, Cloudflare, ngrok, reverse proxy, TLS, firewall/listener
  changes;
- config delivery secrets, QR, `.conf`, `vpn://`, private key or PSK output;
- Telegram live send/profile/media mutation;
- write/install execution;
- backup restore/import/reboot;
- production user/peer mutation.

## First read in Phase 8

Read:

- `research/amn2/phase-8-p8-c003-readiness-confirmation-2026-06-21.md`
- `research/amn2/phase-8-p8-s002-fresh-from-zero-preflight-ledger-2026-06-21.md`
- `research/amn2/phase-8-p8-c003-destructive-gate-proposal-2026-06-21.md`
- `research/amn2/phase-8-p8-c002-187949b-package-apply-smoke-2026-06-21.md`
- `research/amn2/phase-8-p8-c001-fresh-android-config-acceptance-2026-06-21.md`
- `research/amn2/phase-7-mobile-dataplane-closeout-c011f2-2026-06-21.md`
- `research/amn2/phase-7-android-acceptance-contract-471bca8-2026-06-21.md`
- `research/amn2/phase-7-state-drift-clean-worktree-2026-06-21.md`
- `docs/PHASE_7_RELEASE_CANDIDATE_PLAN.ru.md`
- `docs/AMN2_PHASE_7_EVIDENCE_INDEX.ru.md`
- `docs/PROJECT_STATUS_CURRENT.ru.md`
- `docs/PROJECT_CONTEXT_IMPORT.ru.md`
