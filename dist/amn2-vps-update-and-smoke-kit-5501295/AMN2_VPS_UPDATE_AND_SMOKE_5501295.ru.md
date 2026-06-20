# AMN2 VPS update/smoke kit 5501295

Дата: 2026-06-19
Статус: package-ready-for-opened-P7-C005-live-gate. Public exposure/config delivery/restore/import/reboot/Telegram mutation не открыты.

## Граница Gate

- Этот пакет собран для AMN2 Phase 7 P7-C005 write API / install mutation gate.
- Разрешён только scoped write/install contour: POST /api/install/mutation-requests со scope install:write.
- Route является audit-only/preparation contour: он фиксирует безопасный pi_write audit event и при VPS_APPLY_ENABLED=false возвращает blocked status.
- Пакет не выполняет public exposure, config delivery, restore/import/reboot, Local Agent mutation, Telegram action или provider action.
- Runtime apply/smoke на VPS допустим только внутри уже открытого named gate P7-C005 для disposable VPS 89.185.80.166.

## Источник

- Repo: barakov-dot/amn2
- Branch: codex-vps-test-prep
- Commit: 55012958ff6b8338254f3f68dfe6779f4bc56f5d
- Subject: Add P7 install write contour
- Previous VPS clean-installer smoked head: b121865 Add multi instance conflict model

## Артефакты

- Source zip: $SourceName
- Source SHA256: $SourceSha
- Apply script: mn2_apply_source_zip.sh
- Smoke script: mn2_api_loopback_smoke.sh

## P7-C005 Smoke Plan

1. Verify uploaded kit SHA256 before extract.
2. Apply source zip to /opt/amn2 with mn2_apply_source_zip.sh.
3. Restart only loopback AMN2 web runtime so the API route inventory can load the new code.
4. Run mn2_api_loopback_smoke.sh loopback-only on 127.0.0.1:3040.
5. Run P7-C005 scoped route smoke:
   - server:read token must receive 403 on POST /api/install/mutation-requests.
   - install:write token must receive 202.
   - response status must be ecorded_blocked_by_vps_apply_disabled while VPS_APPLY_ENABLED=false.
   - audit entry must be pi_write with secret-safe metadata only.
6. Confirm external probes remain closed on 3030/3040/80/443.
7. Confirm no config delivery, restore/import/reboot, public listener, Telegram action, Local Agent mutation or actual install execution happened.

## Не Печатать В Evidence

- raw API tokens, Authorization headers, cookies;
- .env, servers.yml, DB rows;
- configs, QR, pn://, private keys, PSK;
- backup contents or secret-bearing logs.
