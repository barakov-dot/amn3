# Текущее состояние проекта

Дата: 2026-05-31.

## AMN3 / VPN Ops Lab

Локальный checkout:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB
```

GitHub remote:

```text
https://github.com/barakov-dot/amn3.git
```

Текущая ветка:

```text
master
```

Последний опубликованный commit:

```text
b24720f Add AMN3 local agent research
```

AMN3 теперь является приватной базой знаний проекта: research, design specs, implementation plans, transfer notes и skill-кандидаты.

В AMN3 уже запушены:

- KYORESUAS upstream card;
- Local Amnezia Agent design spec;
- Local Amnezia Agent first-slice implementation plan;
- обновления очередей `amn2`, `hybrid`, `skill`.

На момент этого snapshot в рабочей копии AMN3 есть отдельные незакоммиченные research/watch изменения по PRVTPRO/GitHub watch-направлению. Они не относятся к Local Agent integration и должны коммититься отдельным срезом.

## Amneziya / `amn2`

Локальный checkout:

```text
C:\Users\SooL\Documents\Amneziya
```

Текущая ветка Local Agent:

```text
codex/local-agent-first-slice
```

Remote branch:

```text
origin/codex/local-agent-first-slice
```

Текущий head:

```text
ac2baa8 Add typed local agent auth errors
```

Stacked base:

```text
origin/codex-vps-test-prep @ 8ecb0b4 Add configurable client config defaults
```

Local Agent branch содержит два commit:

- `3119ee6 Add local Amnezia agent first slice`
- `ac2baa8 Add typed local agent auth errors`

PR нужно открывать как stacked PR:

```text
base: codex-vps-test-prep
head: codex/local-agent-first-slice
```

Manual PR URL:

```text
https://github.com/barakov-dot/amn2/pull/new/codex/local-agent-first-slice
```

Автоматическое создание PR из Codex пока заблокировано: GitHub connector не видит приватный `barakov-dot/amn2`, а локальный `gh` не установлен.

## Что есть в Local Amnezia Agent first slice

Файлы:

- `app/agent/`
- `tests/agent/`
- `docs/LOCAL_AGENT.ru.md`

Включено:

- route policy matrix;
- hash-only scoped bearer token auth;
- typed auth error reasons;
- fake runtime adapter;
- protected FastAPI app factory;
- endpoints `/agent/health`, `/agent/version`, `/agent/runtime`, `/agent/protocols`;
- disabled public docs/openapi;
- audit events for allowed read routes;
- no config/QR/`vpn://`/backup/import/reboot/write routes.

Проверка после последнего commit:

```text
tests/agent tests/server/test_operation_runner.py tests/server/test_checks.py tests/web/test_servers.py -v
70 passed, 1 existing Starlette/httpx warning
```

`git diff --check` чистый.

## Что теперь есть в `amn2` base branch

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

## Ближайший безопасный порядок

1. Открыть stacked PR `codex/local-agent-first-slice` -> `codex-vps-test-prep`.
2. Review/merge Local Agent slice в `codex-vps-test-prep`.
3. После этого возвращаться к live VPS retest на последнем `codex-vps-test-prep`.
4. Следующий implementation slice для Local Agent делать только после PR/review:
   - feature flag / settings для agent app;
   - real read-only runtime detection;
   - secure token provisioning;
   - no write/config/backup routes until отдельный policy gate.

## Ближайший live VPS retest

На VPS нужно подтвердить:

- установлен коммит `8ecb0b4` или более свежий commit из `codex-vps-test-prep`;
- `server retest-plan` работает и ничего не меняет;
- web block `VPS retest bundle` показывает команды;
- peer sync корректно различает known panel peers, Amnezia-created peers и local missing devices;
- новый peer получает следующий IP из live `/opt/amnezia/awg/awg0.conf`;
- `Disable VPN` и `Enable VPN` работают на Docker runtime;
- config defaults из `.env` попадают в выдаваемые client configs и preview;
- email config/recovery требуют подтвержденный email.
