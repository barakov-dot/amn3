# Spain systemd cgroup ports subreason diagnostic — bilingual design

Дата: 2026-07-20

Статус: approved for local implementation; live run not authorized

Authority:
`APPROVE_PHASE11_SPAIN_SYSTEMD_CGROUP_PORTS_SUBREASON_DIAGNOSTIC_DESIGN`.

## 1. Контекст / Context

Read-only run `spain-fresh-20260720-003` дошёл до checksum-bound remote probe и
остановился с нормализованным результатом
`remote_probe/systemd_cgroup_ports/exit=1`. Claim и sanitized failure evidence
созданы, success evidence отсутствует. Run `003` consumed и не повторяется.

The existing envelope identifies the collector group but cannot distinguish a
cgroup process-list failure from a disappearing PID/FD, readlink race, socket
table read, or socket parser failure. No raw remote output may be added.

## 2. Цель / Goal

Добавить минимальную allowlisted subreason taxonomy внутри
`systemd_cgroup_ports`, чтобы следующий отдельно разрешённый read-only run
локализовал отказ без unit name, PID, cgroup path, FD, socket row, address,
command text или stderr.

Add a minimal allowlisted subreason taxonomy for `systemd_cgroup_ports` while
preserving read-only behavior, exact approval binding, sanitized evidence, and
the AWG/unrelated-service no-mutation boundary.

## 3. Выбранная архитектура / Selected architecture

`ports_for_cgroup` заменяется direct-call collector. Он не печатает failure
envelope и не вызывается через command substitution. Результат передаётся через
две внутренние переменные:

- `COLLECTED_UNIT_PORTS` — нормализованный comma-separated port set;
- `CGROUP_PORTS_SUBREASON` — одно значение из закрытого allowlist.

Caller остаётся в основном shell process. При failure он преобразует subreason
в отдельный fixed exit code и вызывает существующий `emit_failure`; поэтому
envelope не захватывается как port output.

The runner maps only a matching `(stage, exit)` pair to a safe `subreason`
field. Unknown combinations remain fail-closed.

## 4. Allowlist и коды / Allowlist and codes

| Exit | Subreason | Безопасный смысл |
|---:|---|---|
| 75 | `cgroup_procs` | cgroup process list недоступен или не прочитан полностью |
| 76 | `pid` | process-list содержит невалидный PID |
| 77 | `fd_directory` | proc FD directory недоступен |
| 78 | `fd_readlink` | FD исчез или readlink не завершился |
| 79 | `socket_table` | обязательная tcp/tcp6/udp/udp6 table недоступна |
| 80 | `socket_parse` | socket table parser/sort normalization не завершились |

Ни exit, ни subreason не раскрывают конкретный unit, PID, FD, путь или порт.
Existing codes `64–74` не меняют смысл.

## 5. Data flow

1. Resolver выдаёт проверенный cgroup path.
2. Direct collector обнуляет обе result-переменные.
3. Каждый обязательный read/parse boundary устанавливает только allowlisted
   subreason и возвращает nonzero.
4. Caller отображает subreason в `75–80` или закрывается на unknown value.
5. Runner принимает ровно одну existing envelope строку, проверяет stage/exit и
   добавляет safe `subreason` в failure evidence.
6. Raw SSH output очищается и не сохраняется.

## 6. Fail-closed invariants

- Нет `eval`, shell interpolation или raw diagnostic output.
- Unknown/empty/duplicate subreason не превращается в success.
- Empty port set разрешён только после полного collector pass.
- Disappearing FD остаётся диагностируемым failure, а не автоматически
  игнорируется в этом slice.
- Runner/source/run id привязаны к новым SHA и outcome run `004`.
- Immutable trust bundle остаётся `spain-fresh-20260720-001`.
- Consumed runs `001–003` не удаляются и не переиспользуются.

## 7. TDD и acceptance

- RED harness отдельно воспроизводит каждый subreason boundary.
- GREEN подтверждает exact codes `75–80` и отсутствие raw values.
- Runner tests подтверждают safe subreason mapping, unknown-pair rejection и
  новый run `spain-fresh-20260720-004`.
- Focused и полный suite, Bash/PowerShell parse, diff/security и secret-pattern
  scan проходят.
- Empty approval печатает новую checksum-bound literal и останавливается до
  private state/SSH.

## 8. Вне scope / Out of scope

- SSH или повтор run `003`;
- автоматический retry, tolerance или remediation disappearing FD;
- чтение/публикация raw unit/PID/cgroup/FD/socket details;
- install, firewall/Docker/systemd/service mutations;
- изменение постороннего сервиса, Telegram, AWG или production USA;
- fresh install и генерация VPN-конфигов.
