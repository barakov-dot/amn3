# AMN2 VPS update/smoke kit 0de7a77

Дата: 2026-06-14
Статус: package-ready-not-vps-smoked. Live VPS apply/smoke этим шагом не выполнялся.

## Граница gate

- Это local package/preflight artifact для текущей ветки AMN2.
- Live SSH/upload/apply/restart/smoke не открыт и требует отдельный named live gate.
- До открытия live gate `VPS_APPLY_ENABLED=false` остается обязательным.
- Этот пакет не открывает public exposure, config delivery, write API, Local
  Agent mutations, backup/import/reboot, destructive cleanup/reinstall или
  production peer/user mutation.

## Источник

- Repo: barakov-dot/amn2
- Branch: codex-vps-test-prep
- Commit: 0de7a77f3eb09d23dc2785d402bc51c2b5eb7835
- Subject: Polish fresh installer preflight planning
- Previous latest VPS-smoked/package head: c46f664 Add public taxonomy cleanup checklist

## Артефакты

- Source zip: `amn2-codex-vps-test-prep-0de7a77-source.zip`
- Source SHA256: `B8D0E7E2A40051AB38EDF09947977DFE5F7197CEEEE87D1523734D3C1C505295`
- Apply script: `amn2_apply_source_zip.sh`
- Smoke script: `amn2_api_loopback_smoke.sh`

## Current-Head Smoke Plan После Отдельного Named Gate

1. Operator opens a separate live gate by exact phrase, for example:
   `Открываю P6-C010 live apply/smoke gate для 0de7a77 на текущем disposable VPS 89.185.80.166.`
2. Confirm target is still the disposable VPS `89.185.80.166` and the current
   latest VPS-smoked package is still `c46f664`.
3. Upload only this kit and checksum to the target; verify checksum before extract.
4. Extract to `/root/amn2-vps-update-and-smoke-kit-0de7a77` and inspect the five expected files.
5. Run `amn2_apply_source_zip.sh` only after confirming target path and stop criteria.
6. Keep API smoke loopback-only: `AMN2_API_HOST=127.0.0.1`, target server name
   `local`, and `VPS_APPLY_ENABLED=false`.
7. Run `amn2_api_loopback_smoke.sh` and collect only safe summary/evidence.
8. Verify web/bot runtime status only inside the named gate; do not open public listeners.
9. If smoke passes, record `0de7a77` as latest VPS-smoked/package head. If
   blocked, keep `c46f664` as latest VPS-smoked/package head and record blocker evidence.

## Named Live Gate Checklist

Before live apply/smoke can run, record:

- exact operator phrase naming the live gate, commit `0de7a77`, and target `89.185.80.166`;
- current package SHA256 and source SHA256 from this kit;
- stop criteria for checksum mismatch, source overlay failure, import failure,
  listener drift, web/bot inactive state, or smoke failure;
- confirmation that no public exposure/config delivery/write API/Local Agent
  mutation/backup-import/destructive cleanup/Telegram identity mutation is being opened;
- safe evidence destination and redaction rule: no raw tokens, no config
  material, no peer keys, no endpoint secrets.

## Не Выполнять Этим Пакетом

- live VPS command без отдельного named live gate;
- SSH command без отдельного named live gate;
- package upload/apply on VPS без отдельного named live gate;
- service restart/deploy без отдельного named live gate;
- public exposure;
- config delivery, `.conf`, QR или `vpn://` delivery;
- write API;
- Local Agent mutation;
- backup/import/reboot;
- production peer/user mutation;
- destructive provider/VPS action;
- Telegram token use, live bot send или Telegram identity/profile mutation;
- secret-bearing evidence publication;
- upstream/GPL code copy.
