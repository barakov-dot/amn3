# AMN2 API/Web Panel VPS Test Runbook

Current override 2026-06-06: stable branch head is `32d01fd Update integration status for controlled prod`; AMN3 package `32d01fd` is published and pending read-only VPS smoke. Last proven VPS runtime/source remains `1a193b9 Add remote partial failure contract`, `run_id=20260606T154636Z`.

```text
dist/amn2-vps-update-and-smoke-kit-32d01fd.zip
sha256: BE59AF74001AC4F094C753B565A4E672194D823C4F65B6CB476F4FF01B310807
source zip: dist/amn2-codex-vps-test-prep-32d01fd-source.zip
source sha256: 034753DA7EC42ACF869519F43909EEFDC8A392A5665B2A33C935F8A058CCB99B
operator doc: dist/amn2-vps-update-and-smoke-kit-32d01fd/AMN2_VPS_UPDATE_AND_SMOKE_32d01fd.ru.md
local verification: focused 7 passed; adjacent smoke/security 26 passed; package SHA/source SHA/no-BOM/no-forbidden-source-entry/test-extract checks passed
VPS result: pending-read-only-smoke
evidence: research/amn2/integration-status-controlled-prod-update-2026-06-06.md
```

Older `294803e`, `5f12736`, `7764ae7`, `568c611` and `1a193b9` package blocks below are historical evidence. This override does not authorize live apply/revoke.

Актуализация 2026-06-04: текущий Phase 1 closeout package — `7764ae7 Cover integration status in API smoke`.

```text
dist/amn2-vps-update-and-smoke-kit-7764ae7.zip
sha256: 832E1B1F6516A02E0D6AA45672B8FF526DF15D27117D2063CE45F9966825A66A
operator doc: dist/amn2-vps-update-and-smoke-kit-7764ae7/AMN2_VPS_UPDATE_AND_SMOKE_7764ae7.ru.md
evidence: research/amn2/phase-1-closeout-2026-06-04.md
```

Пакет `294803e` ниже остается historical API/web-panel evidence. Для следующей VPS-проверки Фазы 1 использовать `7764ae7`; он проверяет 5 read-only API routes, включая `/api/integration/status`, и не разрешает live apply/revoke.

Дата: 2026-06-04.

Назначение: зафиксировать, что делать на VPS при следующих API/web-panel доработках после подтвержденного API-only pass `run_id=20260603T112418Z`. Этот runbook не является разрешением на live apply/revoke/config delivery.

Актуализация 2026-06-04: real VPS API/web-panel gate для `294803e` пройден, `run_id=20260604T102355Z`; evidence `research/amn2/api-web-panel-vps-evidence-2026-06-04.md`. Если web-панель временно запускалась на `0.0.0.0`, это считать только операторским route-rendering check в закрытой сети; штатный повторный gate должен использовать `127.0.0.1` + SSH tunnel или отдельное firewall/TLS/reverse-proxy решение.

## Границы

Разрешено на VPS в этом gate:

- обновить `/opt/amn2` через AMN3 update+smoke kit;
- держать `VPS_APPLY_ENABLED=false`;
- выполнить API-only loopback smoke на `127.0.0.1`;
- выполнить DB-only server config sync из `servers.yml` в SQLite;
- поднять web-панель на `127.0.0.1:3030`;
- открыть web-панель только через SSH tunnel или локальный loopback;
- проверить login, navigation, API readiness/status, API token lifecycle UI, server list/detail read-only views.

Запрещено без отдельного подтверждения оператора:

- `VPS_APPLY_ENABLED=true`;
- `apply-peer --apply`, `revoke-peer --apply`;
- web действия, которые добавляют/удаляют/отключают peer на live VPS;
- public/self-service config download;
- API `config:read`;
- `/api/clients` write CRUD;
- backup/import/reboot;
- публикация web/API наружу без отдельного TLS/reverse-proxy/firewall gate.

Не публиковать в чат:

- `.env`;
- `servers.yml`;
- raw API token;
- Authorization header;
- token hash;
- private keys, PSK, `.conf`, QR, `vpn://`;
- полный `api-server.log` или web/bot logs без ручной редактуры.

## 1. Обновить пакет на VPS

Важно: команды ниже используют текущий package `32d01fd`; он опубликован и ожидает read-only VPS smoke. Последний уже доказанный runtime/source baseline - `1a193b9`, `run_id=20260606T154636Z`. Пакет `568c611` остается historical prior VPS-smoked runtime/source, а `294803e` остается historical API/web-panel evidence.

```bash
cd /root

curl -fL -o amn2-vps-update-and-smoke-kit-32d01fd.zip \
  https://github.com/barakov-dot/amn3/raw/master/dist/amn2-vps-update-and-smoke-kit-32d01fd.zip

curl -fL -o amn2-vps-update-and-smoke-kit-32d01fd.zip.sha256.txt \
  https://raw.githubusercontent.com/barakov-dot/amn3/master/dist/amn2-vps-update-and-smoke-kit-32d01fd.zip.sha256.txt

sha256sum -c amn2-vps-update-and-smoke-kit-32d01fd.zip.sha256.txt
```

Ожидаемый SHA256:

```text
BE59AF74001AC4F094C753B565A4E672194D823C4F65B6CB476F4FF01B310807
```

Распаковать и применить source overlay:

```bash
rm -rf amn2-vps-update-and-smoke-kit-32d01fd
mkdir -p amn2-vps-update-and-smoke-kit-32d01fd
python3 -m zipfile -e amn2-vps-update-and-smoke-kit-32d01fd.zip amn2-vps-update-and-smoke-kit-32d01fd

cd amn2-vps-update-and-smoke-kit-32d01fd
export VPS_APPLY_ENABLED=false
export AMN2_DIR=/opt/amn2
bash ./amn2_apply_source_zip.sh
install -m 700 ./amn2_api_loopback_smoke.sh /opt/amn2/amn2_api_loopback_smoke.sh
```

## 2. Проверить конфигурацию без вывода секретов

```bash
cd /opt/amn2
source venv/bin/activate
export VPS_APPLY_ENABLED=false

python - <<'PY'
from pathlib import Path
import yaml

data = yaml.safe_load(Path("servers.yml").read_text(encoding="utf-8"))
found = []

def walk(value, path="servers.yml"):
    if isinstance(value, dict):
        for key, child in value.items():
            walk(child, f"{path}.{key}")
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            walk(child, f"{path}[{idx}]")
    elif isinstance(value, str) and value.startswith("CHANGE_ME"):
        found.append(path)

walk(data)
print("placeholders:", len(found))
for path in found:
    print(path)
PY
```

Ожидаемо:

```text
placeholders: 0
```

Если значение больше нуля, исправить только локальный `/opt/amn2/servers.yml`; значения в чат не отправлять.

## 3. API-only smoke

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

Можно вернуть в coordination chat:

- `api-smoke-safe-summary.txt`;
- `api-smoke-result.json`;
- `api-auth-evidence.txt`;
- `api-listener-evidence.txt`;
- `api-audit-evidence.txt`;
- `server-db-sync.txt`;
- путь к `safe_bundle`.

## 4. Web-панель только через loopback

Запустить web-панель вручную:

```bash
cd /opt/amn2
source venv/bin/activate
export VPS_APPLY_ENABLED=false
python -m app.cli web serve --host 127.0.0.1 --port 3030
```

На локальной машине оператора открыть SSH tunnel:

```bash
ssh -L 3030:127.0.0.1:3030 root@<VPS_HOST>
```

Открыть в браузере:

```text
http://127.0.0.1:3030/login
```

Минимальная проверка без публикации секретов:

- login проходит;
- dashboard открывается;
- `/servers` показывает server `local`;
- server detail открывается;
- API readiness/status page открывается после реализации;
- API token lifecycle page открывается после реализации;
- при issue API token raw token отображается один раз и не попадает в logs/chat;
- revoke API token отражается в UI;
- после revoke loopback API request с этим token получает `401`;
- в UI нет `.conf`, QR, `vpn://`, private key, PSK, token hash.

## 5. Отдельный SSH/server dry-run gate

Запускать только если оператор отдельно решил проверить SSH/server контур. Это не часть API-only smoke.

```bash
cd /opt/amn2
source venv/bin/activate
export VPS_APPLY_ENABLED=false

python -m app.cli bot check-network
python -m app.cli server preflight --config servers.yml --server local --db data/amneziya.sqlite3
python -m app.cli server check --config servers.yml --server local --dry-run
```

Ожидаемо команды показывают dry-run план и `No changes will be made`. Если появляется `--apply`, Docker restart, config write или peer mutation вне dry-run, остановиться и не продолжать.

## 6. Что считается готовым VPS evidence

Gate считается пройденным, если:

- API-only smoke `VPS verdict: pass`;
- web-панель проверена только через loopback/tunnel;
- `VPS_APPLY_ENABLED=false` во всех командах;
- не выполнялись live apply/revoke/config delivery;
- в AMN3 возвращены только safe summary/evidence;
- оператор отдельно подтвердил, что UI не показал secret-bearing artifacts.
