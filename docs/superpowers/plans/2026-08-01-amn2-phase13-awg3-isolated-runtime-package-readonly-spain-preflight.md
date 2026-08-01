# AMN2 Phase 13 — план локальной TDD-реализации комплекта AWG3 и предварительной проверки Spain только для чтения

> **Для агентных исполнителей:** обязательный навык для исполнения —
> `superpowers:subagent-driven-development` (рекомендуется) либо
> `superpowers:executing-plans`. Задачи выполняются последовательно,
> task-by-task, с отдельным RED/GREEN и отдельным commit.

**Цель:** локально реализовать и проверить fail-closed инструменты подготовки
checksum-bound предварительной проверки изолированного AWG3 runtime, не
собирая runtime package, не подключаясь по SSH и не изменяя Spain/USA/AWG.

**Архитектура:** принятая Phase 12 проверка стабильного foreign projection
остаётся неизменной и получает parity-tests через новый небольшой модуль
контракта. Новый Bash collector наблюдает candidate resources, AWG2 и foreign
state только для чтения; новый PowerShell runner связывает collector, schemas,
manifest, trust bundle и одноразовый outcome. Production manifest и точная SSH
approval не создаются до отдельного последующего gate.

**Технологии:** Python 3.12, `pytest`, стандартная библиотека Python,
PowerShell 5.1, Git Bash, JSON Schema 2020-12 как машиночитаемый контракт,
SHA-256 и существующий локальный Spain trust bundle.

## Общие ограничения

- Authoritative AMN2 base:
  `55dc243b8e6c6bdb57f8301b56326e4cd4072d19`.
- Начальный Phase 13 head:
  `ff115b63ca1329640ca13ae0a502d155f99b456b`.
- Принятый Spain operational overlay:
  `f1bf099ddb47da26a4080714376babaf5b0de92c`.
- Текущий AMN2 worktree:
  `worktrees/amn2-phase13-awg2-awg3-local`.
- Spain AWG2 d1–d7, USA rollback contour и посторонний Spain-сервис не
  изменяются.
- Запрещены package build, deploy, SSH, upload, config/peer/key issuance,
  AWG stop/restart/recreate/upgrade, reboot, rollback rehearsal и USA
  shutdown/cleanup/reuse.
- Новые файлы комплекта создаются только локально и не содержат runtime image,
  installer, config, peer или secret material.
- `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` не изменяется и не попадает в
  staging.
- Все operator-facing тексты, планы, receipts и статусы пишутся по-русски;
  английский сохраняется только для машинных идентификаторов, имён файлов,
  API и команд.
- Каждая задача завершается отдельным commit в соответствующем repository.
- AMN2 source и VPS-OPS-LAB docs/tooling commits не смешиваются.
- Любой неизвестный, неполный или неоднозначный результат означает stop.

## Структура файлов

### AMN2 source worktree

- Изменить: `app/services/protocol_admission.py` — выбирать только самый новый
  exact compatibility evidence и отдавать приоритет отрицательному evidence
  при одинаковом времени.
- Изменить: `tests/services/test_protocol_admission.py` — regression tests для
  старого `PASSED` и более нового `FAILED|SUPERSEDED|CLAIMED`.

### VPS-OPS-LAB

- Создать: `packaging/phase13-awg3-preflight/phase12-equality-foundation.json`
  — замороженные принятые safe invariants Phase 12.
- Создать: `packaging/phase13-awg3-preflight/manifest.schema.json` — strict
  schema manifest.
- Создать: `packaging/phase13-awg3-preflight/evidence.schema.json` — strict
  schema успешного evidence.
- Создать: `packaging/phase13-awg3-preflight/failure-evidence.schema.json` —
  strict schema очищенного failure evidence.
- Создать: `scripts/phase13_awg3_preflight_contract.py` — canonical JSON,
  checksum, strict validation, foreign-projection parity и manifest builder.
- Создать: `scripts/vps/phase13_spain_awg3_readonly_preflight_remote.sh` —
  удалённый read-only collector.
- Создать: `scripts/vps/phase13_spain_awg3_readonly_preflight_ssh_runner.ps1`
  — локальный checksum/outcome/transport runner.
- Создать: `tests/test_phase13_awg3_preflight_contract.py` — Python contract
  tests.
- Создать: `tests/test_phase13_awg3_readonly_preflight.py` — Bash/PowerShell
  static, harness и fail-closed tests.
- Создать после реализации:
  `research/amn2/phase13-awg3-preflight-local-tooling-receipt-2026-08-01.md`.
- Изменить после реализации: `docs/PROJECT_STATUS_CURRENT.ru.md` — только
  верхний Phase 13 block.

---

### Задача 1. Исправить выбор compatibility evidence

**Критичность:** критичная.

**Модель:** GPT-5.6 Terra medium.

**Repository:** AMN2 isolated worktree.

**Файлы:**

- Изменить: `tests/services/test_protocol_admission.py`.
- Изменить: `app/services/protocol_admission.py`.

**Интерфейсы:**

- Использует: `ClientCompatibilityEvidence.observed_at`, `.status`,
  `.evidence_id` и exact `ClientIdentity`/`ProtocolVersion`.
- Сохраняет: `ProtocolAdmissionService.decide(request) -> AdmissionResult`.
- Гарантирует: более новое отрицательное evidence блокирует старое `PASSED`;
  при одинаковом `observed_at` отрицательный status имеет приоритет.

- [ ] **Шаг 1. Добавить RED-тест более нового отрицательного evidence**

```python
import pytest


@pytest.mark.parametrize(
    "new_status",
    [
        CompatibilityEvidenceStatus.FAILED,
        CompatibilityEvidenceStatus.SUPERSEDED,
    ],
)
def test_newer_negative_evidence_blocks_older_passed(new_status):
    older_pass = replace(
        evidence(CompatibilityEvidenceStatus.PASSED),
        evidence_id="older-pass",
        observed_at=NOW - timedelta(hours=1),
    )
    newer_negative = replace(
        evidence(new_status),
        evidence_id=f"newer-{new_status.value}",
        observed_at=NOW,
    )
    result = ProtocolAdmissionService(
        evidence=(older_pass, newer_negative),
        runtimes=(runtime(ProtocolVersion.AWG3, accepted=True),),
        now=NOW,
    ).decide(request("amnezia_vpn", "5.0.0.5"))

    assert result.decision == "blocked_evidence_stale_or_failed"
    assert result.admitted is False
```

- [ ] **Шаг 2. Добавить RED-тест более нового `CLAIMED`**

```python
def test_newer_claimed_evidence_blocks_older_passed():
    older_pass = replace(
        evidence(CompatibilityEvidenceStatus.PASSED),
        evidence_id="older-pass",
        observed_at=NOW - timedelta(hours=1),
    )
    newer_claim = replace(
        evidence(CompatibilityEvidenceStatus.CLAIMED),
        evidence_id="newer-claim",
        observed_at=NOW,
    )
    result = ProtocolAdmissionService(
        evidence=(older_pass, newer_claim),
        runtimes=(runtime(ProtocolVersion.AWG3, accepted=True),),
        now=NOW,
    ).decide(request("amnezia_vpn", "5.0.0.5"))

    assert result.decision == "blocked_unverified_version"
    assert result.admitted is False
```

- [ ] **Шаг 3. Добавить RED-тест отрицательного evidence при одинаковом времени**

```python
def test_equal_timestamp_negative_evidence_wins_over_passed():
    passed = replace(
        evidence(CompatibilityEvidenceStatus.PASSED),
        evidence_id="same-time-pass",
    )
    failed = replace(
        evidence(CompatibilityEvidenceStatus.FAILED),
        evidence_id="same-time-fail",
    )
    result = ProtocolAdmissionService(
        evidence=(passed, failed),
        runtimes=(runtime(ProtocolVersion.AWG3, accepted=True),),
        now=NOW,
    ).decide(request("amnezia_vpn", "5.0.0.5"))

    assert result.decision == "blocked_evidence_stale_or_failed"
```

- [ ] **Шаг 4. Запустить RED**

```powershell
& '.venv\Scripts\python.exe' -m pytest tests/services/test_protocol_admission.py -q
```

Ожидается: новые тесты падают, потому что старое `PASSED` сейчас выбирается до
анализа более новых rows.

- [ ] **Шаг 5. Реализовать минимальный latest-observation contract**

В `decide()` после построения `exact` вычислить максимальный `observed_at`,
ограничить выбор rows этим временем и применить status priority:

```python
latest_at = max((item.observed_at for item in exact), default=None)
latest = tuple(item for item in exact if item.observed_at == latest_at)
latest_has_negative = any(
    item.status
    in {
        CompatibilityEvidenceStatus.FAILED,
        CompatibilityEvidenceStatus.SUPERSEDED,
    }
    for item in latest
)
if latest_has_negative:
    return AdmissionResult(
        "blocked_evidence_stale_or_failed",
        request.protocol_version,
        None,
        None,
    )
passed = next(
    (
        item
        for item in latest
        if item.status is CompatibilityEvidenceStatus.PASSED
        and timedelta(0)
        <= self._now - item.observed_at
        <= self._max_evidence_age
    ),
    None,
)
```

Если latest rows не содержат `PASSED`, существующая ветка различает
`blocked_unverified_version` и `blocked_evidence_stale_or_failed`. Нельзя снова
искать `PASSED` среди более старых rows.

- [ ] **Шаг 6. Запустить GREEN и соседние admission/issuance tests**

```powershell
& '.venv\Scripts\python.exe' -m pytest tests/services/test_protocol_admission.py tests/services/test_admin_config_issuance.py tests/cli/test_admin_config_issuance.py -q
```

Ожидается: все тесты проходят.

- [ ] **Шаг 7. Проверить diff и создать отдельный AMN2 commit**

```powershell
git diff --check
git add -- app/services/protocol_admission.py tests/services/test_protocol_admission.py
git diff --cached --check
git commit -m "Исправить выбор актуального compatibility evidence"
```

**Критерий завершения:** regression воспроизведён RED, исправлен GREEN, API не
расширен, live-код не запускался.

---

### Задача 2. Зафиксировать основу Phase 12 и строгие JSON-схемы

**Критичность:** критичная.

**Модель:** GPT-5.6 Terra medium.

**Repository:** VPS-OPS-LAB.

**Файлы:**

- Создать: четыре JSON-файла в `packaging/phase13-awg3-preflight/`.
- Создать: `tests/test_phase13_awg3_preflight_contract.py`.

**Интерфейсы:**

- `phase12-equality-foundation.json` содержит только safe accepted facts.
- Schemas запрещают дополнительные поля через `additionalProperties=false`.
- Python module из задачи 3 читает эти files без неявных defaults.

- [ ] **Шаг 1. Написать RED-тест frozen foundation**

```python
def test_phase12_foundation_contains_exact_accepted_safe_facts():
    foundation = load_json(FOUNDATION_PATH)
    assert foundation == {
        "schema": "amn2.phase13.phase12-equality-foundation.v1",
        "source_head": "ff115b63ca1329640ca13ae0a502d155f99b456b",
        "foreign": {
            "persistent_entries": 153,
            "stable_sha256": "f5767f361a9441dd4b5361c07da164a3059e0d1347d5217594534797d367b7e8",
            "equality_receipt_sha256": "bc9065b3fa7cab40f5eefebbfd8093f2d62477e972777fe665e8d9f6028aa704",
        },
        "awg2": {
            "udp_port": 30001,
            "vpn_cidr": "10.212.12.0/24",
            "route_device": "amn2spbr0",
            "persistent_peers": 7,
            "live_peers": 7,
            "restart_count": 59,
            "forward_rule_count": 3,
            "web_listener": "127.0.0.1:3031",
            "bot_enabled": False,
        },
    }
```

- [ ] **Шаг 2. Написать RED-тест schema closure**

```python
def test_all_phase13_schemas_are_closed_objects():
    for path in (MANIFEST_SCHEMA, EVIDENCE_SCHEMA, FAILURE_SCHEMA):
        schema = load_json(path)
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert schema["type"] == "object"
        assert schema["additionalProperties"] is False
        assert schema["required"]
```

- [ ] **Шаг 3. Запустить RED**

```powershell
& 'worktrees\amn2-phase13-awg2-awg3-local\.venv\Scripts\python.exe' -m pytest tests/test_phase13_awg3_preflight_contract.py -q
```

Ожидается: FAIL, потому что файлы ещё отсутствуют.

- [ ] **Шаг 4. Создать точную основу и схемы**

Основа должна точно совпасть с объектом из шага 1. Корневая схема манифеста
обязательно требует все поля без неявных значений по умолчанию:
`schema`, `outcome_id`, `created_at`, `expires_at`, `target_role`,
`source_base`, `source_head`, `candidate`, `artifacts`,
`foundation_sha256`, `allowed_command_families`, `forbidden_actions`,
`max_attempts`, `remote_write_allowed`, `package_build_allowed` и
`live_action_authorized`.

Тесты отдельно фиксируют точные константы: `schema` равен
`amn2.phase13.awg3-readonly-preflight-manifest.v1`, `target_role` равен
`spain-primary`, `source_base` и `source_head` равны указанным в общих
ограничениях хешам, `max_attempts` равен `1`, а три разрешающих флага равны
`false`. Полный `candidate` совпадает с принятым объектом из задачи 3.
`artifacts` допускает только объекты с обязательными полями `path`, `size` и
`sha256`; все вложенные объекты также закрыты через
`additionalProperties=false`.

- [ ] **Шаг 5. Запустить GREEN**

```powershell
& 'worktrees\amn2-phase13-awg2-awg3-local\.venv\Scripts\python.exe' -m pytest tests/test_phase13_awg3_preflight_contract.py -q
```

- [ ] **Шаг 6. Создать отдельный VPS-OPS-LAB commit**

```powershell
git diff --check
git add -- packaging/phase13-awg3-preflight tests/test_phase13_awg3_preflight_contract.py
git diff --cached --check
git commit -m "Добавить схемы Phase 13 AWG3 preflight"
```

**Критерий завершения:** frozen facts exact, schemas закрыты, secrets и target
identifiers отсутствуют.

---

### Задача 3. Реализовать canonical manifest и evidence validator

**Критичность:** очень важная.

**Модель:** GPT-5.6 Terra medium.

**Файлы:**

- Создать: `scripts/phase13_awg3_preflight_contract.py`.
- Изменить: `tests/test_phase13_awg3_preflight_contract.py`.

**Интерфейсы:**

```python
class ContractError(ValueError): ...

def canonical_json_bytes(value: object) -> bytes: ...
def sha256_bytes(value: bytes) -> str: ...
def load_json_object_strict(raw: bytes, *, label: str) -> dict[str, object]: ...
def stable_foreign_projection(items: list[dict[str, object]]) -> list[dict[str, object]]: ...
def build_manifest(*, outcome_id: str, created_at: datetime, expires_at: datetime,
                   artifact_paths: tuple[Path, ...]) -> dict[str, object]: ...
def validate_manifest(value: object, *, artifact_root: Path) -> dict[str, object]: ...
def validate_success_evidence(value: object, *, manifest: Mapping[str, object]) -> dict[str, object]: ...
def validate_failure_evidence(value: object, *, manifest: Mapping[str, object]) -> dict[str, object]: ...
```

- [ ] **Шаг 1. Добавить RED-тест canonical JSON и duplicate-key rejection**

```python
def test_strict_json_rejects_duplicate_keys_and_noncanonical_bytes():
    with pytest.raises(ContractError, match="duplicate key"):
        load_json_object_strict(b'{"schema":"a","schema":"b"}', label="manifest")

    value = {"b": 2, "a": 1}
    assert canonical_json_bytes(value) == b'{"a":1,"b":2}\n'
```

- [ ] **Шаг 2. Добавить RED-тест parity с Phase 12 equality**

```python
def test_stable_foreign_projection_removes_only_volatile_fields():
    rows = [{
        "name_sha256": "a" * 64,
        "image_or_unit_sha256": "b" * 64,
        "active_state": "active",
        "restart_count": 59,
        "bound_port_set": [443],
    }]
    assert stable_foreign_projection(rows) == [{
        "active_state": "active",
        "image_or_unit_sha256": "b" * 64,
        "name_sha256": "a" * 64,
    }]
```

- [ ] **Шаг 3. Добавить RED-тест manifest candidate и artifact binding**

```python
def test_manifest_binds_exact_candidate_and_artifact_bytes(tmp_path):
    collector = tmp_path / "collector.sh"
    collector.write_bytes(b"#!/bin/sh\nexit 0\n")
    manifest = build_manifest(
        outcome_id="test-outcome-001",
        created_at=datetime(2026, 8, 1, tzinfo=timezone.utc),
        expires_at=datetime(2026, 8, 2, tzinfo=timezone.utc),
        artifact_paths=(collector,),
    )
    assert manifest["candidate"]["udp_port"] == 30002
    assert manifest["candidate"]["vpn_cidr"] == "10.212.13.0/24"
    assert manifest["artifacts"][0]["sha256"] == hashlib.sha256(
        collector.read_bytes()
    ).hexdigest()
```

- [ ] **Шаг 4. Запустить RED**

```powershell
& 'worktrees\amn2-phase13-awg2-awg3-local\.venv\Scripts\python.exe' -m pytest tests/test_phase13_awg3_preflight_contract.py -q
```

- [ ] **Шаг 5. Реализовать минимальный stdlib-only contract**

Duplicate keys проверяются через `json.loads(..., object_pairs_hook=...)`.
Файлы открываются один раз с `O_NOFOLLOW` при наличии этой возможности; size и
SHA-256 считаются из уже открытого descriptor. Candidate object всегда exact:

```python
CANDIDATE = {
    "runtime_instance_id": "spain-awg3-candidate-001",
    "protocol_version": "awg3",
    "interface_name": "awg3",
    "host_bridge": "amn2sp3br0",
    "udp_port": 30002,
    "vpn_cidr": "10.212.13.0/24",
    "server_vpn_address": "10.212.13.1/24",
    "container_cidr": "172.29.252.0/28",
    "container_name": "amn2-spain-awg3",
    "service_name": "amn2-spain-awg3.service",
    "state_root": "/var/lib/amn2-spain/awg3",
    "config_path": "/var/lib/amn2-spain/awg3/awg3.conf",
}
```

- [ ] **Шаг 6. Добавить negative matrix**

Тесты обязаны отклонять unknown fields, wrong candidate, invalid SHA, symlink,
artifact replacement, expired outcome, `max_attempts != 1`, любое `true` в
трёх authorization flags, inconsistent `decision` и неупорядоченные
`stop_reasons`.

- [ ] **Шаг 7. Запустить GREEN**

```powershell
& 'worktrees\amn2-phase13-awg2-awg3-local\.venv\Scripts\python.exe' -m pytest tests/test_phase13_awg3_preflight_contract.py -q
```

- [ ] **Шаг 8. Commit**

```powershell
git add -- scripts/phase13_awg3_preflight_contract.py tests/test_phase13_awg3_preflight_contract.py
git diff --cached --check
git commit -m "Добавить контракт Phase 13 AWG3 preflight"
```

**Критерий завершения:** canonicalization и validation детерминированы,
Phase 12 volatile fields не расширены, external dependencies не добавлены.

---

### Задача 4. Реализовать удалённый collector только для чтения

**Критичность:** очень важная.

**Модель:** GPT-5.6 SOL medium.

**Файлы:**

- Создать: `scripts/vps/phase13_spain_awg3_readonly_preflight_remote.sh`.
- Создать: `tests/test_phase13_awg3_readonly_preflight.py`.

**Интерфейсы:**

- Вход: единственный mode `preflight`; candidate constants встроены в script.
- Выход: один JSON `amn2.phase13.awg3-readonly-preflight.v1` либо одна строка
  `AMN2_PHASE13_AWG3_PREFLIGHT_FAILURE_V1|stage=<allowlisted>|exit=<n>`.
- Remote filesystem writes: запрещены.

- [ ] **Шаг 1. Написать RED static allowlist/denylist test**

```python
def test_remote_collector_is_exact_read_only_awg3_probe():
    source = REMOTE.read_text(encoding="utf-8")
    for marker in (
        "set -Eeuo pipefail",
        'readonly CANDIDATE_UDP_PORT="30002"',
        'readonly CANDIDATE_INTERFACE="awg3"',
        'readonly CANDIDATE_BRIDGE="amn2sp3br0"',
        'readonly CANDIDATE_VPN_CIDR="10.212.13.0/24"',
        'readonly CANDIDATE_CONTAINER_CIDR="172.29.252.0/28"',
        '"schema":"amn2.phase13.awg3-readonly-preflight.v1"',
        '"mutation_attempted":false',
    ):
        assert marker in source

    forbidden = (
        r"\bsystemctl\s+(start|stop|restart|reload|enable|disable|mask|unmask)\b",
        r"\bdocker\s+(run|create|start|stop|restart|rm|exec)\b",
        r"\bip\s+(address|route|link)\s+(add|del|replace|set)\b",
        r"\bnft\s+(add|delete|flush|insert|replace)\b",
        r"\b(?:wg|awg)\s+(set|setconf|addconf|syncconf)\b",
        r"(?:^|\s)>+\s*[^&]",
        r"\btee\b",
    )
    for pattern in forbidden:
        assert re.search(pattern, source, re.I | re.M) is None
```

- [ ] **Шаг 2. Добавить RED harness-tests для conflict taxonomy**

Извлечённые pure Bash functions тестируются fixtures для:

- occupied/free UDP `30002`;
- interface/bridge name collision;
- IPv4 CIDR overlap и non-overlap;
- container/service/path existence;
- permission/parse ambiguity;
- empty process/socket set как точный пустой результат.

Пример:

```python
def test_candidate_port_conflict_is_fail_closed():
    result = run_bash_harness(PORT_CLASSIFIER + "\nclassify_udp_port 30002 '53,443,30002'")
    assert result.returncode == 71
    assert result.stdout == "udp_port_conflict\n"
```

- [ ] **Шаг 3. Запустить RED**

```powershell
& 'worktrees\amn2-phase13-awg2-awg3-local\.venv\Scripts\python.exe' -m pytest tests/test_phase13_awg3_readonly_preflight.py -q
```

- [ ] **Шаг 4. Реализовать collector по отдельным bounded stages**

Stages: `bootstrap`, `candidate_sockets`, `candidate_links`,
`candidate_addresses_routes`, `candidate_docker`, `candidate_systemd`,
`candidate_paths`, `awg2_projection`, `foreign_projection`, `render`.

Каждый command имеет отдельную проверку exit status. Запрещены `|| true` и
`2>&1`. Raw config и peer identifiers не выводятся; peer set нормализуется и
хешируется на remote до JSON render.

- [ ] **Шаг 5. Добавить tests AWG2/foreign fail-closed projection**

Tests проверяют exact `30001`, `10.212.12.0/24`, `amn2spbr0`, peer counts
`7/7`, restart count `59`, forward rules `3`, web listener, bot disabled,
foreign count `153` и stable SHA-256 из foundation.

- [ ] **Шаг 6. Запустить Bash syntax и GREEN**

```powershell
& 'C:\Program Files\Git\bin\bash.exe' -n scripts/vps/phase13_spain_awg3_readonly_preflight_remote.sh
& 'worktrees\amn2-phase13-awg2-awg3-local\.venv\Scripts\python.exe' -m pytest tests/test_phase13_awg3_readonly_preflight.py -q
```

- [ ] **Шаг 7. Commit**

```powershell
git add -- scripts/vps/phase13_spain_awg3_readonly_preflight_remote.sh tests/test_phase13_awg3_readonly_preflight.py
git diff --cached --check
git commit -m "Добавить read-only collector Phase 13 AWG3"
```

**Критерий завершения:** static denylist и dynamic fixtures проходят; script
не содержит mutation verbs, secret-bearing reads или remote writes.

---

### Задача 5. Реализовать checksum/outcome PowerShell runner

**Критичность:** очень важная.

**Модель:** GPT-5.6 SOL medium.

**Файлы:**

- Создать: `scripts/vps/phase13_spain_awg3_readonly_preflight_ssh_runner.ps1`.
- Изменить: `tests/test_phase13_awg3_readonly_preflight.py`.

**Интерфейсы:**

```powershell
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("preflight")]
    [string]$Mode,
    [Parameter(Mandatory = $true)]
    [string]$OutcomeId,
    [string]$Approval = ""
)
```

Runner использует fixed paths относительно repository, существующий private
trust bundle `spain-fresh-20260720-001`, exact OpenSSH binaries и новый
локальный outcome root. Он не принимает target path, key path или manifest
path от пользователя.

- [ ] **Шаг 1. Добавить RED-тест отсутствующей approval**

```python
def test_missing_approval_prints_exact_phrase_before_private_or_network_access():
    result = run_runner("test-outcome-001", approval=None)
    assert result.returncode != 0
    assert "УТВЕРЖДАЮ ОДИН READ-ONLY SPAIN PREFLIGHT" in result.stdout
    combined = (result.stdout + result.stderr).casefold()
    assert "ssh.exe" not in combined
    assert "target.env" not in combined
```

- [ ] **Шаг 2. Добавить RED replay/checksum tests**

Tests создают private temp root и доказывают:

- wrong runner/collector/schema/foundation hash блокируется до binding/SSH;
- existing claim блокирует повтор;
- expired outcome блокируется;
- evidence и failure evidence используют create-new/no-replace;
- symlink/reparse point/foreign owner/weak ACL блокируются;
- raw stdout/stderr не записываются.

- [ ] **Шаг 3. Добавить RED transport envelope tests**

Fake SSH process возвращает success JSON, allowlisted failure line, timeout,
extra line, CRLF corruption, invalid UTF-8, oversized output и unknown exit.
Допускается ровно один canonical document.

- [ ] **Шаг 4. Запустить RED**

```powershell
& 'worktrees\amn2-phase13-awg2-awg3-local\.venv\Scripts\python.exe' -m pytest tests/test_phase13_awg3_readonly_preflight.py -q
```

- [ ] **Шаг 5. Реализовать минимальный runner**

Порядок строго фиксирован:

1. validation args;
2. self/manifest/artifact checksum;
3. exact approval comparison;
4. private root/ACL/reparse/owner checks;
5. create-new claim;
6. trust binding и host-key pin;
7. один `ssh.exe` с collector bytes через stdin;
8. bounded output parse;
9. Python contract validation;
10. create-new evidence или sanitized failure evidence;
11. SHA-256 результата.

Approval phrase строится из exact hashes и явно содержит запреты package
build/deploy/mutation. При пустой approval runner только печатает phrase и
останавливается до private state/network.

- [ ] **Шаг 6. Запустить PowerShell parser и GREEN**

```powershell
& 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe' -NoLogo -NoProfile -NonInteractive -Command "[void][scriptblock]::Create((Get-Content -Raw -LiteralPath 'scripts\vps\phase13_spain_awg3_readonly_preflight_ssh_runner.ps1'))"
& 'worktrees\amn2-phase13-awg2-awg3-local\.venv\Scripts\python.exe' -m pytest tests/test_phase13_awg3_readonly_preflight.py -q
```

- [ ] **Шаг 7. Commit**

```powershell
git add -- scripts/vps/phase13_spain_awg3_readonly_preflight_ssh_runner.ps1 tests/test_phase13_awg3_readonly_preflight.py
git diff --cached --check
git commit -m "Добавить checksum-bound runner Phase 13 AWG3"
```

**Критерий завершения:** все failure paths доказанно завершаются до SSH либо
создают только очищенную локальную квитанцию; реальный SSH не выполнялся.

---

### Задача 6. Связать manifest, collector, runner и foundation

**Критичность:** важная.

**Модель:** GPT-5.6 Terra medium.

**Файлы:**

- Изменить: `scripts/phase13_awg3_preflight_contract.py`.
- Изменить: оба Phase 13 test-файла.
- Создать только test fixtures под `tests/fixtures/phase13-awg3-preflight/`.

**Интерфейсы:**

- CLI mode `verify-local` проверяет repository artifacts без network.
- CLI mode `prepare-test-manifest` разрешён только для temp test directory.
- Production outcome/manifest mode отсутствует до отдельного gate.

- [ ] **Шаг 1. Добавить RED end-to-end local test**

```python
def test_local_contract_binds_every_artifact_without_network(tmp_path):
    report = run_contract_verify_local(repo_root=ROOT)
    assert report["result"] == "passed"
    assert report["artifact_count"] == 6
    assert re.fullmatch(r"[0-9a-f]{64}", report["candidate_sha256"])
    assert report["network_attempted"] is False
    assert report["package_build_performed"] is False
    assert report["live_action_authorized"] is False
```

- [ ] **Шаг 2. Добавить deterministic fixture matrix**

Одинаковые bytes дают одинаковый manifest SHA-256; изменение каждого artifact
даёт mismatch. Отдельные fixtures покрывают все exit codes `64..75`.

- [ ] **Шаг 3. Реализовать только local verification modes**

CLI не имеет параметров host/user/key/SSH. Любая неизвестная команда возвращает
`64`. Никакой archive, runtime image или installer не создаётся.

- [ ] **Шаг 4. Запустить focused suite**

```powershell
& 'worktrees\amn2-phase13-awg2-awg3-local\.venv\Scripts\python.exe' -m pytest tests/test_phase13_awg3_preflight_contract.py tests/test_phase13_awg3_readonly_preflight.py -q
```

- [ ] **Шаг 5. Запустить существующую Spain regression suite**

```powershell
& 'worktrees\amn2-phase13-awg2-awg3-local\.venv\Scripts\python.exe' -m pytest tests/test_post_release_spain_readonly_preflight.py tests/test_phase12_spain_package_tooling.py -q
```

- [ ] **Шаг 6. Commit**

```powershell
git add -- scripts/phase13_awg3_preflight_contract.py tests/test_phase13_awg3_preflight_contract.py tests/test_phase13_awg3_readonly_preflight.py tests/fixtures/phase13-awg3-preflight
git diff --cached --check
git commit -m "Связать локальный комплект Phase 13 AWG3"
```

**Критерий завершения:** локальный комплект детерминирован, existing Phase 12
tests не регрессировали, network/package/live paths отсутствуют.

---

### Задача 7. Полная проверка, diff/secret/security review

**Критичность:** важная.

**Модель:** GPT-5.6 SOL medium.

**Файлы:** изменения запрещены до получения результатов проверки; fixes при
необходимости получают отдельные RED/GREEN commits.

- [ ] **Шаг 1. Запустить полный AMN2 suite после задачи 1**

```powershell
& '.venv\Scripts\python.exe' -m pytest -q
```

Рабочая папка: AMN2 worktree. Ожидается: `0 failed`; exact counts записываются
в receipt и не подменяются историческими `1108/1/1`.

- [ ] **Шаг 2. Запустить весь новый и существующий Spain tooling suite**

```powershell
& 'worktrees\amn2-phase13-awg2-awg3-local\.venv\Scripts\python.exe' -m pytest tests/test_phase13_awg3_preflight_contract.py tests/test_phase13_awg3_readonly_preflight.py tests/test_post_release_spain_readonly_preflight.py tests/test_phase12_spain_package_tooling.py -q
```

- [ ] **Шаг 3. Выполнить syntax/diff checks**

```powershell
& 'C:\Program Files\Git\bin\bash.exe' -n scripts/vps/phase13_spain_awg3_readonly_preflight_remote.sh
git diff --check
```

- [ ] **Шаг 4. Проверить secret и mutation patterns**

```powershell
rg -n "BEGIN .*PRIVATE KEY|PrivateKey\s*=|PresharedKey\s*=|HeaderProtectionKey\s*=|vpn://|password\s*=|token\s*=" packaging/phase13-awg3-preflight scripts/phase13_awg3_preflight_contract.py scripts/vps/phase13_spain_awg3_readonly_preflight_* tests/test_phase13_awg3_*
rg -n "systemctl (start|stop|restart|reload|enable|disable)|docker (run|create|start|stop|restart|rm|exec)|wg set|awg set|nft (add|delete|flush)|ip (address|route|link) (add|del|replace|set)" scripts/vps/phase13_spain_awg3_readonly_preflight_remote.sh
```

Каждое совпадение разбирается вручную; test assertions могут содержать
запрещённые строки только как negative sentinel.

- [ ] **Шаг 5. Выполнить security diff scan**

Scope: AMN2 task-1 commit относительно `ff115b63` и VPS-OPS-LAB tooling commits
относительно `59aad68`. Каждый candidate получает validation/closure receipt.

- [ ] **Шаг 6. Проверить границы**

```text
implementation_scope=local_only
runtime_package_built=false
ssh_attempted=false
preflight_run_attempted=false
spain_mutation_attempted=false
usa_mutation_attempted=false
foreign_service_changed=false
live_action_authorized=false
```

**Критерий завершения:** tests и security gate закрыты; report hash записан;
открытый блокирующий finding отсутствует. Иначе exact approval phrase не
готовится.

---

### Задача 8. Receipt, status, commits, push и origin readback

**Критичность:** простая после прохождения всех предыдущих gates.

**Модель:** GPT-5.6 Terra low.

**Файлы:**

- Создать:
  `research/amn2/phase13-awg3-preflight-local-tooling-receipt-2026-08-01.md`.
- Изменить: первый block `docs/PROJECT_STATUS_CURRENT.ru.md`.

- [ ] **Шаг 1. Записать secret-free receipt**

Receipt содержит exact AMN2 base/head, VPS-OPS-LAB commits, test counts,
artifact hashes, security report hash и все значения `false` из задачи 7.
Target host/user/IP/key paths и raw outputs запрещены.

- [ ] **Шаг 2. Обновить только верхний Phase 13 status**

Status сообщает: local tooling готов, но production manifest, exact outcome,
SSH approval, preflight run, package build и live actions отсутствуют. USA
остаётся rollback contour: критерий готовности к её отключению или иному
использованию не достигнут. Отдельное уведомление оператору разрешается только
после будущего USA retirement readiness gate с точными evidence и отдельным
решением.

- [ ] **Шаг 3. Проверить и staged только разрешённые файлы**

```powershell
git diff --check
git add -- docs/PROJECT_STATUS_CURRENT.ru.md research/amn2/phase13-awg3-preflight-local-tooling-receipt-2026-08-01.md
git diff --cached --check
git diff --cached --name-only
```

- [ ] **Шаг 4. Создать отдельный docs receipt commit**

```powershell
git commit -m "Записать готовность Phase 13 AWG3 preflight tooling"
```

- [ ] **Шаг 5. Push обеих веток**

AMN2 source branch содержит только admission fix; VPS-OPS-LAB branch содержит
только schemas/tooling/tests/docs commits.

- [ ] **Шаг 6. Fetch и доказать origin equality**

```powershell
git fetch origin
git rev-parse HEAD
git rev-parse '@{upstream}'
```

Команда выполняется отдельно в обоих repositories; hashes обязаны совпасть.

**Критерий завершения:** local/origin equality подтверждена, unrelated files
не staged, SSH/preflight не выполнялись.

---

## Отложенный checksum-bound запуск

Этот план заканчивается готовностью локального tooling. Он не создаёт и не
использует production `outcome_id`.

После завершения задач 1–8 нужен отдельный gate с моделью GPT-5.6 SOL medium:

1. создать новый production outcome и manifest из уже проверенных bytes;
2. записать exact runner/collector/schema/foundation/manifest SHA-256;
3. вывести literal approval phrase;
4. остановиться без SSH;
5. получить отдельное подтверждение оператора;
6. выполнить ровно один read-only Spain preflight;
7. доказать AWG2/foreign equality и отсутствие всех mutations.

Package build, deploy, AWG3 runtime creation и rollback rehearsal требуют ещё
одних отдельных проектного и live gates и не являются продолжением этой
approval.

## Общие критерии завершения

- Более новое отрицательное compatibility evidence блокирует старое `PASSED`.
- Phase 12 stable foreign projection semantics не изменены.
- Candidate values exact и не заменяются автоматически.
- Manifest/evidence schemas закрыты и fail closed.
- Remote collector содержит только команды для чтения.
- Runner checksum-bound, one-outcome и create-new/no-replace.
- Raw sensitive output не сохраняется.
- Все focused/full/regression/security checks закрыты.
- Runtime package не собран.
- SSH и предварительная проверка Spain не запускались.
- Spain AWG2, USA и посторонний Spain-сервис не изменялись.
