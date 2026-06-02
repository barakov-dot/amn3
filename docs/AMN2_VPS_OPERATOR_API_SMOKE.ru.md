# AMN2 VPS Operator API Smoke

Дата: 2026-06-02.

Назначение: дать оператору автономный способ проверить `amn2/codex/read-only-api-route-shell` на реальном VPS без передачи доступа в чат и без публикации секретов.

Пакет проверки:

```text
scripts/vps/amn2_api_loopback_smoke.sh
```

Готовый zip для загрузки:

```text
dist/amn2-api-vps-smoke-operator-kit-2026-06-02.zip
dist/amn2-api-vps-smoke-operator-kit-2026-06-02.zip.sha256.txt
```

Скрипт делает только loopback read-only API smoke:

- проверяет, что `VPS_APPLY_ENABLED=false`;
- запускает API только на `127.0.0.1`;
- выдает временный scoped token с `server:read` и `metrics:read`;
- не печатает raw token в итоговый вывод;
- выполняет `api smoke-check`;
- проверяет missing bearer, wrong scope и revoked token;
- проверяет audit metadata на отсутствие token/header/hash/config/key markers;
- собирает safe evidence bundle.

Скрипт не делает peer apply/revoke, не читает `.conf`, QR, `vpn://`, private keys, PSK, не вызывает Docker restart и не открывает API наружу.

Если скрипт останавливается на:

```text
ModuleNotFoundError: No module named 'app.api'
```

значит на VPS установлен старый source tree без read-only API route shell. В этом случае сначала использовать:

```text
docs/AMN2_VPS_API_UPDATE_AND_SMOKE.ru.md
dist/amn2-api-vps-update-and-smoke-kit-2026-06-02.zip
```

## 1. Подготовить ветку на VPS

Если `/opt/amn2` является git checkout:

```bash
cd /opt/amn2
git fetch origin codex/read-only-api-route-shell
git switch codex/read-only-api-route-shell
git pull --ff-only origin codex/read-only-api-route-shell
git log -1 --oneline
```

Ожидаемая рабочая точка:

```text
2010d60 Add API VPS smoke evidence template
```

Установить зависимости в активный venv:

```bash
cd /opt/amn2
source venv/bin/activate
python -m pip install -e .
```

Если `/opt/amn2` установлен из zip без `.git`, сначала нужно заменить source tree на сборку/checkout ветки `codex/read-only-api-route-shell`. Старый stable package `dist/amn2-vps-install-d0939d8.zip` не содержит read-only API route shell.

## 2. Загрузить скрипт

С локальной машины:

```powershell
cd C:\Users\SooL\Documents\VPS-OPS-LAB
scp .\scripts\vps\amn2_api_loopback_smoke.sh root@<VPS_HOST>:/root/amn2_api_loopback_smoke.sh
```

Или загрузить готовый zip:

```powershell
cd C:\Users\SooL\Documents\VPS-OPS-LAB
scp .\dist\amn2-api-vps-smoke-operator-kit-2026-06-02.zip root@<VPS_HOST>:/root/
scp .\dist\amn2-api-vps-smoke-operator-kit-2026-06-02.zip.sha256.txt root@<VPS_HOST>:/root/
```

На VPS:

```bash
install -m 700 /root/amn2_api_loopback_smoke.sh /opt/amn2/amn2_api_loopback_smoke.sh
```

Если загружен zip:

```bash
cd /root
sha256sum -c amn2-api-vps-smoke-operator-kit-2026-06-02.zip.sha256.txt
python3 - <<'PY'
import hashlib
from pathlib import Path

path = Path("amn2-api-vps-smoke-operator-kit-2026-06-02.zip")
print(hashlib.sha256(path.read_bytes()).hexdigest().upper())
PY
mkdir -p amn2-api-vps-smoke-kit-2026-06-02
python3 -m zipfile -e amn2-api-vps-smoke-operator-kit-2026-06-02.zip amn2-api-vps-smoke-kit-2026-06-02
install -m 700 /root/amn2-api-vps-smoke-kit-2026-06-02/amn2_api_loopback_smoke.sh /opt/amn2/amn2_api_loopback_smoke.sh
```

## 3. Запустить smoke

Минимальный запуск:

```bash
cd /opt/amn2
export VPS_APPLY_ENABLED=false
export AMN2_SERVER_NAME=debian-vps-1
bash ./amn2_api_loopback_smoke.sh
```

Если пути отличаются:

```bash
cd /opt/amn2
export VPS_APPLY_ENABLED=false
export AMN2_DIR=/opt/amn2
export AMN2_DB=data/amneziya.sqlite3
export AMN2_CONFIG=servers.yml
export AMN2_SERVER_NAME=debian-vps-1
export AMN2_API_PORT=3040
bash ./amn2_api_loopback_smoke.sh
```

Опциональные флаги:

```bash
export AMN2_RUN_PREFLIGHT=auto
export AMN2_REQUIRE_PREFLIGHT=0
export AMN2_EXPECTED_COMMIT=2010d60
```

`AMN2_RUN_PREFLIGHT=auto` запускает `server preflight` и `server check --dry-run`, если найден `servers.yml`. Это локальная/preview проверка, без live apply.

## 4. Что прислать обратно

После успешного запуска скрипт напечатает путь:

```text
safe_bundle: /opt/amn2/vps-smoke/api-loopback-safe-evidence-<RUN_ID>.tar.gz
```

Можно прислать:

- сам `api-loopback-safe-evidence-<RUN_ID>.tar.gz`;
- или текст из `api-smoke-safe-summary.txt`;
- `api-smoke-result.json`;
- `api-auth/audit/listener` evidence из bundle.

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
- полный `api-server.log`, если он не проверен и не отредактирован оператором.

## 5. Как читать результат

Успех:

```text
VPS verdict: pass
api_smoke_status: passed
auth_status: passed
listener_status: passed
audit_status: passed
```

Блокер:

```text
VPS verdict: blocked
```

При `blocked` не расширять API и не начинать PR/merge. Нужно передать safe bundle и кратко указать, какая строка failed: imports, preflight, smoke, auth, listener или audit.

Если в старой версии скрипта перед summary были строки `curl: (7) Failed to connect`, это был шум ожидания старта API. Это не ошибка, если `api_ready_status`, `api_smoke_status`, `auth_status` и `audit_status` равны `passed`.

Если единственный blocker - `listener_status: failed`, прислать только safe `api-listener-evidence.txt` или перезапустить обновленный `scripts/vps/amn2_api_loopback_smoke.sh`. Обновленная версия проверяет listener по PID временного API-процесса и не печатает startup polling noise.

## 6. Что делать после pass

После `pass` в coordination chat можно принять решение:

1. открыть PR/merge `codex/read-only-api-route-shell` обратно в stable `codex-vps-test-prep`;
2. обновить AMN3 transfer evidence;
3. только потом планировать следующий API/web panel slice.

Write API, `/clients` CRUD, API `config:read`, public config delivery, backup/import/reboot и routes, которые вызывают SSH/sync/config/runtime writes, остаются заблокированы до отдельного controlled VPS gate.
