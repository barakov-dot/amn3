# `amn2`: config delivery inventory

## Паспорт

- Production repo: `C:\Users\SooL\Documents\Amneziya`
- Дата снимка: 2026-05-30
- Режим: read-only inventory, без изменений в `amn2`.
- Секреты: `.env` намеренно не читался.
- Цель: описать, где VPN-конфиг создается, собирается в артефакты, отправляется пользователю или восстанавливается, чтобы любые public/self-service идеи проходили через policy, audit и test gate.

## Краткий вывод

В `amn2` уже есть централизованная точка сборки delivery-пакета: `app/services/config_delivery.py::build_device_config_delivery()`. Она восстанавливает config из encrypted device secrets, рендерит нужную версию шаблона и передает результат в `app/bot/delivery.py::build_config_delivery()`.

Главный вывод: `.conf`, QR PNG и `vpn://` link являются secret-bearing output. `vpn://` не содержит строку `PrivateKey` в открытом виде, но reversibly encodes полный config, включая private key и preshared key. Поэтому любые новые ссылки, preview, email, self-service endpoints и audit events должны считать этот link таким же чувствительным артефактом, как raw config.

## Pipeline выдачи

1. `build_device_config_delivery()` получает user, server и device из `Repository`.
2. `SecretBox` decrypt-ит `device["peer_private_key_encrypted"]` и `device["preshared_key_encrypted"]`.
3. `render_client_config_for_version()` рендерит config по `device["config_version"]`, DNS, allowed IPs и optional template directory.
4. Message template берется по `CONFIG_READY_TEMPLATE_KEY`, с fallback на `DEFAULT_CONFIG_READY_TEMPLATE`.
5. `build_config_delivery()` собирает:
   - raw `config_text`;
   - `.conf` attachment bytes;
   - QR PNG из raw config;
   - `vpn://` import link;
   - user-facing message text with app links.

## Классы артефактов

| Артефакт | Класс риска | Почему важно | Минимальное правило |
| --- | --- | --- | --- |
| `config_text` | `secret-read` | содержит peer private key и preshared key | не логировать, не класть в audit metadata, отдавать только через проверенный канал |
| `.conf` bytes | `secret-read` | raw config as file attachment | выдавать только после auth/ownership/token gate |
| QR PNG | `secret-read` | содержит полный config в кодируемом виде | не сохранять как plain artifact без явного решения |
| `vpn://` link | `secret-read` | reversibly encodes полный config | считать секретом, даже если `PrivateKey` не виден как строка |
| Message template | `secret-adjacent` | становится secret-bearing, если включает `{vpn_link}` | шаблоны проверять отдельно от audit/log output |
| Email recovery token | `public-token-secret-read-gate` | raw token открывает выдачу config через public endpoint | хранить только hash, TTL, one-time, rate-limit review |

## Поверхности выдачи

| Surface | Actor / gate | Output | Текущие controls | Что проверять перед изменениями |
| --- | --- | --- | --- | --- |
| Bot approval flow | admin Telegram actor | config delivery после approve | admin check, encrypted secrets, config version validation | audit metadata без config/link/QR, remote apply failure behavior |
| Bot admin resend | admin Telegram actor + `device_id` | regenerated config delivery | `is_admin()`, encrypted secret decrypt, delivery tests | device-id direct access остается только admin surface |
| Bot user resend | Telegram user + owned `device_id` | regenerated config delivery | user lookup, ownership check through `get_user_device()` | privilege escalation tests for чужой device |
| Web email config send | web admin session + CSRF | config email to user email | admin session, CSRF, email enabled, optional verified email requirement, ownership lookup | audit event без secret-bearing payload |
| Web email recovery start | web admin session + CSRF | one-time recovery token email | admin session, CSRF, verified email, hashed token, TTL | token must not appear in URL, logs or metadata |
| Public email recover | raw token + email | config email after token redeem | hashed token lookup, purpose, TTL, one-time, verified email, ownership lookup | rate-limit, audit of successful/failed redemption, generic errors |
| Config template preview | web admin session | safe preview / template page | auth-only, tests hide real private/psk/app secret | preview must stay synthetic, never real device secrets |

## Уже сильные места

- Device private key и preshared key не хранятся plain в DB, а decrypt-ятся только для runtime delivery.
- Config versions ограничены поддерживаемыми значениями: `amneziawg_v1_5` и `amneziawg_v2`.
- Template override проверяет поля шаблона и rejects unknown/malformed template variables.
- Email recovery tokens хранятся как SHA-256 hash и используются one-time.
- Web admin email actions защищены session + CSRF.
- User resend и web email flows проверяют ownership через user/device lookup.
- Tests уже покрывают raw-token discipline, verified email requirement, safe template preview и то, что `vpn://` не содержит literal `PrivateKey`.

## Gaps перед production-доработками

- Нет единой route/config delivery policy table, где каждая выдача config явно помечена как `secret-read`.
- Для public token redemption не найден отдельный rate-limit слой в рамках этого прохода.
- Для public token redemption стоит отдельно решить, нужен ли audit event успешного и неуспешного redeem без raw token и без config/link.
- `vpn://` link легко воспринимается как безопасный, потому что он не показывает private key строкой; в policy и docs его надо считать secret-bearing.
- После PRVTPRO issues #41/#51 нужен byte-level QR test: отрисованный QR должен декодироваться в тот же UTF-8 payload, включая non-ASCII names.
- После PRVTPRO issue #49 нужен единый manager export contract или аналогичный слой, чтобы новые protocol manager-ы не ломали self-service/admin/public config delivery несовместимыми signatures. Update 2026-06-01: design boundary подготовлен в `manager-config-export-contract.md`.
- Новые self-service endpoints нельзя добавлять как "просто скачать конфиг": им нужен ownership/token gate, expiry, revoke story, audit и tests.

## Transfer gate для идей из lab

Любая идея из upstream-проектов про public links, QR, download, email recovery или self-service config delivery проходит отдельные вопросы:

- License gate: переносим только идею/подход, без копирования GPL/AGPL кода.
- Value gate: какая реальная боль закрывается по сравнению с текущим bot/email resend.
- Risk gate: какой actor получает `secret-read` доступ и как этот доступ отзывается.
- Architecture fit: новый flow использует существующий `build_device_config_delivery()` или явно объясняет, почему нужен другой путь.
- Test plan: ownership denial, expired token, used token, disabled email, unverified email, чужой device, redaction/audit без secret-bearing payload, QR decode round-trip, `vpn://` decode round-trip и manager export contract tests.

## Решение для lab

Статус: `config-delivery-inventory-first-pass`; manager export contract design prepared in `manager-config-export-contract.md`.

Пока не переносим public/self-service delivery в `amn2` как code edit. Сначала фиксируем policy-слой: какие endpoints могут выдавать config, кто actor, какой gate, какой audit, какие tests и как revoke работает после выдачи.

## Следующие рабочие шаги

1. Использовать `manager-config-export-contract.md` как вход для no-route contract/adapters/tests перед любым новым protocol manager, public/self-service endpoint или API `config:read`.
2. Подготовить route/config delivery policy design на базе этого inventory и текущего route/auth surface.
3. Расширить test matrix для существующего `build_device_config_delivery()` на `.conf`, QR, `vpn://`, UTF-8/non-ASCII и no-secret-leak checks.
4. Перед любым self-service config endpoint добавить обязательный test matrix для ownership, token lifecycle, audit и redaction.
5. Перейти к remote operations inventory: approve flow и config delivery связаны с server apply, поэтому remote failure/rollback нужно рассмотреть отдельно.
