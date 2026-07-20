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

## Correction verification

Контракт реализован локально для нового outcome `spain-fresh-20260720-005`:

```text
tdd_red=empty_cgroup_procs_exit_93
tdd_green=zero_rows_success_empty_ports_empty_subreason
malformed_nonempty_pid=still_fail_closed
remote_probe_sha256=B45764A57E4258C8DD1AFC1570FE5F4359C755C146449225EAC0B74044E3F3F1
runner_sha256=B42EEE2ED6D63DDC81BCDAF337B9A1581757C8B1E5B1475FACFF69322DD75C82
focused_tests=27_passed
full_tests=203_passed
bash_powershell_parse=pass
security=codex_diff_scan_complete|reportable_findings_0|secret_matches_0
run_005=not_created|not_run
ssh=not_run
```

Эта local verification не открывает live gate. Требуется отдельная exact
checksum-bound approval после commit/push и trusted-origin readback.

## Safety boundary

Run был только read-only. Install/update, firewall, Docker, systemd, service,
config, Telegram и AWG mutations не выполнялись. Посторонний сервис не
изменялся. Полный preflight success не доказан, поэтому fresh Spain install и
batch config issuance gate остаются заблокированными.
