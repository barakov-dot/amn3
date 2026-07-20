# POST-RELEASE Spain preflight run 004 failure evidence

Дата: 2026-07-20

Статус: fail-closed; approval consumed; retry forbidden

## Sanitized outcome

```text
run_id=spain-fresh-20260720-004
claim=present
failure_evidence=present
success_evidence=absent
classification=remote_probe
stage=systemd_cgroup_ports
subreason=pid
exit_code=76
runner_sha256_match=true
remote_probe_sha256_match=true
source_revision_match=true
```

Runner сохранил только allowlisted failure fields. Private target, login, unit,
PID, cgroup path, FD, socket values, raw stdout/stderr, key и host-pin bytes не
публиковались и не добавлялись в Git.

## Root-cause evidence

Локальная Bash reproduction без SSH показала:

```text
empty_here_string_iterations=1
observed_value=empty
```

Collector сначала получает текст process list, затем использует
`while read ... done <<< "$cgroup_pids"`. При пустом process list here-string
создаёт одну пустую итерацию; строгая PID-проверка переводит её в safe
`subreason=pid`. Это полностью согласуется с run `004` receipt.

Correction contract должен:

- считать ноль process rows валидным завершённым empty port set;
- проверять каждую существующую process row как numeric PID;
- сохранять fail-closed поведение для malformed row, FD/readlink/socket ошибок;
- получить отдельные design/implementation и live approvals;
- не повторять consumed run `004`.

## Safety boundary

Run был только read-only. Install/update, firewall, Docker, systemd, service,
config, Telegram и AWG mutations не выполнялись. Посторонний сервис не
изменялся. Полный preflight success не доказан, поэтому fresh Spain install и
batch config issuance gate остаются заблокированными.
