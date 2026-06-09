# NEXT CHAT: AMN2 Phase 3 Service Mode Gate

Дата: 2026-06-09.

Рабочая папка нового чата:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB
```

Назначение нового чата: продолжить Phase 3 для нового target VPS после уже закрытых bootstrap, AWG2 runtime, live disposable peer apply/revoke и manual web/bot readiness gates. Новый чат должен владеть следующим controlled production/service-mode решением: оставаться в manual mode или запускать отдельный gate для `systemd` + HTTPS reverse proxy.

Этот handoff не разрешает public API, public config delivery, production peer writes или service-mode без отдельного решения оператора.

## Текущая Точка Правды

AMN3 / lab repo:

```text
repo: C:\Users\SooL\Documents\VPS-OPS-LAB
remote: https://github.com/barakov-dot/amn3.git
branch: master
head before this handoff: 615efc7 Record target server manual web bot gate
```

Production repo:

```text
repo: C:\Users\SooL\Documents\Amneziya
remote: https://github.com/barakov-dot/amn2.git
branch: codex-vps-test-prep
current source-overlay/package head: f7f6131 Update integration status for c92 manual prelaunch
```

Current AMN3 package:

```text
dist/amn2-vps-update-and-smoke-kit-f7f6131.zip
sha256: 19BF96A7E1057C042B89630BF80ADC7A9F5A09A62436E33A8555D7E2991AF282
source sha256: 720B6C9FE3CADDBC65C19BDEC5B0C811D00C94EB0D095D6311DCD90DD77BE4E1
status: read-only-vps-smoke-pass
```

## Что Уже Закрыто На Новом Target VPS

```text
bootstrap: partial-pass
AWG2 runtime: read-only-smoke-pass
live peer gate: verified-live for exactly one disposable test peer
manual web/bot gate: passed
current source overlay: f7f6131
AWG2 container: running
final peer count: 0
direct public web 3030: closed
public API 3040: closed
service-mode systemd: not-enabled
reverse proxy/public HTTPS cutover: not-enabled
VPS_APPLY_ENABLED: false/not-set outside narrow live gates
```

Evidence:

```text
research/amn2/target-server-bootstrap-evidence-2026-06-08.md
research/amn2/target-server-awg2-runtime-smoke-evidence-2026-06-09.md
research/amn2/target-server-live-peer-gate-evidence-2026-06-09.md
research/amn2/target-server-manual-web-bot-evidence-2026-06-09.md
```

Latest safe manual web/bot result:

```text
bot_check_network: passed
bot_identity: @NeobyatnayaAMNZ_bot
web_login_http: 200
web_listener: 127.0.0.1:3030 during diagnostic check only
web_listener_after_cleanup: stopped
tcp_3030_final: absent
tcp_3040_final: absent
peer_count_final: 0
```

## Обязательно Прочитать В Новом Чате

Start with:

```text
docs/NEXT_CHAT_AMN2_PHASE_3_SERVICE_MODE.ru.md
docs/PROJECT_STATUS_CURRENT.ru.md
docs/PROJECT_CONTEXT_IMPORT.ru.md
docs/AMN_UNIFIED_PROD_GATE_HANDOFF.ru.md
research/amn2/target-server-bootstrap-evidence-2026-06-08.md
research/amn2/target-server-awg2-runtime-smoke-evidence-2026-06-09.md
research/amn2/target-server-live-peer-gate-evidence-2026-06-09.md
research/amn2/target-server-manual-web-bot-evidence-2026-06-09.md
research/amn2/transfer-backlog.md
```

Operator/runbook context:

```text
docs/AMN2_TARGET_SERVER_PREP_GATE.ru.md
docs/AMN2_TARGET_SERVER_PREP_RUNBOOK.ru.md
docs/AMN2_CONTROLLED_PROD_READINESS_RUNBOOK.ru.md
docs/AMN2_API_WEB_PANEL_VPS_TEST_RUNBOOK.ru.md
docs/AMN2_VPS_API_UPDATE_AND_SMOKE.ru.md
```

## Строгие Правила Phase 3

Нельзя публиковать в чат или GitHub:

- `.env`;
- `servers.yml`;
- raw Telegram bot token;
- raw API token;
- Authorization header;
- token hash;
- web admin password hash;
- session secret;
- private key;
- PSK;
- peer public key;
- full `.conf`;
- QR payload/PNG;
- `vpn://`;
- backup contents;
- full logs;
- provider console credentials;
- SSH private key or SSH command with secret-bearing material.

Нельзя без отдельного подтверждения оператора:

- persistent `systemd` enable/start for web or bot;
- HTTPS reverse proxy/public cutover;
- `VPS_APPLY_ENABLED=true`;
- `apply-peer --apply`;
- `revoke-peer --apply`;
- production peer/user mutation;
- public web/API exposure;
- API `config:read`;
- `/api/clients` write CRUD;
- public/self-service config delivery;
- Local Agent configs/mutations;
- backup/import/reboot routes.

## Recommended Phase 3 Order

### Step 0: local/git sanity

Check AMN3 and AMN2:

```powershell
cd C:\Users\SooL\Documents\VPS-OPS-LAB
& 'C:\Program Files\Git\cmd\git.exe' status --short --branch
& 'C:\Program Files\Git\cmd\git.exe' log -5 --oneline --decorate

cd C:\Users\SooL\Documents\Amneziya
& 'C:\Program Files\Git\cmd\git.exe' status --short --branch
& 'C:\Program Files\Git\cmd\git.exe' log -5 --oneline --decorate
```

Expected:

```text
AMN3 master clean and synced with origin/master
AMN2 codex-vps-test-prep clean at the current stable/source-overlay head
```

### Step 1: confirm target VPS final safe baseline

Run only read-only checks first:

```text
source_overlay_commit: f7f6131
AWG2 container: running
peer_count: 0
tcp_3030: absent
tcp_3040: absent
telegram_bot_token: present
web_admin_password_hash: present
web_admin_session_secret: present
VPS_APPLY_ENABLED: false/not-set
```

Do not paste secret values.

### Step 2: decide Phase 3 path

Ask the operator for one explicit choice:

```text
Do we keep Phase 3 in manual runtime mode for now, or proceed to a service-mode gate for web/bot systemd plus HTTPS reverse proxy?
```

If the answer is not explicit, remain in manual mode.

### Step 3A: manual-mode continuation

Allowed without service-mode approval:

- docs/evidence updates;
- read-only API loopback smoke;
- manual web/admin diagnostic check on `127.0.0.1:3030`;
- bot `check-network`;
- local product/API planning;
- local tests and package preparation.

Still blocked:

- persistent public exposure;
- production peer writes;
- config delivery expansion.

### Step 3B: service-mode gate, only after explicit approval

Before enabling anything persistently:

- verify loopback bind for web/admin;
- verify bot token and web secrets are present without printing values;
- decide whether service units are copied/installed or only dry-run checked;
- decide HTTPS reverse proxy path and public access boundary;
- define rollback:
  - stop/disable units;
  - remove reverse proxy route;
  - verify `3030`/`3040` are not public;
  - keep AWG2 peer state unchanged.

Expected service-mode evidence must be safe:

```text
service_mode_gate_status:
web_unit_enabled:
web_unit_active:
bot_unit_enabled:
bot_unit_active:
web_bind:
web_login_http:
direct_public_3030:
public_api_3040:
reverse_proxy_status:
rollback_status:
peer_count:
VPS_APPLY_ENABLED:
safe_evidence_dir:
```

## Expected Outcomes

One of:

```text
phase3_manual_mode_pass
phase3_service_mode_pass
phase3_service_mode_deferred
needs-fix with safe AMN2/AMN3 plan
```

No outcome in Phase 3 should unlock broad write API, config delivery, production peer mutation, backup/import/reboot or public API `3040` by default.

## One-Copy Message For Creating The New Chat

```text
Работаем в C:\Users\SooL\Documents\VPS-OPS-LAB.

Новый чат: AMN2 Phase 3 Service Mode Gate.

Сначала прочитай:
- docs/NEXT_CHAT_AMN2_PHASE_3_SERVICE_MODE.ru.md
- docs/PROJECT_STATUS_CURRENT.ru.md
- docs/PROJECT_CONTEXT_IMPORT.ru.md
- docs/AMN_UNIFIED_PROD_GATE_HANDOFF.ru.md
- research/amn2/target-server-bootstrap-evidence-2026-06-08.md
- research/amn2/target-server-awg2-runtime-smoke-evidence-2026-06-09.md
- research/amn2/target-server-live-peer-gate-evidence-2026-06-09.md
- research/amn2/target-server-manual-web-bot-evidence-2026-06-09.md
- research/amn2/transfer-backlog.md
- docs/AMN2_TARGET_SERVER_PREP_GATE.ru.md
- docs/AMN2_TARGET_SERVER_PREP_RUNBOOK.ru.md
- docs/AMN2_CONTROLLED_PROD_READINESS_RUNBOOK.ru.md
- docs/AMN2_API_WEB_PANEL_VPS_TEST_RUNBOOK.ru.md
- docs/AMN2_VPS_API_UPDATE_AND_SMOKE.ru.md

Проверь git status/log:
- AMN3: C:\Users\SooL\Documents\VPS-OPS-LAB, branch master
- amn2: C:\Users\SooL\Documents\Amneziya, branch codex-vps-test-prep

Текущая production/source-overlay точка:
- AMN2 branch: codex-vps-test-prep
- AMN2 source-overlay/package head: f7f6131 Update integration status for c92 manual prelaunch
- AMN3 head before handoff: 615efc7 Record target server manual web bot gate
- package: dist/amn2-vps-update-and-smoke-kit-f7f6131.zip
- package sha256: 19BF96A7E1057C042B89630BF80ADC7A9F5A09A62436E33A8555D7E2991AF282

Что уже закрыто на новом target VPS:
- bootstrap: partial-pass
- AWG2 runtime: read-only-smoke-pass
- live peer gate: verified-live for exactly one disposable test peer
- manual web/bot gate: passed
- final peer count: 0
- direct public web 3030: closed
- public API 3040: closed
- service-mode systemd/reverse proxy: not-enabled

Задача:
1. Начать Phase 3 controlled service-mode/prod-readiness gate.
2. Сначала подтвердить read-only baseline: f7f6131, AWG2 running, peer_count=0, 3030/3040 closed, bot/web secrets present without printing values, VPS_APPLY_ENABLED=false/not-set.
3. Затем отдельно спросить решение: остаемся в manual mode или идем в service-mode gate для web/bot systemd + HTTPS reverse proxy.
4. Если service-mode gate подтвержден, делать только loopback web/admin + controlled HTTPS reverse proxy path, с rollback и safe evidence.
5. Не открывать public API 3040, direct public 3030, config delivery, /api/clients write CRUD, Local Agent mutations, backup/import/reboot или production peer writes без отдельного gate.

Не публиковать:
- .env, servers.yml, raw tokens, Authorization headers, token hash, web password hash, session secret, private keys, PSK, peer public keys, .conf, QR, vpn://, backup contents или full logs.

Ожидаемый результат чата:
- phase3_manual_mode_pass;
- либо phase3_service_mode_pass;
- либо phase3_service_mode_deferred;
- либо needs-fix с безопасным планом исправления.
```
