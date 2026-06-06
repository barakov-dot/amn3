# Local Amnezia Agent

## Статус

Первый slice agent является read-only foundation. Он нужен, чтобы controller мог безопасно спросить сервер о состоянии runtime и поддерживаемых protocols без выдачи клиентских конфигов, QR, `vpn://`, private keys, PSK, backup payloads или выполнения write operations.

## Что включено

- `GET /agent/health`
- `GET /agent/version`
- `GET /agent/runtime`
- `GET /agent/protocols`
- hash-only bearer token auth
- explicit scopes
- route policy matrix
- fake runtime adapter for tests
- audit events for allowed read routes
- production audit sink в `admin_actions` при запуске через `agent serve`
- `runtime_contract_version` и список first-slice routes в `/agent/version`
- disabled public docs/openapi in the agent app
- controller-facing API summary `GET /api/local-agent/runtime/summary`

`GET /api/local-agent/runtime/summary` живет в основном `/api/*` контуре, требует `server:read` и не ходит в Local Agent по сети. Он возвращает только controller-safe summary из `app.agent.runtime_summary`: configured flag, connectivity `not_checked`, `write_routes_enabled=false`, runtime status `unknown` и пустой protocols list до отдельной live/transport проверки. В ответ не попадают `LOCAL_AGENT_HOST`, `LOCAL_AGENT_PORT`, token id, token hash, container name, interface, config path или command output.

## Что не включено

- создание клиентов
- отключение или удаление клиентов
- выдача конфигов
- QR и `vpn://`
- backup/import
- reboot/reset
- Docker mutation
- public HTTP exposure

## Scopes

| Scope | Доступ |
| --- | --- |
| `agent:health` | `/agent/health`, `/agent/version` |
| `agent:read` | `/agent/runtime` |
| `agent:protocols:read` | `/agent/protocols` |

## Production правило

Agent считается привилегированным local runtime adapter. Его нельзя публиковать как общий root API к серверу. Любое расширение за пределы read-only routes требует route policy, secret inventory, audit plan и отдельного implementation plan.

## Production wiring

Agent disabled by default:

```text
LOCAL_AGENT_ENABLED=false
```

Минимальный production режим:

```text
LOCAL_AGENT_ENABLED=true
LOCAL_AGENT_HOST=127.0.0.1
LOCAL_AGENT_PORT=3031
LOCAL_AGENT_TOKEN_ID=local-controller
LOCAL_AGENT_TOKEN_OWNER=local-controller
LOCAL_AGENT_TOKEN_SCOPES=agent:health,agent:read,agent:protocols:read
LOCAL_AGENT_TOKEN_EXPIRES_AT=
LOCAL_AGENT_TOKEN_HASH=sha256:<generated-hash>
```

Raw token не хранится в `.env`. Сгенерировать hash:

```powershell
python -m app.cli agent hash-token
```

Запуск:

```powershell
python -m app.cli agent serve
```

Allowed read-запросы (`/agent/health`, `/agent/version`, `/agent/runtime`, `/agent/protocols`) записываются в `admin_actions` с action `local_agent_read`. Metadata содержит route, scope, risk class, token id, token owner и result. Raw bearer token в audit не пишется.

Для первого production режима держать `LOCAL_AGENT_HOST=127.0.0.1` и открывать доступ только через SSH tunnel, reverse proxy с auth или будущий controller-side transport. Публично наружу agent не выставлять.
