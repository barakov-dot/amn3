# AMN2 VPS Update And Smoke Kit c8a6363

Дата: 2026-06-06.

Назначение: обновить существующий `/opt/amn2` до `amn2/codex-vps-test-prep` head `c8a6363` и выполнить read-only/API/web-panel gate без live peer mutations.

`c8a6363` обновляет только read-only integration status contract plus mapper-only Local Agent runtime summary source: Phase 2 live gate теперь отражается как `verified_live`, а следующий gate - operator-only controlled prod readiness. Этот kit не включает live apply/revoke и не открывает новые public/write/config/agent/backup поверхности.

## Границы

Разрешено:

- сохранить существующие `/opt/amn2/.env`, `/opt/amn2/servers.yml`, `/opt/amn2/data`, `/opt/amn2/venv`;
- применить source overlay из tracked source zip;
- держать `VPS_APPLY_ENABLED=false`;
- выполнить API loopback smoke на `127.0.0.1:3040`;
- выполнить web-panel route check через `127.0.0.1:3030` и SSH tunnel.

Запрещено без отдельного подтверждения:

- `VPS_APPLY_ENABLED=true`;
- live `apply-peer --apply` или `revoke-peer --apply`;
- public/self-service config delivery;
- API `config:read`, `/api/clients` write CRUD, backup/import/reboot routes;
- Local Agent clients/configs/write mutations;
- публикация `.env`, `servers.yml`, raw token, Authorization header, token hash, private keys, PSK, `.conf`, QR, `vpn://`.

## 1. Распаковать kit

На VPS:

```bash
cd /root
sha256sum -c amn2-vps-update-and-smoke-kit-c8a6363.zip.sha256.txt
rm -rf amn2-vps-update-and-smoke-kit-c8a6363
mkdir -p amn2-vps-update-and-smoke-kit-c8a6363
python3 -m zipfile -e amn2-vps-update-and-smoke-kit-c8a6363.zip amn2-vps-update-and-smoke-kit-c8a6363
cd amn2-vps-update-and-smoke-kit-c8a6363
sha256sum -c amn2-codex-vps-test-prep-c8a6363-source.zip.sha256.txt
```

## 2. Применить source overlay

```bash
cd /root/amn2-vps-update-and-smoke-kit-c8a6363
export VPS_APPLY_ENABLED=false
export AMN2_DIR=/opt/amn2
bash ./amn2_apply_source_zip.sh
install -m 700 ./amn2_api_loopback_smoke.sh /opt/amn2/amn2_api_loopback_smoke.sh
```

Ожидаемый финал update script:

```text
source_update_status=passed
source_commit=c8a6363
next=run ./amn2_api_loopback_smoke.sh from /opt/amn2
```

## 3. Запустить API loopback smoke

```bash
cd /opt/amn2
source venv/bin/activate
export VPS_APPLY_ENABLED=false
export AMN2_RUN_PREFLIGHT=0
export AMN2_SYNC_SERVER_CONFIG=1
export AMN2_REQUIRE_SERVER_DB_SYNC=1
export AMN2_SERVER_NAME=local
bash ./amn2_api_loopback_smoke.sh
```

Ожидаемый summary:

```text
VPS verdict: pass
preflight_status: skipped
server_db_sync_status: passed
api_ready_status: passed
api_smoke_status: passed
auth_status: passed
missing_bearer_http: 401
wrong_scope_http: 403
revoked_token_http: 401
listener_status: passed
audit_status: passed
```

`api-smoke-result.json` должен проверять 5 read-only routes: `servers`, `integration_status`, `server_summary`, `metrics_summary`, `users_summary`.

Для `/api/integration/status` ожидаем safe state:

```text
status: read_only_vps_smoked
remote_operation_gate.phase_2: verified_live
controlled_prod_readiness.decision: pending_operator_evidence
api_baseline.write_routes_enabled: false
remote_operation_gate.write_operations_enabled: false
next_gate: operator-only controlled prod readiness checklist
```

## 4. Проверить web-panel через loopback/tunnel

На VPS:

```bash
cd /opt/amn2
source venv/bin/activate
export VPS_APPLY_ENABLED=false
python -m app.cli web serve --host 127.0.0.1 --port 3030
```

На локальной машине оператора:

```bash
ssh -L 3030:127.0.0.1:3030 root@<VPS_HOST>
```

Открыть:

```text
http://127.0.0.1:3030/login
```

Проверить: `/api-readiness`, `/integration-status`, `/api-tokens`, `/servers`, `/servers/1`. Не публиковать скриншоты или логи, если в них есть secret-bearing artifacts.

## 5. Что можно вернуть в coordination chat

Можно:

- `api-smoke-safe-summary.txt`;
- `api-smoke-result.json`;
- `api-auth-evidence.txt`;
- `api-listener-evidence.txt`;
- `api-audit-evidence.txt`;
- `server-db-sync.txt`;
- путь к `safe_bundle`;
- `source-update-summary.txt`, если update script не прошел.

Нельзя:

- raw API token;
- Authorization header;
- token hash;
- `.env`, `servers.yml`;
- `.conf`, QR, `vpn://`;
- `PrivateKey`, `PresharedKey`, SSH private key/password;
- полный `api-server.log` без ручной редакции.

## 6. После pass

После read-only smoke pass `c8a6363` станет новым VPS-smoked runtime/source baseline для controlled prod readiness. Это не разрешает public prod, live peer mutations или broad API/config/agent/backup surfaces.
