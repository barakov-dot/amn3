# Web Admin Panel Design

## Цель

Добавить локальную web-панель управления Amneziya на порту `3030`, чтобы администратор мог визуально управлять пользователями, серверами и диагностикой без Telegram-интерфейса. Панель должна быть пригодна для первого VPS-запуска: простая эксплуатация, минимальная зависимость от frontend-сборки, безопасная авторизация и понятное логирование.

## Контекст

Сейчас управление идет через Telegram bot и CLI. База данных уже содержит основные сущности: `users`, `servers`, `devices`, `orders`, `admin_actions`, `device_traffic_snapshots`, `message_templates`. Настройки читаются из `.env` через `app.config.Settings`. Для VPS уже есть `server check`, `apply-peer`, `revoke-peer`, `collect-traffic` и `bot check-network`.

## Рекомендуемый подход

Использовать `FastAPI + Jinja2 + Uvicorn` внутри существующего Python-проекта.

Причины:

- один runtime и один dependency stack с текущим приложением;
- нет Node.js build step на VPS;
- server-rendered UI достаточно для CRUD, логов и диагностических экранов;
- легко переиспользовать существующие `Repository`, `Settings`, redaction и сервисы.

React/Vue SPA пока не нужен: он усложнит деплой и авторизацию, а ценность на первом этапе даст именно надежная админская поверхность.

## Новые настройки `.env`

```env
WEB_ADMIN_ENABLED=false
WEB_ADMIN_HOST=0.0.0.0
WEB_ADMIN_PORT=3030
WEB_ADMIN_USERNAME=admin
WEB_ADMIN_PASSWORD_HASH=replace-with-password-hash
WEB_ADMIN_SESSION_SECRET=replace-with-generated-random-secret-32-plus-chars
WEB_ADMIN_SESSION_COOKIE_SECURE=true
APP_LOG_ENABLED=true
APP_LOG_LEVEL=INFO
APP_LOG_MAX_LINES=500
APP_LOG_PATH=logs/app.log
CLIENT_CONFIG_TEMPLATE_DIR=config_templates
EMAIL_DELIVERY_ENABLED=false
SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM=
SMTP_USE_TLS=true
EMAIL_REQUIRE_VERIFICATION=true
EMAIL_RECOVERY_TOKEN_TTL_MINUTES=30
EMAIL_CONFIG_ATTACHMENTS_ENABLED=true
```

`WEB_ADMIN_PASSWORD_HASH` хранит hash пароля, не исходный пароль. Если hash пустой или placeholder, web-панель должна отказаться стартовать и вывести понятную ошибку. `WEB_ADMIN_SESSION_SECRET` используется для signed session cookie и должен храниться отдельно вместе с `.env`. `WEB_ADMIN_SESSION_COOKIE_SECURE=true` включает Secure flag для cookie; при временном plain HTTP-тесте на `:3030` его можно явно выключить, но production-доступ должен идти через HTTPS/reverse proxy или SSH tunnel.

`APP_LOG_ENABLED=false` отключает запись application log. `APP_LOG_LEVEL` поддерживает `DEBUG`, `INFO`, `WARNING`, `ERROR`. `APP_LOG_MAX_LINES` задает глубину просмотра в UI, а не бесконечное хранение. Ротация файла может быть простой: ограничение размера через Python logging rotating handler.

`CLIENT_CONFIG_TEMPLATE_DIR` задает внешнюю директорию с редактируемыми шаблонами клиентских конфигов. Если директория пуста или не задана, используются дефолтные шаблоны из кода. На VPS лучше хранить локальные шаблоны вне package-каталога, чтобы обновление через `git pull` не перетирало ручные правки.

Email-канал по умолчанию выключен. Если `EMAIL_DELIVERY_ENABLED=true`, должны быть заданы `SMTP_HOST` и `SMTP_FROM`; пароль SMTP хранится только в `.env` и редактируется вне UI. `EMAIL_REQUIRE_VERIFICATION=true` означает, что конфиги и recovery-письма отправляются только на подтвержденный адрес.

## Архитектура

```mermaid
flowchart TD
    CLI["python -m app.cli web serve"] --> WebApp["FastAPI app"]
    WebApp --> Auth["Session auth middleware"]
    WebApp --> Templates["Jinja2 templates"]
    WebApp --> Repo["Repository"]
    Repo --> DB["SQLite database"]
    WebApp --> Logs["Log reader / redaction"]
    WebApp --> ServerConfig["servers.yml loader"]
    WebApp --> ConfigTemplates["Client config templates"]
    WebApp --> Email["Email delivery / recovery"]
```

Панель запускается отдельным процессом от Telegram bot:

```bash
python -m app.cli web serve --host 0.0.0.0 --port 3030
```

Флаги CLI могут переопределять `.env`, но defaults берутся из `Settings`.

## Авторизация

Панель использует форму входа `/login`:

- username сравнивается с `WEB_ADMIN_USERNAME`;
- password проверяется против `WEB_ADMIN_PASSWORD_HASH`;
- при успехе выставляется signed session cookie;
- `/logout` удаляет сессию;
- все страницы, кроме `/login` и health endpoint, требуют авторизации.

На первом этапе достаточно одного web-admin аккаунта из `.env`. Telegram-admin роли не дают автоматический web-доступ.

## UI и страницы

Панель должна быть рабочей поверхностью, не landing page:

- `/` Dashboard: состояние БД, количество пользователей, активных устройств, pending orders, серверов, последние ошибки.
- `/users`: таблица пользователей с поиском по Telegram ID, username, имени; действия добавления, редактирования, блокировки, soft-delete.
- `/users/new`: создание пользователя по Telegram ID, username, first/last name, email, admin flag.
- `/users/{id}`: карточка пользователя, статус, admin flag, email/verification status, устройства, заявки, последние admin actions.
- `/servers`: таблица всех серверов из БД и связанной конфигурации; ручной status, live-состояние, ping/latency, SSH reachability, endpoint, VPN port, devices count, время последней проверки.
- `/servers/new`: добавление серверной записи в БД; секреты не вводятся и не показываются.
- `/servers/{id}`: редактирование host, ssh port, endpoint host, vpn port, network CIDR, server address, server public key, runtime, firewall, status, max devices.
- `/servers/{id}/health`: карточка live-диагностики сервера: ping/latency, TCP/SSH доступность, read-only `server check`, состояние `awg-quick`, видимость UDP-порта, последняя ошибка.
- `/orders`: pending/fulfilled/rejected заявки для дебага Telegram flow.
- `/config-templates`: редактируемые шаблоны доставки и клиентских `.conf` файлов, список placeholders, preview итогового конфига и `vpn://` ссылки без сохранения секретов в логах.
- `/email`: диагностика SMTP-настроек, шаблоны email-доставки и recovery, последние безопасные события отправки без секретов.
- `/logs`: просмотр последних `APP_LOG_MAX_LINES`, фильтр по уровню и plain-text поиск.
- `/settings`: read-only страница ключевых runtime-настроек с redaction секретов.

Удаление пользователей и серверов на первом этапе должно быть безопасным:

- пользователь: `status='deleted'` или `status='blocked'`, без физического удаления строк;
- сервер: `status='disabled'`, без физического удаления, если есть связанные устройства;
- физическое удаление можно добавить позже после отдельного backup/restore сценария.

## Управление пользователями

Минимальные действия:

- показывать всех уже существующих пользователей из текущей таблицы `users`, включая созданных ранее через Telegram bot;
- создать пользователя;
- редактировать `telegram_id`, `username`, `first_name`, `last_name`, `email`, `status`, `is_admin`;
- заблокировать пользователя;
- пометить пользователя удаленным;
- видеть, подтвержден ли email, и инициировать повторную проверку адреса;
- посмотреть active/total devices;
- посмотреть последние admin actions.

Изменения должны записываться в `admin_actions` с action вроде `web_user_create`, `web_user_update`, `web_user_block`, `web_user_delete`.

Для web-панели не создается отдельная таблица пользователей. Источник правды - существующая таблица `users`; связанные `devices`, `orders` и `admin_actions` должны отображаться для уже созданных пользователей без миграции или ручного импорта.

## Управление серверами

Минимальные действия:

- создать серверную запись в БД;
- редактировать основные поля сервера;
- отключить сервер;
- посмотреть количество устройств и базовую конфигурацию;
- увидеть live-состояние всех серверов;
- вручную запустить health check для одного сервера;
- обновить health check всех серверов.

Панель не должна хранить SSH private key, пароли или PSK. На первом этапе она управляет серверной записью в БД; `servers.yml` остается runtime-конфигом для SSH/VPS операций. Если поле в БД и `servers.yml` расходятся, UI должен показывать предупреждение на странице сервера.

Live-состояние сервера должно храниться отдельно от ручного `servers.status`. Для этого добавляется таблица `server_health_checks` или эквивалентный repository-слой с полями:

- `server_id`;
- `status`: `online`, `degraded`, `offline`, `unknown`;
- `latency_ms`;
- `ssh_ok`;
- `awg_ok`;
- `udp_port_ok`;
- `checked_at`;
- `error`.

`ping` в UI означает быструю reachability-проверку. Для MVP допустимо использовать TCP connect к SSH-порту с timeout и полный read-only `server check` по кнопке/обновлению. ICMP ping не обязателен, потому что на VPS/firewall он часто отключен.

## Шаблоны клиентских конфигов и доставка

Сейчас в коде уже заложены такие способы получения конфига пользователем:

- Telegram-сообщение по шаблону `config_ready`;
- вложенный `.conf` файл;
- QR PNG, построенный из готового текста конфига;
- повторная отправка пользователем из раздела устройств;
- повторная отправка администратором из админского Telegram-интерфейса;
- аварийный fallback: если отправка файла/QR падает после создания устройства, бот отправляет текст сообщения и сырой конфиг отдельным сообщением.

В доработку web-панели добавляется отдельный слой шаблонов клиентских конфигов:

- дефолтные шаблоны `amneziawg_v1_5.conf.tpl` и `amneziawg_v2.conf.tpl` хранятся в коде;
- локальные VPS-шаблоны могут лежать в `CLIENT_CONFIG_TEMPLATE_DIR` и переопределять дефолты;
- шаблон содержит постоянные строки формата `[Interface]`, `[Peer]`, `DNS`, `AllowedIPs`, `PersistentKeepalive`, obfuscation-поля AmneziaWG и placeholders для переменных значений;
- переменные значения подставляются из текущего flow: `private_key`, `address`, `server_public_key`, `preshared_key`, `endpoint`, `device_id`, `config_version`, параметры сервера и выбранная версия конфига;
- неизвестные placeholders не должны молча исчезать: preview и тесты должны показывать ошибку, чтобы не выдать пользователю битый конфиг;
- web-панель должна показывать текущий шаблон, источник шаблона (default или override), список доступных placeholders и preview на тестовых данных;
- запись шаблона через UI разрешена только во внешнюю директорию `CLIENT_CONFIG_TEMPLATE_DIR`; package defaults остаются read-only.

Для пользователя также добавляется import-link вида `vpn://...`. MVP-формат ссылки выносится в отдельный helper `build_vpn_import_link(config_text)`, чтобы при проверке на реальном AmneziaVPN-клиенте можно было поменять payload в одном месте. Первый вариант payload: URL-safe Base64 от UTF-8 текста готового `.conf` после префикса `vpn://`. Ссылка отображается:

- в Telegram-сообщении через placeholder `{vpn_link}`;
- в web-карточке устройства;
- в preview на странице `/config-templates`;
- в QR payload после подтверждения на реальном клиенте; до подтверждения `.conf` файл остается каноническим способом доставки.

## Email-доставка и восстановление

Если пользователь указывает email, система должна заложить дополнительный канал доставки и восстановления, но только после проверки адреса:

- email хранится в `users.email`, статус проверки - в `users.email_verified_at`;
- новый или измененный email считается неподтвержденным;
- подтверждение выполняется одноразовым кодом/токеном с TTL, token/hash не пишется в лог;
- конфиг можно отправить на email только если `EMAIL_DELIVERY_ENABLED=true`, SMTP настроен, и email подтвержден или админ явно запускает ручную проверку;
- письмо доставки содержит краткую инструкцию, `vpn://` ссылку и, если `EMAIL_CONFIG_ATTACHMENTS_ENABLED=true`, вложенный `.conf`;
- письмо не должно содержать QR по умолчанию, чтобы не плодить тяжелые вложения; QR остается в Telegram/web;
- восстановление отправляется только на ранее подтвержденный email и использует одноразовую recovery-ссылку/код;
- recovery-ссылка не должна раскрывать полный конфиг без проверки токена, TTL и одноразовости;
- все email-события логируются без секретов: user id, device id, канал, статус, тип ошибки, но не конфиг, не токен и не SMTP password.

Минимальный поток восстановления:

1. Пользователь или админ инициирует восстановление для подтвержденного email.
2. Система создает одноразовый recovery token с TTL `EMAIL_RECOVERY_TOKEN_TTL_MINUTES`.
3. Пользователь получает письмо с recovery-ссылкой/кодом.
4. После проверки token система повторно отправляет конфиг на тот же подтвержденный email или показывает в авторизованной web-панели одноразовый download.

Для первого VPS запуска допускается начать с admin-triggered recovery из web-панели. Публичную `/recover` форму можно включать только вместе с rate limiting и понятным аудитом.

## Логирование

Нужно добавить централизованную настройку logging:

- консольные логи остаются для systemd;
- при `APP_LOG_ENABLED=true` пишется `APP_LOG_PATH`;
- уровень берется из `APP_LOG_LEVEL`;
- секреты перед записью проходят через `redact()`;
- web `/logs` показывает только последние `APP_LOG_MAX_LINES`.

Для дебага Telegram/админки полезны события:

- старт приложения;
- успешная/неуспешная web-авторизация без пароля в логе;
- создание/изменение пользователя;
- создание/изменение сервера;
- успешная/неуспешная проверка состояния сервера;
- ошибки handlers;
- network check Telegram;
- VPS apply/revoke/traffic commands и их результат без секретов.

## Ошибки и безопасность

- Все формы используют POST с CSRF token или session-bound nonce.
- Ошибки UI показывают короткое сообщение; подробности идут в лог.
- Секреты не показываются в UI и не пишутся в лог.
- Password hash и session secret проверяются при старте.
- Web-панель должна быть рассчитана на запуск за firewall/VPN/reverse proxy. Публичное выставление порта `3030` без сетевого ограничения не рекомендуется.

## Тестирование

Покрыть тестами:

- Settings читает web/logging параметры;
- login success/failure;
- protected route redirect без session;
- users list/create/update/block/delete;
- servers list/create/update/disable;
- server health check stores online/degraded/offline state and exposes it in UI;
- logs viewer применяет `APP_LOG_MAX_LINES` и redaction;
- client config templates render current AmneziaWG configs, expose placeholders, and show `vpn://` import links;
- email settings, verified user emails, SMTP disabled/error states, and email recovery tokens are covered without logging secrets;
- CLI принимает `web serve`;
- startup отказывается стартовать при пустом password hash.

## Критерии приемки MVP

- `python -m app.cli web serve --host 0.0.0.0 --port 3030` запускает web-панель.
- `/login` принимает корректный логин/пароль и защищает остальные страницы.
- Пользователи, ранее созданные через Telegram bot, отображаются в `/users` и в карточках вместе с их устройствами и заявками.
- Пользователей можно добавить, отредактировать, заблокировать и пометить удаленными.
- Серверы можно добавить, отредактировать и отключить.
- Все серверы отображаются с live-состоянием: online/degraded/offline/unknown, latency, временем последней проверки и последней ошибкой.
- `/config-templates` показывает шаблон сообщения, шаблоны `.conf` по версиям, preview, доступные placeholders и `vpn://` ссылку.
- Пользователь может получить конфиг как Telegram-текст, `.conf` файл, QR, повторную отправку, `vpn://` ссылку и, если email подтвержден, email-письмо с восстановлением; аварийный fallback сохраняет возможность получить сырой config text.
- Email-восстановление работает только для подтвержденного адреса, с одноразовым TTL-token и без записи секретов в логи.
- `/logs` показывает последние строки логов с redaction.
- `APP_LOG_ENABLED`, `APP_LOG_LEVEL`, `APP_LOG_MAX_LINES`, `APP_LOG_PATH` управляют логированием.
- Все новые behavior-тесты проходят вместе с существующим набором.

## Не входит в MVP

- отдельные роли и multi-admin web accounts;
- React/Vue SPA;
- публичная регистрация пользователей;
- физическое удаление связанных production-записей;
- редактирование SSH private keys и секретов через UI;
- автоматическое provisioning VPS из web-панели.
