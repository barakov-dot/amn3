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
- disabled public docs/openapi in the agent app

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
