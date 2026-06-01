# API VPS Smoke Evidence

Заполнять после реального VPS smoke на ветке `codex/read-only-api-route-shell`.

Цель документа - зафиксировать только безопасные факты проверки read-only API shell. Не вставлять raw API token, Authorization header, token hash, `.conf`, QR, `vpn://`, `PrivateKey`, `PresharedKey`, SSH password/private key или полные response bodies.

## 1. Контекст

```text
Дата и время проверки:
VPS alias:
Оператор:
Branch:
Commit:
Python:
Database path:
API bind:
```

Минимальные команды для заполнения:

```bash
git status --short
git log -1 --oneline
python --version
python -m app.cli api token issue --db data/amneziya.sqlite3 --name vps-smoke --owner-label ops --scope server:read --scope metrics:read --expires-at "$(date -u -d '+7 days' '+%Y-%m-%dT%H:%M:%S+00:00')" --pretty
python -m app.cli api serve --host 127.0.0.1 --port 3040
python -m app.cli api smoke-check --base-url http://127.0.0.1:3040 --token "$API_TOKEN" --server-name debian-vps-1 --pretty
python -m app.cli api token revoke --db data/amneziya.sqlite3 --token-id "$TOKEN_ID" --reason smoke-complete --pretty
```

## 2. Route Evidence

Фиксировать только HTTP code, aggregate counts и forbidden marker status.

```text
GET /api/servers:
  HTTP:
  server_count:
  forbidden_markers:

GET /api/servers/{server_name}/summary:
  HTTP:
  server_name:
  device_counts.total:
  health.status:
  forbidden_markers:

GET /api/metrics/summary:
  HTTP:
  users.total:
  servers.total:
  devices.total:
  traffic.rx_bytes:
  traffic.tx_bytes:
  forbidden_markers:

GET /api/users/summary:
  HTTP:
  users.total:
  users.active:
  users.blocked:
  users.deleted:
  orders.total:
  forbidden_markers:
```

## 3. Auth And Scope Evidence

```text
Missing bearer token:
  route:
  expected HTTP:
  actual HTTP:

Wrong scope:
  route:
  token scope used:
  expected HTTP:
  actual HTTP:

Revoked token after smoke:
  token_id:
  revoke status:
  route retest HTTP:
```

## 4. Audit Evidence

Проверить, что successful read routes пишут `api_read` без секретов.

```bash
sqlite3 data/amneziya.sqlite3 "SELECT action, metadata_json FROM admin_actions WHERE action='api_read' ORDER BY id DESC LIMIT 5;"
```

```text
api_read rows present:
metadata contains method/path/scope/token_id:
metadata does not contain raw API token:
metadata does not contain Authorization header:
metadata does not contain token hash:
metadata does not contain response body:
```

## 5. Network Exposure Evidence

```text
Loopback check:
  curl http://127.0.0.1:3040/api/servers:
  local bind:

External exposure check:
  command used:
  expected:
  actual:
```

API должен оставаться на loopback (`127.0.0.1`) до отдельного решения о reverse proxy, TLS, rate-limit и production auth boundary.

## 6. VPS verdict

```text
VPS verdict: pass / blocked / fail
Blocker:
Safe evidence attached:
Next local action:
Next VPS action:
```

## 7. Если проверка не прошла

Прислать только безопасные данные:

- `git log -1 --oneline`;
- вывод `python -m app.cli api smoke-check ... --pretty` без raw token;
- HTTP-коды routes;
- aggregate counts;
- последние `api_read` metadata без token/hash/header;
- `journalctl`/`logs/app.log` только после redaction.

Не присылать:

- raw API token;
- Authorization header;
- token hash;
- `.conf`, QR или `vpn://`;
- `PrivateKey`;
- `PresharedKey`;
- SSH secrets;
- полные response bodies, если в них есть сомнения.
