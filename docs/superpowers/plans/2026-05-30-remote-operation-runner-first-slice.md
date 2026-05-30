# RemoteOperationRunner First Slice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ввести первый безопасный slice `RemoteOperationRunner` в `amn2`: read-only server health check через typed operation contract, общий command policy, structured result и web audit metadata без изменения live VPS state.

**Architecture:** Первый slice не трогает peer apply/revoke и не добавляет destructive operations. Он оборачивает уже существующий read-only `server check`/web health flow: command allowlist остается в `app/server/checks.py`, SSH остается за `SshClient`, новый runner валидирует `RemoteOperation`, выполняет только read-only steps и возвращает structured result для текущей health summary логики.

**Tech Stack:** Python 3.12+, dataclasses, pytest, FastAPI TestClient, существующие `SshClient`, `CommandResult`, `ServerCheckReport`, `HealthSummary`, `Repository`.

---

## Область первого slice

Рабочий репозиторий для исполнения плана: `C:\Users\SooL\Documents\Amneziya`.

Входит в первый slice:

- typed модели `RemoteOperation`, `CommandStep`, `OperationPlan`, `OperationResult`;
- `RemoteOperationRunner` только для `read-only-remote`;
- shared command policy через существующий `ensure_read_only_command()`;
- `build_server_check_operation(server)`;
- перевод `run_server_checks()` на runner без изменения внешнего поведения;
- web health audit metadata с `operation_id`, `risk_class`, `consistency_status`;
- tests для fake runner, command blocking, behavior parity и web audit.

Не входит в первый slice:

- host key enrollment;
- sudo policy;
- peer apply/revoke migration;
- traffic telemetry migration;
- secret-safe CLI migration;
- Docker live apply/revoke;
- destructive operations.

---

## Структура файлов

- Создать: `app/server/operations.py` - dataclasses и validation helpers для remote operation contracts.
- Создать: `app/server/operation_runner.py` - read-only runner, который выполняет validated command steps через `SshClient`.
- Изменить: `app/server/checks.py` - добавить `build_server_check_operation()` и провести `run_server_checks()` через runner.
- Изменить: `app/web/app.py` - добавить runner metadata в audit payload `web_server_health_run`.
- Изменить: `app/web/server_health.py` - отдавать operation metadata из health execution, сохранив стабильность существующих полей `HealthSummary`.
- Тест: `tests/server/test_operation_runner.py`.
- Тест: `tests/server/test_checks.py`.
- Тест: `tests/web/test_server_health.py`.
- Тест: `tests/web/test_servers.py`.
- Опциональное обновление docs после успешных тестов: `docs/RUNTIME_REGISTRY.ru.md`.

---

### Task 1: Модели Remote Operation

**Файлы:**
- Создать: `app/server/operations.py`
- Тест: `tests/server/test_operation_runner.py`

- [ ] **Step 1: Написать failing tests для validation моделей operation**

Create `tests/server/test_operation_runner.py` with:

```python
import pytest

from app.server.operations import (
    CommandStep,
    OperationValidationError,
    RemoteOperation,
    validate_operation,
)


def test_validate_operation_allows_read_only_remote_steps():
    operation = RemoteOperation(
        id="server.health.check",
        risk_class="read-only-remote",
        server_id="debian-vps-1",
        actor_id="web-admin",
        actor_auth_method="session",
        inputs={"server_name": "debian-vps-1"},
        secret_refs=(),
        local_side_effects=("server_health_checks", "admin_actions"),
        remote_side_effects=(),
        command_policy="read-only",
        steps=(
            CommandStep(
                id="os-release",
                command="cat /etc/os-release",
                command_policy_class="read-only",
                expected_remote_effect="none",
                allowed_exit_codes=(0,),
                timeout_seconds=20,
                output_policy="internal-only",
            ),
        ),
        consistency_policy="read-only",
        audit_summary="Run read-only server health check",
        rollback_note="No rollback is needed for read-only health checks.",
        confirmation_required=False,
    )

    validate_operation(operation)


@pytest.mark.parametrize(
    "key",
    ["password", "private_key", "token", "preshared_key", "client_config"],
)
def test_validate_operation_rejects_secret_like_inputs(key):
    operation = RemoteOperation(
        id="server.health.check",
        risk_class="read-only-remote",
        server_id="debian-vps-1",
        actor_id="cli",
        actor_auth_method="cli",
        inputs={key: "secret-value"},
        secret_refs=(),
        local_side_effects=(),
        remote_side_effects=(),
        command_policy="read-only",
        steps=(),
        consistency_policy="read-only",
        audit_summary="Run read-only server health check",
        rollback_note="No rollback is needed for read-only health checks.",
        confirmation_required=False,
    )

    with pytest.raises(OperationValidationError, match="secret-like input"):
        validate_operation(operation)
```

- [ ] **Step 2: Запустить focused test и подтвердить начальное падение**

Run from `C:\Users\SooL\Documents\Amneziya`:

```powershell
python -m pytest tests/server/test_operation_runner.py -v
```

Ожидаемо: FAIL with `ModuleNotFoundError: No module named 'app.server.operations'`.

- [ ] **Step 3: Реализовать operation dataclasses и validation**

Create `app/server/operations.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


RiskClass = Literal[
    "read-only",
    "read-only-remote",
    "read-only-remote-telemetry",
    "secret-read",
    "state-write",
    "remote-state-write",
    "remote-exec",
    "destructive-remote",
]
ActorAuthMethod = Literal["session", "telegram-admin", "scoped-token", "cli", "system"]
CommandPolicyClass = Literal["read-only", "telemetry", "state-write"]
OutputPolicy = Literal["internal-only", "discard", "redact-and-store"]
ConsistencyPolicy = Literal["read-only", "local-first", "remote-first", "two-phase-best-effort"]
ConsistencyStatus = Literal[
    "read-only",
    "consistent",
    "remote-changed-local-failed",
    "local-changed-remote-failed",
    "unknown",
]


class OperationValidationError(ValueError):
    pass


@dataclass(frozen=True)
class CommandStep:
    id: str
    command: str
    command_policy_class: CommandPolicyClass
    expected_remote_effect: str
    allowed_exit_codes: tuple[int, ...]
    timeout_seconds: int
    output_policy: OutputPolicy
    stdin_secret_ref: str | None = None


@dataclass(frozen=True)
class RemoteOperation:
    id: str
    risk_class: RiskClass
    server_id: str
    actor_id: str
    actor_auth_method: ActorAuthMethod
    inputs: dict[str, str]
    secret_refs: tuple[str, ...]
    local_side_effects: tuple[str, ...]
    remote_side_effects: tuple[str, ...]
    command_policy: CommandPolicyClass
    steps: tuple[CommandStep, ...]
    consistency_policy: ConsistencyPolicy
    audit_summary: str
    rollback_note: str
    confirmation_required: bool
    run_id: str | None = None
    idempotency_key: str | None = None


@dataclass(frozen=True)
class OperationPlan:
    operation_id: str
    risk_class: RiskClass
    commands: tuple[str, ...]
    audit_summary: str
    rollback_note: str


@dataclass(frozen=True)
class StepExecutionResult:
    step_id: str
    command: str
    exit_code: int
    stdout: str
    stderr: str
    status: Literal["succeeded", "failed"]


@dataclass(frozen=True)
class OperationResult:
    operation_id: str
    risk_class: RiskClass
    status: Literal["planned", "completed", "failed", "blocked"]
    consistency_status: ConsistencyStatus
    steps: tuple[StepExecutionResult, ...]
    redacted_stdout_summary: str
    redacted_stderr_summary: str
    recovery_note: str


_SECRET_INPUT_MARKERS = (
    "password",
    "private_key",
    "token",
    "secret",
    "preshared_key",
    "client_config",
)


def validate_operation(operation: RemoteOperation) -> None:
    if not operation.id.strip():
        raise OperationValidationError("operation id cannot be blank")
    if operation.risk_class == "destructive-remote" and not operation.confirmation_required:
        raise OperationValidationError("destructive-remote operation requires confirmation")
    for key in operation.inputs:
        lowered = key.lower()
        if any(marker in lowered for marker in _SECRET_INPUT_MARKERS):
            raise OperationValidationError(f"secret-like input is not allowed: {key}")
    for step in operation.steps:
        if step.command_policy_class != operation.command_policy:
            raise OperationValidationError(
                f"step policy {step.command_policy_class} does not match operation policy {operation.command_policy}"
            )
        if step.timeout_seconds < 1:
            raise OperationValidationError(f"step timeout must be positive: {step.id}")
        if not step.allowed_exit_codes:
            raise OperationValidationError(f"allowed exit codes cannot be empty: {step.id}")
```

- [ ] **Step 4: Запустить focused model tests**

Run:

```powershell
python -m pytest tests/server/test_operation_runner.py::test_validate_operation_allows_read_only_remote_steps tests/server/test_operation_runner.py::test_validate_operation_rejects_secret_like_inputs -v
```

Ожидаемо: PASS для обоих tests.

- [ ] **Step 5: Сделать commit Task 1 в `amn2`**

Run:

```powershell
git add app/server/operations.py tests/server/test_operation_runner.py
git commit -m "Add remote operation contract models"
```

---

### Task 2: Read-Only Remote Runner

**Файлы:**
- Создать: `app/server/operation_runner.py`
- Изменить: `tests/server/test_operation_runner.py`

- [ ] **Step 1: Добавить failing runner tests**

Append to `tests/server/test_operation_runner.py`:

```python
from app.server.operation_runner import RemoteOperationRunner
from app.server.ssh import CommandResult


class RecordingSshClient:
    def __init__(self, *, results=None):
        self.calls = []
        self._results = results or {}

    def run(self, command: str, stdin: str | None = None) -> CommandResult:
        self.calls.append((command, stdin))
        return self._results.get(command, CommandResult(exit_code=0, stdout="ok", stderr=""))


def _read_only_operation(command: str = "cat /etc/os-release") -> RemoteOperation:
    return RemoteOperation(
        id="server.health.check",
        risk_class="read-only-remote",
        server_id="debian-vps-1",
        actor_id="cli",
        actor_auth_method="cli",
        inputs={"server_name": "debian-vps-1"},
        secret_refs=(),
        local_side_effects=(),
        remote_side_effects=(),
        command_policy="read-only",
        steps=(
            CommandStep(
                id="step-1",
                command=command,
                command_policy_class="read-only",
                expected_remote_effect="none",
                allowed_exit_codes=(0,),
                timeout_seconds=20,
                output_policy="internal-only",
            ),
        ),
        consistency_policy="read-only",
        audit_summary="Run read-only server health check",
        rollback_note="No rollback is needed for read-only health checks.",
        confirmation_required=False,
    )


def test_runner_builds_plan_without_executing_ssh():
    ssh = RecordingSshClient()
    runner = RemoteOperationRunner(ssh)

    plan = runner.plan(_read_only_operation())

    assert plan.operation_id == "server.health.check"
    assert plan.risk_class == "read-only-remote"
    assert plan.commands == ("cat /etc/os-release",)
    assert ssh.calls == []


def test_runner_executes_read_only_operation():
    ssh = RecordingSshClient(
        results={
            "cat /etc/os-release": CommandResult(
                exit_code=0,
                stdout="ID=debian\n",
                stderr="",
            )
        }
    )
    runner = RemoteOperationRunner(ssh)

    result = runner.apply(_read_only_operation())

    assert result.status == "completed"
    assert result.consistency_status == "read-only"
    assert result.steps[0].stdout == "ID=debian\n"
    assert ssh.calls == [("cat /etc/os-release", None)]


def test_runner_blocks_mutating_command_before_ssh():
    ssh = RecordingSshClient()
    runner = RemoteOperationRunner(ssh)

    result = runner.apply(_read_only_operation("systemctl restart awg-quick@awg0"))

    assert result.status == "blocked"
    assert "not in the read-only allowlist" in result.recovery_note or "Mutating command" in result.recovery_note
    assert ssh.calls == []
```

- [ ] **Step 2: Запустить focused runner tests и подтвердить падение**

Run:

```powershell
python -m pytest tests/server/test_operation_runner.py -v
```

Ожидаемо: FAIL with `ModuleNotFoundError: No module named 'app.server.operation_runner'`.

- [ ] **Step 3: Реализовать read-only runner**

Create `app/server/operation_runner.py`:

```python
from __future__ import annotations

from app.security.redaction import redact
from app.server.checks import CommandPolicyError, ensure_read_only_command
from app.server.operations import (
    OperationPlan,
    OperationResult,
    RemoteOperation,
    StepExecutionResult,
    validate_operation,
)
from app.server.ssh import SshClient


class RemoteOperationRunner:
    def __init__(self, ssh_client: SshClient) -> None:
        self._ssh_client = ssh_client

    def plan(self, operation: RemoteOperation) -> OperationPlan:
        validate_operation(operation)
        return OperationPlan(
            operation_id=operation.id,
            risk_class=operation.risk_class,
            commands=tuple(step.command for step in operation.steps),
            audit_summary=operation.audit_summary,
            rollback_note=operation.rollback_note,
        )

    def apply(self, operation: RemoteOperation) -> OperationResult:
        try:
            validate_operation(operation)
            if operation.risk_class != "read-only-remote":
                return _blocked(operation, "First runner slice only supports read-only-remote operations.")
            step_results: list[StepExecutionResult] = []
            for step in operation.steps:
                try:
                    ensure_read_only_command(step.command)
                except CommandPolicyError as exc:
                    return _blocked(operation, str(exc))
                result = self._ssh_client.run(step.command)
                status = "succeeded" if result.exit_code in step.allowed_exit_codes else "failed"
                step_results.append(
                    StepExecutionResult(
                        step_id=step.id,
                        command=step.command,
                        exit_code=result.exit_code,
                        stdout=result.stdout,
                        stderr=result.stderr,
                        status=status,
                    )
                )
                if status == "failed":
                    return OperationResult(
                        operation_id=operation.id,
                        risk_class=operation.risk_class,
                        status="failed",
                        consistency_status="read-only",
                        steps=tuple(step_results),
                        redacted_stdout_summary=_stream_summary(result.stdout),
                        redacted_stderr_summary=_stream_summary(result.stderr),
                        recovery_note=operation.rollback_note,
                    )
            return OperationResult(
                operation_id=operation.id,
                risk_class=operation.risk_class,
                status="completed",
                consistency_status="read-only",
                steps=tuple(step_results),
                redacted_stdout_summary=_combined_summary(step.stdout for step in step_results),
                redacted_stderr_summary=_combined_summary(step.stderr for step in step_results),
                recovery_note=operation.rollback_note,
            )
        except Exception as exc:
            return OperationResult(
                operation_id=operation.id,
                risk_class=operation.risk_class,
                status="failed",
                consistency_status="unknown",
                steps=(),
                redacted_stdout_summary="empty",
                redacted_stderr_summary="empty",
                recovery_note=redact(f"Remote operation failed before completion: {type(exc).__name__}: {exc}"),
            )


def _blocked(operation: RemoteOperation, reason: str) -> OperationResult:
    return OperationResult(
        operation_id=operation.id,
        risk_class=operation.risk_class,
        status="blocked",
        consistency_status="read-only",
        steps=(),
        redacted_stdout_summary="empty",
        redacted_stderr_summary="empty",
        recovery_note=redact(reason),
    )


def _stream_summary(value: str) -> str:
    return "present" if value else "empty"


def _combined_summary(values) -> str:
    return "present" if any(values) else "empty"
```

- [ ] **Step 4: Запустить runner tests**

Run:

```powershell
python -m pytest tests/server/test_operation_runner.py -v
```

Ожидаемо: PASS.

- [ ] **Step 5: Сделать commit Task 2 в `amn2`**

Run:

```powershell
git add app/server/operation_runner.py tests/server/test_operation_runner.py
git commit -m "Add read-only remote operation runner"
```

---

### Task 3: Factory для Server Check Operation

**Файлы:**
- Изменить: `app/server/checks.py`
- Изменить: `tests/server/test_checks.py`

- [ ] **Step 1: Добавить failing tests для operation factory**

Append to `tests/server/test_checks.py`:

```python
from app.server.checks import build_server_check_operation


def test_build_server_check_operation_describes_host_health_check(tmp_path):
    server = _server(tmp_path)

    operation = build_server_check_operation(server, actor_id="web-admin", actor_auth_method="session")

    assert operation.id == "server.health.check"
    assert operation.risk_class == "read-only-remote"
    assert operation.server_id == "debian-vps-1"
    assert operation.command_policy == "read-only"
    assert operation.consistency_policy == "read-only"
    assert [step.command for step in operation.steps] == planned_check_commands(server)
    assert all(step.expected_remote_effect == "none" for step in operation.steps)
    assert all(step.command_policy_class == "read-only" for step in operation.steps)


def test_build_server_check_operation_describes_docker_health_check(tmp_path):
    server = _docker_server(tmp_path)

    operation = build_server_check_operation(server, actor_id="cli", actor_auth_method="cli")

    assert operation.id == "server.health.check"
    assert "docker exec amnezia-awg command -v awg" in [step.command for step in operation.steps]
    assert operation.inputs == {
        "server_name": "debian-vps-1",
        "runtime": "docker",
    }
```

- [ ] **Step 2: Запустить focused tests и подтвердить падение**

Run:

```powershell
python -m pytest tests/server/test_checks.py::test_build_server_check_operation_describes_host_health_check tests/server/test_checks.py::test_build_server_check_operation_describes_docker_health_check -v
```

Ожидаемо: FAIL with import error for `build_server_check_operation`.

- [ ] **Step 3: Реализовать operation factory**

Modify `app/server/checks.py`:

```python
from app.server.operations import CommandStep, RemoteOperation
```

Add near `planned_check_commands()`:

```python
def build_server_check_operation(
    server: ServerConfig,
    *,
    actor_id: str,
    actor_auth_method,
) -> RemoteOperation:
    commands = planned_check_commands(server)
    steps = tuple(
        CommandStep(
            id=f"server-check-{index + 1}",
            command=command,
            command_policy_class="read-only",
            expected_remote_effect="none",
            allowed_exit_codes=(0,),
            timeout_seconds=20,
            output_policy="internal-only",
        )
        for index, command in enumerate(commands)
    )
    return RemoteOperation(
        id="server.health.check",
        risk_class="read-only-remote",
        server_id=server.name,
        actor_id=actor_id,
        actor_auth_method=actor_auth_method,
        inputs={
            "server_name": server.name,
            "runtime": server.runtime.type,
        },
        secret_refs=(),
        local_side_effects=("server_health_checks", "admin_actions"),
        remote_side_effects=(),
        command_policy="read-only",
        steps=steps,
        consistency_policy="read-only",
        audit_summary=f"Run read-only health check for server {server.name}",
        rollback_note="No rollback is needed for read-only health checks. Re-run server check after fixing server access.",
        confirmation_required=False,
    )
```

- [ ] **Step 4: Запустить focused factory tests**

Run:

```powershell
python -m pytest tests/server/test_checks.py::test_build_server_check_operation_describes_host_health_check tests/server/test_checks.py::test_build_server_check_operation_describes_docker_health_check -v
```

Ожидаемо: PASS.

- [ ] **Step 5: Сделать commit Task 3 в `amn2`**

Run:

```powershell
git add app/server/checks.py tests/server/test_checks.py
git commit -m "Describe server health as remote operation"
```

---

### Task 4: Выполнение Server Checks через Runner

**Файлы:**
- Изменить: `app/server/checks.py`
- Изменить: `tests/server/test_checks.py`

- [ ] **Step 1: Добавить tests на behavior parity и blocked command**

Append to `tests/server/test_checks.py`:

```python
def test_run_server_checks_still_runs_host_commands_in_order(tmp_path):
    server = _server(tmp_path)
    ssh = FakeSshClient(
        {
            "cat /etc/os-release": CommandResult(0, "ID=debian\n", ""),
            "command -v systemctl": CommandResult(0, "/usr/bin/systemctl\n", ""),
            "command -v awg": CommandResult(0, "/usr/bin/awg\n", ""),
            "command -v awg-quick": CommandResult(0, "/usr/bin/awg-quick\n", ""),
            "command -v ufw": CommandResult(0, "/usr/sbin/ufw\n", ""),
            "systemctl is-active awg-quick@awg0": CommandResult(0, "active\n", ""),
            "ss -lun": CommandResult(0, "udp UNCONN 0 0 0.0.0.0:30001 0.0.0.0:*\n", ""),
        }
    )

    report = run_server_checks(server, ssh)

    assert ssh.commands == planned_check_commands(server)
    assert report.ok is True


def test_run_server_checks_reports_blocked_policy_violation(tmp_path, monkeypatch):
    server = _server(tmp_path)

    monkeypatch.setattr(
        "app.server.checks.planned_check_commands",
        lambda server: ["systemctl restart awg-quick@awg0"],
    )

    report = run_server_checks(server, FakeSshClient({}))

    assert report.ok is False
    assert report.results[0].name == "remote-operation-policy"
    assert report.results[0].status == "error"
    assert "Mutating command" in report.results[0].message or "allowlist" in report.results[0].message
```

- [ ] **Step 2: Запустить parity tests и подтвердить текущее поведение**

Run:

```powershell
python -m pytest tests/server/test_checks.py::test_run_server_checks_still_runs_host_commands_in_order tests/server/test_checks.py::test_run_server_checks_reports_blocked_policy_violation -v
```

Ожидаемо: first test may pass before migration; second fails because `run_server_checks()` currently raises instead of returning a policy report.

- [ ] **Step 3: Перевести `run_server_checks()` на runner**

Modify `app/server/checks.py` imports:

```python
from app.server.operation_runner import RemoteOperationRunner
from app.server.operations import OperationResult
```

Replace the first line inside `run_server_checks()`:

```python
    operation = build_server_check_operation(
        server,
        actor_id="system",
        actor_auth_method="system",
    )
    operation_result = RemoteOperationRunner(ssh).apply(operation)
    if operation_result.status == "blocked":
        return ServerCheckReport(
            server_name=server.name,
            results=[
                CheckResult(
                    "remote-operation-policy",
                    "error",
                    operation_result.recovery_note,
                )
            ],
        )
    commands = [step.command for step in operation_result.steps]
    command_results = {
        step.command: CommandResult(step.exit_code, step.stdout, step.stderr)
        for step in operation_result.steps
    }
```

Then replace each `_run(ssh, commands[n])` call with `command_results[commands[n]]`.

Keep `_run()` in the file for compatibility until all direct call sites are checked; do not remove it in this task.

- [ ] **Step 4: Запустить server check tests**

Run:

```powershell
python -m pytest tests/server/test_checks.py tests/server/test_command_policy.py -v
```

Ожидаемо: PASS.

- [ ] **Step 5: Запустить CLI server check tests**

Run:

```powershell
python -m pytest tests/server/test_cli_server_check.py -v
```

Ожидаемо: PASS.

- [ ] **Step 6: Сделать commit Task 4 в `amn2`**

Run:

```powershell
git add app/server/checks.py tests/server/test_checks.py
git commit -m "Run server health checks through operation runner"
```

---

### Task 5: Web Health Metadata

**Файлы:**
- Изменить: `app/web/server_health.py`
- Изменить: `app/web/app.py`
- Изменить: `tests/web/test_server_health.py`
- Изменить: `tests/web/test_servers.py`

- [ ] **Step 1: Добавить metadata fields в health summary tests**

Modify `tests/web/test_server_health.py` expected summary assertions:

```python
assert summary.operation_id == "server.health.check"
assert summary.risk_class == "read-only-remote"
assert summary.consistency_status == "read-only"
```

Добавить эти assertions в:

- `test_summarize_check_report_marks_online_when_all_checks_pass`;
- `test_summarize_check_report_marks_degraded_for_warnings`;
- `test_summarize_check_report_marks_offline_for_errors`;
- `test_summarize_check_report_marks_unknown_when_no_results_exist`.

- [ ] **Step 2: Добавить web audit metadata assertion**

In `tests/web/test_servers.py::test_health_run_stores_unknown_when_server_config_is_unavailable`, replace the final admin action assertion with:

```python
        action = _latest_admin_action(repo)
        assert action["action"] == "web_server_health_run"
        metadata = json.loads(action["metadata_json"])
        assert metadata["operation_id"] == "server.health.check"
        assert metadata["risk_class"] == "read-only-remote"
        assert metadata["consistency_status"] == "read-only"
        assert metadata["status"] == "unknown"
```

- [ ] **Step 3: Запустить web tests и подтвердить падение**

Run:

```powershell
python -m pytest tests/web/test_server_health.py tests/web/test_servers.py -v
```

Ожидаемо: FAIL because `HealthSummary` has no operation metadata yet.

- [ ] **Step 4: Расширить `HealthSummary` metadata**

Modify `app/web/server_health.py`:

```python
@dataclass(frozen=True)
class HealthSummary:
    status: HealthStatus
    latency_ms: int | None
    ssh_ok: bool
    awg_ok: bool
    udp_port_ok: bool
    error: str | None
    operation_id: str = "server.health.check"
    risk_class: str = "read-only-remote"
    consistency_status: str = "read-only"
```

Новые required arguments в call sites не нужны: defaults сохраняют существующее поведение.

- [ ] **Step 5: Добавить metadata в web audit payload**

Modify `app/web/app.py` in `web_server_health_run` metadata:

```python
                        metadata={
                            "operation_id": summary.operation_id,
                            "risk_class": summary.risk_class,
                            "consistency_status": summary.consistency_status,
                            "status": summary.status,
                            "error": summary.error,
                        },
```

- [ ] **Step 6: Запустить web tests**

Run:

```powershell
python -m pytest tests/web/test_server_health.py tests/web/test_servers.py -v
```

Ожидаемо: PASS.

- [ ] **Step 7: Сделать commit Task 5 в `amn2`**

Run:

```powershell
git add app/web/server_health.py app/web/app.py tests/web/test_server_health.py tests/web/test_servers.py
git commit -m "Record server health operation metadata"
```

---

### Task 6: Документация и Verification

**Файлы:**
- Изменить: `docs/RUNTIME_REGISTRY.ru.md`
- Опционально: `docs/RUNTIME_REGISTRY.en.md`

- [ ] **Step 1: Задокументировать первый runner slice**

Добавить короткий русский раздел в `docs/RUNTIME_REGISTRY.ru.md` после read-only checks:

```markdown
## RemoteOperationRunner first slice

Server health checks use the first `RemoteOperationRunner` slice:

- risk class: `read-only-remote`;
- command policy: existing read-only allowlist;
- remote side effects: none;
- local side effects: health snapshot and admin audit event when launched from web;
- consistency status: `read-only`.

This slice does not enable peer apply/revoke, Docker live changes, firewall changes or destructive operations.
```

Если English docs в этой ветке поддерживаются синхронно, добавить тот же смысл в `docs/RUNTIME_REGISTRY.en.md`.

- [ ] **Step 2: Запустить focused verification**

Run:

```powershell
python -m pytest tests/server/test_operation_runner.py tests/server/test_checks.py tests/server/test_command_policy.py tests/server/test_cli_server_check.py tests/web/test_server_health.py tests/web/test_servers.py -v
```

Ожидаемо: PASS.

- [ ] **Step 3: Запустить full tests**

Run:

```powershell
python -m pytest tests -v
```

Ожидаемо: PASS.

- [ ] **Step 4: Запустить markdown/security scan, если он есть в branch**

Запустить existing hygiene checks репозитория:

```powershell
python -m pytest tests/test_file_hygiene.py tests/security/test_redaction.py -v
```

Ожидаемо: PASS.

- [ ] **Step 5: Сделать commit Task 6 в `amn2`**

Run:

```powershell
git add docs/RUNTIME_REGISTRY.ru.md docs/RUNTIME_REGISTRY.en.md
git commit -m "Document remote operation runner first slice"
```

Если `docs/RUNTIME_REGISTRY.en.md` не изменялся, не добавлять его в `git add`.

---

## Self-Review Checklist

- [ ] План начинается с operation models, затем runner, затем server health integration.
- [ ] State-changing remote operation не вводится.
- [ ] Peer apply/revoke behavior не меняется.
- [ ] Existing server health и CLI tests остаются в scope.
- [ ] New tests доказывают, что mutating commands блокируются до SSH.
- [ ] Web audit записывает operation metadata без raw command output.
- [ ] Следующий slice явно отложен: telemetry command policy или peer apply migration после review.

## Handoff

После approve этот plan исполняется в `C:\Users\SooL\Documents\Amneziya`, не в `vpn-ops-lab`. Использовать feature branch, сохранять commits per task и не включать `VPS_APPLY_ENABLED=true` в рамках этого slice.
