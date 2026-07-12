# AMN2 Phase 10: lifecycle, web diagnostics and cascade revoke

Дата: 2026-07-12.

## Решение upstream

Принудительный upstream-прогон принят. В PRVTPRO, kyoresuas и Amnezia нет
новых релевантных изменений относительно 2026-07-11. Launch plan не изменен.
Новые уроки реализованы поверх `e709746` тремя логическими коммитами.

## Что уже существовало и повторно использовано

- `OperationPlan`, idempotency и partial-failure records;
- report-only reconciliation и remote peer inventory collector;
- `SurfacePolicy` для authenticated, audited, remote-read web sync;
- одноразовая выдача конфигурации, delivery/recovery links, user/device/peer
  models и assignments.

Новый live apply, Telegram delivery, public enrollment и автоматическое
исправление drift не открывались.

## Реализовано

`bdbf740` добавляет детерминированный lifecycle:
`issued -> claimed -> config_ready -> delivered -> acceptance_verified`.
Каждое событие хранит timestamp, безопасную duration, failure stage и
структурированное evidence без токенов и чувствительных client logs.

`956e76b` выводит в существующей read-only admin/web диагностике desired,
observed, drift, freshness, reason, recommended action, evidence count и
связанный passport ID. Повторный remote collection не выполняется.

`3c91601` исправляет security-дефект отзыва физического устройства. Cascade
revoke строится как remote-first `OperationPlan`, закрывает активные tickets,
delivery/recovery links и assignments, отзывает passport и удаляет remote
peer. При закрытом VPS apply локальное удаление, оставляющее peer живым,
запрещено. Late acceptance, reconnect и повторное observation не возвращают
доступ отозванному устройству.

## Миграции и контракты

Добавлена таблица `device_lifecycle_events` с индексами. Enrollment и passport
контракты расширены безопасными lifecycle/revoke состояниями. Hardware
attestation, MDM и полноценный endpoint posture не заявляются.

## Проверки

- lifecycle/passport/enrollment: `17 passed`;
- web/drift/security: `55 passed, 1 warning`;
- cascade focused: `3 passed`;
- expanded affected surfaces: `106 passed, 1 warning`;
- revoke/passport/delivery regression: `20 passed`;
- full AMN2 suite: `870 passed, 1 skipped, 1 warning`;
- `git diff --check e709746..3c91601`: passed.

## Runtime и запуск

Оператор подтвердил недоступность ранее работающих клиентских конфигураций.
SSH/22 и ICMP до `89.185.80.166` также timeout. В этой работе VPS runtime не
останавливался и не изменялся; последняя проверенная база 2026-07-11 была
`overlay 1c7fb78`, `amnezia-awg2` running, web active/enabled, bot
inactive/disabled. Текущее состояние требует восстановления доступности
host/provider и повторной read-only проверки; нельзя выдавать это за
service-level restart.

Read-only diagnostics остается ближайшим launch-compatible продуктовым
срезом. Enrollment Ticket не задерживает релиз без обязательного self-service.
Cascade revoke включен как исправление найденного security-дефекта. Live
remediation остается закрытой. Следующий локальный кандидат:
`START_PHASE10_3C91601_VPS_PACKAGE_PREP_SLICE`.
