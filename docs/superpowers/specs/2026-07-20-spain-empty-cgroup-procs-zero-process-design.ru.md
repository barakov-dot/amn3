# Spain empty cgroup.procs zero-process correction — bilingual design

Дата: 2026-07-20

Статус: approved in principle for Phase 11 local correction; live run not authorized

## 1. Контекст / Context

Single-use read-only run `spain-fresh-20260720-004` завершился fail-closed с
`remote_probe/systemd_cgroup_ports/pid/exit=76`. Claim и sanitized failure
evidence присутствуют, success evidence отсутствует; run `004` consumed и не
повторяется.

Локальная Bash reproduction показала, что `while read ... done <<< ""`
выполняет одну синтетическую итерацию с пустой строкой. Текущий collector
получает пустой результат из корректно прочитанного `cgroup.procs`, затем
ошибочно классифицирует эту синтетическую строку как malformed PID.

The failure is in local probe interpretation, not evidence of a broken Spain
host. A successfully read cgroup process list may legitimately contain zero
process rows. That state must be represented as a complete empty port set.

## 2. Рассмотренные варианты / Considered approaches

### A. Явное zero-row состояние до PID loop — выбрано / Selected

После успешного чтения `cgroup.procs` collector явно различает:

- zero rows: success, `COLLECTED_UNIT_PORTS=""`, no subreason;
- one or more rows: every row must be a strict numeric PID;
- read/parser failure: existing fail-closed subreason remains unchanged.

This preserves completeness semantics and fixes only the synthetic empty-row
artifact. It does not weaken PID, FD, readlink, socket-table, or socket-parser
checks.

### B. Пропускать пустые строки внутри PID loop — отклонено / Rejected

`[[ -n "$pid" ]] || continue` был бы короче, но смешал бы legitimate zero rows
с malformed embedded blank rows and could silently normalize incomplete input.

### C. Не проверять cgroup units без sockets — отклонено / Rejected

Такой подход изменил бы inventory contract, мог скрыть service state и вышел бы
за пределы узкой коррекции.

## 3. Контракт / Contract

Remote collector keeps the existing interface:

```text
collect_ports_for_cgroup(control_group, cgroup_root, proc_root)
COLLECTED_UNIT_PORTS=<normalized comma-separated ports or empty>
CGROUP_PORTS_SUBREASON=<allowlisted failure name or empty>
```

Обязательные состояния:

1. `cgroup.procs` unreadable or read failure → `cgroup_procs`, nonzero.
2. Successfully read zero process rows → success, empty port set.
3. Any existing nonnumeric process row → `pid`, nonzero.
4. Numeric rows continue through the unchanged strict FD/readlink/socket flow.
5. `COLLECTED_UNIT_PORTS` is assigned only after complete successful processing.

No raw unit, PID, cgroup path, FD, socket inode, address, stderr, or command text
may enter the failure envelope, local evidence, docs, or exceptions.

## 4. TDD acceptance

- A harness with an existing empty `cgroup.procs` must fail before the fix and
  pass after it with empty `COLLECTED_UNIT_PORTS` and empty subreason.
- A harness with a malformed nonempty row must remain `pid` failure.
- A harness with numeric rows must retain all existing FD/readlink/socket
  behavior.
- Run `004` remains consumed; runner moves to a new single-use outcome `005`.
- Remote probe SHA and runner SHA are rebound to exact final bytes.
- Empty approval preview stops before private state and SSH.
- Focused/full tests, Bash/PowerShell parse, diff/security review and added-lines
  secret scan must pass before commit/push.

## 5. Safety and live boundary

Local design, tests, code, docs, commit and push do not authorize SSH. A future
run `spain-fresh-20260720-005` requires a separate exact checksum-bound literal
approval after trusted-origin readback.

Never repeat runs `001–004`. Never install, restart, stop, remediate, mutate
firewall/Docker/systemd/config, call Telegram, or touch AWG under this correction
authority. Fresh Spain install and batch config issuance remain blocked until a
corrected preflight produces validated success evidence.
