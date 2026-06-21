# Следующий чат: AMN2 Phase 8 Prep

Дата: 2026-06-21.

## Короткий старт

```text
Продолжаем AMN2 после Phase 7 closeout.

Phase 7 status: phase8-prep-ready.
Phase 8 launch gate status:
blocked-until-fresh-from-zero-vps-rehearsal.

Default lane: local-only/docs/tests/package-preflight unless an exact named
Phase 8 live/destructive/config gate is opened.

Do not use historical shared .conf files as release delivery artifacts.
They are diagnostic proof only.
```

## Update 2026-06-21: P8-S002 + P8-C003 proposal prepared

`P8-S002` fresh-from-zero preflight ledger is complete as docs-only evidence.
`P8-C003` destructive gate proposal is prepared but not opened. Evidence:

- `research/amn2/phase-8-p8-s002-fresh-from-zero-preflight-ledger-2026-06-21.md`
- `research/amn2/phase-8-p8-c003-destructive-gate-proposal-2026-06-21.md`

Current status remains:

```text
phase8_launch_gate_status=blocked-until-fresh-from-zero-vps-rehearsal
operator_explicit_destructive_gate_opened=false
next_action=operator_review_or_open_exact_P8_C003_gate
```

If the operator chooses to open `P8-C003`, use the copy/paste gate text from
the proposal. Do not treat this handoff or proposal as permission to wipe or
install.

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

Следующий exact gate:

```text
P8-C003 fresh-from-zero VPS rehearsal gate
```

Prepared docs:

- `P8-S002` preflight ledger with criticality/size grouping, package inputs,
  readiness checklist, pass criteria and stop-lines;
- `P8-C003` destructive gate proposal with copy/paste operator text and
  confirmation strings.

Suggested scope:

- destructive clean/fresh install on the disposable VPS;
- initialize fresh safe env/DB;
- apply/package current selected AMN2 head only under this exact gate;
- loopback web/API smoke;
- Telegram getMe/non-polling smoke;
- backup create+verify;
- external public probes remain closed;
- one fresh Android per-device config acceptance;
- no public web/API exposure;
- no Telegram profile/media mutation;
- no payload output in evidence.

After that, if passed:

```text
P8-SFINAL launch readiness freeze
```

`P8-SFINAL` should decide one final status: `private/operator RC launch-ready`,
`launch-ready-with-explicit-limitations`, or
`blocked-with-exact-remaining-blockers`.

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
