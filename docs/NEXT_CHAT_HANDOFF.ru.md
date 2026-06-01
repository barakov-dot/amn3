# Переезд в новый чат: Amneziya / amn2

Документ нужен, чтобы продолжить работу в новом чате без перечитывания длинной истории. Новый чат не должен начинаться с нуля: использовать текущую папку проекта и этот handoff как стартовую карту.

## 1. Как переезжаем

Рекомендуемый вариант: новый чат в рамках той же локальной папки проекта.

Локальная папка:

```text
C:\Users\SooL\Documents\Amneziya
```

GitHub:

```text
https://github.com/barakov-dot/amn2.git
```

Рабочая ветка:

```text
codex/read-only-api-route-shell
```

Текущий актуальный фокус:

```text
read-only API route shell + local API hardening before VPS smoke
```

Стабильная проверенная точка живого VPS-цикла помечена тегом:

```text
vps-live-cycle-verified -> d6eda20 Document verified VPS live cycle
```

Не начинать отдельный проект с нуля. Новый чат должен открыть эту же папку, проверить ветку и продолжить от текущего состояния.

## 2. Первый текст для нового чата

Скопировать в новый чат:

```text
Продолжаем проект Amneziya / amn2.

Репозиторий: https://github.com/barakov-dot/amn2.git
Ветка: codex/read-only-api-route-shell
Локальная папка: C:\Users\SooL\Documents\Amneziya
Стартовый документ: docs/NEXT_CHAT_HANDOFF.ru.md

Цель текущего этапа: проверить read-only API shell на реальном VPS через loopback smoke, не открывая write/config routes.

Прошу сначала прочитать docs/NEXT_CHAT_HANDOFF.ru.md, затем проверить git status, последний коммит и актуальные документы:
- docs/PRODUCTION_VPS_CHECKLIST.ru.md
- docs/WEB_PANEL_AND_BOT_SETUP.ru.md
- docs/VPS_RETEST_PROTOCOL.ru.md
- docs/API_VPS_SMOKE_EVIDENCE.ru.md
- docs/VPS_LOG_COLLECTION.ru.md
- docs/SERVER_CONFIG_TEMPLATE.ru.md

Работать не с нуля, а от текущей ветки и текущей папки проекта.
```

## 3. Быстрая проверка локального состояния

В PowerShell из папки проекта:

```powershell
cd C:\Users\SooL\Documents\Amneziya
& 'C:\Program Files\Git\cmd\git.exe' status --short --branch
& 'C:\Program Files\Git\cmd\git.exe' log -5 --oneline --decorate
```

Ожидаем:

```text
## codex/read-only-api-route-shell...amn2/codex/read-only-api-route-shell
```

В `git log -5` верхние коммиты должны относиться к read-only API shell и local API hardening.

Тег `vps-live-cycle-verified` должен указывать на коммит `d6eda20 Document verified VPS live cycle`: это последняя точка, где базовый live cycle был проверен на VPS.

Если ветка не совпадает:

```powershell
& 'C:\Program Files\Git\cmd\git.exe' fetch amn2
& 'C:\Program Files\Git\cmd\git.exe' switch codex/read-only-api-route-shell
& 'C:\Program Files\Git\cmd\git.exe' pull amn2 codex/read-only-api-route-shell
```

## 4. Проверка тестов локально

В этой среде тесты запускались через bundled Python и `.codex_deps`:

```powershell
$env:PYTHONPATH='.codex_deps;.'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest -q
```

Последний результат:

```text
588 passed, 1 warning
```

Предупреждение ожидаемое:

```text
StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated
```

## 5. Что уже сделано

Главная линия проекта: Telegram-бот и web-панель для управления AmneziaWG-доступом на живом VPS.

Реализовано и залито в GitHub:

- SOCKS5 proxy для Telegram через `.env` без системного proxy.
- Web-панель на порту `3030` с авторизацией по логину и паролю.
- Управление пользователями, серверами, заявками, логами, настройками.
- Отображение пользователей, созданных через бота.
- Шаблоны клиентского конфига, редактор `.conf.tpl` override-файлов и preview `vpn://`.
- Постоянные параметры клиентского AmneziaWG-конфига (`DNS`, `AllowedIPs`, `PersistentKeepalive`, `Jc/Jmin/Jmax/S1-S4/H1-H4/I1-I5`) вынесены в `CLIENT_*` настройки `.env`; `H1-H4` принимают и числа, и диапазоны из `awg show`, `I2-I5` могут быть пустыми, ключи, `Address`, имя устройства и имя файла остаются уникальными на каждое устройство.
- Если `server_address` в `servers.yml` указан с CIDR-префиксом, например `10.8.1.1/24`, приложение использует его как фактическую сеть `10.8.1.0/24`; это защищает от старого `network_cidr: 10.8.0.0/24`.
- Инструкция по web-панели и боту: `docs/WEB_PANEL_AND_BOT_SETUP.ru.md`.
- Docker runtime для AmneziaWG: чтение и запись persistent `awg0.conf`, затем `docker restart`.
- Ошибки `PeerApplyError` в Telegram и web-панели теперь показывают безопасную строку `Details`, очищенную через `redact()`.
- В карточке сервера добавлен блок `VPS readiness`: `VPS_APPLY_ENABLED`, `SERVER_CONFIG_PATH`, выбранный сервер из `servers.yml`, runtime/container/config_path, последняя health-проверка и текущий peer sync из сессии браузера.
- В карточке сервера добавлен блок `VPS retest bundle`, а в CLI команда `python -m app.cli server retest-plan`: они печатают безопасный порядок повторного VPS-прогона после `git pull`.
- Неудачные VPS-операции теперь пишутся в `admin_actions` с action `*_failed`, `error_type` и `redacted_error`; секреты проходят через `redact()`.
- В карточке сервера добавлен блок `Recent server actions`, где видны последние server-level audit events, включая failed операции.
- Опасные действия web-панели (`Disable VPN`, `Enable VPN`, `Soft delete`, `Delete permanently`, удаление устройства, отключение сервера, добавление missing device в AmneziaWG) теперь требуют browser confirm перед отправкой формы.
- Если `VPS_APPLY_ENABLED=false`, удаление отдельного устройства, `Disable VPN` и `Delete permanently` работают локально без попытки трогать VPS; в `admin_actions.metadata_json` пишется `vps_apply: skipped`.
- В карточке пользователя `Disable VPN` и `Enable VPN` показывают доступность по статусам устройств: active/pending можно отключать, disabled можно включать, а неприменимые действия отображаются disabled с короткой причиной.
- Добавлен экран `/devices/disabled`: список отключенных устройств с владельцем, сервером, IP, причиной/временем отключения и ссылкой на карточку пользователя для повторного включения.
- В карточке пользователя таблица `Admin actions` показывает `target_device_id` и `metadata_json`, чтобы failed VPS-события можно было читать без перехода в базу.
- Email-доставка конфигов и запуск recovery теперь всегда требуют подтвержденный `users.email_verified_at`; старый флаг `EMAIL_REQUIRE_VERIFICATION=false` больше не разрешает отправку конфигов на неподтвержденный адрес.
- Peer sync в карточке сервера:
  - известные peer панели;
  - peer, созданные в приложении Amnezia и еще не помеченные;
  - локальные устройства без peer на сервере;
  - peer, помеченные как `Созданы в Amnezia`.
- Карточка сервера всегда показывает таблицу `Working configs on server` для активных управляемых конфигов из панели сразу после approve, без ручного `Run peer sync`. В строке видны владелец, Telegram ID, устройство, статус, версия конфига, VPN IP и public key.
- Последний `Run peer sync` дополняет эту таблицу live-статусом: `confirmed live`, `missing on server`, `not in last sync` или `sync error`, а также live `AllowedIPs`. Это нужно потому, что peer может работать на сервере, но не отображаться в приложении Amnezia.
- После `Добавить в Amnezia` отчет обновляется и показывает `Added to Amnezia` вместе с добавленным peer.
- Первый живой VPS-цикл подтвержден на сервере: approve создает рабочий peer, конфиг работает, `Run peer sync` показывает `confirmed live`, `Disable VPN`/`Enable VPN` работают, выборочное удаление устройства работает как ожидалось.
- В Telegram выбор версии конфига теперь показывает `AmneziaWG 2.0` первой. В админском списке заявок отображается запрошенная версия, а кнопки approve ставят запрошенную версию заявки первой.
- Добавлен read-only API route shell:
  - `GET /api/servers` под `server:read`;
  - `GET /api/servers/{server_name}/summary` под `server:read`;
  - `GET /api/metrics/summary` под `metrics:read`;
  - `GET /api/users/summary` под `metrics:read`.
- API route shell возвращает только aggregate/safe поля, пишет `api_read` audit events и не выдает `.conf`, QR, `vpn://`, keys, PSK, SSH host/port, endpoint host, raw token или token hash.
- Добавлены CLI-команды для API smoke:
  - `python -m app.cli api token issue`;
  - `python -m app.cli api smoke-check`;
  - `python -m app.cli api token revoke`.
- Добавлен шаблон evidence для реального VPS API smoke: `docs/API_VPS_SMOKE_EVIDENCE.ru.md`.
- Если новый `.conf` снова выглядит как старый шаблон без `S3/S4/I1-I5` и с `AllowedIPs = 0.0.0.0/0`, первым делом проверить `devices.config_version`/`orders.requested_config_version`: это почти наверняка `amneziawg_v1_5`, а не `amneziawg_v2`.
- Действия в карточке сервера:
  - `Пометить как созданный в Amnezia` для внешнего peer;
  - `Снять пометку` для peer, ошибочно помеченного как созданный в Amnezia;
  - `Добавить в Amnezia` для локального устройства без peer на сервере.
- Действия в карточке пользователя:
  - `Block`;
  - `Soft delete`;
  - `Disable VPN`;
  - `Enable VPN`;
  - `Удалить устройство` для выборочного удаления одного устройства;
  - `Delete permanently`.
- `Disable VPN` теперь не делает `revoked`: он удаляет peer из AmneziaWG, но оставляет устройство в базе со статусом `disabled`.
- `Enable VPN` добавляет `disabled` peer обратно в AmneziaWG с тем же IP/public key/preshared key.
- Private key и preshared key сохраняются encrypted в базе; в web-панели показываются под звездочками и раскрываются кнопкой `Show secrets`.
- При создании нового устройства Docker runtime читает live `AllowedIPs` из `runtime.config_path` и выдает следующий IP после уже существующих peer в `awg0.conf`.

## 6. Важные решения и ограничения

`APP_SECRET_KEY` нельзя менять после запуска. Он нужен для расшифровки сохраненных peer-секретов.

`VPS_APPLY_ENABLED=true` включать только когда:

- `servers.yml` указывает на реальную ноду;
- SSH-доступ проверен;
- `runtime.config_path` указывает на настоящий persistent config AmneziaWG;
- команда `server check` проходит;
- понятно, что Docker container restart допустим.

Для Docker runtime добавление/удаление peer меняет файл внутри контейнера:

```text
runtime.config_path: /opt/amnezia/awg/awg0.conf
```

После изменения peer выполняется:

```text
docker restart <container_name>
```

Это важно: без рестарта AmneziaWG на тестовом сервере переставала работать корректно.

Peer, созданные напрямую в приложении Amnezia, не нужно удалять или adopt-ить как существующего клиента, потому что private key неизвестен. Правильная пометка в панели: `Созданы в Amnezia`. Если надо взять такой peer под управление панели, правильный путь: создать нового управляемого пользователя/устройство и выдать новый конфиг.

## 7. Текущее состояние VPS по последним логам

Последняя проверенная реальная нода:

- Docker container: `amnezia-awg2`
- Найденный persistent config: `/opt/amnezia/awg/awg0.conf`
- Live network по `awg0.conf`: `10.8.1.0/24`
- Live peers были:
  - `ArBY+A10VO7V7JtgbQrkkcUHJILdq6NA6lBn3FP2yH4=` с `10.8.1.1/32`
  - `vyCE59B5698fdH0YI+ftTiaMdYKzI0R1gqc9srZf0FU=` с `10.8.1.2/32`
- Локальные старые устройства в базе ранее были в сети `10.8.0.0/24`, что давало рассинхрон.

После последней правки новые устройства должны получать IP после live peer из `awg0.conf`, то есть для приведенного случая следующим ожидается `10.8.1.3`.

## 8. Команды на VPS после обновления из GitHub

На VPS:

```bash
cd /home/amn2
git pull origin codex/read-only-api-route-shell
source venv/bin/activate
python -m pip install -e .
python -m app.cli server retest-plan --config servers.yml --server local --db data/amneziya.sqlite3
```

Проверить коммит:

```bash
git log -1 --oneline
```

Ожидаемый фокус верхнего коммита:

```text
local API hardening / read-only API smoke
```

Проверить server config:

```bash
python -m app.cli server preflight --config servers.yml --server local --db data/amneziya.sqlite3
python -m app.cli server check --config servers.yml --server local
python -m app.cli server sync-peers --config servers.yml --server local --db data/amneziya.sqlite3
```

Если сервисы через systemd:

```bash
sudo systemctl restart amneziya-web
sudo systemctl restart amneziya-bot
sudo systemctl status amneziya-web --no-pager
sudo systemctl status amneziya-bot --no-pager
```

Если вручную:

```bash
python -m app.cli web serve --host 0.0.0.0 --port 3030
python -m app.main
```

Проверить web:

```bash
curl -i http://127.0.0.1:3030/login
tail -n 200 logs/app.log
```

Проверить read-only API smoke:

```bash
python -m app.cli api token issue --db data/amneziya.sqlite3 --name vps-smoke --owner-label ops --scope server:read --scope metrics:read --expires-at "$(date -u -d '+7 days' '+%Y-%m-%dT%H:%M:%S+00:00')" --pretty
export API_TOKEN='RAW_TOKEN_FROM_ONE_TIME_OUTPUT'
python -m app.cli api serve --host 127.0.0.1 --port 3040
python -m app.cli api smoke-check --base-url http://127.0.0.1:3040 --token "$API_TOKEN" --server-name local --pretty
python -m app.cli api token revoke --db data/amneziya.sqlite3 --token-id TOKEN_ID_FROM_ISSUE_OUTPUT --reason smoke-complete --pretty
```

Если на VPS установлен `jq`, можно не копировать id вручную:

```bash
ISSUE_JSON="$(python -m app.cli api token issue --db data/amneziya.sqlite3 --name vps-smoke --owner-label ops --scope server:read --scope metrics:read --expires-at "$(date -u -d '+7 days' '+%Y-%m-%dT%H:%M:%S+00:00')")"
export API_TOKEN="$(printf '%s' "$ISSUE_JSON" | jq -r .raw_token)"
TOKEN_ID="$(printf '%s' "$ISSUE_JSON" | jq -r .token_id)"
```

Результаты VPS smoke после проверки занести в `docs/API_VPS_SMOKE_EVIDENCE.ru.md`: HTTP-коды, aggregate counts, forbidden marker status, safe `api_read` metadata и итоговый verdict.

## 9. Что уже проверено на VPS

Живой цикл на VPS уже прошел успешно:

1. `git log -1 --oneline` показывал актуальный коммит ветки.
2. Web-панель открывалась.
3. `Server check` в панели/CLI проходил без критичных ошибок.
4. Approve заявки создавал peer на сервере.
5. Клиентский конфиг работал.
6. Сразу после approve карточка сервера показывала устройство в `Working configs on server`.
7. После `Run peer sync` устройство переходило в live-статус `confirmed live`.
8. `Disable VPN` удалял peer из AmneziaWG и оставлял устройство в базе со статусом `disabled`.
9. `Enable VPN` возвращал peer обратно с тем же IP/public key/preshared key.
10. Выборочное удаление устройства удаляло нужный peer и не трогало лишние устройства.

Этот набор больше не считается открытым риском. Повторять его полностью нужно только после изменений в approve/sync/enable/disable/delete логике.

## 10. Что прислать в новый чат после теста

Минимальный набор логов:

```bash
cd /home/amn2
git log -1 --oneline
git status --short
python -m app.cli server check --config servers.yml --server local
python -m app.cli server sync-peers --config servers.yml --server local --db data/amneziya.sqlite3
docker exec amnezia-awg2 sh -c 'grep -n "^\[Interface\]\|^\[Peer\]\|^Address\|^ListenPort\|^PublicKey\|^AllowedIPs" /opt/amnezia/awg/awg0.conf | head -120'
tail -n 200 logs/app.log
```

Если используется systemd:

```bash
sudo journalctl -u amneziya-web -n 200 --no-pager
sudo journalctl -u amneziya-bot -n 200 --no-pager
```

Перед отправкой скрыть:

- Telegram bot token;
- `APP_SECRET_KEY`;
- SSH password/private key;
- private keys и preshared keys клиентов;
- полный пользовательский `.conf`, если не нужен для конкретного разбора.

## 11. Ближайшие задачи

Критично перед следующим стабильным этапом:

1. Не трогать базовый VPS live cycle без новой причины: он подтвержден.
2. Если `PeerApplyError` повторится, разбирать уже по строке `Details` и failed event в `admin_actions`.
3. Если останутся внешние peer из Amnezia, пометить их как `Созданы в Amnezia` или создать новых управляемых клиентов вместо удаления существующих peer.
4. Следующий полезный продуктовый шаг выбрать отдельно: например, улучшение UX списков пользователей/устройств, отчеты по traffic, backup/restore или отдельная инструкция эксплуатации.

Некритично, но полезно дальше:

1. Вернуться к идее skill по проекту Amneziya, когда текущий VPS-тест будет стабилен.
2. Позже продолжить исследовательский параллельный проект/hybrid lab по похожему GitHub-проекту.

## 12. Главные файлы проекта

Рабочие документы:

- `docs/PRODUCTION_VPS_CHECKLIST.ru.md`
- `docs/WEB_PANEL_AND_BOT_SETUP.ru.md`
- `docs/VPS_RETEST_PROTOCOL.ru.md`
- `docs/VPS_LOG_COLLECTION.ru.md`
- `docs/SERVER_CONFIG_TEMPLATE.ru.md`
- `docs/RUNTIME_REGISTRY.ru.md`

Кодовые зоны:

- `app/web/app.py`
- `app/web/templates/`
- `app/web/static/admin.css`
- `app/db/schema.py`
- `app/db/repositories.py`
- `app/services/access.py`
- `app/server/peer_apply.py`
- `app/services/peer_inventory.py`
- `app/cli.py`
- `app/main.py`

Тесты:

- `tests/web/test_users.py`
- `tests/web/test_servers.py`
- `tests/db/test_repositories.py`
- `tests/services/test_access_service.py`
- `tests/server/test_peer_apply.py`
- `tests/server/test_cli_server_check.py`
