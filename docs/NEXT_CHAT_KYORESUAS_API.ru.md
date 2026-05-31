# VPN Ops Lab - KYORESUAS-API

## Назначение нового чата

Этот документ - стартовый бриф для отдельного Codex-чата внутри проекта `VPN Ops Lab`.

Название чата:

```text
VPN Ops Lab — KYORESUAS-API
```

Основной upstream:

- GitHub: https://github.com/kyoresuas/amnezia-api

## Контекст

Проект `kyoresuas/amnezia-api` рассматривается как потенциальный API-слой для управления пользователями Amnezia/AmneziaWG на сервере.

Рабочая гипотеза: скрипт или сервис устанавливается на сервер Amnezia, после чего внешняя панель, бот, CLI или другая система управляет пользователями через API.

Это близко к текущей цели `AMNEZIYA`/`amn2`: получить управляемую, проверяемую и production-safe модель пользовательского API без ручного редактирования серверного состояния.

## Правила анализа

- Документы и выводы писать на русском языке.
- Код из upstream не копировать.
- Начинать с license verdict.
- Разделять идеи, архитектурные паттерны, API-контракты и конкретную реализацию.
- Любой перенос в `amn2` рассматривать только как самостоятельное проектирование.
- Отдельно проверять security, secrets, audit, rollback, idempotency и тестируемость.
- Не устанавливать и не запускать скрипт на реальном сервере без отдельного явного решения.

## Что проверить в upstream

1. Лицензия:
   - есть ли `LICENSE`;
   - что разрешено для кода, документации и идей;
   - можно ли использовать только концепцию без копирования реализации;
   - есть ли риск copyleft, unclear license или vendored third-party code.

2. Архитектура:
   - это standalone API, CLI-обертка, daemon, systemd-service, Docker-сервис или набор скриптов;
   - как он подключается к установленной Amnezia;
   - какие файлы, контейнеры, интерфейсы, команды и state-хранилища меняет;
   - есть ли read-only detect перед write/apply;
   - есть ли план установки, обновления и удаления.

3. API surface:
   - какие endpoints есть для пользователей;
   - есть ли OpenAPI/Swagger или другая документация API;
   - есть ли операции create, list, get config, revoke/delete, disable/enable, reset, sync;
   - какие операции являются `read-only`, `secret-read`, `state-write`, `remote-exec` и `destructive`;
   - как API сообщает partial failure и ошибки remote state.

4. Auth и secrets:
   - как API защищен: token, password, local-only bind, reverse proxy, mTLS или другое;
   - где хранятся токены и секреты;
   - попадают ли private keys, config bodies, QR, `vpn://` links или raw tokens в logs/errors;
   - есть ли revoke, rotation, expiry, rate limit и audit;
   - можно ли разделить admin API и integration API.

5. Production-подход:
   - есть ли systemd/Docker/restart policy;
   - как устроены health checks;
   - есть ли backup/restore или recovery note;
   - есть ли dry-run/preview перед изменениями;
   - есть ли idempotency и защита от повторного apply;
   - есть ли тесты или хотя бы проверяемый сценарий на staging VPS.

6. UX:
   - насколько API удобно использовать из панели, Telegram-бота и CLI;
   - какие ответы нужны оператору после создания/удаления пользователя;
   - как выдаются конфиги: файл, QR, import link, JSON;
   - как пользователь/оператор понимает статус peer и ошибки.

## Ожидаемые артефакты в этом проекте

Первый слой:

- `research/upstreams/kyoresuas-amnezia-api.md` - основная карточка upstream.

Если проект окажется достаточно важным:

- `research/upstreams/kyoresuas-amnezia-api-api-surface.md`
- `research/upstreams/kyoresuas-amnezia-api-install-runtime.md`
- `research/upstreams/kyoresuas-amnezia-api-auth-secrets.md`
- `research/upstreams/kyoresuas-amnezia-api-feature-gap.md`

После анализа обновить, если есть сильные кандидаты:

- `ideas/candidates-for-amn2.md`
- `ideas/candidates-for-hybrid.md`
- `ideas/add-to-skill.md`
- `ideas/rejected.md`

## Предварительные кандидаты для оценки

Для `amn2`:

- server-side API для управления AmneziaWG users/peers;
- route policy matrix для всех user-management операций;
- scoped integration tokens для внешней панели/бота;
- secret-safe config delivery через API;
- dry-run/apply модель для операций, меняющих серверное состояние.

Для будущего hybrid:

- единый API-слой поверх разных VPN runtime;
- attach/reconcile existing Amnezia server;
- external billing/support/bot integration через стабильный API;
- фоновая job-модель для долгих remote operations.

Для общего skill:

- checklist анализа server-installed API wrappers;
- отдельный license/security gate для скриптов, которые получают полный контроль над пользователями VPN;
- обязательная классификация endpoints по risk class.

## Стартовый промпт для нового чата

```text
Работаем в проекте VPN Ops Lab. Название чата: VPN Ops Lab — KYORESUAS-API.

Нужно проанализировать GitHub upstream:
https://github.com/kyoresuas/amnezia-api

Анализируем по правилам VPN Ops Lab: лицензия, архитектура, функции, UX, production-подходы, кандидаты для amn2, hybrid и общего skill. Документы на русском в приоритете. Код не копируем.

Контекст: это API-управление пользователями Amnezia/AmneziaWG. Гипотеза - ставим скрипт или сервис на сервер Amnezia и дальше полностью управляем пользователями через API. Нужно понять, что можно безопасно взять как идею для amn2, что годится только для hybrid, а что надо отклонить.

Начни с проверки лицензии и структуры репозитория. Затем создай или обнови:
- research/upstreams/kyoresuas-amnezia-api.md
- при необходимости deep-dive документы по API surface, install/runtime, auth/secrets и feature gap
- списки candidates-for-amn2, candidates-for-hybrid, add-to-skill или rejected.

Не устанавливай ничего на реальный сервер и не копируй upstream-код.
```

## Первый следующий шаг

Открыть новый Codex-чат с названием `VPN Ops Lab — KYORESUAS-API`, вставить стартовый промпт выше и начать анализ с primary sources GitHub: README, LICENSE, installation/runtime files, API routes, dependency files и docs.
