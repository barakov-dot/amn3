# AMN2 VPS update/smoke kit c46f664

Дата: 2026-06-13
Статус: package-ready, live VPS apply/smoke не выполнялся в этом шаге.

## Граница gate

- Это P6-C008 local package/preflight artifact для текущей ветки AMN2.
- Live SSH/upload/apply/restart/smoke не открыт и требует отдельный named gate P6-C009.
- До открытия live gate VPS_APPLY_ENABLED=false остается обязательным.
- Этот пакет не открывает public exposure, config delivery, write API, Local Agent mutations, backup/import/reboot, destructive cleanup/reinstall или production peer/user mutation.

## Источник

- Repo: barakov-dot/amn2
- Branch: codex-vps-test-prep
- Commit: c46f664762d7774756b88db8d4e1ebc038b20bb5
- Subject: Add public taxonomy cleanup checklist
- Previous latest VPS-smoked/package head: b3102db Add client compatibility delivery boundary

## Артефакты

- Source zip: amn2-codex-vps-test-prep-c46f664-source.zip
- Source SHA256: 5A92EA9BD5B60626F120B5367A02EDDCB742ECF5E6C4FCB8444151BFEB18B248
- Apply script: amn2_apply_source_zip.sh
- Smoke script: amn2_api_loopback_smoke.sh

## Current-head smoke plan после отдельного named gate

1. Operator opens the live gate by exact phrase, for example:
   Открываю P6-C009 live apply/smoke gate для c46f664 на текущем disposable VPS 89.185.80.166.
2. Confirm target is still the disposable VPS 89.185.80.166 and the current latest VPS-smoked package is still 3102db.
3. Upload only this kit and checksum to the target; verify checksum before extract.
4. Extract to /root/amn2-vps-update-and-smoke-kit-c46f664 and inspect the five expected files.
5. Run mn2_apply_source_zip.sh only after confirming target path and stop criteria.
6. Keep API smoke loopback-only: AMN2_API_HOST=127.0.0.1, target server name local, and VPS_APPLY_ENABLED=false.
7. Run mn2_api_loopback_smoke.sh and collect only safe summary/evidence.
8. Verify web/bot runtime status only inside the named gate; do not open public listeners.
9. If smoke passes, record c46f664 as latest VPS-smoked/package head. If blocked, keep 3102db as latest VPS-smoked/package head and record blocker evidence.

## Named live gate checklist

Before P6-C009 can run, record:

- exact operator phrase naming P6-C009, commit c46f664, and target 89.185.80.166;
- current package SHA256 and source SHA256 from this kit;
- stop criteria for checksum mismatch, source overlay failure, import failure, listener drift, web/bot inactive state, or smoke failure;
- confirmation that no public exposure/config delivery/write API/Local Agent mutation/backup-import/destructive cleanup/Telegram identity mutation is being opened;
- safe evidence destination and redaction rule: no raw tokens, no config material, no peer keys, no endpoint secrets.

## Не выполнять этим пакетом

- live VPS command без P6-C009;
- SSH command без P6-C009;
- package upload/apply on VPS без P6-C009;
- service restart/deploy без P6-C009;
- public exposure;
- config delivery, .conf, QR или pn:// delivery;
- write API;
- Local Agent mutation;
- backup/import/reboot;
- production peer/user mutation;
- destructive provider/VPS action;
- Telegram token use, live bot send или Telegram identity/profile mutation;
- secret-bearing evidence publication;
- upstream/GPL code copy.