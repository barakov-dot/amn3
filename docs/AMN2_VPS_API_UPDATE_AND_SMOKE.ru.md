# AMN2 VPS API Update And Smoke

Current override 2026-06-12: Phase 5 `P5-C003` applied AMN2 `de25576` to the disposable test VPS and passed read-only loopback API smoke. Current package:

```text
dist/amn2-vps-update-and-smoke-kit-de25576.zip
sha256: B35D176F871ADB3B4CFDD3EC8D55B9BC5DF972E537038345B2E66899CFD21F87
source sha256: CFF46C44CFB8F321DEB88CE64A0F5D2154CFC02CD3931CF9955DDC466615B8CC
source update run_id: 20260612T054750Z
api smoke run_id: 20260612T054913Z
evidence: research/amn2/phase-5-live-rollout-de25576-2026-06-12.md
```

For this target, set `AMN2_SERVER_NAME=local` when running the API smoke. Before any future package apply, close `P5-C005` so the source-overlay apply script preserves `/opt/amn2` service-mode permissions without a manual repair step.

Current override 2026-06-07.3: stable branch head `c92bd1a Bind web admin systemd to loopback` has passed safe source-overlay update and read-only API smoke on `/opt/amn2`. Current VPS-smoked source overlay is now `c92bd1a`; previous source overlay `42ffa65 Record git checkout smoke status` remains the historical status-visibility baseline, original promotion `api_smoke_run_id=20260607T165625Z`, latest repeat `api_smoke_run_id=20260607T165807Z`. `c92bd1a` is a controlled production launch safety follow-up: web/admin systemd backend binds to `127.0.0.1:3030` by default for approved HTTPS reverse proxy mode.

```text
dist/amn2-vps-update-and-smoke-kit-c92bd1a.zip
sha256: EC48DBA7C91F189512AB77EB5490432C85DA79F987068A98C1CC7F3082387F12
source zip: dist/amn2-codex-vps-test-prep-c92bd1a-source.zip
source sha256: 272CC013A416937AAA2256A1643B2C77F707874D28FDCB2EA16534E349DD4FC2
operator doc: dist/amn2-vps-update-and-smoke-kit-c92bd1a/AMN2_VPS_UPDATE_AND_SMOKE_c92bd1a.ru.md
local validation: focused deploy tests 11 passed; package SHA/source SHA/no-BOM/no-CRLF/no-forbidden-source-entry/test-extract checks passed
VPS result: read-only-vps-smoke-pass, source_update_run_id 20260607T182118Z, api_smoke_run_id 20260607T182131Z
checked_routes: 6
route_status_codes: all 200
forbidden_markers: none
web template: 127.0.0.1:3030 loopback-only
evidence: research/amn2/web-admin-loopback-systemd-vps-package-2026-06-07.md
smoke evidence: research/amn2/web-admin-loopback-systemd-vps-smoke-evidence-2026-06-07.md
```

Previous source-overlay package:

Current override 2026-06-07: stable branch head `42ffa65 Record git checkout smoke status` has passed safe source-overlay update and read-only API smoke on `/opt/amn2`. Last VPS-smoked source overlay is now `42ffa65`, `source_update_run_id=20260607T165559Z`, `api_smoke_run_id=20260607T165625Z`. `c8a6363` is the historical prior VPS-smoked runtime/source, `run_id=20260606T202040Z`; `32d01fd` and `1a193b9` are older historical baselines.

```text
dist/amn2-vps-update-and-smoke-kit-42ffa65.zip
sha256: 5B43B467E014E87FEC1E49E8D9A8B7A2FBF841541BE88FDC6768097806240E39
source zip: dist/amn2-codex-vps-test-prep-42ffa65-source.zip
source sha256: 8A5B83D9AB95BE4230AAC221CE0321A37EF37E4E4B6EAB5EDECAE3C98A944829
operator doc: dist/amn2-vps-update-and-smoke-kit-42ffa65/AMN2_VPS_UPDATE_AND_SMOKE_42ffa65.ru.md
local validation: focused status tests 8 passed; package SHA/source SHA/no-BOM/no-CRLF/no-forbidden-source-entry/test-extract checks passed
VPS result: read-only-vps-smoke-pass, source_update_run_id 20260607T165559Z, api_smoke_run_id 20260607T165625Z, latest_repeat_api_smoke_run_id 20260607T165807Z
checked_routes: 6
listener: 127.0.0.1:3040 loopback-only
evidence: research/amn2/controlled-prod-status-visibility-vps-smoke-evidence-2026-06-07.md
repeat evidence: research/amn2/controlled-prod-status-visibility-vps-repeat-smoke-2026-06-07.md
```

Historical prior source-overlay package:

```text
dist/amn2-vps-update-and-smoke-kit-c8a6363.zip
sha256: 027ECC1BAD7321FCCD61A4CCCA3AC9F06AAA9AC6A3D7115B4813253D19C2CFBF
source zip: dist/amn2-codex-vps-test-prep-c8a6363-source.zip
source sha256: E1E198979D988B3A5AA038CF732B8DCDBE854C48A6D381FADBA05BFDEE0251C6
operator doc: dist/amn2-vps-update-and-smoke-kit-c8a6363/AMN2_VPS_UPDATE_AND_SMOKE_c8a6363.ru.md
local verification: focused/adjacent 37 passed; full 619 passed; package SHA/source SHA/no-BOM/no-forbidden-source-entry/test-extract checks passed
VPS result: read-only-vps-smoke-pass, run_id 20260606T202040Z
evidence: research/amn2/local-agent-runtime-summary-vps-smoke-evidence-2026-06-06.md
```

Older `42ffa65`, `c8a6363`, `32d01fd`, `294803e`, `5f12736`, `7764ae7`, `568c611` and `1a193b9` package blocks below are historical evidence after the `c92bd1a` VPS smoke pass. This override does not authorize live apply/revoke.

For the current VPS update/smoke commands, use:

```text
dist/amn2-vps-update-and-smoke-kit-c92bd1a/AMN2_VPS_UPDATE_AND_SMOKE_c92bd1a.ru.md
```

Актуализация 2026-06-04: текущий Phase 1 closeout package для существующего `/opt/amn2` — `7764ae7 Cover integration status in API smoke`.

```text
dist/amn2-vps-update-and-smoke-kit-7764ae7.zip
sha256: 832E1B1F6516A02E0D6AA45672B8FF526DF15D27117D2063CE45F9966825A66A
operator doc: dist/amn2-vps-update-and-smoke-kit-7764ae7/AMN2_VPS_UPDATE_AND_SMOKE_7764ae7.ru.md
evidence: research/amn2/phase-1-closeout-2026-06-04.md
```

Пакет `294803e` ниже остается historical API/web-panel evidence. Для следующей VPS-проверки Фазы 1 использовать `7764ae7`; он добавляет `/api/integration/status` в API smoke и не включает live apply/revoke.

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
