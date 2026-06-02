# AMN2 VPS API Update And Smoke

Дата: 2026-06-02.

Назначение: обновить установленный на VPS `/opt/amn2` до ветки `codex/read-only-api-route-shell` и затем выполнить loopback API smoke без передачи SSH-доступа в чат.

## Почему нужен этот пакет

Если при запуске `amn2_api_loopback_smoke.sh` появляется:

```text
ModuleNotFoundError: No module named 'app.api'
```

значит текущий `/opt/amn2` на VPS установлен из старого stable package `d0939d8` или другой ветки, где еще нет read-only API route shell.

Smoke-скрипт сам API-код не устанавливает. Он проверяет уже установленный `amn2`.

## Пакеты

Source package для API-ветки:

```text
dist/amn2-read-only-api-route-shell-2010d60-source.zip
dist/amn2-read-only-api-route-shell-2010d60-source.zip.sha256.txt
```

Operator update+smoke kit:

```text
dist/amn2-api-vps-update-and-smoke-kit-2026-06-02.zip
dist/amn2-api-vps-update-and-smoke-kit-2026-06-02.zip.sha256.txt
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
- распаковывает tracked source files из ветки `2010d60`;
- накладывает их поверх `/opt/amn2`;
- не удаляет и не копирует `.env`, `data`, `venv`, `servers.yml`;
- запускает `python -m pip install -e .`;
- проверяет imports: `fastapi`, `uvicorn`, `app.cli`, `app.api.app`, `app.services.api_smoke`.

Это не запускает peer apply/revoke и не меняет live VPS runtime state.

## 1. Загрузить kit на VPS

С локальной машины:

```powershell
cd C:\Users\SooL\Documents\VPS-OPS-LAB
scp .\dist\amn2-api-vps-update-and-smoke-kit-2026-06-02.zip root@<VPS_HOST>:/root/
scp .\dist\amn2-api-vps-update-and-smoke-kit-2026-06-02.zip.sha256.txt root@<VPS_HOST>:/root/
```

На VPS:

```bash
cd /root
sha256sum -c amn2-api-vps-update-and-smoke-kit-2026-06-02.zip.sha256.txt
mkdir -p amn2-api-vps-update-and-smoke-kit-2026-06-02
python3 -m zipfile -e amn2-api-vps-update-and-smoke-kit-2026-06-02.zip amn2-api-vps-update-and-smoke-kit-2026-06-02
cd amn2-api-vps-update-and-smoke-kit-2026-06-02
sha256sum -c amn2-read-only-api-route-shell-2010d60-source.zip.sha256.txt
```

## 2. Обновить `/opt/amn2`

```bash
cd /root/amn2-api-vps-update-and-smoke-kit-2026-06-02
export AMN2_DIR=/opt/amn2
export AMN2_SOURCE_ZIP=/root/amn2-api-vps-update-and-smoke-kit-2026-06-02/amn2-read-only-api-route-shell-2010d60-source.zip
bash ./amn2_apply_source_zip.sh
```

Ожидаемый конец вывода:

```text
source_update_status=passed
source_commit=2010d60
next=run ./amn2_api_loopback_smoke.sh from /opt/amn2
```

## 3. Установить smoke script и запустить проверку

```bash
install -m 700 /root/amn2-api-vps-update-and-smoke-kit-2026-06-02/amn2_api_loopback_smoke.sh /opt/amn2/amn2_api_loopback_smoke.sh
cd /opt/amn2
export VPS_APPLY_ENABLED=false
export AMN2_SERVER_NAME=debian-vps-1
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
listener_status: passed
audit_status: passed
```

## 4. Что прислать обратно

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

## 5. Как читать шум запуска

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

## 6. После pass

После `VPS verdict: pass` можно вернуться в coordination chat и принять решение по PR/merge `codex/read-only-api-route-shell` обратно в stable `codex-vps-test-prep`.

Write API, `/clients` CRUD, API `config:read`, public config delivery, backup/import/reboot и SSH/sync/config/runtime-changing routes остаются закрытыми до отдельного controlled VPS gate.
