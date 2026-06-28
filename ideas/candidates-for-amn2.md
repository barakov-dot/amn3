# Кандидаты для `amn2`

Идеи из этой очереди не являются задачами на реализацию. Каждая идея должна пройти gate:

- совместимость лицензии;
- практическая польза;
- operational- и security-риски;
- архитектурная совместимость с `amn2`;
- тестовый план.

Общий checklist для переноса: [Design Specs Index + `amn2` Transfer Checklist](../docs/superpowers/specs/2026-05-30-design-specs-index-amn2-transfer-checklist.md).

## Из PRVTPRO/Amnezia-Web-Panel

Источник: [research/upstreams/prvtpro-amnezia-web-panel.md](../research/upstreams/prvtpro-amnezia-web-panel.md)

Статус лицензии: GPL-3.0, только самостоятельная реализация идей.

Актуализация 2026-06-09: после AMN2 target VPS Phase 3 service-mode evidence `bc00b77` текущая web/admin модель - приватная панель через SSH local port forward к `127.0.0.1:3030`, без публичного домена, без HTTPS reverse proxy/public cutover, без public API `3040` и при `VPS_APPLY_ENABLED=false`. Поэтому PRVTPRO-кандидаты ниже рассматривать сначала как read-only UX/product improvements для operator panel. Идеи, требующие public exposure, raw config delivery, backup/import/reboot, direct server management или destructive write actions, остаются заблокированными до отдельного explicit gate.

### API tokens для интеграций

- Идея: токены для внешних интеграций, где raw token показывается один раз, а в хранилище лежит только hash.
- Польза: безопаснее для CI, мониторинга и внешних админ-инструментов.
- Риски: token scope, rotation, audit, revoke, role inheritance.
- Статус: research.

### Self-service endpoints

- Идея: отделить пользовательские `/my/*` endpoints от admin API.
- Польза: меньше риска случайно открыть admin-действия обычному пользователю.
- Риски: authorization boundary, тесты на privilege escalation.
- Статус: design candidate описан в [Public/Self-service Config Delivery для `amn2`](../docs/superpowers/specs/2026-05-30-public-self-service-config-delivery-design.md); текущий `amn2` baseline уточнен в [config delivery inventory](../research/amn2/config-delivery-inventory.md).

### Параллельная проверка статусов

- Идея: проверять ping/status протоколов параллельно, чтобы UI не зависал на медленных серверах.
- Польза: быстрее и отзывчивее для панели управления.
- Риски: rate limits, SSH connection fan-out, timeouts, cancellation.
- Статус: research.

### Token-protected sharing

- Идея: публичные ссылки для получения конфигурации без доступа к панели.
- Польза: удобная выдача конфигов пользователям.
- Риски: срок жизни ссылок, одноразовость, аудит, утечки, revoke.
- Статус: first local-only no-route share-token/policy slice выполнен в `amn2/codex/public-config-delivery-policy-contract`, commit `2ef3af7`; details in [Public config delivery policy contract implementation](../research/amn2/public-config-delivery-policy-contract-implementation.md).

### Config delivery integrity tests

- Идея: тестировать `.conf`, QR и `vpn://` links как importable artifacts, а не только как строки, которые успешно сгенерировались.
- Польза: снижает риск выдать пользователю config, который выглядит корректным в панели, но не импортируется на Android/client side.
- Риски: нужно поддерживать byte-level encoding tests, non-ASCII names, QR decode checks и client-specific import constraints без копирования upstream code.
- Статус: research candidate после [PRVTPRO config delivery integrity](../research/upstreams/prvtpro-amnezia-web-panel-config-delivery-integrity.md); AMN2 bot delivery UX/localization slice выполнен в commit `908cafc`, follow-up device sequence/external import visibility выполнен в commit `59bc266`, `P4-AMNEZIA-REFRESH-002` client import compatibility matrix выполнен в commit `d2e234f`, `P4-BOT-ONBOARDING-001` bot onboarding language/header выполнен в commit `137d471`, `P5-I003` runtime/toolchain standardization выполнен в commit `578d91e`, `P5-I002` external-only backfill rehearsal выполнен в commit `23f18ef`, `P5-I004` operator-only smoke checklist закрыт как AMN3 docs-only artifact, `P5-M003` AMN3 evidence discipline закрепил closeout rules, `P5-M001` support/news bot asset inventory отделил будущие support/news bot assets от текущего access bot, `P5-M005` bot media asset upload/apply boundary закрепил local registry vs Telegram identity apply gate, `P5-M004` граница ассета шапки веб-панели отделила admin-panel asset от bot/runtime media, `P5-M002` QA клиентских инструкций доставки конфигурации зафиксировал требование one-tap copy для Telegram import-ссылки, `P5-M006` добавил bounded Telegram copy affordance в AMN2 commit `ad6aa1b`, `P5-N002` отполировал web-panel service-mode/external-only copy в commit `17454e9`, `P5-X002` уточнил bot delivery labels/captions в commit `fed832c`, `P5-X001` отполировал Russian-first bot/web microtexts в commit `de25576`, `P5-S002` закрыл stale active-plan/recommendation cleanup как AMN3 docs-only checkpoint, а `P5-C002` закрыл retention decision для disposable test VPS; details in [Phase 4 bot config delivery localization](../research/amn2/phase-4-bot-config-delivery-localization-2026-06-11.md), [Phase 4 device sequence and external import visibility](../research/amn2/phase-4-device-sequence-external-import-2026-06-11.md), [Phase 4 Amnezia client compatibility matrix](../research/amn2/phase-4-amnezia-client-compatibility-matrix-2026-06-11.md), [Phase 4 bot onboarding language/header](../research/amn2/phase-4-bot-onboarding-language-header-2026-06-11.md), [Phase 5 runtime/toolchain standardization](../research/amn2/phase-5-runtime-toolchain-standardization-2026-06-11.md), [Phase 5 external-only backfill rehearsal](../research/amn2/phase-5-external-only-backfill-rehearsal-2026-06-11.md), [Phase 5 operator-only smoke checklist](../research/amn2/phase-5-operator-only-smoke-checklist-2026-06-11.md), [Phase 5 AMN3 evidence discipline](../research/amn2/phase-5-amn3-evidence-discipline-2026-06-11.md), [Phase 5 support/news bot asset inventory](../research/amn2/phase-5-support-news-bot-asset-inventory-2026-06-11.md), [Phase 5 bot media asset upload boundary](../research/amn2/phase-5-bot-media-asset-upload-boundary-2026-06-11.md), [Phase 5 web/admin header asset boundary](../research/amn2/phase-5-web-admin-header-asset-boundary-2026-06-11.md), [Phase 5 client config delivery QA](../research/amn2/phase-5-client-config-delivery-qa-2026-06-11.md), [Phase 5 Telegram import link copy](../research/amn2/phase-5-telegram-import-link-copy-2026-06-11.md), [Phase 5 web-panel service-mode copy](../research/amn2/phase-5-web-panel-service-mode-copy-2026-06-11.md), [Phase 5 bot labels/captions](../research/amn2/phase-5-bot-labels-captions-2026-06-11.md), [Phase 5 Russian-first microtexts](../research/amn2/phase-5-russian-first-microtexts-2026-06-11.md), [Phase 5 active-plan cleanup](../research/amn2/phase-5-active-plan-stale-recommendation-cleanup-2026-06-12.md) and [Phase 5 VPS retention decision](../research/amn2/phase-5-vps-retention-disposable-test-server-2026-06-12.md). Следующий safe step: `P5-C001` named local package-rebuild gate от AMN2 head `de25576`.

### Bot onboarding language/header assets

- Идея: привести `/start` нового пользователя к текущему production-like UX: header image, prompt `Выберите язык / Choose your language`, buttons `Русский` и `English`, default Russian path and English fallback.
- Польза: новый пользователь сразу видит бренд/бот-шапку и осознанно выбирает язык; снижает риск снова получить англоязычный default в выдаче конфигов.
- Риски: нужны bot-specific image assets, хранение media, Telegram file upload behavior, locale persistence, regression tests on callback flow.
- Статус: завершено как AMN2 local-only slice в commit `137d471`; evidence [Phase 4 bot onboarding language/header](../research/amn2/phase-4-bot-onboarding-language-header-2026-06-11.md). Использован только supplied `NEOBYATNAYA-AMNZ-BOT.png` для текущего access bot. `NEOBYATNAYA-AMNZ-SUPPORT-BOT.png` and `NEOBYATNAYA-AMNZ-NEWS-BOT.png` теперь описаны в [Phase 5 support/news bot asset inventory](../research/amn2/phase-5-support-news-bot-asset-inventory-2026-06-11.md) as planning-only assets for future separate bot runtimes; `NEOBYATNAYA-AMNZ-ADMIN-PANEL.png` закрыт отдельной [Phase 5 web/admin header asset boundary](../research/amn2/phase-5-web-admin-header-asset-boundary-2026-06-11.md).

### Manager config export contract

- Идея: для protocol manager-ов ввести единый `export_config`/`export_artifacts` contract вместо разрозненных `get_client_config` signatures.
- Польза: снижает риск runtime-ошибок при показе config, public share и self-service выдаче, особенно при добавлении новых протоколов.
- Риски: нужен capability-based дизайн, чтобы не заставлять все протоколы возвращать одинаковые artifacts, если формат импорта отличается.
- Статус: first local-only no-route adapter/tests slice выполнен в `amn2/codex/manager-config-export-contract`, commit `4d4e7a4`; details in [Manager config export contract implementation](../research/amn2/manager-config-export-contract-implementation.md).

### Runtime config path / manager export contract checks

- Идея: при config retrieval/export не предполагать статический путь вроде
  `wg0.conf`/`awg0.conf`, а валидировать или обнаруживать actual runtime config
  path через единый manager/export adapter contract.
- Польза: снижает риск показать/выдать не тот config artifact после миграции,
  legacy layout или multi-instance setup.
- Риски: config export является secret-read boundary; нужны redaction,
  client-compat tests и exact gate перед live/config delivery.
- Статус: `P9-N007` docs-only candidate после PRVTPRO Phase 9 refresh
  2026-06-28; без переноса GPL code/templates/managers/workflows.

### XRay validation checklist

- Идея: для будущих config/manager surfaces валидировать host/SNI/path/ranges
  до save/apply.
- Польза: уменьшает риск сохранить runtime-invalid config и затем сломать
  live apply/restart path.
- Риски: это не перенос upstream code; нужны локальные тесты и отдельный gate,
  если появится live config/manager behavior.
- Статус: `P9-N007` docs-only/local-test checklist candidate после Amnezia
  Phase 9 refresh 2026-06-28.

### OpenAPI-группировка по доменам

- Идея: группировать API-документацию по понятным доменам.
- Польза: проще проверять admin/user/protocol/settings surface.
- Риски: минимальные, но нужна синхронизация docs с реальными route guards.
- Статус: research.

### Scoped API tokens

- Идея: развить концепцию API tokens в сторону granular scopes, expiry, revoke, audit и отдельного scope для destructive operations.
- Польза: безопаснее для CI, мониторинга и ограниченных внешних интеграций, чем admin-equivalent bearer tokens.
- Риски: сложность UX, миграции токенов, тесты на privilege escalation, хранение token hashes.
- Статус: design candidate описан в [Scoped API Tokens для `amn2`](../docs/superpowers/specs/2026-05-30-scoped-api-tokens-design.md).

### Hardened first-run bootstrap

- Идея: заменить default credentials на forced password setup, one-time bootstrap token или локальный first-run secret.
- Польза: снимает классический риск `admin/admin` после первого запуска.
- Риски: recovery flow, headless install, UX первого запуска, тесты bootstrap/recovery.
- Статус: research после deep-dive.

### Secret inventory и redacted backup

- Идея: перед любым backup/restore явно классифицировать секреты и по умолчанию отдавать redacted backup.
- Польза: снижает риск случайной утечки SSH keys, panel tokens, Telegram tokens и внешних API keys.
- Риски: пользователю нужен понятный full-backup режим, encryption key management, restore compatibility.
- Статус: first machine-checkable no-route registry выполнен в `amn2/codex/secret-inventory-registry`, commit `9ce42f4`; details in [Secret inventory registry implementation](../research/amn2/secret-inventory-registry-implementation.md). Backup/import policy отдельно выполнен в `amn2/codex/backup-import-policy-contract`.

### Safe SSH/sudo policy

- Идея: описать безопасный SSH execution layer: host key pinning, no password in command string, secret redaction in logs, dry-run, audit, rollback.
- Польза: критично для любых операций, которые меняют удаленный VPN-сервер.
- Риски: сложность реализации, разные sudoers-конфигурации, совместимость с существующими серверами.
- Статус: reinforced by [`amn2` remote operations inventory](../research/amn2/remote-operations-inventory.md).

### Route policy matrix

- Идея: перед реализацией API фиксировать таблицу endpoint, role, auth method, side effect, audit requirement и tests.
- Польза: снижает риск разнородных guards и случайного privilege escalation.
- Риски: требует дисциплины при добавлении endpoints и синхронизации OpenAPI/docs.
- Статус: design candidate описан в [Route Policy Matrix для `amn2`](../docs/superpowers/specs/2026-05-30-route-policy-matrix-design.md).

### API operation risk classes

- Идея: классифицировать API-действия как read-only, secret-read, state-write, remote-exec и destructive.
- Польза: помогает заранее определить confirmation, audit, dry-run и test requirements.
- Риски: ошибочная классификация может дать слишком мягкие guardrails.
- Статус: research после API surface deep-dive.

### Destructive operation test plan

- Идея: для reboot, clear, uninstall, raw config save и restore иметь отдельные тесты отказов, audit events и recovery notes.
- Польза: production-перенос становится проверяемым, а не только “осторожным”.
- Риски: нужны test doubles для remote server и аккуратная модель dry-run.
- Статус: research после API surface deep-dive.

### Command execution contract

- Идея: remote operation должна описываться contract-ом: тип риска, inputs, expected side effects, timeout, allowed exit codes, redaction, audit summary и recovery note.
- Польза: SSH/sudo/Docker/firewall операции становятся тестируемыми и обозримыми до выполнения.
- Риски: больше design работы перед первой реализацией; понадобится fake runner и дисциплина в manager-ах.
- Статус: design candidate updated after [`amn2` remote operations inventory](../research/amn2/remote-operations-inventory.md): [RemoteOperationRunner для `amn2`](../docs/superpowers/specs/2026-05-30-remote-operation-runner-design.md).

### Dry-run-first remote operations

- Идея: install, uninstall, clear, raw config save и firewall/Docker changes сначала строят plan preview, а уже затем применяются.
- Польза: снижает риск случайно сломать VPS или удалить рабочие контейнеры.
- Риски: не все remote checks можно идеально эмулировать; dry-run не должен создавать ложное чувство безопасности.
- Статус: reinforced by [`amn2` remote operations inventory](../research/amn2/remote-operations-inventory.md).

### Remote operation audit events

- Идея: каждая state-changing remote operation пишет audit event до и после выполнения, без секретов в payload.
- Польза: проще разбирать инциденты, partial failures и действия операторов.
- Риски: нужно хранить audit отдельно от sensitive outputs и продумать retention.
- Статус: reinforced by [`amn2` remote operations inventory](../research/amn2/remote-operations-inventory.md).

### Manager interface checklist

- Идея: для каждого protocol/service manager заранее фиксировать обязательные методы: `detect`, `status`, `plan`, `apply`, `rollback_note`, `audit_summary`, `test_double`.
- Польза: уменьшает хаос при добавлении новых протоколов и облегчает тестирование.
- Риски: слишком жесткий interface может мешать нестандартным протоколам; нужен capability-based подход.
- Статус: research после manager architecture deep-dive.

### Host key enrollment

- Идея: добавление VPS должно включать явный SSH host key enrollment/pinning вместо автоматического доверия неизвестному ключу.
- Польза: снижает риск MITM при управлении production-сервером.
- Риски: UX сложнее для новичков; нужен recovery-flow при переустановке VPS.
- Статус: reinforced by [`amn2` remote operations inventory](../research/amn2/remote-operations-inventory.md).

### Configurable VPN subnet/IPAM

- Идея: сделать subnet/IPAM для AWG/WireGuard явной настройкой server/profile, а не hardcoded значением.
- Польза: несколько серверов, routed/site-to-site сценарии и будущая миграция становятся безопаснее.
- Риски: изменение subnet может ломать existing peers; нужны CIDR validation, conflict detection, migration story, dry-run preview и audit.
- Статус: research candidate после [GitHub watch PRVTPRO](../research/upstreams/prvtpro-amnezia-web-panel-github-watch.md); открывать design spec только после review текущей IPAM/server model в `amn2`.

### PRVTPRO upstream refresh 2026-06-10

Источник: [PRVTPRO/Amnezia-Web-Panel upstream refresh 2026-06-10](../research/upstreams/prvtpro-amnezia-web-panel-upstream-refresh-2026-06-10.md).

Лицензия: GPL-3.0, только самостоятельная реализация идей.

Рекомендованная очередь для AMN2 Phase 4:

- `P4-PRVTPRO-REFRESH-002`: expiration-field contract tests для user/device lifecycle fields. Статус: завершено как AMN2 local-only, evidence `research/amn2/phase-4-prvtpro-expiration-contract-tests-implementation-2026-06-10.md`.
- `P4-PRVTPRO-REFRESH-001`: read-only About/Version/Build status в operator UI. Статус: завершено как AMN2 local-only, evidence `research/amn2/phase-4-prvtpro-build-status-implementation-2026-06-10.md`.
- `P4-PRVTPRO-REFRESH-003`: read-only server status/latency UX. Статус: только после design boundary, без SSH write и без sync/health action.
- `P4-PRVTPRO-REFRESH-004`: API taxonomy/OpenAPI grouping. Статус: завершено как AMN3 docs-only policy support, evidence `research/amn2/phase-4-prvtpro-api-taxonomy-openapi-grouping-2026-06-10.md`.

Negative control: не переносить upstream Bearer token model как admin-equivalent access ко всем admin endpoints; сохраняем scoped tokens, route policy, audit и named gates.

## Из текущего `amn2` baseline

Источники: [`amn2`: config delivery inventory](../research/amn2/config-delivery-inventory.md), [`amn2`: remote operations inventory](../research/amn2/remote-operations-inventory.md)

### Config delivery policy table

- Идея: перед новыми download/share/recovery endpoints описывать actor, gate, risk class, output, audit и tests для каждой выдачи config.
- Польза: снижает риск случайно сделать public/self-service flow шире, чем задумано.
- Риски: policy должна оставаться синхронизированной с реальными routes, bot workflows и email recovery.
- Статус: `inventory-complete-first-pass`, следующий шаг - route/config delivery policy design.

### Secret-bearing import links

- Идея: считать `vpn://` import link таким же чувствительным артефактом, как `.conf` и QR, потому что он reversibly encodes полный config.
- Польза: меньше риск положить link в audit, logs, metadata, diagnostics или публичный preview.
- Риски: UX и support могут воспринимать link как “не секрет”, если private key не виден строкой.
- Статус: добавить в policy/test checklist перед любыми delivery changes.

### Public recovery audit and rate-limit review

- Идея: отдельно проверить rate-limit и audit для public token redemption без сохранения raw token, config, QR или `vpn://` link.
- Польза: public endpoint остается удобным, но его проще анализировать при инциденте.
- Риски: audit не должен раскрывать secret-bearing payload, а errors не должны помогать подбирать token/email.
- Статус: research candidate после `amn2` config delivery inventory.

### Remote operation partial-failure contract

- Идея: для live apply/revoke описывать, что делать если remote step уже прошел, а local DB/audit step упал, или если reset нескольких устройств оборвался посередине.
- Польза: меньше риск рассинхронизации между VPS и локальной базой.
- Риски: rollback не всегда возможен автоматически, поэтому нужен recovery note и повторяемый resume flow.
- Статус: covered by updated [RemoteOperationRunner design](../docs/superpowers/specs/2026-05-30-remote-operation-runner-design.md), следующий шаг - implementation plan review для узкого first slice.

### Secret-safe peer apply CLI

- Идея: заменить secret-bearing CLI аргумент `--preshared-key` на stdin/file descriptor/one-shot prompt или другой безопасный канал.
- Польза: PSK не попадает в shell history и process args.
- Риски: UX CLI станет чуть сложнее; нужны тесты, что dry-run/live output не печатает PSK.
- Status: implemented in `amn2` PR #8 (`568c611`) as `--preshared-key-stdin`; verified locally and by VPS read-only smoke. Keep `--preshared-key` only as a compatibility path for explicitly accepted disposable one-time tests.

### Shared command policy for telemetry

- Идея: traffic collection должна использовать общий read-only command policy или отдельную allowlist, синхронную с server health checks.
- Польза: telemetry не станет обходом вокруг SSH command guardrails.
- Риски: policy должна поддержать runtime-specific команды без расширения до unsafe shell.
- Статус: covered as requirement in updated [RemoteOperationRunner design](../docs/superpowers/specs/2026-05-30-remote-operation-runner-design.md).

### Domain Zone Exclusion Policy

- Идея: добавить включаемую настройку профиля/сервера, при которой выбранные доменные зоны, например `.ru` и `.рф`, не отправляются через VPN-туннель, а обрабатываются отдельной policy.
- Важное уточнение: настоящий bypass возможен только на клиенте до входа пакета в VPN. Если трафик уже попал на VPN-сервер, он уже прошел через AmneziaWG/WireGuard; сервер может только выпустить его наружу, заблокировать или отдать DNS policy response.
- Рекомендуемая архитектура: client-side `domain_exclusions` как основная функция, server-side DNS/egress blocklist как страховка от случайного выхода через VPN.
- Польза: operator может явно задать split-routing policy для доменных зон, где нужен прямой маршрут клиента или запрет выхода через VPN.
- Риски: WireGuard/AmneziaWG не поддерживает domain routing нативно; нужны OS/client-specific rules, split DNS, локальный resolver/proxy или обновляемые IP sets. IP-based approximation может устаревать, ломать CDN и давать ложное чувство точности.
- Guardrails: default off, явное включение, preview affected zones, audit события изменения policy, тесты генерации config/profile и тесты, что server-side fallback не выдает эту функцию за полноценный client bypass.
- Статус: новый design candidate; если принимаем, реализация должна попасть и в начальный проект `AMNEZIYA`, а не оставаться только идеей для будущего hybrid.

### Ближайшая очередь design review

- `RemoteOperationRunner`: updated design готов к review; первый implementation plan подготовлен для read-only server health slice: [RemoteOperationRunner First Slice](../docs/superpowers/plans/2026-05-30-remote-operation-runner-first-slice.md).
- `Domain Zone Exclusion Policy`: client-side split-routing для доменных зон плюс server-side DNS/egress fallback; default off, нужен отдельный design spec перед implementation plan.
- `Remote operation partial-failure contract`: local/remote consistency, rollback notes и resume flow.
- `Route Policy Matrix`: endpoint, role, auth method, side effect, risk class, audit и tests.
- `Scoped API Tokens`: one-time display, hash storage, scopes, expiry, revoke и owner inheritance.
- `Secret Inventory + Backup Policy`: redacted backup по умолчанию и encrypted full backup как явный режим.
- `Public/Self-service Config Delivery`: ownership tests, hashed share tokens, expiry, revoke, audit и `secret-read` handling для `.conf`, QR и `vpn://`.
- `Config delivery integrity tests`: byte-level QR/config encoding, non-ASCII names, Android/import compatibility и no secret leakage в logs/audit.
- `Manager config export contract`: единый export/result model для protocol manager-ов, чтобы self-service/share/admin UI не зависели от несовместимых method signatures.
- `Configurable VPN subnet/IPAM`: CIDR validation, conflict detection, migration story и dry-run/audit перед изменением live server.
- `Config delivery policy table`: actor, gate, risk class, output, audit и tests для текущих и будущих config delivery flows.
- `Web-admin 2FA`: поставлена на паузу решением от 2026-05-30; inventories сохраняем как контекст, но implementation plan не пишем без отдельного решения: [`amn2` decision log](../research/amn2/decisions.md).
- Статус: `paused`.

## Из wg-easy/wg-easy

Источник: [research/upstreams/wg-easy-wg-easy.md](../research/upstreams/wg-easy-wg-easy.md)

Статус лицензии: AGPL-3.0-only, только самостоятельная реализация идей.

Итоговый feature gap: [research/upstreams/wg-easy-wg-easy-feature-gap.md](../research/upstreams/wg-easy-wg-easy-feature-gap.md)

### Public-safe client read models

- Идея: разделять internal client model и public-safe representation, где private key/pre-shared key исключены по умолчанию.
- Польза: снижает риск случайной утечки client secrets через list/detail endpoints.
- Риски: нужен secret inventory и тесты, что sensitive fields не попадают в API/backup/logs.
- Статус: reinforced by [wg-easy config delivery deep-dive](../research/upstreams/wg-easy-wg-easy-config-delivery.md).

### Client expiration

- Идея: добавить expiration как часть lifecycle connection/client.
- Польза: удобно для временного доступа, trial, support и cleanup.
- Риски: что значит expiration для уже выданного config, нужен revoke/disable behavior и tests.
- Статус: reinforced by [wg-easy config delivery deep-dive](../research/upstreams/wg-easy-wg-easy-config-delivery.md).

### Metrics surface для peers

- Идея: read-only metrics endpoint для configured/enabled/connected peers, traffic и latest handshake.
- Польза: полезно для monitoring без захода в admin UI.
- Риски: labels могут раскрывать client names/IP, нужен route policy, bearer scope и privacy review.
- Статус: reinforced by [wg-easy metrics surface deep-dive](../research/upstreams/wg-easy-wg-easy-metrics-surface.md).

### Metrics privacy policy

- Идея: для metrics заранее описывать privacy class каждого label/field: aggregate, per-peer pseudonymous, per-user, IP/endpoint, activity metadata.
- Польза: снижает риск утечки client names, IP, endpoint и usage metadata в Prometheus/Grafana/backup.
- Риски: меньше удобства в dashboards по умолчанию; нужны opt-in labels и tests.
- Статус: research candidate после [wg-easy metrics surface deep-dive](../research/upstreams/wg-easy-wg-easy-metrics-surface.md).

### Scoped metrics token

- Идея: metrics endpoint должен использовать scoped token вроде `metrics:read`, а не optional broad password.
- Польза: expiry, revoke, owner inheritance и audit становятся едиными с общей token model.
- Риски: нужна связка с `Scoped API Tokens` и migration story для Prometheus scrape configs.
- Статус: research candidate после [wg-easy metrics surface deep-dive](../research/upstreams/wg-easy-wg-easy-metrics-surface.md).

### Permission wrapper with required resource check

- Идея: route wrapper должен заставлять handler выполнить resource-level check, если policy зависит от конкретного resource.
- Польза: снижает риск забыть ownership check после role check.
- Риски: требует аккуратного API middleware/dependency design и тестов на denied ownership.
- Статус: reinforced by [wg-easy permissions/auth/2FA deep-dive](../research/upstreams/wg-easy-wg-easy-auth-permissions-2fa.md).

### Account-level TOTP/2FA

- Идея: добавить 2FA как account-level security primitive, а не только UI-функцию login form.
- Польза: снижает риск компрометации operator/user password.
- Риски: recovery flow, rate limit, lockout, audit, secret inventory для TOTP key, запрет обхода через alternate auth methods.
- Статус: `paused`; первые `amn2` inventories сохраняются как справочный контекст, но 2FA не идет в ближайшую работу до отдельного решения: [decision log](../research/amn2/decisions.md), [amn2 auth/security inventory](../research/amn2/current-auth-security-inventory.md), [route/auth inventory](../research/amn2/route-auth-surface-inventory.md), [secret inventory](../research/amn2/secret-surface-inventory.md).

### Disabled user effective access gate

- Идея: disabled/demoted user должен терять effective access во всех auth methods: session, scoped token, self-service и integration.
- Польза: проще revoke доступа без ручной очистки каждого канала.
- Риски: нужны tests для session/token inheritance и понятная UX-модель active sessions.
- Статус: research candidate после [wg-easy permissions/auth/2FA deep-dive](../research/upstreams/wg-easy-wg-easy-auth-permissions-2fa.md).

### Forced setup/bootstrap flow

- Идея: первый admin создается через явный setup/bootstrap, а не через default credentials.
- Польза: снижает риск забытых стандартных паролей после установки.
- Риски: headless install, recovery, one-time bootstrap token, audit и закрытие setup после completion.
- Статус: reinforced by [wg-easy permissions/auth/2FA deep-dive](../research/upstreams/wg-easy-wg-easy-auth-permissions-2fa.md).

### Versioned migration/import guide

- Идея: для breaking changes и config import держать versioned migration guide с backup-first flow, compatibility limits, preflight, rollback и test plan.
- Польза: снижает риск потерять доступ, секреты или client state при обновлениях и переносах.
- Риски: migration docs должны совпадать с реальным wizard/API behavior; import file содержит private keys и pre-shared keys.
- Статус: research candidate после [wg-easy operational docs/migration deep-dive](../research/upstreams/wg-easy-wg-easy-operational-docs-migration.md).

### Operational docs as transfer gate

- Идея: feature не считается готовой к переносу в `amn2`, если для нее нет operator-facing docs по backup, update, rollback, recovery, security caveats и tests.
- Польза: production-перенос становится проверяемым и поддерживаемым, а не только реализованным.
- Риски: больше upfront work; docs must not drift from route guards and actual behavior.
- Статус: research candidate после [wg-easy operational docs/migration deep-dive](../research/upstreams/wg-easy-wg-easy-operational-docs-migration.md).

## Из kyoresuas/amnezia-api

Источник: [research/upstreams/kyoresuas-amnezia-api.md](../research/upstreams/kyoresuas-amnezia-api.md)

Статус лицензии: MIT, но перенос в `amn2` только как самостоятельный дизайн без копирования кода.

Актуализация 2026-06-10: свежий GitHub refresh зафиксирован в [kyoresuas/amnezia-api GitHub refresh 2026-06-10](../research/upstreams/kyoresuas-amnezia-api-github-watch-2026-06-10.md). Новые полезные сигналы: operation lock/serialization, safer atomic config write pattern, `active|disabled` + `expiresAt` lifecycle vocabulary, QR/`vpn://` import compatibility tests, Fastify rate-limit/Helmet hardening and setup/deploy resilience. Это усиливает будущий `WAPI-V001` threat model, но не открывает `/api/clients`, `config:read`, public API `3040`, backup/import/reboot или установку upstream service.

### Local Amnezia API agent

- Идея: поставить рядом с Amnezia локальный API-agent, который управляет users/peers через ограниченный HTTP contract, а не через постоянный внешний SSH control plane.
- Польза: хорошо совпадает с текущей задачей управления пользователями Amnezia по API.
- Риски: agent получает высокий доступ к Docker/config/secret state; нужны local-only bind, scoped tokens, audit и hardening.
- Статус: high-priority design candidate.

### Client lifecycle API

- Идея: формализовать lifecycle peer/user: create, list, disable, enable, delete, `expiresAt`, config delivery.
- Польза: дает основу для панели, Telegram-бота, billing и support tooling.
- Риски: disable/delete semantics должны быть одинаково понятны для AmneziaWG, AmneziaWG2 и Xray; нужны tests на partial failure.
- Статус: research candidate.

### Secret-safe `vpn://` and QR delivery

- Идея: считать `vpn://`, QR и downloadable config одинаковым `secret-read` output с явной policy.
- Польза: снижает риск случайно логировать или отдавать import link как обычное metadata.
- Риски: нужны redaction, audit, expiry/revoke для share flows и tests на отсутствие secret leakage.
- Статус: reinforced candidate.

### Backup/import as dangerous API

- Идея: backup/import endpoint проектировать только через redacted/full режимы, validation, dry-run preview, encryption option и recovery note.
- Польза: полезно для восстановления сервера, но не должно становиться простой кнопкой утечки всех ключей.
- Риски: full backup содержит private keys, PSK, server configs и client state; import может разрушить runtime.
- Статус: first local-only no-route policy/preview slice выполнен в `amn2/codex/backup-import-policy-contract`, head `afb2702` with foundation commit `d2c160b`; details in [Backup/import policy contract implementation](../research/amn2/backup-import-policy-contract-implementation.md). Web/API full backup, restore apply и import apply остаются отдельными gates.

## Automation intake aggregation 2026-06-14

Источник: [Automation intake aggregation and closeout readiness](../research/amn2/after-phase-6-automation-intake-aggregation-closeout-readiness-2026-06-14.md).

PRVTPRO heartbeat output was available and normalized. KYORESUAS/Amnezia final
automation reports were not visible in the current AMN2 thread or local AMN3
evidence, so they are marked `missing-input` and supplemented only with direct
public GitHub metadata refresh.

### `FI-M004` Package asset path preflight

- Идея: перед будущим installer/package apply проверять, что все referenced
  operator-kit assets, upload paths and generated runbook paths exist and are
  packaged.
- Польза: снижает риск сломанного обновления из-за missing/stale asset path.
- Gate: `package/preflight only`.
- Статус: completed as AMN2 local-only code/tests/docs in `4cde273`; evidence
  [FI-M004 + P6-N005 installer preflight and taxonomy guards](../research/amn2/after-phase-6-installer-preflight-taxonomy-guards-2026-06-14.md).

### `P6-M005` Multi-instance, port and IPAM conflict model

- Идея: описать multi-instance/protocol runtime capabilities with port,
  subnet, endpoint and address constraints before any live multi-server action.
- Польза: будущий clean installer and hybrid path смогут заранее показать
  conflicts instead of discovering them during live apply.
- Gate: `local-only/docs/tests`.
- Статус: completed as AMN2 local-only code/tests/docs in `b121865`; evidence
  [P6-M005 multi-instance/IPAM conflict model](../research/amn2/after-phase-6-multi-instance-ipam-conflict-model-2026-06-14.md).

### `P6-N005` OpenAPI/taxonomy route-order drift guard

- Идея: если AMN2 генерирует public/operator API docs, держать deterministic
  route grouping/order aligned with surface policy.
- Польза: уменьшает drift между route policy, docs taxonomy and generated API
  surface.
- Gate: `local-only/docs/tests`; public publication still requires `P6-C001`.
- Статус: completed as AMN2 local-only code/tests/docs in `4cde273`; evidence
  [FI-M004 + P6-N005 installer preflight and taxonomy guards](../research/amn2/after-phase-6-installer-preflight-taxonomy-guards-2026-06-14.md).

### Amnezia client compatibility watch

- Идея: keep DefaultVPN/iOS, installed AmneziaWG iOS/Android and desktop client
  compatibility as watch-only unless a concrete import/connectivity regression
  appears.
- Польза: сохраняет актуальность пользовательских инструкций без преждевременного
  открытия config delivery.
- Gate: `watch-only`.
- Статус: no active AMN2 item required after
  [Amnezia ecosystem refresh 2026-06-14](../research/upstreams/amnezia-vpn-client-defaultvpn-refresh-2026-06-14.md); current copy/client matrix remains the `b3102db` baseline and latest smoked head is `0de7a77`.
