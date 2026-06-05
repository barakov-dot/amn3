# Протокол повторного VPS-теста

Короткий порядок действий перед следующим заходом на живой VPS. Цель - обновить сервер до последней версии ветки, проверить базовые зависимости, выполнить read-only проверки и при ошибке собрать полный snapshot.

## 1. Обновить код на VPS

```bash
cd /opt/amn2
git pull origin codex-vps-test-prep
git log -1 --oneline
source venv/bin/activate
python -m pip install -e .
python -m app.cli server retest-plan --config servers.yml --server debian-vps-1 --db data/amneziya.sqlite3
```

Сохранить вывод `git log -1 --oneline`: по нему мы понимаем, действительно ли на сервере последняя сборка.
Команда `server retest-plan` печатает короткий порядок повторного прогона для выбранного сервера и не меняет VPS.

Если соседний API/VPS gate должен проверить remote-operation dry-run/audit срез до слияния в `codex-vps-test-prep`, использовать gate-ветку:

```bash
cd /opt/amn2
git fetch origin codex/remote-operation-vps-gate-prep
git switch codex/remote-operation-vps-gate-prep
git pull origin codex/remote-operation-vps-gate-prep
git log -1 --oneline
source venv/bin/activate
python -m pip install -e .
```

Эта ветка собрана от актуального API-head и включает remote-operation contract, partial-failure model, dry-run/audit metadata и Runtime Registry local gate. Не смешивать выводы этого gate с обычным `codex-vps-test-prep`: в отчете обязательно указать branch и commit hash.

## 2. Проверить окружение перед запуском

```bash
python -m app.cli bot check-network
python -m app.cli server preflight --config servers.yml --server debian-vps-1 --db data/amneziya.sqlite3
python -m app.cli server check --config servers.yml --server debian-vps-1 --dry-run
bash deploy/runtime/check_vps.sh
```

Если в `servers.yml` стоит `ssh.auth.type: password`, перед live health check проверить:

```bash
command -v sshpass
grep '^VPS_SSH_PASSWORD=' .env
```

Если `sshpass` не установлен:

```bash
sudo apt-get update
sudo apt-get install -y sshpass
```

Для Docker-ноды вместо обычного runtime-check:

```bash
AMN_RUNTIME=docker AMN_CONTAINER_NAME=amnezia-awg bash deploy/runtime/check_vps.sh
```

До успешных проверок держать:

```env
VPS_APPLY_ENABLED=false
```

## 3. Проверить SSH host key

Перед первым live SSH-подключением отдельно сверить SSH host key по `docs/SSH_HOST_KEY_VERIFICATION.ru.md`.

Если fingerprint неизвестен, не совпал или появился новый unknown host prompt, остановиться и подтвердить ключ через независимый канал. Не использовать `accept-new` как production-доверие без ручной проверки.

## 4. Проверить read-only API shell

API smoke выполняется только на loopback и только read-only aggregate routes.

Выдать короткоживущий route-scoped token:

```bash
python -m app.cli api token issue \
  --db data/amneziya.sqlite3 \
  --name vps-smoke \
  --owner-label ops \
  --scope server:read \
  --scope metrics:read \
  --expires-at "$(date -u -d '+7 days' '+%Y-%m-%dT%H:%M:%S+00:00')" \
  --pretty
```

Скопировать `raw_token` из вывода только в переменную текущей shell:

```bash
export API_TOKEN='RAW_TOKEN_FROM_ONE_TIME_OUTPUT'
```

В отдельной shell запустить API:

```bash
python -m app.cli api serve --host 127.0.0.1 --port 3040
```

Проверить read-only endpoints:

```bash
curl -sS -H "Authorization: Bearer $API_TOKEN" http://127.0.0.1:3040/api/servers
curl -sS -H "Authorization: Bearer $API_TOKEN" http://127.0.0.1:3040/api/servers/debian-vps-1/summary
curl -sS -H "Authorization: Bearer $API_TOKEN" http://127.0.0.1:3040/api/metrics/summary
curl -sS -H "Authorization: Bearer $API_TOKEN" http://127.0.0.1:3040/api/users/summary
python -m app.cli api smoke-check --base-url http://127.0.0.1:3040 --token "$API_TOKEN" --server-name debian-vps-1 --pretty
```

После проверки отозвать token:

```bash
python -m app.cli api token revoke \
  --db data/amneziya.sqlite3 \
  --token-id TOKEN_ID_FROM_ISSUE_OUTPUT \
  --reason smoke-complete \
  --pretty
```

Если установлен `jq`, можно извлечь `raw_token` и `token_id` без ручного копирования:

```bash
ISSUE_JSON="$(python -m app.cli api token issue --db data/amneziya.sqlite3 --name vps-smoke --owner-label ops --scope server:read --scope metrics:read --expires-at "$(date -u -d '+7 days' '+%Y-%m-%dT%H:%M:%S+00:00')")"
export API_TOKEN="$(printf '%s' "$ISSUE_JSON" | jq -r .raw_token)"
TOKEN_ID="$(printf '%s' "$ISSUE_JSON" | jq -r .token_id)"
```

Не присылать raw API token, token hash, Authorization header, `.conf`, QR, `vpn://`, `PrivateKey` или `PresharedKey`.

Результаты проверки фиксировать в `docs/API_VPS_SMOKE_EVIDENCE.ru.md`: туда заносим только HTTP-коды, aggregate counts, forbidden marker status, `api_read` audit metadata без секретов и итоговый VPS verdict.

## 5. Remote-operation dry-run/audit gate

До любого live `apply-peer --apply` или `revoke-peer --apply` выполнить только preview-команды на тестовом peer:

```bash
printf '%s\n' "$TEST_PEER_PSK" | python -m app.cli server apply-peer --config servers.yml --server debian-vps-1 --public-key TEST_PEER_PUBLIC_KEY --preshared-key-stdin --vpn-ip TEST_VPN_IP --dry-run
python -m app.cli server revoke-peer --config servers.yml --server debian-vps-1 --public-key TEST_PEER_PUBLIC_KEY --dry-run
```

`--preshared-key-stdin` предпочтителен для VPS gate: PSK передается через stdin и не попадает в локальную command line. Старый `--preshared-key` остается только для одноразовых disposable тестов, где оператор явно принял этот риск.

В выводе `apply-peer --dry-run` должны быть:

```text
Operation ID: server.peer.apply
Risk class: remote-state-write
Consistency status: dry-run
Remote side effects:
Rollback note:
```

В выводе `revoke-peer --dry-run` должны быть:

```text
Operation ID: server.peer.revoke
Risk class: remote-state-write
Consistency status: dry-run
Remote side effects:
Rollback note:
```

В выводе не должно быть `TEST_PEER_PSK`, `PrivateKey`, `PresharedKey`, полного `.conf` или `vpn://`.

Live `apply-peer --apply` и `revoke-peer --apply` запускать только после отдельного подтверждения оператора в соседнем чате. Для Docker runtime перед этим еще раз проверить, что `runtime.config_path` указывает на реальный persistent config внутри контейнера.

## 6. Запустить нужный сценарий теста

Проверить web-панель:

```bash
python -m app.cli web serve --host 127.0.0.1 --port 3030
```

Открывать web-панель штатно через SSH tunnel или другой отдельно утвержденный TLS/reverse-proxy/firewall gate. Не публиковать web/API наружу как часть remote-operation dry-run gate.

Проверить бота:

```bash
python -m app.main
```

Если сервисы уже запущены через systemd:

```bash
sudo systemctl status amneziya-web --no-pager
sudo systemctl status amneziya-bot --no-pager
```

В Telegram или web-панели записать, что нажимал перед ошибкой: раздел, кнопка, пользователь, устройство, сервер, примерное время.
В карточке сервера web-панель показывает блок `VPS retest bundle` с теми же базовыми командами для `git pull`, `preflight`, `server check` и `sync-peers`.

## 7. При ошибке собрать snapshot

Обычный runtime:

```bash
bash deploy/runtime/collect_debug_snapshot.sh
```

Docker runtime:

```bash
AMN_RUNTIME=docker AMN_CONTAINER_NAME=amnezia-awg AMN_INTERFACE=awg0 bash deploy/runtime/collect_debug_snapshot.sh
```

Если нужно сохранить в файл:

```bash
AMN_RUNTIME=docker AMN_CONTAINER_NAME=amnezia-awg AMN_INTERFACE=awg0 bash deploy/runtime/collect_debug_snapshot.sh > debug-snapshot.txt 2>&1
```

Перед отправкой файла проверить, что секреты скрыты. Правила маскировки и ручной набор команд описаны в `docs/VPS_LOG_COLLECTION.ru.md`.

## 8. Что прислать для анализа

Прислать:

- branch и commit hash из `git log -1 --oneline`;
- последний commit hash из `git log -1 --oneline`;
- вывод `python -m app.cli server check --config servers.yml --server debian-vps-1 --dry-run`;
- вывод `apply-peer --dry-run` и `revoke-peer --dry-run` с проверкой, что секреты скрыты;
- вывод `python -m app.cli server check --config servers.yml --server debian-vps-1`, если запускался;
- статус API smoke: HTTP-коды и безопасные aggregate counts без raw token и без Authorization header;
- вывод `bash deploy/runtime/check_vps.sh` или Docker-варианта;
- debug snapshot из `deploy/runtime/collect_debug_snapshot.sh`;
- последние строки `logs/app.log`, если snapshot не собрался;
- что нажимал перед ошибкой и в какое время.

Не присылать без маскировки:

- `TELEGRAM_BOT_TOKEN`;
- `APP_SECRET_KEY`;
- `WEB_ADMIN_PASSWORD_HASH`;
- `WEB_ADMIN_SESSION_SECRET`;
- `SMTP_PASSWORD`;
- SSH private key;
- `PrivateKey` и `PresharedKey`;
- полный пользовательский `.conf`.

## 9. Когда останавливаемся

Если ошибка относится к Docker `apply-peer` или `revoke-peer`, перед повтором проверить `runtime.config_path` в `servers.yml`: он должен указывать на реальный постоянный конфиг AmneziaWG внутри контейнера. Эти операции переписывают конфиг и выполняют `docker restart <container_name>`, поэтому не включать `VPS_APPLY_ENABLED=true`, пока dry-run и ручной тестовый peer не пройдены.
