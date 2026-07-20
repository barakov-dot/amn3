# Spain preflight stage-coded diagnostic gate — design

Дата: 2026-07-20

Статус: design approved; implementation not started

Design approval:
`APPROVE_POST_RELEASE_SPAIN_PREFLIGHT_STAGE_CODED_DIAGNOSTIC_GATE_DESIGN`

## 1. Контекст и проблема

Две отдельно разрешённые попытки Spain read-only preflight завершились
fail-closed до создания `preflight-evidence.json`.

Первая попытка показала диагностический stderr `nft`, который Windows
PowerShell преобразовал в terminating `NativeCommandError`. После узкого
подавления только stderr команды `nft list ruleset` вторая попытка завершилась
ненулевым SSH exit code. Текущий runner подавляет весь SSH stderr и при
ненулевом exit code уничтожает stdout, поэтому имеющихся данных недостаточно,
чтобы различить transport failure и конкретный обязательный remote collector.

Повторный live-запуск без новой byte-bound approval запрещён. Исправлять
предполагаемый collector без подтверждённой причины также запрещено.

## 2. Цель

Добавить минимальную read-only диагностику, которая при ненулевом завершении
возвращает только:

- версию failure-envelope;
- один stage code из закрытого allowlist;
- числовой exit code;
- признак `transport` или `remote_probe`, определённый локальным runner.

Диагностика не должна возвращать raw stderr, команды, пути, адреса, hostname,
логин, unit/container names, конфиги, environment, ключи, токены или другие
private target data.

## 3. Рассмотренные варианты

### A. Stage-coded failure envelope — выбран

Remote probe отмечает текущий этап константой и при ошибке печатает одну
строго нормализованную failure-envelope. Runner принимает только точную схему и
allowlisted stage, отбрасывает все остальные remote bytes и создаёт приватный
create-new failure receipt. Это даёт минимально достаточную локализацию без raw
логов.

### B. Private raw SSH stderr artifact — отклонён

Полный stderr мог бы быстрее показать исходную ошибку, но способен содержать
target address, unit names, пути и другие чувствительные сведения. Даже
защищённый ACL artifact расширяет secret-handling и cleanup boundary.

### C. Ручная диагностика через provider console — отклонён

Ручные команды хуже воспроизводятся, не связаны с reviewed bytes и создают
риск случайного выхода за read-only scope.

## 4. Архитектура

### 4.1 Remote probe

Probe сохраняет `set -Eeuo pipefail`. Перед каждым обязательным блоком он
устанавливает stage из закрытого списка:

```text
bootstrap
os_kernel
capacity
sockets
firewall
ssh_policy
docker_inventory
systemd_inventory
systemd_unit_content
systemd_cgroup_ports
render
```

ERR handler использует только константный stage и сохранённый numeric exit
code. Он печатает отдельной строкой единственную envelope фиксированной формы:

```text
AMN2_SPAIN_PREFLIGHT_FAILURE_V1|stage=<allowlisted>|exit=<1..255>
```

Handler не печатает `$BASH_COMMAND`, line number, stderr, command output или
переменные окружения. Он завершает probe исходным ненулевым кодом. Успешный
путь и JSON schema `amn2.spain-readonly-preflight.v1` не меняются.

Если ошибка происходит после начала render, stdout может содержать
незавершённый success JSON. Эти bytes считаются недоверенными и никогда не
попадают в receipt, сообщение оператору или Git. Runner извлекает только одну
точно совпавшую envelope и очищает остальной буфер.

### 4.2 Local PowerShell runner

Runner продолжает запускать абсолютный trusted Windows OpenSSH с `-F none`,
dedicated Ed25519 identity, strict host-key checking и независимым host pin.
SSH stderr остаётся направленным в null и нигде не сохраняется.

Сразу после SSH runner фиксирует exit code:

- `0` — применяет существующую строгую success JSON validation и создаёт только
  `preflight-evidence.json`;
- ненулевой код и ровно одна валидная envelope — создаёт только
  `preflight-failure-evidence.json`;
- ненулевой код без envelope — создаёт generic transport failure receipt без
  remote bytes;
- malformed, duplicate или unknown-stage envelope — fail-closed без receipt,
  кроме локального generic сообщения.

Failure receipt имеет фиксированную схему:

```text
schema=amn2.spain-readonly-preflight-failure.v1
classification=remote_probe|transport
stage=<allowlisted>|unavailable
exit_code=<1..255>
runner_sha256=<public digest>
remote_probe_sha256=<public digest>
source_revision=55dc243b8e6c6bdb57f8301b56326e4cd4072d19
```

Receipt создаётся `CreateNew`, защищается current-user-only ACL и не может
заменить существующий файл. Timestamp, target, user, host key и private artifact
paths не включаются, чтобы receipt оставался детерминированным и безопасным для
последующей ручной сводки.

### 4.3 Authority boundary

Design approval не разрешает SSH. Implementation, tests, security review,
commit, push и exact origin readback выполняются локально. Только после них
выдаётся новая отдельная literal approval, связанная с точными runner SHA,
remote probe SHA и AMN2 source `55dc243...`.

Каждая live approval одноразовая. Failure receipt не разрешает remediation,
повтор, install или изменение collector. Следующее действие выбирается только
после анализа подтверждённого stage.

## 5. Поток данных

```text
exact approval
  -> local checksum/trust validation
  -> strict pinned SSH, remote script over stdin
  -> success: validated preflight JSON -> success evidence
  -> remote failure: allowlisted envelope only -> failure receipt
  -> no envelope: generic transport receipt
  -> stop; no retry and no remediation
```

Raw remote stderr и непроверенные stdout bytes заканчивают жизненный цикл в
памяти процесса и не выводятся пользователю, не записываются и не коммитятся.

## 6. Инварианты безопасности

- Никаких install/update/remove действий.
- Никаких start/stop/restart/enable/disable действий.
- Никаких записей на Spain VPS.
- Никаких firewall, Docker, systemd, SSH config, Telegram или AWG mutations.
- Посторонний сервис только читается и fingerprint-ится существующим probe.
- Не используются `2>&1`, raw stderr artifact, `$BASH_COMMAND`, command echo,
  ambient SSH config или relaxed host-key checking.
- Failure никогда не принимается как success evidence.
- Unknown, malformed и duplicate envelope не нормализуются автоматически.
- Старые approvals не принимаются после изменения любых runner/probe bytes.
- `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` остаётся вне scope.

## 7. TDD и проверки

Implementation plan обязан начать с RED tests:

1. Bash test запускает probe с изолированным fake-command PATH и намеренно
   ломает конкретный collector. До реализации тест не находит корректную
   failure-envelope.
2. PowerShell parser tests принимают только одну точную envelope с allowlisted
   stage и exit code `1..255`.
3. Negative tests отклоняют unknown stage, exit `0`, overflow, дополнительные
   поля, duplicate envelope, raw stderr text и target-like values.
4. Runner tests доказывают взаимную исключительность success evidence и failure
   receipt, а также `CreateNew`/no-replace и protected ACL.
5. Static tests запрещают raw stderr persistence, `2>&1`, mutation commands,
   relaxed SSH trust и approval-after-private-state.
6. Embedded remote SHA должен совпадать с точными remote bytes; пустой approval
   печатает новую literal-фразу и завершается до private artifacts/SSH.

После GREEN выполняются focused Spain tests, полный root suite `tests/`, Bash и
PowerShell parse, `git diff --check`, added-line secret scan и security diff
review всех изменённых файлов.

## 8. Acceptance criteria

Design считается реализованным только если:

- локально доказан RED -> GREEN для remote stage failure и runner parsing;
- успешный preflight contract не ослаблен;
- failure даёт только allowlisted stage/exit или generic transport result;
- ни один raw remote byte не попадает в receipt, docs или console output;
- success и failure artifacts нельзя создать одновременно или перезаписать;
- exact approval проверяется до private target state;
- focused и full tests проходят;
- security review имеет полное покрытие и не оставляет reportable findings;
- commit опубликован и origin SHA совпадает;
- новый live запуск не происходит до отдельной буквальной approval.

## 9. Вне scope

- исправление конкретного remote collector до получения stage evidence;
- fresh install AMN2 на Spain;
- изменение или перенос постороннего сервиса;
- генерация и выдача новых VPN-конфигов;
- изменение production USA, Telegram или AWG;
- provider mutation и любые повторные попытки по старому approval.
