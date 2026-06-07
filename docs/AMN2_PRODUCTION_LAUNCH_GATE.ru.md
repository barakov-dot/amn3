# AMN2 Production Launch Gate

Дата: 2026-06-07.

Назначение: безопасно перевести текущий срез AMN2 в controlled production режим на `/opt/amn2`, не открывая broad write API и не расширяя поверхность мутаций. Этот gate опирается на уже подтвержденный source overlay `c92bd1a`, VPS smoke `20260607T182131Z` и loopback web/admin systemd template.

## 1. Текущая Точка Правды

```text
workspace: /opt/amn2
source overlay: c92bd1a Bind web admin systemd to loopback
previous evidence commit: 26b1b9a Record source overlay smoke promotion
status: controlled-prod-ready
api bind for smoke: 127.0.0.1:3040
web/admin access: HTTPS reverse proxy
VPS_APPLY_ENABLED=false
```

Уже подтверждено на VPS:

- source update kit применен к `/opt/amn2`;
- runtime сохранен: `data/`, `.env`, `servers.yml`, `venv/`;
- `cat /opt/amn2/.amn2_source_overlay_commit` показывает `c92bd1a`;
- `python -m app.cli api smoke-cycle` прошел: API readiness, auth, listener и audit `passed`;
- `deploy/systemd/amneziya-web.service.example` использует `web serve --host 127.0.0.1 --port 3030`;
- временный smoke token отозван автоматически;
- API 3040 наружу не выставлять.

Operator launch evidence от 2026-06-07 19:24 UTC показал успешный backup/smoke/web-login на фактически наблюдаемом `/opt/amn2 = 42ffa65`. Это safe working-runtime evidence, но текущий gate target остается `c92bd1a`; если VPS показывает `42ffa65`, сначала выровнять source overlay или явно выбрать historical runtime, не смешивая эти статусы.

Для выравнивания использовать короткий runbook: `docs/AMN2_C92_SOURCE_OVERLAY_ALIGNMENT.ru.md`.

## 2. Что Именно Считаем Production Сейчас

Разрешенный controlled production scope:

- operator-only Telegram bot;
- operator-only web/admin через HTTPS reverse proxy;
- существующие verified live peer flows из проекта;
- read-only API smoke/status только на loopback `127.0.0.1:3040`;
- ручные VPS evidence-отчеты без секретов.

Не считать это broad SaaS/API production. До отдельного design/live gate заблокированы:

- `/api/clients write CRUD`;
- API `config:read`;
- public/self-service config delivery;
- Local Agent clients/configs/write mutations;
- backup/import/reboot routes;
- public API exposure;
- detailed per-peer/client metrics;
- restore/import apply;
- full logs, QR, `vpn://`, private keys, PSK or token material in GitHub/chat.

## 3. Stop Conditions

Остановиться и не продолжать production launch, если выполнено хоть одно условие:

- `/opt/amn2/.amn2_source_overlay_commit` не равен `c92bd1a`;
- backup не создается или `backup verify` не проходит;
- `.env`, `servers.yml`, `data/` или `venv/` отсутствуют;
- `VPS_APPLY_ENABLED` неожиданно равен `true` до отдельного live-write окна;
- API 3040 доступен не только на `127.0.0.1`;
- `api smoke-cycle` не дает `api_smoke_status=passed`, либо auth/listener/audit checks не проходят;
- bot `check-network` не проходит;
- `amneziya-web` или `amneziya-bot` flapping/failing в systemd;
- в evidence попали raw API token, Authorization header, token hash, PrivateKey, PresharedKey, QR, `vpn://`, `.env`, full config или полный лог.

## 4. VPS Launch Window

Работать только из `/opt/amn2`.

```bash
cd /opt/amn2
source venv/bin/activate

echo "source overlay:"
cat .amn2_source_overlay_commit

echo "runtime:"
test -d data && echo "data_dir=present" || echo "data_dir=missing"
test -f .env && echo "env_file=present" || echo "env_file=missing"
test -f servers.yml && echo "servers_yml=present" || echo "servers_yml=missing"
test -d venv && echo "venv=present" || echo "venv=missing"

export VPS_APPLY_ENABLED=false
printf 'VPS_APPLY_ENABLED=%s\n' "$VPS_APPLY_ENABLED"
```

Ожидаем:

```text
source overlay: c92bd1a
data_dir=present
env_file=present
servers_yml=present
venv=present
VPS_APPLY_ENABLED=false
```

## 5. Backup Перед Стартом

```bash
cd /opt/amn2
source venv/bin/activate

python -m app.cli backup create --db data/amneziya.sqlite3 --output backups
python -m app.cli backup verify --file backups/<backup-file>.tar.enc
```

В evidence отправлять только:

```text
backup_create: passed
backup_file: backups/<filename-only>.tar.enc
backup_verify: passed
```

Не отправлять `.env`, backup content, raw encryption material or full DB paths outside this shape.

## 6. Safe Preflight

```bash
cd /opt/amn2
source venv/bin/activate

export VPS_APPLY_ENABLED=false
export AMN2_RUN_PREFLIGHT=0
export AMN2_SYNC_SERVER_CONFIG=1
export AMN2_REQUIRE_SERVER_DB_SYNC=1
export AMN2_SERVER_NAME=local

python -m app.cli bot check-network
python -m app.cli server preflight --config servers.yml --server "$AMN2_SERVER_NAME" --db data/amneziya.sqlite3
python -m app.cli server check --config servers.yml --server "$AMN2_SERVER_NAME" --dry-run
```

Если нужен read-only live server check без изменения peer/config, выполнять только после backup verify:

```bash
python -m app.cli server check --config servers.yml --server "$AMN2_SERVER_NAME"
```

## 7. API Smoke Только На Loopback

В одном терминале:

```bash
cd /opt/amn2
source venv/bin/activate

export VPS_APPLY_ENABLED=false
python -m app.cli api serve --host 127.0.0.1 --port 3040
```

Во втором терминале:

```bash
cd /opt/amn2
source venv/bin/activate

python -m app.cli api smoke-cycle \
  --db /opt/amn2/data/amneziya.sqlite3 \
  --base-url http://127.0.0.1:3040 \
  --server-name local \
  --name prod-launch-smoke \
  --owner-label ops \
  --expires-at "$(date -u -d '+7 days' '+%Y-%m-%dT%H:%M:%S+00:00')" \
  --pretty
```

Ожидаем:

```text
status: passed
checked_routes: 6
route status codes: 200
forbidden_markers: []
token.raw_token_display: hidden
revoke.status: revoked
```

Наружу публиковать только этот safe summary. Не публиковать raw API token, Authorization header, token hash, response body, PrivateKey или PresharedKey.

## 8. Web/Admin И Bot В Systemd

Проверить unit templates перед копированием. Если локальные unit уже установлены, сначала сравнить `sudo systemctl cat`.

Для web/admin в текущем approved reverse-proxy режиме template должен слушать только loopback:

```bash
grep -F 'web serve --host 127.0.0.1 --port 3030' deploy/systemd/amneziya-web.service.example
```

Если в unit или template остается `--host 0.0.0.0`, остановиться и заменить на `--host 127.0.0.1` перед `systemctl enable --now`.

```bash
cd /opt/amn2

sudo cp deploy/systemd/amneziya-web.service.example /etc/systemd/system/amneziya-web.service
sudo cp deploy/systemd/amneziya-bot.service.example /etc/systemd/system/amneziya-bot.service

sudo systemctl daemon-reload
sudo systemctl enable --now amneziya-web
sudo systemctl enable --now amneziya-bot

sudo systemctl status amneziya-web --no-pager
sudo systemctl status amneziya-bot --no-pager
```

Минимальная web-проверка:

```bash
curl -sS -o /dev/null -w 'web_login_http=%{http_code}\n' http://127.0.0.1:3030/login
```

Минимальная проверка портов:

```bash
ss -ltnp | grep -E ':3030|:3040' || true
```

Ожидаем:

```text
web 3030: 127.0.0.1/reverse-proxy path only
api 3040: loopback smoke only, not public
```

## 9. Evidence Для Чата И GitHub

Присылать сюда только безопасный итог:

```text
source_overlay_commit: c92bd1a
previous_evidence_commit: 26b1b9a
backup_create: passed
backup_verify: passed
bot_check_network: ok
server_preflight: ok
server_check_dry_run: ok
api_smoke_status: passed
api_auth_status: passed
api_listener_status: passed
api_audit_status: passed
api_token_lifecycle: issued-hidden-and-revoked
web_login_http: <code>
systemd_web: active
systemd_bot: active
api_3040_public: no
VPS_APPLY_ENABLED: false
```

Не присылать:

- raw API token;
- Authorization header;
- token hash;
- `.env`;
- `servers.yml` целиком;
- PrivateKey;
- PresharedKey;
- QR;
- `vpn://`;
- full config;
- full logs.

## 10. Решение После Gate

Если все пункты выше прошли, текущий правильный следующий шаг: открыть controlled production для operator-only web/admin и bot.

Если нужна реальная выдача нового пользователя через web/bot с записью peer на VPS, это отдельное live-write окно:

1. Повторить backup create/verify.
2. Убедиться, что dry-run peer apply/revoke все еще ok.
3. Явно согласовать включение `VPS_APPLY_ENABLED=true`.
4. Выполнить ровно одну тестовую операцию.
5. Проверить sync и рабочий config.
6. Вернуть shell default к `VPS_APPLY_ENABLED=false`.

Broad API, public config delivery, Local Agent mutations и backup/import/reboot API не начинать в этом gate.
