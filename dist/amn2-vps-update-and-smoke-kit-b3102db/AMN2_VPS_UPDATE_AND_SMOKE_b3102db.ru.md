# AMN2 VPS update/smoke kit b3102db

Дата: 2026-06-13
Статус: package-ready, live VPS apply/smoke не выполнялся в этом шаге.

## Граница gate

- Это P6-C006 package preflight artifact для текущей ветки AMN2.
- Live SSH/upload/apply/restart/smoke требует отдельный named gate.
- До открытия live gate VPS_APPLY_ENABLED остается false.
- Этот пакет не открывает public exposure, config delivery, write API, Local Agent mutations, backup/import/reboot или production peer/user mutation.

## Источник

- Repo: barakov-dot/amn2
- Branch: codex-vps-test-prep
- Commit: b3102db250da7ca9aef78ca095602187d0efc462
- Subject: Add client compatibility delivery boundary

## Артефакты

- Source zip: amn2-codex-vps-test-prep-b3102db-source.zip
- Source SHA256: 72342DB625D53AE2F6B68835A1FC4E080684A4A1E9018E791820899BB9A09778
- Apply script: amn2_apply_source_zip.sh
- Smoke script: amn2_api_loopback_smoke.sh

## Будущий live порядок после named gate

1. Upload kit directory to /root/amn2-vps-update-and-smoke-kit-b3102db on the disposable VPS.
2. Run amn2_apply_source_zip.sh only after confirming the target path and current backup/snapshot posture.
3. Keep API smoke loopback-only: AMN2_API_HOST=127.0.0.1 and VPS_APPLY_ENABLED=false.
4. Run amn2_api_loopback_smoke.sh and collect only safe evidence bundle/summary.
5. Do not publish config delivery, write API, public exposure, production peer/user mutations, or Telegram identity changes from this gate.

## После smoke

- If live smoke passes, update project status from package-ready to VPS-smoked/package head b3102db.
- If blocked, keep latest VPS-smoked/package head at 2215761 and record blocker evidence.
