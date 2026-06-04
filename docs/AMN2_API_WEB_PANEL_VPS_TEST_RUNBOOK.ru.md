# AMN2 API/Web Panel VPS Test Runbook

Дата: 2026-06-04.

Назначение: зафиксировать, что делать на VPS при следующих API/web-panel доработках после подтвержденного API-only pass `run_id=20260603T112418Z`. Этот runbook не является разрешением на live apply/revoke/config delivery.

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

Важно: пакет `5f12736` ниже является текущим verified baseline package. После реализации API/web-panel slice в `amn2` нужно пересобрать AMN3 install/update package от нового production head и заменить имя архива/SHA в этом разделе перед VPS тестом новой панели.

```bash
cd /root

curl -fL -o amn2-vps-update-and-smoke-kit-5f12736.zip \
  https://github.com/barakov-dot/amn3/raw/master/dist/amn2-vps-update-and-smoke-kit-5f12736.zip

curl -fL -o amn2-vps-update-and-smoke-kit-5f12736.zip.sha256.txt \
  https://raw.githubusercontent.com/barakov-dot/amn3/master/dist/amn2-vps-update-and-smoke-kit-5f12736.zip.sha256.txt

sha256sum -c amn2-vps-update-and-smoke-kit-5f12736.zip.sha256.txt
```

Ожидаемый SHA256:

```text
557C3B0C589BE98E1F5780DBBF289ACB3EB350F468BF369A6672B2A10DB2BB3C
```

Распаковать и применить source overlay:

```bash
rm -rf amn2-vps-update-and-smoke-kit-5f12736
mkdir -p amn2-vps-update-and-smoke-kit-5f12736
python3 -m zipfile -e amn2-vps-update-and-smoke-kit-5f12736.zip amn2-vps-update-and-smoke-kit-5f12736

cd amn2-vps-update-and-smoke-kit-5f12736
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
