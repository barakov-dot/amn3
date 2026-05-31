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
codex-vps-test-prep
```

Текущий актуальный коммит:

```text
Add web VPS readiness summary
```

Не начинать отдельный проект с нуля. Новый чат должен открыть эту же папку, проверить ветку и продолжить от текущего состояния.

## 2. Первый текст для нового чата

Скопировать в новый чат:

```text
Продолжаем проект Amneziya / amn2.

Репозиторий: https://github.com/barakov-dot/amn2.git
Ветка: codex-vps-test-prep
Локальная папка: C:\Users\SooL\Documents\Amneziya
Стартовый документ: docs/NEXT_CHAT_HANDOFF.ru.md

Цель текущего этапа: довести первый живой VPS-тест до стабильного состояния.

Прошу сначала прочитать docs/NEXT_CHAT_HANDOFF.ru.md, затем проверить git status, последний коммит и актуальные документы:
- docs/PRODUCTION_VPS_CHECKLIST.ru.md
- docs/WEB_PANEL_AND_BOT_SETUP.ru.md
- docs/VPS_RETEST_PROTOCOL.ru.md
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
## codex-vps-test-prep...origin/codex-vps-test-prep
```

В `git log -5` верхний коммит должен иметь сообщение `Add web VPS readiness summary`.

Если ветка не совпадает:

```powershell
& 'C:\Program Files\Git\cmd\git.exe' fetch origin
& 'C:\Program Files\Git\cmd\git.exe' switch codex-vps-test-prep
& 'C:\Program Files\Git\cmd\git.exe' pull origin codex-vps-test-prep
```

## 4. Проверка тестов локально

В этой среде тесты запускались через bundled Python и `.codex_deps`:

```powershell
$env:PYTHONPATH='.codex_deps;.'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest -q
```

Последний результат:

```text
423 passed, 1 warning
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
- Инструкция по web-панели и боту: `docs/WEB_PANEL_AND_BOT_SETUP.ru.md`.
- Docker runtime для AmneziaWG: чтение и запись persistent `awg0.conf`, затем `docker restart`.
- Ошибки `PeerApplyError` в Telegram и web-панели теперь показывают безопасную строку `Details`, очищенную через `redact()`.
- В карточке сервера добавлен блок `VPS readiness`: `VPS_APPLY_ENABLED`, `SERVER_CONFIG_PATH`, выбранный сервер из `servers.yml`, runtime/container/config_path, последняя health-проверка и текущий peer sync из сессии браузера.
- Peer sync в карточке сервера:
  - известные peer панели;
  - peer, созданные в приложении Amnezia и еще не помеченные;
  - локальные устройства без peer на сервере;
  - peer, помеченные как `Созданы в Amnezia`.
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
git pull origin codex-vps-test-prep
source venv/bin/activate
python -m pip install -e .
```

Проверить коммит:

```bash
git log -1 --oneline
```

Ожидаемый коммит:

```text
Add web VPS readiness summary
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

## 9. Что проверить на VPS следующим тестом

Порядок проверки:

1. `git log -1 --oneline` показывает коммит `Add web VPS readiness summary`.
2. Web-панель открывается.
3. В карточке сервера блок `VPS readiness` показывает:
   - `VPS_APPLY_ENABLED`;
   - `SERVER_CONFIG_PATH`;
   - найденный сервер из `servers.yml`;
   - Docker runtime `amnezia-awg2`;
   - `runtime.config_path` `/opt/amnezia/awg/awg0.conf`;
   - последнюю health-проверку.
4. `Server check` в панели или CLI показывает `OK`/понятный degraded без SSH/backend ошибок.
5. `Run peer sync` показывает live peers из AmneziaWG, а `VPS readiness` обновляет строку `Peer sync`.
6. Создать нового пользователя через бота или web flow.
7. Одобрить заявку.
8. Если снова будет `PeerApplyError`, прислать строку `Details`.
9. Проверить, что новый клиент получил IP после live `AllowedIPs` из `/opt/amnezia/awg/awg0.conf`.
10. Проверить, что в `awg0.conf` добавился новый `[Peer]`.
11. Проверить, что после добавления был `docker restart amnezia-awg2`.
12. Открыть карточку пользователя в web:
    - устройство видно;
    - secrets скрыты;
    - `Show secrets` раскрывает private key и preshared key.
13. Нажать `Disable VPN`:
    - peer удаляется из AmneziaWG;
    - устройство остается в базе со статусом `disabled`;
    - IP и ключи сохраняются.
14. Нажать `Enable VPN`:
    - peer возвращается в AmneziaWG;
    - IP тот же;
    - ключ тот же;
    - клиентский старый конфиг должен снова работать.

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

1. Пройти VPS retest после коммита `Add web VPS readiness summary`.
2. Подтвердить, что новый IP берется из live `awg0.conf`.
3. Подтвердить disable/enable на реальном Docker runtime.
4. Убедиться, что old/local peers из сети `10.8.0.0/24` не мешают новой live-сети `10.8.1.0/24`.
5. Если `PeerApplyError` повторится, разбирать уже по строке `Details`.
6. Если останутся внешние peer из Amnezia, пометить их как `Созданы в Amnezia` или создать новых управляемых клиентов вместо удаления существующих peer.

Некритично, но полезно дальше:

1. Улучшить UX действий `Enable VPN`/`Disable VPN`: показывать доступность кнопок по статусам устройств.
2. Добавить отдельный экран/фильтр disabled devices.
3. Сделать более удобный audit в карточке пользователя.
4. Добавить будущую email-доставку и восстановление конфигов только для подтвержденного email.
5. Вернуться к идее skill по проекту Amneziya, когда текущий VPS-тест будет стабилен.
6. Позже продолжить исследовательский параллельный проект/hybrid lab по похожему GitHub-проекту.

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
