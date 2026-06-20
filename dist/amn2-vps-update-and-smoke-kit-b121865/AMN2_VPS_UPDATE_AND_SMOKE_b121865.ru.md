# AMN2 VPS update/smoke kit b121865

Дата: 2026-06-14
Статус: package-ready-not-vps-smoked. Live VPS apply/smoke этим шагом не выполнялся.

## Граница Gate

- Это local package/preflight artifact для AMN2 Phase 7 RC readiness.
- Live SSH/upload/apply/restart/smoke не открыт и требует отдельный named gate.
- До открытия live gate `VPS_APPLY_ENABLED=false` остается обязательным.
- Этот пакет не открывает public exposure, config delivery, write API, Local
  Agent mutations, backup/import/reboot, destructive cleanup/reinstall,
  Telegram identity mutations или production peer/user mutation.
- Known-good VPS baseline остается `0de7a77` до отдельного `P7-C001` gate.

## Источник

- Repo: barakov-dot/amn2
- Branch: codex-vps-test-prep
- Commit: b121865f488821f6fc471c9529fb26e5d7992515
- Subject: Add multi instance conflict model
- Previous latest VPS-smoked/package head: 0de7a77 Polish fresh installer preflight planning

## Артефакты

- Source zip: `amn2-codex-vps-test-prep-b121865-source.zip`
- Source SHA256: `D0FB561D5A12C3B2C095521C3B44923B001F49C8E94CA5C13DB1E811ABB17647`
- Apply script: `amn2_apply_source_zip.sh`
- Smoke script: `amn2_api_loopback_smoke.sh`

## Current-Head Smoke Plan После Отдельного Named Gate

1. Operator opens a separate live gate by exact phrase:
   `Открываю P7-C001 live package/apply/smoke gate для b121865 на текущем disposable VPS 89.185.80.166.`
2. Confirm target is still the disposable VPS `89.185.80.166` and the current
   latest VPS-smoked package is still `0de7a77`.
3. Upload only this kit and checksum to the target; verify checksum before extract.
4. Extract to `/root/amn2-vps-update-and-smoke-kit-b121865` and inspect the five expected files.
5. Run `amn2_apply_source_zip.sh` only after confirming target path and stop criteria.
6. Keep API smoke loopback-only: `AMN2_API_HOST=127.0.0.1`, target server name
   `local`, and `VPS_APPLY_ENABLED=false`.
7. Run `amn2_api_loopback_smoke.sh` and collect only safe summary/evidence.
8. Verify web/bot runtime status only inside the named gate; do not open public listeners.
9. If smoke passes, record `b121865` as latest VPS-smoked/package head. If
   blocked, keep `0de7a77` as latest known-good and record blocker evidence.

## Named Live Gate Checklist

Before live apply/smoke can run, record:

- exact operator phrase naming `P7-C001`, commit `b121865`, and target `89.185.80.166`;
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
