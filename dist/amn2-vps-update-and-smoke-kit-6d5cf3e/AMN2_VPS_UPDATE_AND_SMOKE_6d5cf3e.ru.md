# AMN2 VPS update/smoke kit 6d5cf3e

Date: 2026-06-20
Status: package-ready-for-opened-P7-C010c-live-gate. Public exposure, restore/import/reboot, provider mutation, write execution and production user mutation are not opened.

## Gate Boundary

- This package is built for AMN2 Phase 7 `P7-C010c` package/apply plus Mobile Telegram UX retest gate.
- Allowed inside the named gate only: upload package, verify SHA256, apply tracked source overlay to `/opt/amn2`, restart loopback web runtime, run loopback API smoke, run Telegram getMe/non-polling smoke, send operator-only test payload to the operator test chat, create+verify backup evidence if included by the smoke helper, and confirm external probes stay closed.
- Not allowed: public web/API exposure, restore/import/reboot/download, provider mutation, write execution/installer executor, production user mutation outside the test scenario, Local Agent mutation, Telegram profile/media mutation, or secret-bearing evidence.

## Source

- Repo: barakov-dot/amn2
- Branch: codex-vps-test-prep
- Commit: 6d5cf3ea929f26b6b352ad341bff1dd4bd5a8da5
- Subject: Make Telegram config delivery conf-first
- Previous VPS smoked head: c9587332d425583ed627899d7fa950756b64c4dc

## Artifacts

- Source zip: `amn2-codex-vps-test-prep-6d5cf3e-source.zip`
- Source SHA256: `19D4F480F740972B124FAC64E9A335C9753D5DCDB9FBC9C84D9BB3923B96EDA4`
- Apply script: `amn2_apply_source_zip.sh`
- Smoke script: `amn2_api_loopback_smoke.sh`

## Mobile UX Retest Focus

- `.conf` is the primary install path.
- QR is for scanners inside compatible VPN clients, not a promise that the phone camera will open the VPN app.
- `vpn://` is a fallback/convenience channel; full config links may be too long for Telegram one-tap copy.
- iPhone DefaultVPN first-connect should be retested with attempt count recorded safely.

## Evidence Hygiene

Do not print or paste raw Telegram tokens, API tokens, Authorization headers, cookies, `.env`, `servers.yml`, DB rows, configs, QR, `vpn://` links, private keys, PSK, backup contents, or secret-bearing logs.
