# PRVTPRO/Amnezia-Web-Panel

## Паспорт

- Репозиторий: https://github.com/PRVTPRO/Amnezia-Web-Panel
- Дата первичного анализа: 2026-05-29
- Тип проекта: web-панель управления удаленными VPN-серверами и связанными сервисами.
- Основной стек: Python, FastAPI, Jinja2, Vanilla JS, Paramiko, локальное JSON-хранилище, Docker.
- Лицензия: GNU GPL v3.0.
- Статус для `amn2`: только исследование идей, без копирования кода.
- Статус для будущего гибридного проекта: полезный upstream для UX, multi-protocol orchestration и production-checklist.

## Краткое описание

Amnezia Web Panel - web-интерфейс для управления AmneziaWG, classic WireGuard, Xray Reality, Telegram MTProxy, AmneziaDNS, AdGuard Home и SOCKS5 на удаленных Ubuntu-серверах через единую панель.

README заявляет совместимость с официальными Amnezia-клиентами: можно добавить уже настроенный сервер по IP, логину и паролю, после чего панель должна определить установленные протоколы, пользователей и текущую конфигурацию.

Проект позиционируется как research/educational abstraction layer над публично доступными приложениями, а не как собственная реализация всех нижележащих VPN-компонентов.

## Лицензия и ограничения

В репозитории указан `LICENSE` с GNU GPL v3.0, а README отдельно говорит, что проект лицензирован под GNU GPL v3.0.

Вывод для `amn2`:

- код, структуру файлов, UI-реализацию, manager-скрипты, Dockerfile, API-роуты и точные install-flow переносить нельзя без отдельной юридической проверки;
- идеи можно изучать как архитектурные паттерны, но реализация в `amn2` должна быть самостоятельной;
- любые заимствования текста, UI-ассетов, скриптов или конфигураций требуют отдельной проверки и, скорее всего, не подходят для production-направления `amn2`.

Первичный license verdict: `research-only`. В `amn2` переносить только самостоятельно спроектированные идеи.

## Архитектура и стек

По README и `app.py` проект построен как FastAPI-приложение с HTML-шаблонами, JSON API, Swagger UI и кастомным ReDoc.

Состояние хранится в локальном `data.json`. В `app.py` есть `asyncio.Lock` для потокобезопасной записи, а структура состояния включает servers, users, user_connections, api_tokens и settings.

Удаленные серверы управляются через Paramiko/SSH. В README описана папка `managers/`, где разные протоколы и сервисы вынесены в отдельные manager-файлы: AmneziaWG, WireGuard, Xray, Telemt, DNS, AdGuard, SOCKS5 и SSH abstraction.

Docker-сценарий простой: официальный образ `prvtpro/amnezia-panel:1.4.3`, порт `5000`, volume для `/app/data`, restart policy и healthcheck через локальное TCP-подключение к приложению.

## Полезные идеи для `amn2`

- Feature gate перед production-переносом: отдельно проверять лицензию, пользу, риски, архитектурную совместимость и тест-план.
- API tokens для интеграций: raw token показывается один раз, в хранилище лежит только SHA-256 hash.
- Command execution contract для remote operations: отделять план, выполнение, audit, redaction и recovery note.
- Ролевые пользователи панели: admin, support, regular user.
- Self-service endpoints для обычного пользователя, отделенные от admin API.
- Public sharing через token-protected links без доступа к панели.
- JSON backup/restore как минимальный disaster-recovery механизм для небольшой панели.
- Live ping indicator и параллельная проверка статусов протоколов, чтобы UI не зависал на медленных endpoint-ах.
- Группировка OpenAPI-документации по доменам: Authentication, Servers, Protocols, Connections, Users, Settings, API Tokens.
- Явное предупреждение после первого входа с default credentials.

## Полезные идеи для будущего гибридного проекта

- Единая панель для нескольких типов сервисов: VPN-протоколы, DNS, ad blocking, proxy, Telegram-интеграция.
- Attach existing server flow: подключение уже настроенного узла с автоопределением протоколов, пользователей и конфигурации.
- Multi-protocol manager architecture: общий слой SSH плюс отдельные manager-объекты на каждый протокол.
- Два режима установки AdGuard Home: replacement для базового DNS и side-by-side deployment.
- Telegram bot как внешний канал уведомлений и ограниченного управления.
- Remnawave sync как пример интеграции с внешней системой пользователей.
- i18n с несколькими языками и RTL-поддержкой.

## UX и production-подходы

Интересны не визуальные детали, а продуктовые сценарии:

- onboarding существующего сервера;
- статусная модель серверов и протоколов;
- отдельные роли пользователей;
- backup/restore из UI;
- API documentation прямо в панели;
- settings surface для токенов, Telegram, sync и внешних интеграций;
- security recommendations в README: reverse proxy, SSL, SSH keys, SECRET_KEY, token rotation.

## Риски

- GPL-3.0 делает проект непригодным для прямого копирования в `amn2` без совместимости лицензий.
- README указывает default login `admin` / `admin`, что требует жесткого first-run hardening в любом production-дизайне.
- `SECRET_KEY` берется из environment или генерируется на старте. Для production важно запрещать ephemeral secret без явной конфигурации.
- Локальное JSON-хранилище удобно для старта, но требует осторожной оценки на backup, concurrency, corruption recovery и масштабирование.
- Управление через SSH и sudo-скрипты имеет высокий operational-риск: нужны dry-run, audit log, least privilege и rollback-подход.
- Dockerfile использует `python:3.14-slim`, а README заявляет prerequisites Python 3.10+. Это стоит проверить отдельно как consistency risk.
- В requirements одновременно есть FastAPI и Flask/Werkzeug. Возможно, это legacy-зависимости или смешанный стек, нужно проверить перед выводами о чистоте архитектуры.
- README не показывает тестовый контур. Для production-переноса в `amn2` любая идея должна получить отдельный тест-план.

## Решение

Проект стоит держать в `research/upstreams` как сильный UX/architecture reference, но не как источник кода.

Первичный статус:

- для `amn2`: `candidate ideas only`;
- для гибридного проекта: `high-signal reference`;
- для копирования кода: `blocked by GPL-3.0 until separate legal decision`.

## Следующие шаги

- Auth/session/secrets deep-dive выполнен: [prvtpro-amnezia-web-panel-auth-secrets.md](prvtpro-amnezia-web-panel-auth-secrets.md).
- API surface deep-dive выполнен: [prvtpro-amnezia-web-panel-api-surface.md](prvtpro-amnezia-web-panel-api-surface.md).
- Manager/SSH/protocol architecture deep-dive выполнен: [prvtpro-amnezia-web-panel-manager-architecture.md](prvtpro-amnezia-web-panel-manager-architecture.md).
- Составить feature gap таблицу `amn2` vs Amnezia Web Panel после просмотра текущего `amn2`.

## Источники

- Репозиторий: https://github.com/PRVTPRO/Amnezia-Web-Panel
- README: https://github.com/PRVTPRO/Amnezia-Web-Panel/blob/main/README.md
- LICENSE: https://github.com/PRVTPRO/Amnezia-Web-Panel/blob/main/LICENSE
- `app.py`: https://github.com/PRVTPRO/Amnezia-Web-Panel/blob/main/app.py
- `requirements.txt`: https://github.com/PRVTPRO/Amnezia-Web-Panel/blob/main/requirements.txt
- `docker-compose.yml`: https://github.com/PRVTPRO/Amnezia-Web-Panel/blob/main/docker-compose.yml
- `Dockerfile`: https://github.com/PRVTPRO/Amnezia-Web-Panel/blob/main/Dockerfile

## Deep-dive материалы

- [Auth, secrets и API tokens](prvtpro-amnezia-web-panel-auth-secrets.md)
- [API surface и route guards](prvtpro-amnezia-web-panel-api-surface.md)
- [Manager architecture](prvtpro-amnezia-web-panel-manager-architecture.md)
