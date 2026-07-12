# Phase 10: Drift Diagnostics, Device Passport и Enrollment Ticket

Дата: 2026-07-12.

Статус: `completed-local-code-tested-reviewed-pending-package-decision`.

## Границы

Работа выполнена в согласованной AMN2 ветке `codex-vps-test-prep` от
`44287d4`. Она не создавала и не удаляла VPS peer, не генерировала и не
доставляла клиентские конфигурации, не запускала Telegram polling и не
включала автоматическое исправление drift.

```text
baseline=44287d4
drift_commit=fc48a7e
device_passport_commit=a2cbcfa
enrollment_ticket_commit=e709746
final_source_head=e709746
```

## Что существовало до начала

Повторно использованы существующие AMN2 контракты:

- `OperationPlan`, idempotency и remote-operation safety;
- report-only reconciliation boundary;
- read-only `PeerInventoryCollector` и `PeerInventoryService`;
- одноразовая выдача конфигураций, не смешанная с enrollment credential;
- `SurfacePolicy` и отдельные будущие self-service gates;
- safe audit metadata и partial-failure records;
- существующие user, device, peer и config-version модели.

Новые сервисы не открывают remote apply и не подменяют существующую config
delivery модель.

## Desired / Observed / Drift

Добавлена детерминированная `ReconciliationSnapshot` модель:

- desired peer state;
- observed peer state;
- drift state и machine-readable reason;
- nullable время последнего наблюдения;
- отсортированный safe evidence set;
- безопасное рекомендуемое следующее действие без автоматического apply.

Поддержаны состояния:

```text
aligned
missing_remote
unexpected_remote
stale_observation
observation_failed
unknown
```

Peer public key в safe metadata заменяется SHA-256 fingerprint. Ошибка remote
collector не переносит raw stdout/stderr в snapshot. Диагностика только читает
local desired rows и remote inventory; тест сравнивает полный SQLite dump до и
после вызова и подтверждает отсутствие изменений.

## Device Passport

Добавлена таблица `device_passports` и сервис паспорта. Внешний device ID имеет
формат `dev_<uuid4 hex>` и не зависит от hardware fingerprint.

Паспорт хранит:

- owner user и опциональную связь с существующим local device/peer;
- platform, официальный client type и известную client version;
- import method и config schema version;
- только `sha256:<digest>` конфигурации без raw config;
- last seen и структурированное safe acceptance evidence;
- актуальный desired/observed/drift snapshot при чтении.

До первого remote observation паспорт честно возвращает `unknown` и
`last_observed_at=null`. Capability boundary явно фиксирует отсутствие
hardware fingerprint, endpoint posture, device-impersonation protection, MDM
и собственного AMN2 agent.

## Device Enrollment Ticket

Добавлена таблица `device_enrollment_tickets` и local-service-only lifecycle:

- raw secret возвращается только при issue и скрыт из object repr;
- в SQLite сохраняются domain-separated SHA-256 hash и безопасный prefix;
- TTL ограничен, single-use включен и enforced;
- ticket привязан к user, platform и config schema version;
- revoke идемпотентен;
- сохраняются `claimed_at` и стабильный `claimed_device_id`;
- claim и создание паспорта выполняются одной SQLite transaction;
- exact retry с тем же idempotency key возвращает тот же passport;
- другой повторный claim отклоняется;
- invalid, expired, revoked и already-used возвращают одинаковую внешнюю
  ошибку `Device enrollment ticket is unavailable`;
- list/detail repository reads не выбирают token hash или idempotency hash;
- raw token отсутствует в DB dump, logs, safe audit metadata и read payloads.

Публичный self-service/API route не добавлен. Перед его будущим включением
обязательны отдельная authentication boundary, `SurfacePolicy` binding, rate
limiting и production route gate.

## Миграции

`initialize_schema` теперь создаёт две additive таблицы и три индекса:

```text
device_passports
device_enrollment_tickets
idx_device_passports_owner
idx_device_enrollment_tickets_user
idx_device_enrollment_tickets_expiry
```

Существующие user/device/peer строки и working defaults не переписываются.
Foreign keys связывают owner и optional local device; claimed passport FK
является deferred, чтобы ticket claim и passport insert оставались атомарными.

## Проверки

```text
drift_and_existing_reconciliation=16 passed
passport_schema_repository_backup_security=79 passed
enrollment_focused=9 passed
expanded_identity_token_delivery_security_policy=127 passed
full=864 passed, 1 skipped, 1 warning
diff_check=passed
```

Обязательные сценарии покрыты: successful claim, rejected second claim,
expired/revoked/invalid/already-used uniform error, one-winner concurrent
claim, raw-token absence, deterministic drift и read-only no-mutation.

## Влияние на запуск

Launch gate молча не расширен.

- Read-only Drift Diagnostics можно рассматривать как ближайший продуктовый
  slice после добавления authenticated operator read-only surface и
  `SurfacePolicy` binding. Auto-remediation остаётся запрещённым.
- Device Passport persistence готов локально; операторский read-only view и
  acceptance ingestion ещё не подключены.
- Enrollment Ticket не задерживает первый релиз, если self-service onboarding
  не входит в обязательный launch scope. Его public route остаётся выключен.

Следующий локальный кандидат после отдельного package-scope решения:

```text
START_PHASE10_E709746_VPS_PACKAGE_PREP_SLICE
```

## VPS Runtime Check

После full suite оператор запросил проверить, не остался ли service
выключенным после тестов. Последний подтверждённый runtime baseline от
2026-07-11:

```text
source_overlay=1c7fb78
amneziya_web=active_enabled
amnezia_awg2=running
amneziya_bot=inactive_disabled_by_design
```

Read-only SSH check 2026-07-12 не дошёл до авторизации: TCP 22 и ping получили
timeout. Ни один VPS unit/container не был остановлен, запущен или изменён.
Текущее состояние классифицировано как
`management-transport-unreachable-runtime-not-reverified`, а не как
`vpn-service-stopped`.

Новое обязательное operator rule: после любой тестовой остановки production
runtime вернуть исходное состояние, проверить его и явно уведомить оператора.

## После запуска

Post-launch остаются:

- drift history/retention и operator UX поверх snapshots;
- gated reconciliation apply с `OperationPlan`, preview, verify и rollback;
- self-service enrollment route, rate limits и abuse controls;
- acceptance ingestion из доверенного AMN2 agent, если такой agent появится;
- endpoint posture, MDM и защита от подмены устройства только при наличии
  отдельного доверенного agent/device attestation дизайна.
