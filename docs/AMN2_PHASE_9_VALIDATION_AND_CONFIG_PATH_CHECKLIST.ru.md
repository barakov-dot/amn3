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

## XRay validation checklist (completed local snapshot slice)

Status update 2026-06-28: local code slice completed in AMN2 branch
`codex/public-config-delivery-policy-contract`, commit `fdc431d`. The runtime
adapter now accepts `runtime_type=xray_docker` and records a read-only Docker
container presence snapshot for XRay without config generation, config delivery,
peer creation, VPS/SSH/Telegram/public actions, or secret-bearing output.
Scoped verification: `tests/agent/test_runtime.py` +
`tests/server_config/test_loader.py -q` returned `14 passed`.

Status update 2026-06-28: numeric range validation local code slice completed
in AMN2 branch `codex/public-config-delivery-policy-contract`, commit
`5b1d34a`. The server config loader now rejects invalid `ssh.port`,
`vpn.port`, and `vpn.max_devices` values before save/persist boundaries.
Scoped verification: `tests/server_config/test_loader.py` +
`tests/agent/test_runtime.py -q` returned `19 passed`.

Status update 2026-06-28: host/path validation local code slice completed in
AMN2 branch `codex/public-config-delivery-policy-contract`, commit `876ce32`.
The server config loader now rejects empty or URL-like `ssh.host` and
`vpn.endpoint_host` values and rejects relative `runtime.config_path` values
before save/persist boundaries. Scoped verification:
`tests/server_config/test_loader.py` + `tests/agent/test_runtime.py -q`
returned `24 passed`.

Status update 2026-06-28: network/CIDR validation local code slice completed in
AMN2 branch `codex/public-config-delivery-policy-contract`, commit `6e0bbe2`.
The server config loader now validates `vpn.network_cidr`,
`vpn.server_address`, `vpn.dns`, and `vpn.allowed_ips`; invalid
`vpn.server_address` no longer silently falls back to configured network CIDR.
Scoped verification: `tests/server_config/test_loader.py` +
`tests/agent/test_runtime.py -q` returned `28 passed`.

Status update 2026-06-28: identifier validation local code slice completed in
AMN2 branch `codex/public-config-delivery-policy-contract`, commit `0129fc9`.
The server config loader now validates `server.name`, `server.location`,
`vpn.interface`, `runtime.service_name`, and `runtime.container_name` as
non-empty identifiers before save/persist boundaries. Scoped verification:
`tests/server_config/test_loader.py` + `tests/agent/test_runtime.py -q`
returned `33 passed`.

Status update 2026-06-28: unique server name local code slice completed in
AMN2 branch `codex/public-config-delivery-policy-contract`, commit `d1c2bc3`.
The server config loader now rejects duplicate `server.name` values before
`select_server` can resolve an ambiguous runtime target. Scoped verification:
`tests/server_config/test_loader.py` + `tests/agent/test_runtime.py -q`
returned `34 passed`.

Status update 2026-06-28: enum validation local code slice completed in AMN2
branch `codex/public-config-delivery-policy-contract`, commit `c7e5dbb`. The
server config loader now validates `ssh.auth.type`, `firewall.provider`, and
the existing `runtime.type` guard before runtime use. Scoped verification:
`tests/server_config/test_loader.py` + `tests/agent/test_runtime.py -q`
returned `37 passed`.

Status update 2026-06-28: config delivery template placeholder guard completed
in AMN2 branch `codex/public-config-delivery-policy-contract`, commit
`eeef841`. `build_config_delivery` now rejects unknown delivery placeholders
before package build while preserving admin/debug rendering behavior in
`render_template`. Scoped verification: `tests/bot/test_delivery.py` +
`tests/bot/test_bot_workflows.py -q` returned `28 passed`.

### Условия pass

- Host validation поддержана до save/persist для конфигураций.
- SNI validation поддержана до save/persist для конфигураций.
- Path validation поддержана до save/persist для конфигураций.
- Numeric range validation для текущих server config полей поддержана до
  save/persist: `ssh.port`, `vpn.port`, `vpn.max_devices`.
- Network/CIDR validation для текущих server config полей поддержана до
  save/persist: `vpn.network_cidr`, `vpn.server_address`, `vpn.dns`,
  `vpn.allowed_ips`.
- Identifier validation для текущих server config полей поддержана до
  save/persist: `server.name`, `server.location`, `vpn.interface`,
  `runtime.service_name`, `runtime.container_name`.
- Unique server name validation поддержана до runtime target selection:
  duplicate `server.name` values fail before `select_server`.
- Enum validation поддержана до runtime use: `ssh.auth.type`,
  `firewall.provider`, `runtime.type`.
- Delivery template placeholder guard поддержан до package build: unknown
  delivery placeholders fail before user-facing delivery package assembly.
- Везде в docs-only pipeline сохраняется единая ошибка валидации без raw secrets.
- Runtime snapshot для `xray_docker` ограничен read-only проверкой наличия
  контейнера и публикует только status/capabilities без runtime config payload.
- Runtime config path validation требует absolute POSIX path, если путь задан.

### Условия fail / doc gap

- Любая новая проверка без единых предусловий для host/SNI/path/ranges.
- Любая валидация после применения payload без нормализованного error-boundary.
- Любой hardcoded exception bypass без явного pass/fail описания.

### Для future exact gate

- Technical owner подтверждает, что перечисленные валидации покрыты локальными тестами на уровне form handlers.
- Если покрытие временно неполное, фиксировать как `documented limitation` + `stop-line` для будущего exact gate.

## Runtime config-path / manager export compatibility checklist (completed local slice)

Status update 2026-06-28: local code slice completed in AMN2 branch
`codex/public-config-delivery-policy-contract`, commit `990a376`. The config
export contract now supports safe `runtime_config_path_missing` without exposing
the raw runtime path; safe metadata publishes only `runtime_config_path_status`.
Scoped verification: `tests/services/test_config_export.py -q` returned
`7 passed`.

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

- Решение: runtime config-path guard, XRay runtime snapshot, server config
  numeric range validation, host/path validation и network/CIDR validation
  и identifier validation выполнены как local-code slices; duplicate server
  names теперь blocked-before-runtime-selection; enum validation выполнена как
  local-code slice; delivery template placeholder guard выполнен как local-code
  slice. Form-level XRay SNI validation остается future exact-gate hardening
  item, а config delivery остается not-approved.
- `decision_status`: `documented-limitations-accepted-with-hold`.
- Следующий step: keep execution hold until exact gate request.
