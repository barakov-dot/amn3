# NEXT CHAT: AMN2 Phase 2 VPS Live Gate

Дата: 2026-06-05.

Рабочая папка нового чата:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB
```

Назначение нового чата: отдельно и осознанно войти в Phase 2 live single test peer gate после закрытой Phase 1 read-only/API/web-panel baseline. Новый чат не должен начинать широкую API/web/agent integration и не должен запускать live apply/revoke без отдельного подтверждения оператора.

## Текущая точка правды

AMN3 / lab repo:

```text
repo: C:\Users\SooL\Documents\VPS-OPS-LAB
remote: https://github.com/barakov-dot/amn3.git
branch: master
latest before this handoff: e67c6ea Add completed phases skill transfer summary
```

Production repo:

```text
repo: C:\Users\SooL\Documents\Amneziya
remote: https://github.com/barakov-dot/amn2.git
branch: codex-vps-test-prep
head: 7764ae7 Cover integration status in API smoke
```

Important ancestry:

```text
7281254 Merge stable API web panel baseline into remote operation gate
is already an ancestor of
7764ae7 Cover integration status in API smoke
```

Meaning: do not downgrade VPS from `7764ae7` to the historical `7281254` package unless explicitly debugging that old candidate. Phase 2 should start from the current stable `7764ae7` package, because it already contains the remote-operation gate merge plus the Phase 1 closeout API smoke coverage.

## Что уже закрыто

Closed phase:

```text
Phase 1 read-only/API/web-panel baseline
status: closed
amn2 head: 7764ae7
AMN3 evidence: research/amn2/phase-1-closeout-2026-06-04.md
package: dist/amn2-vps-update-and-smoke-kit-7764ae7.zip
package sha256: 832E1B1F6516A02E0D6AA45672B8FF526DF15D27117D2063CE45F9966825A66A
source sha256: 94D110BB9AA17C65E02C1780380BA77E49A4F0ADDDECEA7DE267FFC9F353B42B
```

Phase 1 local verification:

```text
focused: 39 passed
full: 610 passed
```

Remote-operation Phase 1:

```text
status: dry-run-only-pass
candidate origin: 7281254
stable merge: 708c98e
evidence: research/amn2/remote-operation-vps-gate-evidence-2026-06-04.md
live apply/revoke: not run
```

## Что добавили соседние чаты

Нужно учитывать свежий общий snapshot:

```text
research/amn2/completed-phases-and-skill-transfer-2026-06-05.md
```

Ключевое из него:

- `dry-run-only-pass` не равен `verified-live`;
- read-only/API/status surfaces можно развивать отдельно от write lifecycle;
- PRVTPRO/KYORESUAS остаются источниками требований и UX/product signals, не источниками копируемого кода;
- `config:read`, public config delivery, write scopes, backup/import/reboot, Local Agent configs/mutations и detailed per-peer metrics остаются заблокированы;
- любой VPS-ready slice требует package, checksum, expected commit, update path, smoke path, rollback/recovery note and no-secret evidence.

## Обязательно прочитать в новом чате

Сначала:

```text
docs/NEXT_CHAT_AMN2_PHASE_2_VPS_LIVE.ru.md
research/amn2/completed-phases-and-skill-transfer-2026-06-05.md
research/amn2/phase-1-closeout-2026-06-04.md
research/amn2/remote-operation-vps-gate-evidence-2026-06-04.md
research/amn2/vps-gate-evidence-checklist.md
research/amn2/post-vps-gate-merge-decision.md
research/amn2/vps-gate-remote-operation-dry-run-audit.md
research/amn2/transfer-backlog.md
```

Операторские инструкции для current stable update/smoke:

```text
docs/AMN2_API_WEB_PANEL_VPS_TEST_RUNBOOK.ru.md
docs/AMN2_VPS_API_UPDATE_AND_SMOKE.ru.md
dist/amn2-vps-update-and-smoke-kit-7764ae7/AMN2_VPS_UPDATE_AND_SMOKE_7764ae7.ru.md
```

Coordination context:

```text
docs/PROJECT_CONTEXT_IMPORT.ru.md
docs/PROJECT_STATUS_CURRENT.ru.md
docs/AMN2_MAIN_MERGE_ROADMAP.ru.md
```

## Строгие правила Phase 2

Нельзя публиковать в чат или GitHub:

- `.env`;
- `servers.yml`;
- raw API token;
- Authorization header;
- token hash;
- private key;
- PSK;
- full `.conf`;
- QR payload/PNG;
- `vpn://`;
- full `api-server.log`, web/bot logs or command output before manual redaction.

Нельзя без отдельного подтверждения оператора:

- `VPS_APPLY_ENABLED=true`;
- `apply-peer --apply`;
- `revoke-peer --apply`;
- Docker restart outside the exact operation plan;
- public web/API exposure;
- config delivery API;
- `/api/clients` write CRUD;
- API `config:read`;
- Local Agent `/configs` or write lifecycle;
- backup/import/reboot routes.

## Recommended Phase 2 order

### Step 0: local/git sanity

Check both repos:

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
amn2 codex-vps-test-prep clean and at 7764ae7
```

### Step 1: current stable VPS update/read-only smoke

Before any live apply/revoke, update or verify `/opt/amn2` using current stable `7764ae7` kit and run API loopback smoke.

Expected safe result:

```text
VPS verdict: pass
preflight_status: skipped
server_db_sync_status: passed
api_ready_status: passed
api_smoke_status: passed
auth_status: passed
listener_status: passed
audit_status: passed
```

`api-smoke-result.json` should check 5 read-only routes:

```text
servers
integration_status
server_summary
metrics_summary
users_summary
```

This is still not permission for live apply/revoke.

### Step 2: explicit Phase 2 decision

Ask the operator for a separate decision:

```text
Do we proceed with Phase 2 live single test peer apply/revoke now?
```

If the answer is not an explicit yes, stop at `dry-run-only-pass` / read-only status.

### Step 3: PSK handling decision before live apply

Current CLI requires:

```text
--preshared-key
```

The remote Docker/awg command receives PSK through stdin and redacts output, but the local CLI still receives PSK as an argument. Before live apply, the new chat must decide one of:

1. Accept this for a disposable one-time test peer and do not publish commands with real values.
2. First implement a small safer `--preshared-key-stdin` / secret-file local slice in `amn2`, test it locally, package it, then run Phase 2.

If strict no-secret-on-local-command-line is required, choose option 2 before live apply.

### Step 4: prepare disposable test peer

Use only a dedicated synthetic test peer:

```text
TEST_PEER_PUBLIC_KEY=<operator-owned disposable public key>
TEST_PEER_PSK=<operator-owned disposable PSK, never posted>
TEST_PEER_IP=<free test IP, not an existing peer>
SERVER_NAME=local
DB_PATH=data/amneziya.sqlite3
```

Do not use production user/device keys.

### Step 5: repeat dry-run immediately before live

With `VPS_APPLY_ENABLED=false`:

```bash
python -m app.cli server apply-peer \
  --config servers.yml \
  --server "$SERVER_NAME" \
  --public-key "$TEST_PEER_PUBLIC_KEY" \
  --preshared-key "$TEST_PEER_PSK" \
  --vpn-ip "$TEST_PEER_IP" \
  --dry-run

python -m app.cli server revoke-peer \
  --config servers.yml \
  --server "$SERVER_NAME" \
  --public-key "$TEST_PEER_PUBLIC_KEY" \
  --dry-run
```

Expected dry-run output must include operation id, risk class, side effects and rollback note, and must not expose PSK/private key/full config.

### Step 6: live apply/revoke only after confirmation

Only after separate confirmation and only for the disposable test peer:

```bash
export VPS_APPLY_ENABLED=true

python -m app.cli server apply-peer \
  --config servers.yml \
  --server "$SERVER_NAME" \
  --public-key "$TEST_PEER_PUBLIC_KEY" \
  --preshared-key "$TEST_PEER_PSK" \
  --vpn-ip "$TEST_PEER_IP" \
  --apply

python -m app.cli server sync-peers \
  --config servers.yml \
  --server "$SERVER_NAME" \
  --db "$DB_PATH"

python -m app.cli server revoke-peer \
  --config servers.yml \
  --server "$SERVER_NAME" \
  --public-key "$TEST_PEER_PUBLIC_KEY" \
  --apply

python -m app.cli server sync-peers \
  --config servers.yml \
  --server "$SERVER_NAME" \
  --db "$DB_PATH"
```

Expected result:

- exactly one test peer added;
- existing peers unchanged;
- the same test peer revoked/removed;
- final sync confirms cleanup;
- no secrets in evidence;
- recovery note recorded if anything fails.

### Step 7: record evidence

Use:

```text
research/amn2/vps-gate-evidence-checklist.md
```

Allowed evidence:

- safe summaries;
- redacted status lines;
- final decision: `verified-live`, `needs-fix`, or still `dry-run-only-pass`;
- final peer state;
- rollback/recovery used or not needed.

Not allowed evidence:

- raw PSK/key/token/config/logs.

## After Phase 2

If result is `verified-live`:

- update AMN3 evidence;
- rerun focused local remote-operation tests in `amn2`;
- decide merge/status using `research/amn2/post-vps-gate-merge-decision.md`;
- only then discuss write/API integration.

If result is `dry-run-only-pass`:

- do not unlock write lifecycle;
- continue only read-only/status/docs/UX design lanes.

If result is `needs-fix`:

- stop all write integration;
- fix in `amn2` with a safe commit/package;
- retest from read-only/dry-run again.

## One-copy message for creating the new chat

```text
Работаем в C:\Users\SooL\Documents\VPS-OPS-LAB.

Новый чат: AMN2 Phase 2 VPS Live Gate.

Сначала прочитай:
- docs/NEXT_CHAT_AMN2_PHASE_2_VPS_LIVE.ru.md
- research/amn2/completed-phases-and-skill-transfer-2026-06-05.md
- research/amn2/phase-1-closeout-2026-06-04.md
- research/amn2/remote-operation-vps-gate-evidence-2026-06-04.md
- research/amn2/vps-gate-evidence-checklist.md
- research/amn2/post-vps-gate-merge-decision.md
- research/amn2/vps-gate-remote-operation-dry-run-audit.md
- research/amn2/transfer-backlog.md
- docs/AMN2_API_WEB_PANEL_VPS_TEST_RUNBOOK.ru.md
- docs/AMN2_VPS_API_UPDATE_AND_SMOKE.ru.md
- docs/PROJECT_CONTEXT_IMPORT.ru.md
- docs/PROJECT_STATUS_CURRENT.ru.md

Проверь git status/log:
- AMN3: C:\Users\SooL\Documents\VPS-OPS-LAB, branch master
- amn2: C:\Users\SooL\Documents\Amneziya, branch codex-vps-test-prep

Текущая production-точка amn2:
- branch: codex-vps-test-prep
- head: 7764ae7 Cover integration status in API smoke

Текущий AMN3 package:
- dist/amn2-vps-update-and-smoke-kit-7764ae7.zip
- sha256: 832E1B1F6516A02E0D6AA45672B8FF526DF15D27117D2063CE45F9966825A66A

Важное уточнение:
- 7281254 remote-operation candidate уже входит в stable через merge 708c98e и является ancestor of 7764ae7.
- Не откатывать VPS на historical 7281254 package без отдельной причины.
- Phase 2 стартует с current stable 7764ae7 update/read-only smoke.

Задача:
1. Подготовить Phase 2 live single test peer apply/revoke gate.
2. Сначала обновить/проверить VPS через 7764ae7 kit и получить read-only API smoke pass.
3. Затем отдельно спросить подтверждение оператора на Phase 2 live apply/revoke.
4. Перед live apply решить PSK handling: текущий CLI принимает --preshared-key аргумент; если нужен strict no-secret-on-local-command-line, сначала сделать safer --preshared-key-stdin slice.
5. Если оператор подтвердит live gate, использовать только dedicated disposable test peer, не production peer.
6. Не публиковать .env, servers.yml, raw tokens, Authorization headers, token hash, private keys, PSK, .conf, QR, vpn:// или full logs.

Запрещено без отдельного подтверждения:
- VPS_APPLY_ENABLED=true
- apply-peer --apply
- revoke-peer --apply
- public web/API exposure
- config:read
- /api/clients write CRUD
- public/self-service config delivery
- Local Agent configs/mutations
- backup/import/reboot routes

Ожидаемый результат чата:
- либо verified-live evidence для ровно одного disposable test peer apply/revoke;
- либо dry-run-only-pass остается текущим статусом;
- либо needs-fix с безопасным планом исправления в amn2.
```
