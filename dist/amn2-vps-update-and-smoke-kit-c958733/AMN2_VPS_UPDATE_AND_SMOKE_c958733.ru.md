# AMN2 VPS update/smoke kit c958733

Date: 2026-06-20
Status: package-ready-for-opened-P7-C009-live-gate. Public exposure/config delivery/write execution/restore/import/reboot/provider mutation/Telegram live send are not opened.

## Gate Boundary

- This package is built for AMN2 Phase 7 P7-C009 c958733 package apply + loopback/Telegram/backup smoke gate.
- Allowed inside the named gate only: upload package, verify SHA256, apply tracked source overlay to /opt/amn2, restart loopback web runtime, run loopback API smoke, run Telegram getMe plus non-polling dispatcher/user-flow surface smoke, create+verify backup evidence, and confirm external probes stay closed.
- Not allowed: public exposure, config delivery payload output, write execution/installer executor, restore/import/reboot/download, provider mutation, Local Agent mutation, Telegram polling/live send/profile/media mutation, or secret-bearing evidence.

## Source

- Repo: barakov-dot/amn2
- Branch: codex-vps-test-prep
- Commit: c9587332d425583ed627899d7fa950756b64c4dc
- Subject: Harden security-sensitive operations
- Previous VPS smoked head: 55012958ff6b8338254f3f68dfe6779f4bc56f5d

## Artifacts

- Source zip: amn2-codex-vps-test-prep-c958733-source.zip
- Source SHA256: E0F2F823CF4E29B52404E634BA11961B3C2B85604C04498CC3D752DD5DAB6E0B
- Apply script: amn2_apply_source_zip.sh
- Smoke script: amn2_api_loopback_smoke.sh

## Evidence Hygiene

Do not print or paste raw Telegram tokens, API tokens, Authorization headers, cookies, .env, servers.yml, DB rows, configs, QR, vpn:// links, private keys, PSK, backup contents, or secret-bearing logs.
