# Текущее состояние проекта

Дата: 2026-05-31.

## VPN Ops Lab

Главный coordination snapshot обновлен в `docs/PROJECT_CONTEXT_IMPORT.ru.md`.

Текущее активное направление работы: продолжить deep dive в чате `VPN Ops Lab - KYORESUAS-API`.

Main coordination сейчас хранит состояние и решения, но не должен начинать новый implementation step, пока KYORESUAS/API-анализ не вернет очередной вывод или решение.

В lab сейчас есть незакоммиченные исследовательские изменения:

- `ideas/add-to-skill.md`
- `ideas/candidates-for-amn2.md`
- `ideas/candidates-for-hybrid.md`
- `docs/NEXT_CHAT_KYORESUAS_API.ru.md`
- `docs/PROJECT_CONTEXT_IMPORT.ru.md`
- `docs/superpowers/specs/2026-05-31-local-amnezia-agent-design.md`
- `docs/superpowers/plans/2026-05-31-local-amnezia-agent-first-slice.md`
- `research/upstreams/kyoresuas-amnezia-api.md`

Смысл этих изменений: зафиксировать KYORESUAS upstream, Local Amnezia Agent design/plan и обновленную очередь идей для `amn2`, hybrid и общего skill.

## Amneziya / `amn2`

Локальный checkout:

```text
C:\Users\SooL\Documents\Amneziya
```

Текущая ветка:

```text
codex-vps-test-prep
```

Последний коммит:

```text
8ecb0b4 Add configurable client config defaults
```

Ветка синхронизирована с `origin/codex-vps-test-prep`.

Новые коммиты после старого handoff:

- `573c368 Add VPS retest bundle`
- `8ecb0b4 Add configurable client config defaults`

## Что теперь есть в `amn2`

Практический VPS retest bundle:

- CLI: `python -m app.cli server retest-plan --config servers.yml --server debian-vps-1 --db data/amneziya.sqlite3`;
- блок `VPS retest bundle` в карточке сервера;
- обновленные docs и tests.

Настраиваемые defaults клиентского конфига:

- `CLIENT_DNS`;
- `CLIENT_ALLOWED_IPS`;
- `CLIENT_PERSISTENT_KEEPALIVE`;
- `CLIENT_AWG_JC`;
- `CLIENT_AWG_JMIN`;
- `CLIENT_AWG_JMAX`;
- `CLIENT_AWG_S1`;
- `CLIENT_AWG_S2`;
- `CLIENT_AWG_H1`...`CLIENT_AWG_H4`.

Эти значения используются для выдаваемых клиентских конфигов, preview и доставки, а уникальные values вроде keys/IP/endpoint остаются в своих источниках.

## Local Amnezia Agent

First slice фактически реализован в рабочей копии, но не закоммичен:

- `app/agent/`
- `tests/agent/`
- `docs/LOCAL_AGENT.ru.md`

Включено:

- route policy matrix;
- hash-only scoped bearer token auth;
- fake runtime adapter;
- protected FastAPI app factory;
- endpoints `/agent/health`, `/agent/version`, `/agent/runtime`, `/agent/protocols`;
- disabled public docs/openapi;
- audit events for allowed read routes;
- no config/QR/`vpn://`/backup/import/reboot/write routes.

Проверка в текущей рабочей копии:

```text
tests/agent: 33 passed, 1 warning
```

Финальный review: approved, без blocking findings. Неблокирующая заметка: позже заменить текстовое определение missing scope на typed auth error reason.

## Следующий безопасный шаг

Сначала не смешивать незакоммиченный Local Agent с текущей веткой VPS retest.

Так как работа пока продолжается в KYORESUAS-API deep dive, в main coordination ближайшее действие - принимать оттуда новые выводы и обновлять очереди `amn2`, `hybrid`, `skill`, а не запускать новые правки в `amn2`.

Рекомендуемый порядок:

1. Создать свежую ветку от `8ecb0b4`, например `codex/local-agent-first-slice`.
2. Stage только `app/agent/`, `tests/agent/`, `docs/LOCAL_AGENT.ru.md`.
3. Commit: `Add local Amnezia agent first slice`.
4. Прогнать `tests/agent` и связанные regression tests.
5. После этого возвращаться к live VPS retest на последнем `codex-vps-test-prep`.

## Ближайший live VPS retest

На VPS нужно подтвердить:

- установлен коммит `8ecb0b4`;
- `server retest-plan` работает и ничего не меняет;
- web block `VPS retest bundle` показывает команды;
- peer sync корректно различает known panel peers, Amnezia-created peers и local missing devices;
- новый peer получает следующий IP из live `/opt/amnezia/awg/awg0.conf`;
- `Disable VPN` и `Enable VPN` работают на Docker runtime;
- config defaults из `.env` попадают в выдаваемые client configs и preview;
- email config/recovery требуют подтвержденный email.
