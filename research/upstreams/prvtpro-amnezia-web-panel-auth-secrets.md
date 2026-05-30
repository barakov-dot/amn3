# PRVTPRO/Amnezia-Web-Panel: auth, secrets и API tokens

## Паспорт deep-dive

- Upstream: https://github.com/PRVTPRO/Amnezia-Web-Panel
- Дата анализа: 2026-05-30
- Область: authentication, session handling, API tokens, public sharing, Telegram delivery, secret storage, backup/restore, SSH/sudo model.
- License verdict: GPL-3.0, режим `research-only`.
- Production verdict для `amn2`: идеи полезны, реализация должна быть самостоятельной и более строгой.

## Краткий вывод

В upstream есть сильные продуктовые идеи: единая auth-модель для UI и API, bearer tokens для интеграций, self-service surface, public sharing, Telegram-доставка конфигов и backup/restore. Но текущая security-модель слишком мягкая для прямого production-переноса: много секретов хранится в одном `data.json`, public share tokens хранятся открыто, API tokens слишком широкие по правам, bootstrap использует default admin/admin, а SSH/sudo слой может создавать риск утечки пароля через командную строку и логи.

Для `amn2` это не blueprint, а список требований к будущему безопасному дизайну.

## Auth model

Панель использует session cookie через FastAPI/Starlette `SessionMiddleware`. `SECRET_KEY` берется из environment, а если переменная не задана, генерируется новый случайный ключ при старте.

При первом запуске, если пользователей нет, создается admin-пользователь с паролем `admin`. README отдельно предупреждает, что пароль нужно сменить после первого входа.

Пароли пользователей хранятся не в plaintext: используется PBKDF2-HMAC-SHA256 с солью и 100000 итераций. Это лучше plaintext, но для нового production-дизайна стоит рассматривать современный password hashing policy с параметрами, миграциями и rate limiting.

Captcha есть как опциональная настройка. Она включается только если это задано в settings, то есть базовый login-flow не обязан иметь защиту от brute force.

Роли: `admin`, `support`, `user`.

Важное наблюдение: authorization guards смешанные.

- `_check_admin()` принимает admin/support через session cookie или `Authorization: Bearer`.
- Часть user-management endpoints проверяет только session user и роль `admin`, поэтому bearer token там не всегда эквивалентен session admin.
- Это снижает единообразие модели: для production лучше заранее сделать явную матрицу endpoints, ролей и допустимых auth methods.

## API tokens

Идея токенов сильная:

- raw token показывается один раз при создании;
- в `data.json` сохраняется только SHA-256 hash;
- сохраняется короткий prefix для узнавания токена в UI;
- token привязан к пользователю-владельцу;
- если владелец отключен или потерял роль admin/support, token перестает работать;
- `last_used_at` обновляется с throttling, чтобы не писать `data.json` на каждый запрос;
- revoke удаляет token entry.

Ограничение: токены admin/support-эквивалентны для всех endpoints, которые используют `_check_admin()`. Нет granular scopes, expiry, audience, IP allowlist, per-token role, per-token audit policy или forced rotation.

Для `amn2` стоит переносить только концепцию, но не модель прав:

- токены должны быть scoped;
- срок действия должен быть явным;
- опасные действия должны требовать отдельного scope;
- destructive operations должны иметь audit event;
- token hash лучше хранить отдельно от общего state-файла, если появится полноценное secret storage.

## Public sharing и self-service

Self-service endpoints дают обычному пользователю получать только свои connections и config.

Public sharing работает через `share_token`, который хранится в user record. У ссылки может быть optional password, password хранится как hash. Если пароль задан и пользователь прошел auth, в session ставится flag вида `share_auth_<token>`.

Риски для production-дизайна:

- `share_token` хранится в plaintext;
- срок жизни ссылки не виден как обязательная часть модели;
- пароль опционален;
- нет явной одноразовости или ограничений на скачивание;
- получение config через public endpoint делает ссылку очень чувствительным секретом;
- revoke есть через отключение sharing или смену token, но это нужно проектировать явно.

Для `amn2` идея полезна только в более строгом виде: hashed share token, expiry, optional one-time mode, audit, rate limit, clear revoke UX и отдельные тесты на доступ к чужим config.

## Telegram delivery

Telegram bot привязывает пользователя по Telegram ID и может отправлять конфиги или VPN links в чат. Это удобно для user UX, но канал нужно считать sensitive delivery path.

Для production-дизайна важно:

- не считать Telegram безопасным хранилищем секретов;
- логировать факт выдачи config, но не сам config;
- иметь revoke/rotation сценарий после отправки;
- проверять, что Telegram ID нельзя привязать без подтверждения;
- ограничить команды и callback_data только user-owned connections.

## Secret storage

`data.json` является центральным state-хранилищем. По просмотренным участкам туда попадают или могут попадать:

- server host, username, password, private_key;
- users и password hashes;
- user connections;
- API token hashes;
- plaintext share tokens;
- Telegram bot token;
- Remnawave API key;
- SSL certificate/key text или пути;
- settings.

Backup endpoint отдает `data.json` целиком, а restore принимает JSON с базовой проверкой структуры. Это удобно для лабораторной панели, но для production требует отдельной политики:

- redacted backup по умолчанию;
- encrypted backup для полного state;
- явное предупреждение, что backup содержит секреты;
- restore schema validation и миграции;
- audit event на download/restore;
- защита от случайного импорта несовместимого или malicious state.

## SSH и sudo model

SSH layer использует Paramiko и автоматически принимает неизвестные host keys через `AutoAddPolicy`. Это удобно для onboarding, но ослабляет защиту от MITM.

Для sudo при password-based SSH пароль подставляется в команду через `sudo -S`. В этом же manager-слое команды логируются перед запуском. Это создает важный риск: если полный sudo command попадает в лог, пароль может оказаться в логах или быть видимым в process command line на удаленной стороне.

Для `amn2` это прямой anti-pattern. Более безопасная модель:

- предпочитать SSH keys и отдельного пользователя с ограниченными sudoers rules;
- не прокидывать sudo password через command string;
- не логировать команды с секретами;
- разделить command audit и secret material;
- проверять host key pinning;
- иметь dry-run и rollback для destructive operations.

## Что можно взять как идеи

- One-time display API token.
- Token hash вместо plaintext token.
- Token owner inheritance, чтобы отключение/понижение пользователя отзывали token.
- Self-service API отдельно от admin API.
- Public sharing как отдельный surface, но с hashed token, expiry и audit.
- Auth boundary matrix до реализации endpoints.
- Secret inventory как обязательная часть design review.
- Backup/restore как операторская функция, но только с явной secret policy.

## Что нельзя переносить в production как есть

- Default `admin` / `admin`.
- Ephemeral `SECRET_KEY` в production.
- Admin-equivalent tokens без scopes и expiry.
- Plaintext share tokens в общем state.
- Хранение SSH passwords/private keys без отдельного secret storage.
- Backup raw `data.json` без redaction/encryption policy.
- Auto-accept unknown SSH host keys.
- Sudo password inside command string.
- Логи команд без secret redaction.

## Решение для lab

Статус deep-dive: `completed-first-pass`.

Для `amn2` переносить только требования и идеи, не код:

- scoped API tokens;
- hardened first-run bootstrap;
- self-service boundary;
- share links with expiry and audit;
- secret inventory;
- safe SSH/sudo execution policy;
- redacted/encrypted backup policy.

Перед проектированием любой из этих функций нужен отдельный design spec и тест-план.

## Источники

- Репозиторий: https://github.com/PRVTPRO/Amnezia-Web-Panel
- README: https://github.com/PRVTPRO/Amnezia-Web-Panel/blob/main/README.md
- `app.py`: https://github.com/PRVTPRO/Amnezia-Web-Panel/blob/main/app.py
- `telegram_bot.py`: https://github.com/PRVTPRO/Amnezia-Web-Panel/blob/main/telegram_bot.py
- `managers/ssh_manager.py`: https://github.com/PRVTPRO/Amnezia-Web-Panel/blob/main/managers/ssh_manager.py
- `docker-compose.yml`: https://github.com/PRVTPRO/Amnezia-Web-Panel/blob/main/docker-compose.yml
- `Dockerfile`: https://github.com/PRVTPRO/Amnezia-Web-Panel/blob/main/Dockerfile
