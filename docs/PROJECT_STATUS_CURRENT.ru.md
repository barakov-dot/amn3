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

Последний опубликованный commit перед этим status update:

```text
ddb0081 Ignore local worktrees
```

AMN3 теперь является приватной базой знаний проекта: research, design specs, implementation plans, transfer notes и skill-кандидаты.

В AMN3 уже запушены:

- KYORESUAS upstream card;
- Local Amnezia Agent design spec;
- Local Amnezia Agent first-slice implementation plan;
- AMN3 / Amneziya unification design;
- `amn2` transfer backlog;
- Local Agent production wiring implementation plan;
- config delivery artifact integrity plan;
- обновления очередей `amn2`, `hybrid`, `skill`.

На момент этого snapshot AMN3 используется как coordination/knowledge repo. Production-код остается в `amn2`.

## Amneziya / `amn2`

Основной локальный checkout:

```text
C:\Users\SooL\Documents\Amneziya
```

Важно: основной checkout может содержать отдельные незакоммиченные изменения не из Local Agent work. Local Agent production wiring выполнен в isolated worktree:

```text
C:\Users\SooL\Documents\Amneziya\.codex_deps\worktrees\local-agent-production-wiring
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

Compare PR URL with explicit base:

```text
https://github.com/barakov-dot/amn2/compare/codex-vps-test-prep...codex/local-agent-first-slice?expand=1
```

Автоматическое создание PR из Codex пока заблокировано: GitHub connector не видит приватный `barakov-dot/amn2`, а локальный `gh` не установлен.

## Local Agent production wiring branch

Branch:

```text
codex/local-agent-production-wiring
```

Remote branch:

```text
origin/codex/local-agent-production-wiring
```

Head:

```text
8697b60 Document Local Agent production wiring
```

Stacked base while first slice is not merged:

```text
codex/local-agent-first-slice @ ac2baa8 Add typed local agent auth errors
```

Commits:

- `f2f425a Add Local Agent settings`
- `9d343a1 Harden Local Agent token hash settings`
- `c46fe2a Validate configured Local Agent token hash`
- `58d3d07 Build Local Agent tokens from settings`
- `0eb9ff9 Detect Local Agent runtime status`
- `4837d28 Add Local Agent CLI commands`
- `8697b60 Document Local Agent production wiring`

Manual PR URL:

```text
https://github.com/barakov-dot/amn2/compare/codex/local-agent-first-slice...codex/local-agent-production-wiring?expand=1
```

После merge первого Local Agent PR эту ветку можно retarget/rebase на обновленный `codex-vps-test-prep`.

Final verification:

```text
git diff --check
tests/agent tests/config/test_settings.py tests/server/test_operation_runner.py tests/server/test_checks.py tests/web/test_cli_web.py -v
108 passed, 1 existing Starlette/httpx warning
```

Windows pytest cleanup printed a post-summary `PermissionError` for `pytest-current`, but the command exited `0` after the passing summary.

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
3. Открыть stacked PR `codex/local-agent-production-wiring` -> `codex/local-agent-first-slice`.
4. После merge первого PR retarget/rebase production wiring на обновленный `codex-vps-test-prep`, если GitHub не сделал это автоматически.
5. Review/merge Local Agent production wiring.
6. После merge обновить AMN3 status with PR/merge result.
7. Затем возвращаться к live VPS retest на последнем `codex-vps-test-prep`.

Local Agent production wiring plan:

```text
docs/superpowers/plans/2026-05-31-amn2-local-agent-production-wiring.md
```

Transfer backlog:

```text
research/amn2/transfer-backlog.md
```

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
