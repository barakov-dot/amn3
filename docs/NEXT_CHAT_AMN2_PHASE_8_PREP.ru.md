# Следующий чат: AMN2 Phase 8 Prep

Дата: 2026-06-21.

## Короткий старт

```text
Продолжаем AMN2 после Phase 7 closeout.

Phase 7 status: phase8-prep-ready.
Phase 8 launch gate status:
blocked-until-fresh-per-device-android-config-acceptance.

Default lane: local-only/docs/tests/package-preflight unless an exact named
Phase 8 live/destructive/config gate is opened.

Do not use historical shared .conf files as release delivery artifacts.
They are diagnostic proof only.
```

## Источник правды

- AMN3/evidence workspace:
  `C:\Users\SooL\Documents\VPS-OPS-LAB`, branch `master`, verify with
  `git log -1`.
- AMN2 current-fixes worktree:
  `C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-phase7-current`,
  branch `codex/phase7-current-fixes`.
- AMN2 source head for current local policy:
  `4d22ff2 Gate Phase 8 on Android acceptance`.
- AMN2 latest VPS-applied/package-smoked head:
  `6d5cf3e Make Telegram config delivery conf-first`, until a new exact
  package/apply gate is opened.
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
- Android AmneziaWG is the intended mobile candidate, but AMN2 now marks it
  `pending_real_device_acceptance` and `release_primary_allowed=false` until a
  fresh per-device config passes.
- QR and full `vpn://` are not release-primary mobile delivery paths.
- iOS DefaultVPN is experimental/unreliable.
- Windows desktop is accepted by operator observation, but this does not close
  mobile launch acceptance.

## Главный Phase 8 выбор

Выбрать один exact gate:

```text
P8-C001 fresh per-device Android config acceptance gate
```

Suggested scope:

- create or add one fresh Android peer/config through AMN2/dataplane path;
- private operator handoff only;
- Android AmneziaWG import/connect/traffic acceptance;
- no public web/API exposure;
- no Telegram profile/media mutation;
- no payload output in evidence.

Alternative exact gate:

```text
P8-C000 fresh-from-zero VPS launch rehearsal gate
```

Suggested scope:

- destructive clean/fresh install on the disposable VPS;
- package/apply current AMN2 head;
- loopback web/API smoke;
- Telegram getMe/non-polling smoke if needed;
- create one fresh per-device Android config;
- Android acceptance;
- backup create+verify;
- external public probes closed unless public exposure is separately opened.

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

- `research/amn2/phase-7-mobile-dataplane-closeout-c011f2-2026-06-21.md`
- `research/amn2/phase-7-android-acceptance-contract-471bca8-2026-06-21.md`
- `research/amn2/phase-7-state-drift-clean-worktree-2026-06-21.md`
- `docs/PHASE_7_RELEASE_CANDIDATE_PLAN.ru.md`
- `docs/AMN2_PHASE_7_EVIDENCE_INDEX.ru.md`
- `docs/PROJECT_STATUS_CURRENT.ru.md`
- `docs/PROJECT_CONTEXT_IMPORT.ru.md`
