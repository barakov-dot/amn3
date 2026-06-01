# AMN3 Write API Policy Matrix

Цель документа - зафиксировать будущую write API policy matrix до включения
реальных маршрутов. Это локальная подготовка: она не активирует маршруты
`/agent/clients*`, не добавляет FastAPI endpoints и не выполняет mutations.

Кодовая основа:

- `app/agent/write_policy_matrix.py`
- `app/agent/write_contracts.py`
- `tests/agent/test_write_policy_matrix.py`
- `tests/agent/test_write_contracts.py`
- `tests/agent/test_policy.py`

Связанный UX/API flow: `docs/AMN3_WRITE_API_UX_FLOW.ru.md`.
Связанный audit contract: `docs/AMN3_WRITE_API_AUDIT_MODEL.ru.md`.
Связанный preflight/confirmation contract: `docs/AMN3_WRITE_API_PREFLIGHT_CONFIRMATION.ru.md`.
Связанная identity model: `docs/AMN3_USER_DEVICE_PEER_IDENTITY_MODEL.ru.md`.
Локальный release gate до VPS: `docs/AMN3_LOCAL_RELEASE_GATE.ru.md`.

## Gate

Любой write API включается только после успешного read-only smoke на реальном
VPS:

- Local Agent слушает только `127.0.0.1:3031`;
- web admin видит Local Agent без raw token;
- rollback проверен;
- logs проверены на отсутствие secret leakage;
- отдельный token/scope set для `agent:clients:write` подготовлен.

До этого матрица остается справочником и тестовым контрактом.

## Planned Operations

| Operation | Method | Path | Scope | Risk | Dry-run | Confirmation | Gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `local_agent.clients.apply.dry_run` | `POST` | `/agent/clients/dry-run` | `agent:clients:write` | `state-write` | yes | no | VPS smoke required |
| `local_agent.clients.apply` | `POST` | `/agent/clients` | `agent:clients:write` | `state-write` | no | yes | VPS smoke required |
| `local_agent.clients.revoke` | `DELETE` | `/agent/clients/{id}` | `agent:clients:write` | `state-write` | no | yes | VPS smoke required |

Все операции audit-required. Все операции используют отдельный scope
`agent:clients:write`. Этот scope нельзя добавлять к read-only token.

## Response Contract

Разрешенные поля response:

- `operation_id`;
- `status`;
- `dry_run`;
- `risk_class`;
- `consistency_status`;
- `message`;
- `planned_commands`.

Write API не возвращает private key, PSK, QR или vpn://. Mutation endpoint не
является delivery endpoint: выдача конфигов, QR и `vpn://` остается задачей web
admin/bot/controller слоя.

## Error Contracts

| Code | HTTP | Retry | Meaning |
| --- | --- | --- | --- |
| `validation_failed` | 400 | no | Некорректные или неполные поля запроса. |
| `missing_or_invalid_token` | 401 | no | Token отсутствует или не проходит проверку. |
| `missing_scope` | 403 | no | Token не содержит `agent:clients:write`. |
| `preflight_required` | 409 | yes | Перед mutation нужен успешный dry-run/preflight. |
| `runtime_degraded` | 409 | yes | Runtime degraded; сначала диагностика Local Agent. |
| `mutation_failed` | 502 | yes | Локальная peer mutation не прошла; смотреть redacted diagnostics и rollback state. |

Все error responses должны редактировать secrets. Public message не должен
содержать raw token, private key, PSK, full config, QR или `vpn://`.

## What This Enables Locally

- Typed planning for `agent:clients:write`.
- Проверку, что future write routes остаются inactive before VPS smoke.
- Обсуждение UX flow: dry-run -> confirmation -> mutation.
- Синхронизацию web admin, Telegram bot и CLI вокруг `dry-run -> confirmation -> apply/revoke -> audit -> rollback`.
- Подготовку web admin wording и `docs/AMN3_WRITE_API_AUDIT_MODEL.ru.md` без реальных mutations.

## What This Does Not Enable

- Не включает `LOCAL_AGENT_WRITE_ENABLED`.
- Не регистрирует `/agent/clients*` routes.
- Не добавляет peer apply/revoke endpoints.
- Не меняет `.env.example` на write-enabled defaults.
- Не делает Local Agent публичным.
- Не смешивает backup/import/reboot с user/device lifecycle.

## Current Safety Assertion

`tests/agent/test_write_policy_matrix.py` проверяет, что матрица существует, но
`get_policy()` продолжает отклонять planned write paths. Это важная граница:
контракты есть, production mutation surface еще закрыт.
