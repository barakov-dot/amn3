# PRVTPRO/Amnezia-Web-Panel: GitHub watch и repository assembly

## Паспорт

- Upstream: https://github.com/PRVTPRO/Amnezia-Web-Panel
- Дата GitHub watch: 2026-05-31
- Default branch: `main`
- Visibility: public
- License verdict: GPL-3.0, режим `research-only`.
- Цель файла: собрать GitHub-сигналы вокруг репозитория, не копируя код: структура, build/deploy surface, зависимости, issues/PRs, идеи для `amn2`, hybrid и общего skill.

## Что уже собрано в lab

- Первичный паспорт: [prvtpro-amnezia-web-panel.md](prvtpro-amnezia-web-panel.md).
- Auth/secrets deep-dive: [prvtpro-amnezia-web-panel-auth-secrets.md](prvtpro-amnezia-web-panel-auth-secrets.md).
- API surface deep-dive: [prvtpro-amnezia-web-panel-api-surface.md](prvtpro-amnezia-web-panel-api-surface.md).
- Manager architecture deep-dive: [prvtpro-amnezia-web-panel-manager-architecture.md](prvtpro-amnezia-web-panel-manager-architecture.md).
- Feature gap: [prvtpro-amnezia-web-panel-feature-gap.md](prvtpro-amnezia-web-panel-feature-gap.md).
- Upstream refresh 2026-06-10: [prvtpro-amnezia-web-panel-upstream-refresh-2026-06-10.md](prvtpro-amnezia-web-panel-upstream-refresh-2026-06-10.md).

## Upstream refresh 2026-06-10

Повторная проверка upstream зафиксировала latest checked commit `7f062abc2c76bbe19eb7daafdf1191d6c26ff19a` и product-сигналы v1.4.3: SOCKS5, AdGuard Home, node status/latency, API grouping, API tokens, Xray upgrade и расширение Telegram bot. Решение для `amn2`: брать только идеи в режиме `research-only`, без копирования GPL-3.0 кода, и начинать с local/read-only/status/docs/contract-test кандидатов.

Ближайшие AMN2-кандидаты:

- `P4-PRVTPRO-REFRESH-002`: expiration-field contract tests;
- `P4-PRVTPRO-REFRESH-001`: read-only About/Version/Build status;
- `P4-PRVTPRO-REFRESH-003`: read-only server status/latency UX после design boundary;
- `P4-PRVTPRO-REFRESH-004`: API taxonomy/OpenAPI grouping как docs/policy support.

Hybrid-only backlog:

- `HYB-PRVTPRO-REFRESH-001`: AdGuard Home integration;
- `HYB-PRVTPRO-REFRESH-002`: SOCKS5 service manager;
- `HYB-PRVTPRO-REFRESH-003`: Xray migration/attach existing install;
- `HYB-PRVTPRO-REFRESH-004`: multi-protocol capability registry.

## Repository map

README описывает такую структуру:

- `app.py` - FastAPI entry point и route layer;
- `telegram_bot.py` - Telegram bot integration;
- `managers/` - protocol/service managers;
- `static/` - CSS, favicon, vendored JS;
- `templates/` - Jinja2 templates;
- `translations/` - i18n files;
- `data.json` - panel state.

Для lab важна не точная структура upstream, а product decomposition:

- UI/API layer;
- auth/session/token layer;
- local state/backup layer;
- remote execution layer;
- protocol/service managers;
- config delivery surfaces;
- install/update/deploy surface;
- issue/PR feedback loop как источник production-регрессий.

## Build и deploy surface

GitHub files:

- `requirements.txt` содержит pinned Python dependencies, включая FastAPI, Flask/Werkzeug, Paramiko, Telegram bot, captcha, Pillow, PyYAML.
- `Dockerfile` использует `python:3.14-slim`, копирует `requirements.txt`, ставит зависимости и запускает `python3 app.py`.
- `docker-compose.yml` использует image `prvtpro/amnezia-panel:1.4.3`, порт `${APP_PORT:-5000}:5000`, volume `amnezia_data:/app/data`, restart `unless-stopped` и TCP healthcheck на localhost:5000.

Сигналы для `amn2`:

- dependency consistency нужно проверять отдельно: если README говорит Python 3.10+, а Dockerfile уже на Python 3.14, это должно попадать в runtime/deploy checklist;
- presence of Flask/Werkzeug рядом с FastAPI стоит отмечать как possible legacy/mixed stack signal;
- Docker build должен иметь test или CI-gate на encoding/dependency install, иначе repository может выглядеть runnable, но ломаться на базовом build;
- state volume и backup policy нужно связывать: если state содержит secrets, volume не делает backup безопасным.

## GitHub issues: production-сигналы

Актуальные открытые issues показывают, какие классы ошибок стоит превращать в тесты для `amn2`:

| Issue | Сигнал | Что взять как требование |
| --- | --- | --- |
| [#52 API support planning](https://github.com/PRVTPRO/Amnezia-Web-Panel/issues/52) | пользователям нужен внешний API для integrations | scoped API tokens и stable integration surface должны проектироваться заранее |
| [#51 QR code](https://github.com/PRVTPRO/Amnezia-Web-Panel/issues/51) | QR/config import может ломаться на клиентах | config delivery требует byte-level/encoding tests, Android/import smoke tests и redaction |
| [#49 Show config TypeError](https://github.com/PRVTPRO/Amnezia-Web-Panel/issues/49) | mismatch manager method signatures ломает self-service config | нужен contract test на все manager methods, особенно `get_client_config`/export |
| [#45 Settings 422](https://github.com/PRVTPRO/Amnezia-Web-Panel/issues/45) | UI скрывает field, API получает invalid int | нужны tests на пустые списки, hidden controls и form-to-API payload |
| [#44 Xray connection crash](https://github.com/PRVTPRO/Amnezia-Web-Panel/issues/44) | remote config mutation может падать и ронять процесс | нужны partial-failure contract, recovery note и process-safety boundary |
| [#43 WARP integration](https://github.com/PRVTPRO/Amnezia-Web-Panel/issues/43) | пользователи хотят service expansion | hybrid backlog должен отличать core protocol от adjunct service |
| [#39 multi-protocol bugs](https://github.com/PRVTPRO/Amnezia-Web-Panel/issues/39) | Docker install, port conflicts и multi-protocol state могут расходиться | preflight должен проверять Docker, occupied ports и existing protocol state до install |
| [#40 chained routing](https://github.com/PRVTPRO/Amnezia-Web-Panel/issues/40) | спрос на routing chains между сервисами | hybrid-only: chain/routing policy требует threat model, observability и rollback |
| [#42 expiration date](https://github.com/PRVTPRO/Amnezia-Web-Panel/issues/42) | user lifecycle field сохраняется не полностью | expiration/disable/revoke semantics должны иметь end-to-end tests |
| [#41 QR generation](https://github.com/PRVTPRO/Amnezia-Web-Panel/issues/41) | QR encoding может портить non-ASCII bytes | QR generation tests должны проверять raw bytes и mobile import constraints |

## GitHub PRs: идеи и warning signs

| PR | Сигнал | Что взять |
| --- | --- | --- |
| [#48 Configurable AWG subnet](https://github.com/PRVTPRO/Amnezia-Web-Panel/pull/48) | hardcoded VPN subnet мешает нескольким серверам и routed/site-to-site scenarios | `amn2` должен проектировать VPN subnet/IPAM как явную настройку с validation и conflict detection |
| [#34 expiration date fix](https://github.com/PRVTPRO/Amnezia-Web-Panel/pull/34) | backend response не совпадал с frontend expectation | API response contract tests должны покрывать UI-required fields |
| [#30 toggle user](https://github.com/PRVTPRO/Amnezia-Web-Panel/pull/30) | user status должен менять effective access | disabled user access gate должен проверяться во всех auth methods |
| [#26 Docker build encoding](https://github.com/PRVTPRO/Amnezia-Web-Panel/pull/26) | build ломался из-за encoding `requirements.txt` | repository watch должен включать buildability/encoding check для upstream |

## Новые идеи для `amn2`

### Config delivery integrity tests

Идея: для `.conf`, QR и `vpn://` links иметь тесты, которые проверяют не только наличие output, но и пригодность для import:

- byte-level encoding для QR payload;
- non-ASCII profile/client names;
- Android/import compatibility smoke contract;
- запрет попадания config/QR payload в logs, audit, errors и metrics;
- единая `secret-read` classification.

Статус: добавить в `Public/Self-service Config Delivery` и общий skill checklist.

### Configurable VPN subnet/IPAM

Идея: не hardcode-ить client subnet для AWG/WireGuard, а иметь явную настройку server/profile subnet с validation:

- CIDR validation;
- reserved addresses;
- conflict detection между серверами;
- migration story для existing peers;
- dry-run preview перед изменением live server;
- audit event на изменение subnet.

Статус: `candidate-for-amn2-review`, но только после текущей IPAM/server model inventory.

### UI-to-API empty-state tests

Идея: для web forms тестировать empty state и hidden controls, особенно если UI строит JSON payload для API.

Статус: добавить в skill как frontend/API integration checklist.

## Новые идеи для hybrid

- Chained service routing: VPN/proxy/DNS services can be composed, but only after threat model, route policy, observability and recovery design.
- Adjunct services backlog: WARP, DNS, AdGuard, proxy and similar services должны идти через capability registry, а не добавляться как one-off manager.
- Existing server reconciliation should include port conflict and protocol-state conflict detection before install.

## Watch decision

`PRVTPRO/Amnezia-Web-Panel` остается активным upstream для наблюдения.

Приоритет watch:

1. issues/PRs по config delivery, QR, Android import и `.conf` compatibility;
2. changes вокруг API tokens/scopes;
3. changes вокруг safe remote execution, Docker install и port conflicts;
4. changes вокруг configurable subnet/IPAM;
5. releases, которые меняют deploy/runtime model.

## Источники

- Репозиторий: https://github.com/PRVTPRO/Amnezia-Web-Panel
- README: https://github.com/PRVTPRO/Amnezia-Web-Panel/blob/main/README.md
- `requirements.txt`: https://github.com/PRVTPRO/Amnezia-Web-Panel/blob/main/requirements.txt
- `Dockerfile`: https://github.com/PRVTPRO/Amnezia-Web-Panel/blob/main/Dockerfile
- `docker-compose.yml`: https://github.com/PRVTPRO/Amnezia-Web-Panel/blob/main/docker-compose.yml
- Issues: https://github.com/PRVTPRO/Amnezia-Web-Panel/issues
- Pull requests: https://github.com/PRVTPRO/Amnezia-Web-Panel/pulls
