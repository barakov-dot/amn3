# PRVTPRO/Amnezia-Web-Panel: upstream refresh 2026-06-10

## Паспорт

- Upstream: https://github.com/PRVTPRO/Amnezia-Web-Panel
- Дата повторной проверки: 2026-06-10
- Default branch: `main`
- Последний проверенный upstream commit: `7f062abc2c76bbe19eb7daafdf1191d6c26ff19a`
- Лицензия: GPL-3.0
- Статус для `amn2`: `research-only`, переносить можно только идеи и требования, без копирования кода, UI, шаблонов, scripts или manager-ов.
- Статус для future hybrid: источник продуктовых и архитектурных сигналов, но не база для прямого заимствования.

## Короткий вывод

В upstream появились и закрепились полезные product-сигналы: release/build pipeline, multi-protocol расширение, API taxonomy, API tokens, node status/latency, AdGuard Home, SOCKS5, Classic WireGuard и Xray upgrade/migration work. Для `amn2` сейчас пригодны только узкие read-only/status/docs и contract-test идеи. Более широкие multi-protocol, AdGuard/SOCKS5 и миграционные сценарии лучше оставить в hybrid backlog.

## Лицензия и ограничения

Репозиторий распространяется под GPL-3.0. Для нашего проекта это означает:

- код, шаблоны, UI-компоненты, manager-реализации, scripts и тексты из upstream не копируем;
- используем только наблюдения: какие функции нужны операторам, где upstream ломается, какие тесты стоит добавить;
- любые реализации в `amn2` пишутся самостоятельно, в стиле существующей архитектуры и с отдельным тестовым планом;
- перед переносом идеи в production проверяем лицензию, пользу, риски, совместимость с `amn2` и gate на тесты.

## Что изменилось в upstream

### Release/build surface

- Последний проверенный commit на `main`: `7f062abc2c76bbe19eb7daafdf1191d6c26ff19a`, 2026-05-28, `Update build.yml`.
- Сигнал: upstream улучшает release assembly через GitHub Actions и artifacts для Linux/Windows/macOS.
- Для `amn2`: полезно как напоминание, что build/release evidence должен быть отдельным проверяемым артефактом. Код workflow не переносим.

### v1.4.3 product surface

Commit `29def95df8514fbbdc2c9fe589619fbe07f3f706` добавил или закрепил:

- SOCKS5 support;
- AdGuard Home integration;
- node status и latency tracking;
- drag-and-drop server management;
- Xray upgrade с backward compatibility;
- Telegram bot support для всех протоколов;
- improved server cleanup;
- grouped API structure и system routes;
- JWT/Bearer token generation для external integrations.

Для `amn2` это не список задач на перенос. Это карта тем для фильтрации: что можно взять как read-only/status/contract-test улучшение сейчас, а что оставить до hybrid roadmap.

### v1.4.0 product surface

Commit `1fd100e4e99164d0bdb03b5642fe54f02d3f93a2` добавил Classic WireGuard, улучшения Xray link generation и version/new-version UX.

Для `amn2` самый безопасный локальный вывод: операторской панели нужен понятный блок версии/build/runtime status, но без public exposure и без auto-update действий.

### Expiration-field regression signal

Commit `181144a8e38ed92997b722b34ef86fc8a51d64b4` и связанный fix `111d4a98bb6ef43b53ee8ea71316dc14db89cad8` исправляли отсутствие `expiration_date` в `/api/users`.

Для `amn2`: это хороший кандидат на contract tests, чтобы lifecycle-поля пользователя/устройства не терялись между API, UI и формами редактирования.

## Кандидаты для `amn2`

### P4-PRVTPRO-REFRESH-001: read-only About/Version/Build status

- Приоритет: важное, локально выполнимое.
- Идея: добавить в operator UI read-only блок версии/commit/build/runtime status.
- Польза: оператор и основной чат быстрее понимают, какой build стоит на VPS и какие gates уже пройдены.
- Граница: без auto-update, без shell actions, без public exposure, без чтения секретов.
- Gate: local UI/status tests, smoke на отсутствие secret-bearing fields, документированный source/build label.
- Рекомендация: хороший Phase 4 slice после contract-test задач.

### P4-PRVTPRO-REFRESH-002: expiration-field contract tests

- Приоритет: важное, рекомендую первым из PRVTPRO refresh.
- Идея: проверить, что expiration/lifecycle поля не исчезают из API responses, UI forms и edit payloads.
- Польза: снижает риск выдать пользователю доступ без ожидаемого срока или потерять срок действия при редактировании.
- Граница: local-only tests, без live VPS write.
- Gate: unit/API/UI contract tests на list/detail/edit для user/device lifecycle fields.
- Рекомендация: передать в основной чат как первый безопасный локальный slice.

### P4-PRVTPRO-REFRESH-003: read-only server status/latency UX

- Приоритет: полезное, но только с жесткой границей read-only.
- Идея: показать агрегированный статус сервера/ноды и latency/availability, если эти данные уже безопасно доступны.
- Польза: operator UX становится ближе к production-панели без перехода к destructive actions.
- Граница: без SSH write, без sync/health action button, без API `3040` наружу, без raw logs/secrets.
- Gate: route policy, secret-safety tests, read-only audit classification, future VPS smoke только если меняется runtime probe.
- Рекомендация: сначала сделать design boundary, потом реализацию.

### P4-PRVTPRO-REFRESH-004: API taxonomy/OpenAPI grouping

- Приоритет: полезное/docs.
- Идея: использовать доменную группировку API как проверочный список: auth, servers, protocols, users, self-service, sharing, settings, integrations.
- Польза: проще ловить случайные admin/user boundary leaks.
- Граница: только taxonomy idea, без копирования OpenAPI текста.
- Gate: сверка с route policy matrix.

## Кандидаты только для hybrid backlog

### HYB-PRVTPRO-REFRESH-001: AdGuard Home integration

- Идея: DNS/ad-blocking как adjunct service рядом с VPN.
- Почему не `amn2` сейчас: это service lifecycle, ports, DNS policy, secrets и rollback, а не узкое улучшение текущей панели.
- Нужный gate: service mode model, conflict detection, dry-run, recovery plan.

### HYB-PRVTPRO-REFRESH-002: SOCKS5 service manager

- Идея: proxy service как отдельная capability.
- Почему не `amn2` сейчас: расширяет scope за пределы текущего production-направления.
- Нужный gate: capability registry, threat model, observability, route policy.

### HYB-PRVTPRO-REFRESH-003: Xray migration/attach existing install

- Идея: безопасно подключать существующий Xray/server state, сохраняя ключи и configs.
- Почему не `amn2` сейчас: это migration wizard и reconciliation problem.
- Нужный gate: redacted preview, conflict report, no-write dry-run, rollback note.

### HYB-PRVTPRO-REFRESH-004: multi-protocol capability registry

- Идея: описывать protocol/service managers через capabilities, risk classes и supported artifacts.
- Почему не `amn2` сейчас: полезно для будущей платформы, но может раздуть текущий `amn2`.
- Нужный gate: unified adapter contract, test doubles, secret-output classification.

## Negative controls

Не переносить из upstream без отдельного named gate:

- admin-equivalent Bearer token на все admin endpoints;
- public panel exposure, HTTPS/domain cutover и reverse proxy assumptions;
- raw config delivery/public sharing;
- backup/import/reboot/clear/server cleanup из web UI;
- direct server management и destructive write actions;
- drag-and-drop server management как write UX без route policy и audit;
- чужие manager implementations, templates, CSS/JS и workflow code.

## Upstream risk signals

Открытые issues показывают, что v1.4.3 нельзя воспринимать как production-шаблон для прямого переноса:

- issue #49: `WireGuardManager.get_client_config()` signature mismatch ломает показ config;
- issue #44: crash при добавлении Xray connection к существующему user;
- issue #45: settings save может падать 422 при пустом server list;
- issue #60: missing Telemt `config.toml`;
- issue #35: запрос на несколько WG/AWG configurations/devices per user подтверждает, что в `amn2` уже правильнее держать multi-device модель;
- issue #38: безопасная миграция существующего Xray state полезна как hybrid-only тема.

## Что передать в основной чат

Рекомендуемый текст для основного чата:

```text
Добавь PRVTPRO refresh 2026-06-10 в Phase 4 candidate registry.

Источник: VPS-OPS-LAB research/upstreams/prvtpro-amnezia-web-panel-upstream-refresh-2026-06-10.md

Лицензия: PRVTPRO/Amnezia-Web-Panel = GPL-3.0, code/templates/managers/workflows не копируем. Используем только идеи и regression-сигналы.

Для AMN2 Phase 4 берем только local/read-only/status/docs/contract-test slice:
1. P4-PRVTPRO-REFRESH-002 expiration-field contract tests - рекомендую первым.
2. P4-PRVTPRO-REFRESH-001 read-only About/Version/Build status - вторым.
3. P4-PRVTPRO-REFRESH-003 read-only server status/latency UX - только после design boundary.
4. P4-PRVTPRO-REFRESH-004 API taxonomy/OpenAPI grouping - docs/policy support.

Hybrid-only backlog:
- HYB-PRVTPRO-REFRESH-001 AdGuard Home integration.
- HYB-PRVTPRO-REFRESH-002 SOCKS5 service manager.
- HYB-PRVTPRO-REFRESH-003 Xray migration/attach existing install.
- HYB-PRVTPRO-REFRESH-004 multi-protocol capability registry.

Negative controls:
- не переносим admin-equivalent Bearer token на все admin endpoints;
- не открываем public panel/config delivery/reboot/backup/import/server cleanup без отдельного named gate;
- не копируем GPL-код, UI, templates, scripts или manager implementations.

Первое действие в основном чате: выбрать P4-PRVTPRO-REFRESH-002 как ближайший local-only AMN2 slice и подготовить тестовый план.
```

## English short summary

The latest PRVTPRO upstream refresh is useful as research input, not as source code. For AMN2, the safest near-term candidates are expiration/lifecycle contract tests, a read-only version/build status panel, read-only node status UX, and API taxonomy documentation. AdGuard Home, SOCKS5, Xray migration, and multi-protocol capability registry should stay in the future hybrid backlog. GPL-3.0 code, templates, managers, scripts, and workflows must not be copied.

## Источники

- Репозиторий: https://github.com/PRVTPRO/Amnezia-Web-Panel
- Releases: https://github.com/PRVTPRO/Amnezia-Web-Panel/releases
- Latest checked build commit: https://github.com/PRVTPRO/Amnezia-Web-Panel/commit/7f062abc2c76bbe19eb7daafdf1191d6c26ff19a
- v1.4.3 commit: https://github.com/PRVTPRO/Amnezia-Web-Panel/commit/29def95df8514fbbdc2c9fe589619fbe07f3f706
- v1.4.0 commit: https://github.com/PRVTPRO/Amnezia-Web-Panel/commit/1fd100e4e99164d0bdb03b5642fe54f02d3f93a2
- Expiration fix commit: https://github.com/PRVTPRO/Amnezia-Web-Panel/commit/181144a8e38ed92997b722b34ef86fc8a51d64b4
- Issue #49: https://github.com/PRVTPRO/Amnezia-Web-Panel/issues/49
- Issue #44: https://github.com/PRVTPRO/Amnezia-Web-Panel/issues/44
- Issue #45: https://github.com/PRVTPRO/Amnezia-Web-Panel/issues/45
- Issue #60: https://github.com/PRVTPRO/Amnezia-Web-Panel/issues/60
- Issue #35: https://github.com/PRVTPRO/Amnezia-Web-Panel/issues/35
- Issue #38: https://github.com/PRVTPRO/Amnezia-Web-Panel/issues/38
