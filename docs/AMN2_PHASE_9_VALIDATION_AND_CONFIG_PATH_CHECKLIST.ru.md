# AMN2 Phase 9 validation and config-path checklist

Дата: 2026-06-28
Статус: `docs-only-review-only`
Основа: `docs/AMN2_PHASE_9_TASK_MATRIX_REFRESH.ru.md`, `research/upstreams/amnezia-phase-9-refresh-2026-06-28.md`, `research/upstreams/prvtpro-phase-9-refresh-2026-06-28.md`.

## Цель

- Зафиксировать hardening checklist по XRay validation, который появился в upstream после 2026-06-21.
- Зафиксировать checklist по runtime config path и manager-export compatibility для будущих AMN2 config-management gate.
- Сохранить документационный режим: `no-live`, `no-vps`, `no-ssh`, `no-config-delivery`, `no-peer`.

## Ограничения режима

- Блокировать любые live/VPS/SSH/Telegram/public операции.
- Не разрешать config generation/delivery и peer creation.
- Не раскрывать в результате `.conf`, `QR`, `vpn://`, private key, PSK, token, password или raw logs.

## XRay validation checklist (candidate, docs-only)

### Условия pass

- Host validation поддержана до save/persist для конфигураций.
- SNI validation поддержана до save/persist для конфигураций.
- Path validation поддержана до save/persist для конфигураций.
- Numeric range validation (порт/MTU/keepalive/тайминги) поддержана до save/persist.
- Везде в docs-only pipeline сохраняется единая ошибка валидации без raw secrets.

### Условия fail / doc gap

- Любая новая проверка без единых предусловий для host/SNI/path/ranges.
- Любая валидация после применения payload без нормализованного error-boundary.
- Любой hardcoded exception bypass без явного pass/fail описания.

### Для future exact gate

- Technical owner подтверждает, что перечисленные валидации покрыты локальными тестами на уровне form handlers.
- Если покрытие временно неполное, фиксировать как `documented limitation` + `stop-line` для будущего exact gate.

## Runtime config-path / manager export compatibility checklist (candidate, docs-only)

### Принцип

- Менеджер/adapter должен не предполагать один фиксированный runtime config path без проверки.
- Формирование имени конфигурации, устройства и display name должно быть отделено от фактического runtime-path discovery.
- `Neobyatnaya-AMNZ-N` сохраняет статус canonical naming для config/device/filename policy.

### Pass-критерии

- Проверяется, что manager-экспорт опирается на контракт/проверенный контракт адаптера.
- Проверяется, что pipeline умеет находить фактический config path или явно fail-ит с reason code.
- Проверяется, что fallbackы display-name задокументированы и не подменяют production naming без explicit gate.
- Проверяется, что output-пайплайн остаётся redacted и не содержит секреты в логах/markdown.

### Fail / stop-lines

- Hardcode `wg0.conf/awg0.conf` как единственный путь без discovery/validation.
- Принятие generic имени через runtime path как production naming.
- Любая попытка config delivery/payload в этом контуре без exact gate.

### Для future exact gate

- Перед live execution требуется отдельный gate с локальными и remote proof по runtime path и manager-export contract.

## Итог для текущего этапа

- Решение: оба чеклиста фиксируются как docs-only readiness candidates.
- `decision_status`: `documented-limitations-accepted-with-hold`.
- Следующий step: keep execution hold until exact gate request.
