# AMN2 VPS update/smoke kit 187949b

Date: 2026-06-21.

Status: package-ready-for-opened-P8-C002-live-gate.

## Gate Boundary

- This package is built for AMN2 Phase 8 `P8-C002 package/current-head smoke
  and compatible AWG defaults persistence gate`.
- Allowed inside this exact gate only: upload package, verify SHA256, apply the
  tracked source overlay to `/opt/amn2`, preserve existing `.env`, `servers.yml`,
  `data`, `venv`, logs and backups, install the editable package, run loopback
  web/API smoke, run Telegram `getMe`/non-polling smoke, create+verify backup
  evidence, verify external public probes stay closed, and verify normal
  AMN2 runtime defaults now render the Android-accepted AWG parameters.
- Not allowed: public web/API exposure, restore/import/reboot/download,
  provider mutation, write/install execution outside this package apply,
  production peer/user mutation, Local Agent mutation, Telegram live send,
  Telegram profile/media mutation, config payload output, QR output,
  `vpn://` output or secret-bearing evidence.

## Source

- Repo: `barakov-dot/amn2`
- Branch: `codex/phase7-current-fixes`
- Commit: `187949bffb927a0a6d6c1f260fc0bb9ebb972447`
  (`Persist Android-compatible AWG defaults`)
- Previous VPS-smoked/package head: `6d5cf3e`

## Artifacts

- Source zip: `amn2-codex-phase7-current-fixes-187949b-source.zip`
- Source SHA256:
  `649EF03461555B13D8C4AF59709CEEC49F2300C395F69DCA982DF15732409313`
- Apply script: `amn2_apply_source_zip.sh`
- Smoke script: `amn2_api_loopback_smoke.sh`

## P8-C002 Focus

- `ClientConfigDefaults()` and `Settings().client_config_defaults` use the
  Android-accepted AWG parameters from P8-C001:
  `Jc=3`, `Jmin=10`, `Jmax=30`, `S1=15`, `S2=18`, `S3=20`, `S4=23`,
  `H1=1020325451`, `H2=3288052141`, `H3=1766607858`, `H4=2528465083`.
- `.env.example`, `deploy/examples/.env.production.example` and operator docs
  now show those values.
- Existing target `.env` is preserved by the apply script. If the target `.env`
  explicitly contains old `CLIENT_AWG_*` values, the P8-C002 helper must update
  only those non-secret compatible defaults under this exact gate and record
  safe key/value evidence without printing secrets.

## Evidence Hygiene

Do not print or paste raw Telegram tokens, API tokens, Authorization headers,
cookies, `.env`, `servers.yml`, DB rows, configs, QR, `vpn://` links, private
keys, PSK, backup contents or secret-bearing logs.
