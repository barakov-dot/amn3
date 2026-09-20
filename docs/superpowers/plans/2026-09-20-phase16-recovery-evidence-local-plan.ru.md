# Phase16: локальные наблюдения для recovery — план реализации

> Для будущего исполнения: использовать superpowers:executing-plans последовательно.
> План принят оператором 20.09.2026 командой «ДАВАЙ ДЕЛАТЬ». Модель не менять.
> Текущий ход локальной реализации и проверки записаны внизу.

**Goal:** различать неполное наблюдение и изменение идентификатора ресурса между
двумя снимками; исключить превращение этих наблюдений в разрешение очистки.
**Architecture:** отдельный чистый parser/сравнение нормализованных observations,
с использованием существующего canonical JSON decoder. Нет subprocess, SSH,
Docker API, чтения /proc или произвольных файлов в новом модуле.
**Tech Stack:** Python 3.10+, stdlib, pytest на синтетических данных.
**Spec:** [согласованный recovery-контракт v1](../specs/2026-09-08-phase16-controlled-stage-recovery-contract.ru.md).
**Статус:** LOCAL_IMPLEMENTED_TESTED_REVIEW_PENDING_NOT_LIVE_APPROVAL, 2026-09-20.
Baseline исходников: AMN3 3eb18f64374e1c279295d0b434302dcee90377ae.
Это техническая подзадача; [единственная очередь Phase16](2026-08-24-amn2-phase16-awg3-family-3-1-spain-pilot.md)
остаётся главным execution plan.

## Почему следующий шаг именно такой

[Metadata parser](../../../scripts/vps/phase16_recovery_metadata.py) уже различает
outcomes/milestones и проверяет bindings; его 27 исторических PASS не повторять
до изменения связанного кода. Он намеренно не подтверждает ownership/quiescence.

В текущем mutable source проверены только необходимые места:
[coordinator](../../../scripts/vps/phase16_controlled_stage_coordinator.py) создаёт
transaction и пишет milestones, но не сохраняет полный состав процессов с их
стабильными идентификаторами. [Application stage](../../../scripts/vps/phase16_application_stage_remote.sh)
эксклюзивно создаёт staging, но итоговый ledger содержит путь, package/state,
а не inode/mount и transaction-specific creation witness.
[Runtime stage](../../../scripts/vps/phase16_awg31_runtime_stage_remote.sh) записывает
имена созданных объектов и флаг image_created; это не конкретные Docker object IDs,
не независимое доказательство владельца и не доказательство отсутствия потомков.

Поэтому безопасно реализовать сначала различение наблюдений, но нельзя сразу
создать cleanup runner, принимающий имя/PID/ledger за разрешение удаления.
Старый collector/driver transaction007 не подключается и повторно не обследуется:
его ограничения уже описаны в [R1](../../../research/amn2/phase16-recovery-helper-compatibility-review-2026-09-08.md).

## Global Constraints

- AWG2_UNTOUCHED; package016 immutable; general issuance disabled.
- Не менять coordinator/stage/pilot, исходные metadata schemas и frozen packages.
- Не создавать live collector, process controller, cleanup или retry runner.
- Нет `safe_to_delete`, `ownership_proven`, `quiescent` или `recovered` в результате
  нового helper. Он сообщает только свойства переданных наблюдений.
- Метаданные не являются доказательством достоверности самого источника.
  query_id связывает два ответа с запросом, но сам не доказывает freshness.
- Ключи, configs, cmdline, environ, stdout/stderr команд и произвольные raw logs
  не принимаются и не сохраняются. Ошибки фиксированные, без текста входа.
- Существующие excludes сохраняются: minimal pilot, AWG2, Docker owner/socket,
  общий runtime image, backup/audit, protected artifacts, application state, Telegram.
- Даже полное отсутствие перечисленных объектов не доказывает прекращение всех
  операций. Чужие/неидентифицированные ресурсы остаются вне разрешения на очистку.

## Как позже подтверждать ownership и прекращение операций

Это требования к будущему live evidence, не реализуемые ниже предикаты доверия.

| Объект | Нужные независимые сведения | Недостаточные признаки |
| --- | --- | --- |
| Процесс | Host/boot/PID namespace, PID+start_ticks, повторное чтение непосредственно перед действием; связь с exact transaction через проверенный creation/supervision record | pgrep, имя, argv, один PID, consumed claim |
| Контейнер/сеть | Exact Docker object ID, daemon identity и creation record, связанный с transaction/package/state; повторный inspect ограниченных полей | Имя объекта, общий image digest, собственная label без подтверждения её происхождения |
| Каталог/файл | Allowlisted цель и mount/dev/inode, проверка symlink/race, подтверждённое эксклюзивное создание данной операцией; повторная проверка через безопасный descriptor | Путь, владелец Unix uid, факт существования, один inode |
| Служба/cgroup | Invocation ID/состав cgroup и полный набор источников новых операций, включая restart/supervisor | inactive родителя, один пустой cgroup, завершение локального SSH |
| Backup/excludes | Независимый checksum/readback в разрешённом scope; исключения не становятся целью cleanup | backup_preserved=true или runtime_image_created=true в старом metadata |

Для прекращения операций требуется определить **все** источники продолжающейся
работы, отдельно разрешить действия над точными экземплярами, затем подтвердить
остановку и невозможность немедленного повторного запуска в заданном окне.
cgroup.events populated учитывает потомков, но пустота наблюдаемой группы не
доказывает, что не осталось иного источника работы или разрешённого restart.

Для исторических transaction006/007 недостающие creation records не восстанавливаются
по предположению: ownership остаётся UNPROVEN. Разработка будущих creation records
и supervisor/cgroup coverage потребует отдельного scope на mutable producers.
Этим планом не утверждается, что имеющихся исторических данных достаточно.

Источники семантики: [Linux /proc](https://www.kernel.org/doc/html/latest/filesystems/proc.html),
[cgroup v2](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html),
[Docker inspect](https://docs.docker.com/reference/cli/docker/inspect/).
Фактические версии/kernel/cgroup layout VPS сейчас не обследованы.

## Review Focus

1. PID повторно использован или сменился boot/namespace: никакого «тот же процесс».
2. Query failure/неполный scope: отсутствие данных не считается отсутствием объекта.
3. Дубликаты/лишние поля/raw secrets/чрезмерный JSON: фиксированная ошибка без input.
4. Переиспользованное имя Docker/каталога: изменение ID отражается отдельно.
5. Два пустых снимка: только ABSENT_IN_SCOPE; никакого ownership/quiescence GO.

Каждый пункт включён в тесты задач ниже; прочие live-proof вопросы явно оставлены
за пределами локального parser, а не объявлены проверенными.

## Task 1 — строгое описание нормализованного снимка

**Files:** создать `scripts/vps/phase16_recovery_observation.py`,
`tests/test_phase16_recovery_observation.py`; обновить этот план и CHANGELOG.md.
**Read-only dependency:** `scripts/vps/phase16_recovery_metadata.py:parse_canonical`.
**Consumes:** canonical bytes и independently supplied bindings/host/query/scope.
**Produces:** immutable Snapshot/ResourceObservation и parser ниже.

Контракт top-level JSON — только следующие поля:

| Поле | Точный контракт |
| --- | --- |
| schema | amn2.phase16.recovery-observation.v1 |
| bindings | Те же 6 ключей, типы и ограничения BINDING_KEYS; все равны expected_bindings |
| host_id | lowercase hex SHA256, ровно 64 символа, равен independently supplied expected_host_id |
| boot_id | UUID, lowercase canonical representation |
| query_id | lowercase hex SHA256, ровно 64 символа, равен expected_query_id |
| sequence | int, не bool; ровно 0 или 1, равен expected_sequence |
| resources | 1..64 записей; logical_id уникален, точное множество expected_scope |

Каждая resource запись имеет ровно logical_id, kind, status, identity.
logical_id — строка из expected_scope (такой же alphabet/limit, как transaction ID);
kind равен expected_scope[logical_id]. status — present/absent/query_failed.
При absent/query_failed identity — пустой object. При present identity строго по виду:

| kind | Обязательные identity поля |
| --- | --- |
| process | pid, pid_ns: positive int; start_ticks: nonnegative int; не bool |
| container | object_id: 64 lowercase hex |
| network | object_id: 64 lowercase hex |
| directory | mount_id: positive int; dev, inode: nonnegative int; не bool |
| service | invocation_id: 32 lowercase hex |

boot_id и host_id относятся ко всему снимку. Имя контейнера, путь каталога и cgroup
не кодируются как доказательство владения. expected_scope — заранее утверждённые
логические aliases наблюдения, не команды и не разрешённые цели удаления.

Публичные интерфейсы:

```python
@dataclass(frozen=True)
class ResourceObservation:
    logical_id: str
    kind: str
    status: str
    identity: tuple[tuple[str, str | int], ...]

@dataclass(frozen=True)
class Snapshot:
    bindings: tuple[tuple[str, str], ...]
    host_id: str
    boot_id: str
    query_id: str
    sequence: int
    resources: tuple[ResourceObservation, ...]
```

Сигнатура parser (описание API):

```text
parse_observation(
    raw: bytes, *, expected_bindings: dict[str, str], expected_host_id: str,
    expected_query_id: str, expected_sequence: int,
    expected_scope: dict[str, str],
) -> Snapshot
```

Decoder — parse_canonical; валидация — строго по таблицам выше. При любом
невалидном input выдавать ValueError("invalid_observation") from None.
Нормализовать tuples сортировкой по ключам/logical_id; не сортировать и не мутировать
переданный caller object. Ограничение canonical input — уже существующие 64 KiB.
Ошибка expected_* тоже даёт invalid_observation. Не добавлять permissive fallback.

- [x] Написать тесты: valid для всех 5 kinds; absent/query_failed; malformed canonical
  input, duplicate logical IDs, неверные/лишние keys, duplicate JSON keys, NaN,
  oversize, bool вместо int, неверный UUID/hex, wrong host/query/sequence/bindings,
  missing/extra scope, kind mismatch, secret-canary в неизвестном поле.
- [x] Запустить только новый файл; наблюдать RED из-за отсутствия реализации.
- [x] Реализовать strict parser по таблицам и immutable результаты, без I/O.
- [x] Проверить GREEN и неизменность input. Для всех invalid cases дополнительно
  проверять точную строку исключения и отсутствие canary в str/repr.
- [x] Обновить CHANGELOG, проверить diff, выполнить точечный локальный commit.

Пример обязательной проверки границы ошибок:

```python
@pytest.mark.parametrize("raw", [
    b'{"secret":"CANARY_PRIVATE_CONFIG"}\n',
    b'{"schema":NaN}\n',
    b'{"schema":"x","schema":"y"}\n',
    b"x" * 65537,
])
def test_invalid_input_is_redacted(raw, expected):
    with pytest.raises(ValueError) as error:
        parse_observation(raw, **expected)
    assert str(error.value) == "invalid_observation"
    assert "CANARY_PRIVATE_CONFIG" not in repr(error.value)
```

Конкретная синтетическая fixture для этого теста:

```python
@pytest.fixture
def expected():
    return {
        "expected_bindings": {
            "package_id": "synthetic-package",
            "transaction_id": "synthetic-transaction",
            "package_identity_sha256": "a" * 64,
            "manifest_sha256": "b" * 64,
            "state_sha256": "c" * 64,
            "rollback_scope_sha256": "d" * 64,
        },
        "expected_host_id": "e" * 64,
        "expected_query_id": "f" * 64,
        "expected_sequence": 0,
        "expected_scope": {"worker": "process"},
    }
```

Никаких fixtures, полученных из действующих configs/backup.

## Task 2 — сравнение наблюдений без допуска к cleanup

**Files:** тот же новый module/test; существующий metadata parser не менять.
**Consumes:** два Snapshot из Task 1, первый sequence=0, второй sequence=1.
**Produces:** `compare_observations(before, after) -> dict[str, str]` по logical_id.
При несовпадении bindings/host/boot/query/scope/kinds либо порядка sequence —
`ValueError("incompatible_observations")`. Ошибка не содержит input.

Полная таблица одного ресурса:

| before | after | Результат |
| --- | --- | --- |
| query_failed | любое | UNKNOWN |
| present или absent | query_failed | UNKNOWN |
| present | present, identity равен | IDENTITY_UNCHANGED |
| present | present, identity отличается | IDENTITY_CHANGED |
| absent | present | APPEARED |
| present или absent | absent | ABSENT_IN_SCOPE |

Изменившийся boot/namespace не сводится к сравнению одного PID. При том же boot
смена process pid_ns/start_ticks даёт IDENTITY_CHANGED. Исчезновение процесса
даёт ABSENT_IN_SCOPE, но не утверждение о дочерних процессах.
Одинаковые directory dev/inode/mount показывают только совпадение прочитанных
полей: возможное переиспользование inode не считается доказанным исключённым.

- [x] Создать параметризованные тесты по всей таблице; одинаковый PID с новым
  start_ticks, новый pid_ns, новое object_id при том же alias, смена mount/inode.
  Wrong boot/host/query/bindings/sequence и неполный scope должны отклоняться.
- [x] Увидеть RED для отсутствующей функции; реализовать comparison после проверки
  совместимости контекстов. Ни одной ветки, разрешающей signal/delete/retry.
- [x] Проверить два снимка с absent для каждого элемента scope: результат только ABSENT_IN_SCOPE.
  query_failed в любом снимке всегда UNKNOWN, даже если второй сообщает absent.
- [x] Один итоговый целевой прогон нового и существующего metadata набора:

```text
python -m pytest tests/test_phase16_recovery_observation.py tests/test_phase16_recovery_metadata.py -q -p no:cacheprovider
```

Использовать существующий проверенный Python/pytest runtime; не устанавливать
зависимости и не запускать VPS helpers. Старый suite здесь включён только как
регрессия общей canonical decoding зависимости при будущей реализации.

- [x] Записать фактические RED/GREEN и ограничения в этот документ/CHANGELOG,
  проверить отсутствие I/O и новых secrets в diff, commit точных файлов.
- [ ] Перед заявлением «готово» провести одно review bounded diff. Оно не расширяет
  локальный scope и не разрешает live tests.

## Завершение и дальнейшая граница

Готовность этого локального шага: строгие snapshots, проверяемые race/reuse/unknown
outcomes, целевые tests и документированный запрет трактовать их как cleanup GO.
Это не завершённый recovery и не замена его четырёх этапов.

Следующим отдельным решением будет источник свежих observations: ограниченный
Linux collector, доказуемая полнота процессов/ресурсов и создание независимых
ownership witnesses для новых операций. Прежде чем его писать, определить exact
allowlist, способы получения идентичностей, версии OS/API, лимиты, timeout и
redaction. До этого не добавлять collector/SSH runner «для удобства».

Live inventory, signals, cleanup, снятие package-блокировки и повторный stage
по-прежнему требуют отдельных exact approvals из контракта v1.

## Самопроверка плана 2026-09-20

Покрыты 5 Review Focus классов и сформулированы конкретные ошибки/результаты.
План реализует только локальную подготовку к inventory; этапы stop/cleanup/readback
контракта остаются явно вне реализации. Никакой bool из metadata не повышает
статус ownership/quiescence. Сигнатуры и названия результатов едины между задачами.
Уточнены полная таблица query_failed, допустимый нулевой start_ticks и конкретная
синтетическая fixture. Код, tests, новый сборщик и live recovery при подготовке
плана не выполнялись.

## Исполнение — 2026-09-20

Task 1: реализован [parser снимков](../../../scripts/vps/phase16_recovery_observation.py)
и [синтетические тесты](../../../tests/test_phase16_recovery_observation.py).
RED: 98 ожидаемых падений из-за отсутствия модуля; GREEN: 98 PASS. Проверены
все 5 видов, canonical/64 KiB, scope 1..64, контекст, bool/int, нулевой start_ticks,
ошибки без input и неизменяемые копии. Metadata dependency не изменена.
Команда: python -m pytest tests/test_phase16_recovery_observation.py -q -p no:cacheprovider.
Task 1 зафиксирован в e3376c2; никакие ресурсы не обследовались.

Решение по workflow: проверять согласованные связанные наборы в существующем
Python runtime; общий suite и установка зависимостей исключены правилами AGENTS
и планом. Ограничение: это не проверка остальных подсистем репозитория.

Task 2: реализовано compare_observations для двух снимков из parser. Проверяются
контекст, одинаковый scope/kinds и sequence 0→1; результаты строго UNKNOWN,
IDENTITY_UNCHANGED, IDENTITY_CHANGED, APPEARED или ABSENT_IN_SCOPE. Смена
start_ticks/namespace обнаруживается отдельно от PID; совпадение полей не
доказывает исключение повторного использования ресурса.
RED: 39 ожидаемых падений из-за отсутствия функции; итоговый GREEN: 164 PASS
(137 новых + 27 metadata). Команда:
python -m pytest tests/test_phase16_recovery_observation.py tests/test_phase16_recovery_metadata.py -q -p no:cacheprovider.
Тесты — синтетические, действующие конфиги не использовались. Заключительный
обзор всего изменения ещё ожидается; локальный PASS не является live evidence.
