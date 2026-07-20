# Spain systemd empty ControlGroup MainPID fallback — correction design

Дата: 2026-07-20

Статус: design approved; written correction spec awaiting review

Design approval:
`APPROVE_PHASE11_SPAIN_SYSTEMD_EMPTY_CONTROLGROUP_MAINPID_FALLBACK_DIAGNOSTIC_DESIGN`

## 1. Наблюдённый отказ

Одноразовый checksum-bound Spain read-only preflight с trust run id
`spain-fresh-20260720-001` завершился fail-closed. Санитизированная receipt
зафиксировала только:

```text
classification=remote_probe
stage=systemd_inventory
exit_code=67
```

Runner и probe отработали согласованный failure-envelope contract. Raw stdout,
stderr, target data и имя конкретного systemd-unit не сохранялись. Install,
restart, stop, configuration write, Telegram, AWG и unrelated-service mutation
не выполнялись. Claim и approval потреблены; повтор этого run запрещён.

Код `67` создавался локальной проверкой probe, когда unit имел состояние
`active`, но `systemctl show ... ControlGroup` возвращал пустое значение.
Следовательно, transport, host-key binding и ранние collectors не являются
наблюдённой причиной отказа.

## 2. Корневая причина

Probe ошибочно считал, что любой `active` service unit обязан иметь непустой
`ControlGroup`. Systemd допускает активное логическое состояние без живого
процесса, в частности для завершившегося `Type=oneshot` с
`RemainAfterExit=yes`. В таком состоянии пустой `ControlGroup` не доказывает
ошибку и не даёт права приписывать unit живые порты.

При этом простое преобразование пустого `ControlGroup` в пустой port set также
неприемлемо: если у unit существует живой `MainPID`, probe обязан найти его
фактическую cgroup и сохранить полноту socket fingerprint либо завершиться
fail-closed.

## 3. Цель correction

Различать два допустимых случая пустого `ControlGroup` без ослабления
read-only и completeness boundary:

1. active unit без живого main process;
2. active unit с живым `MainPID`, для которого cgroup восстанавливается только
   read-only из `/proc/<pid>/cgroup`.

Любое противоречивое, недоступное или неоднозначное состояние остаётся ошибкой
с санитизированным stage/exit, без raw diagnostics и без retry/remediation.

## 4. Рассмотренные варианты

### A. Считать пустой ControlGroup нулевым набором портов — отклонён

Это устраняет ложный отказ, но может скрыть живой процесс и создать ложный
`no ports` fingerprint.

### B. Оставить безусловный fail-closed — отклонён

Безопасно, но делает корректные active-exited/oneshot units постоянным
блокером инвентаризации.

### C. MainPID и `/proc/<pid>/cgroup` fallback — выбран

Probe сначала использует канонический `ControlGroup`. Только если он пуст,
probe читает `MainPID`, проверяет его формат и либо фиксирует отсутствие живого
процесса, либо выводит фактическую cgroup из procfs. Это сохраняет полноту и не
требует раскрывать имя unit или выполнять mutation.

## 5. Исправленный remote contract

Для каждого systemd service unit порядок строго следующий.

### 5.1 Непустой ControlGroup

- Сохраняется существующий `systemd_cgroup_ports` path.
- `ports_for_cgroup` обязан успешно перечислить PID/FD/socket mapping.
- `bound_port_status=cgroup_complete`.
- Любая ошибка остаётся stage-coded fail-closed.

### 5.2 Пустой ControlGroup и MainPID=0

- Probe читает `MainPID` через `systemctl show --property=MainPID --value`.
- Допускается только каноническое неотрицательное целое.
- Значение `0` означает отсутствие живого main process в момент snapshot.
- Port set остаётся пустым.
- `bound_port_status=active_exited_no_live_process` для active unit либо
  существующий `no_cgroup` для inactive unit.
- Это наблюдение не называется ошибкой и не утверждает наличие endpoint agent
  или иной недоступной endpoint telemetry.

### 5.3 Пустой ControlGroup и MainPID>0

- PID обязан существовать и быть числовым.
- Probe читает только `/proc/<pid>/cgroup`.
- Каждая строка обязана иметь ровно три colon-separated поля. На cgroup v2
  принимается ровно одна запись `0::<absolute_path>`. Если v2-записи нет, на
  cgroup v1 принимается ровно одна запись, список controllers которой содержит
  точный элемент `name=systemd`. Отсутствие либо несколько подходящих записей
  считается неоднозначностью.
- Полученный path обязан быть абсолютным cgroup path, не содержать NUL,
  traversal-сегментов или управляющих символов.
- Затем используется существующий `ports_for_cgroup`.
- `bound_port_status=mainpid_cgroup_complete`.

### 5.4 Fail-closed состояния

Используются отдельные validation exits, все через существующий
stage-coded emitter:

- `71`: `MainPID` пустой, нечисловой или вне диапазона `0..4194304`;
- `72`: `MainPID>0`, но `/proc/<pid>/cgroup` недоступен либо PID исчез между
  чтением systemd и procfs;
- `73`: procfs возвращает пустой, malformed, небезопасный или неоднозначный
  cgroup path;
- `74`: canonical unit id не совпал с procfs cgroup либо MainPID, process
  starttime или cgroup изменились во время snapshot; такое состояние не
  признаётся полным evidence.

Если существующий `ports_for_cgroup` не может завершить PID/FD/socket mapping,
сохраняется его текущий ERR-trap path и stage `systemd_cgroup_ports`; такой
отказ не нормализуется в ложный пустой port set.

Envelope по-прежнему содержит только allowlisted stage и exit code. Unit name,
PID, cgroup path, procfs content, stderr и command text не выводятся и не
сохраняются.

## 6. Local runner и single-use boundary

Runner сохраняет существующий strict parser, create-new outcome claim,
dedicated Ed25519 identity, independent host pin, `-F none`, suppressed SSH
stderr и взаимную исключительность success/failure evidence.

Correction меняет remote bytes, поэтому обязаны измениться:

- embedded remote SHA в runner;
- фактический runner SHA;
- exact trust run id, который не совпадает с потреблённым
  `spain-fresh-20260720-001`;
- буквальная live approval.

Старые approval и claim не могут быть удалены, заменены или использованы для
retry. Пустой approval preview обязан завершаться до private state и SSH.

## 7. Безопасность и приватность

- Только read-only `systemctl show`, procfs и существующий socket inventory.
- Никаких install/update/remove, start/stop/restart/enable/disable.
- Никаких записей на Spain VPS, изменений firewall, Docker, systemd или SSH.
- Никаких Telegram, AWG, production USA или unrelated-service mutations.
- PID и cgroup path считаются private runtime data и не попадают в Git,
  receipt или операторское сообщение.
- Никаких raw stdout/stderr artifacts и blind remediation.
- Success evidence остаётся приватным artifact и проходит существующую schema
  validation.
- `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` остаётся вне scope.

## 8. TDD contract

Implementation plan начинается с отдельных RED tests:

1. Active unit, непустой `ControlGroup`: старый exact cgroup path сохраняется.
2. Active unit, пустой `ControlGroup`, `MainPID=0`: до correction тест ловит
   exit `67`, после correction получает
   `active_exited_no_live_process` и пустой port set.
3. Active unit, пустой `ControlGroup`, `MainPID>0`, валидный procfs cgroup:
   после correction выполняется полный socket mapping и фиксируется
   `mainpid_cgroup_complete`.
4. Невалидный/исчезнувший PID, malformed/ambiguous procfs cgroup и неполный
   socket mapping возвращают только stage-coded failure.
5. Negative static tests запрещают вывод PID/cgroup/raw stderr, mutation
   commands и reuse старого run id.
6. Runner checksum tests требуют новый exact remote SHA, новый runner SHA и
   новый single-use trust run id.

После GREEN обязательны focused Spain tests, полный canonical `tests/` suite,
Bash parse, PowerShell parse, `git diff --check`, added-line secret scan и
security diff review всех изменённых файлов.

## 9. Acceptance criteria

Correction готова к новому approval только если:

- root cause воспроизведён отдельным RED test;
- три ветви ControlGroup/MainPID различаются детерминированно;
- active-exited unit не блокирует preflight и не получает ложные порты;
- живой MainPID без ControlGroup не принимается без полного procfs/cgroup
  socket mapping;
- противоречивые состояния остаются fail-closed и санитизированы;
- старые success schema и failure-envelope parser не ослаблены;
- focused/full tests и parse/diff/security review проходят;
- status/evidence синхронизированы без private runtime data;
- commit опубликован, origin SHA подтверждён;
- новый SSH не выполняется до возврата новой точной approval-фразы.

## 10. Вне scope

- повторное чтение имени или деталей unit, вызвавшего текущий отказ;
- live-debug commands вне checksum-bound runner;
- автоматический retry или remediation;
- fresh install AMN2 на Spain;
- изменение или перенос постороннего сервиса;
- генерация VPN-конфигов;
- любые изменения AWG, production USA, Telegram или provider state.
