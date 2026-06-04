# AMN2 VPS API Update And Smoke

Дата: 2026-06-04.

Назначение: обновить установленный на VPS `/opt/amn2` до stable production head `294803e` и затем выполнить loopback API smoke и web-panel tunnel check без передачи SSH-доступа в чат.

Последний безопасный итог: real VPS loopback API smoke passed 2026-06-03, `run_id=20260603T112418Z`; server config был заранее синхронизирован в SQLite как DB-only step, preflight был `skipped`, API/auth/scope/revoke/listener/audit `passed`, `VPS_APPLY_ENABLED=false`. AMN3 evidence: `research/amn2/api-vps-smoke-evidence-2026-06-03.md`. Package `294803e` дополнительно содержит web-admin `API readiness` и `API tokens` pages.

Важно: API smoke теперь по умолчанию не запускает `server preflight` и не входит в SSH/server gate. Для чистой API-проверки `preflight_status` должен быть `skipped`. Перед route smoke скрипт делает DB-only sync выбранного server config из `servers.yml` в SQLite; ожидаемый `server_db_sync_status` - `passed`. Если нужен отдельный SSH/server dry-run gate, запускать его вручную и осознанно, не смешивая с API smoke.

## Почему нужен этот пакет

Если при запуске `amn2_api_loopback_smoke.sh` появляется:

```text
ModuleNotFoundError: No module named 'app.api'
```

значит текущий `/opt/amn2` на VPS установлен из старого stable package `d0939d8` или другой ветки, где еще нет read-only API route shell.

Smoke-скрипт сам API-код не устанавливает. Он проверяет уже установленный `amn2`.

## Пакеты

Source package для stable head `294803e`:

```text
dist/amn2-codex-vps-test-prep-294803e-source.zip
dist/amn2-codex-vps-test-prep-294803e-source.zip.sha256.txt
```

Operator update+smoke kit:

```text
dist/amn2-vps-update-and-smoke-kit-294803e.zip
dist/amn2-vps-update-and-smoke-kit-294803e.zip.sha256.txt
```

Скрипты внутри:

```text
amn2_apply_source_zip.sh
amn2_api_loopback_smoke.sh
```

## Что делает update script

`amn2_apply_source_zip.sh`:

- проверяет SHA256 source zip;
- проверяет, что source zip не содержит `.env`, `servers.yml`, `data/`, `venv/`, `.git/`, sqlite/db/key/pem files;
- распаковывает tracked source files из production head `294803e`;
- накладывает их поверх `/opt/amn2`;
- не удаляет и не копирует `.env`, `data`, `venv`, `servers.yml`;
- запускает `python -m pip install -e .`;
- проверяет imports: `fastapi`, `uvicorn`, `app.cli`, `app.api.app`, `app.services.api_smoke`.

Это не запускает peer apply/revoke и не меняет live VPS runtime state.

## 1. Загрузить kit на VPS

С локальной машины:

```powershell
cd C:\Users\SooL\Documents\VPS-OPS-LAB
scp .\dist\amn2-vps-update-and-smoke-kit-294803e.zip root@<VPS_HOST>:/root/
scp .\dist\amn2-vps-update-and-smoke-kit-294803e.zip.sha256.txt root@<VPS_HOST>:/root/
```

На VPS:

```bash
cd /root
sha256sum -c amn2-vps-update-and-smoke-kit-294803e.zip.sha256.txt
mkdir -p amn2-vps-update-and-smoke-kit-294803e
python3 -m zipfile -e amn2-vps-update-and-smoke-kit-294803e.zip amn2-vps-update-and-smoke-kit-294803e
cd amn2-vps-update-and-smoke-kit-294803e
sha256sum -c amn2-codex-vps-test-prep-294803e-source.zip.sha256.txt
```

## 2. Обновить `/opt/amn2`

```bash
cd /root/amn2-vps-update-and-smoke-kit-294803e
export AMN2_DIR=/opt/amn2
export AMN2_SOURCE_ZIP=/root/amn2-vps-update-and-smoke-kit-294803e/amn2-codex-vps-test-prep-294803e-source.zip
bash ./amn2_apply_source_zip.sh
```

Ожидаемый конец вывода:

```text
source_update_status=passed
source_commit=294803e
next=run ./amn2_api_loopback_smoke.sh from /opt/amn2
```

## 3. Установить smoke script и запустить проверку

```bash
install -m 700 /root/amn2-vps-update-and-smoke-kit-294803e/amn2_api_loopback_smoke.sh /opt/amn2/amn2_api_loopback_smoke.sh
cd /opt/amn2
export VPS_APPLY_ENABLED=false
export AMN2_RUN_PREFLIGHT=0
export AMN2_SYNC_SERVER_CONFIG=1
export AMN2_REQUIRE_SERVER_DB_SYNC=1
export AMN2_SERVER_NAME=local
bash ./amn2_api_loopback_smoke.sh
```

Если `/opt/amn2` является старым git checkout, smoke summary может показать mismatch по git head, но при overlay-mode должен быть файл:

```text
/opt/amn2/.amn2_source_overlay_commit
```

Это нормально для package overlay. Важнее, чтобы:

```text
api_smoke_status: passed
auth_status: passed
preflight_status: skipped
server_db_sync_status: passed
listener_status: passed
audit_status: passed
```

## 4. Проверить web-panel через SSH tunnel

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

Проверить только web-admin UI:

- `/api-readiness` открывается и показывает aggregate-only status;
- `/api-tokens` открывается;
- issue token показывает raw token один раз;
- refresh/list не показывает raw token или token hash;
- revoke token отражается в UI;
- `.env`, `servers.yml`, `.conf`, QR, `vpn://`, private key, PSK, Authorization header не публиковать.

## 5. Что прислать обратно

Можно прислать:

- safe bundle из `safe_bundle: ...`;
- `api-smoke-safe-summary.txt`;
- `api-smoke-result.json`;
- `api-auth-evidence.txt`;
- `api-listener-evidence.txt`;
- `api-audit-evidence.txt`;
- `source-update-summary.txt`, если update script не прошел.

Нельзя присылать:

- raw API token;
- Authorization header;
- token hash;
- `.env`;
- `.conf`;
- QR payload/PNG;
- `vpn://`;
- `PrivateKey`;
- `PresharedKey`;
- SSH private key/password;
- полный `api-server.log`, если оператор не проверил и не отредактировал его вручную.

## 6. Как читать шум запуска

Если в старой версии скрипта перед summary были строки вида:

```text
curl: (7) Failed to connect to 127.0.0.1 port 3040
```

это был шум ожидания старта API. Само по себе это не ошибка, если итоговый summary показывает:

```text
api_ready_status: passed
api_smoke_status: passed
auth_status: passed
audit_status: passed
```

Если при этом был только `listener_status: failed`, нужно проверить `api-listener-evidence.txt` или перезапустить обновленный `scripts/vps/amn2_api_loopback_smoke.sh`. Обновленный файл подавляет startup polling noise и точнее проверяет listener по PID временного API-процесса.

## 7. После pass

После `VPS verdict: pass` можно вернуться в coordination chat и зафиксировать, что stable `codex-vps-test-prep` на `294803e` подтвержден на VPS API-only smoke. Это выполнено 2026-06-04, `run_id=20260604T102355Z`; evidence `research/amn2/api-web-panel-vps-evidence-2026-06-04.md`.

Write API, `/clients` CRUD, API `config:read`, public config delivery, backup/import/reboot и SSH/sync/config/runtime-changing routes остаются закрытыми до отдельного controlled VPS gate.
