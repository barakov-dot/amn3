# Server Check Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a safe `server check` command that reads `servers.yml`, selects one VPS, and runs read-only readiness checks without modifying the server.

**Architecture:** Add `server_config` for parsing/validation and `server` for report, command policy, and SSH-backed checks. Keep real SSH behind an interface so all check logic can be tested with fake clients before connecting to a VPS.

**Tech Stack:** Python 3.12+, pytest, PyYAML for YAML parsing, argparse CLI, existing security redaction helpers.

---

## File Structure

- Modify `pyproject.toml`: add `PyYAML`.
- Create `app/server_config/__init__.py`: exports config loader/model.
- Create `app/server_config/models.py`: dataclasses for server config.
- Create `app/server_config/loader.py`: YAML loading and validation.
- Create `app/server/__init__.py`: package exports.
- Create `app/server/report.py`: check status/result/report formatting.
- Create `app/server/ssh.py`: SSH client protocol and fake-friendly command result.
- Create `app/server/checks.py`: read-only command policy and check runner.
- Modify `app/cli.py`: add `server check`.
- Modify `docs/NEXT_STAGE_BEGINNER_GUIDE.md`: add the real `server check` command once implemented.
- Add tests under `tests/server_config/` and `tests/server/`.

---

### Task 1: Server Config Loader

**Files:**
- Modify: `pyproject.toml`
- Create: `app/server_config/__init__.py`
- Create: `app/server_config/models.py`
- Create: `app/server_config/loader.py`
- Test: `tests/server_config/test_loader.py`

- [x] **Step 1: Write failing tests**

```python
# tests/server_config/test_loader.py
from pathlib import Path

import pytest

from app.server_config.loader import ConfigError, load_server_config, select_server


VALID_YAML = """
servers:
  - name: debian-vps-1
    enabled: true
    location: default
    ssh:
      host: 203.0.113.10
      port: 22
      user: root
      auth:
        type: key
        private_key_path: C:/Users/me/.ssh/id_ed25519
    vpn:
      endpoint_host: 203.0.113.10
      port: 30001
      interface: awg0
      network_cidr: 10.8.0.0/24
      server_address: 10.8.0.1/24
      dns: 1.1.1.1
      allowed_ips: 0.0.0.0/0
      max_devices: 254
    firewall:
      provider: ufw
      open_vpn_port: true
    runtime:
      type: host_systemd
      service_name: awg-quick@awg0
"""


def test_load_server_config_reads_valid_servers_yml(tmp_path):
    path = tmp_path / "servers.yml"
    path.write_text(VALID_YAML, encoding="utf-8")

    config = load_server_config(path)
    server = select_server(config, "debian-vps-1")

    assert server.name == "debian-vps-1"
    assert server.ssh.host == "203.0.113.10"
    assert server.vpn.interface == "awg0"
    assert server.runtime.service_name == "awg-quick@awg0"


def test_select_server_lists_available_names(tmp_path):
    path = tmp_path / "servers.yml"
    path.write_text(VALID_YAML, encoding="utf-8")

    config = load_server_config(path)

    with pytest.raises(ConfigError, match="debian-vps-1"):
        select_server(config, "missing")


def test_loader_rejects_placeholder_values(tmp_path):
    path = tmp_path / "servers.yml"
    path.write_text(VALID_YAML.replace("203.0.113.10", "CHANGE_ME_SERVER_IP"), encoding="utf-8")

    with pytest.raises(ConfigError, match="placeholder"):
        load_server_config(path)
```

- [x] **Step 2: Run test to verify it fails**

Run:

```powershell
$env:PYTHONPATH='.codex_deps;.'; python -m pytest tests/server_config/test_loader.py -v
```

Expected: FAIL because `app.server_config` does not exist.

- [x] **Step 3: Implement config loader**

Add dependency:

```toml
"PyYAML>=6,<7",
```

Create dataclasses:

```python
# app/server_config/models.py
from dataclasses import dataclass


@dataclass(frozen=True)
class SshAuthConfig:
    type: str
    private_key_path: str | None = None


@dataclass(frozen=True)
class SshConfig:
    host: str
    port: int
    user: str
    auth: SshAuthConfig


@dataclass(frozen=True)
class VpnConfig:
    endpoint_host: str
    port: int | str
    interface: str
    network_cidr: str
    server_address: str
    dns: str
    allowed_ips: str
    max_devices: int


@dataclass(frozen=True)
class FirewallConfig:
    provider: str
    open_vpn_port: bool


@dataclass(frozen=True)
class RuntimeConfig:
    type: str
    service_name: str


@dataclass(frozen=True)
class ServerConfig:
    name: str
    enabled: bool
    location: str
    ssh: SshConfig
    vpn: VpnConfig
    firewall: FirewallConfig
    runtime: RuntimeConfig


@dataclass(frozen=True)
class ServersConfig:
    servers: list[ServerConfig]
```

Implement `load_server_config(path)` with `yaml.safe_load`, required field checks, and placeholder rejection for any string starting with `CHANGE_ME`.

Implement `select_server(config, name)` and `ConfigError`.

- [x] **Step 4: Run test to verify it passes**

Run:

```powershell
$env:PYTHONPATH='.codex_deps;.'; python -m pytest tests/server_config/test_loader.py -v
```

Expected: PASS.

---

### Task 2: Report Model and Safe Formatting

**Files:**
- Create: `app/server/__init__.py`
- Create: `app/server/report.py`
- Test: `tests/server/test_report.py`

- [x] **Step 1: Write failing tests**

```python
# tests/server/test_report.py
from app.server.report import CheckResult, ServerCheckReport


def test_report_marks_overall_failed_when_any_error_exists():
    report = ServerCheckReport(
        server_name="debian-vps-1",
        results=[
            CheckResult(name="ssh", status="ok", message="connected"),
            CheckResult(name="debian", status="error", message="not Debian"),
        ],
    )

    assert report.ok is False


def test_report_safe_text_redacts_secrets():
    report = ServerCheckReport(
        server_name="debian-vps-1",
        results=[
            CheckResult(
                name="ssh",
                status="error",
                message="failed",
                details="APP_SECRET_KEY = secret-value",
            )
        ],
    )

    text = report.to_text()

    assert "secret-value" not in text
    assert "[REDACTED]" in text
```

- [x] **Step 2: Run test to verify it fails**

Run:

```powershell
$env:PYTHONPATH='.codex_deps;.'; python -m pytest tests/server/test_report.py -v
```

Expected: FAIL because `app.server.report` does not exist.

- [x] **Step 3: Implement report model**

Use dataclasses. Valid statuses: `ok`, `warning`, `error`.

`ServerCheckReport.ok` returns false if any result is `error`.

`to_text()` prints safe lines and uses `app.security.redaction.redact`.

- [x] **Step 4: Run test to verify it passes**

Expected: PASS.

---

### Task 3: Read-Only Command Policy

**Files:**
- Create: `app/server/checks.py`
- Test: `tests/server/test_command_policy.py`

- [x] **Step 1: Write failing tests**

```python
# tests/server/test_command_policy.py
import pytest

from app.server.checks import CommandPolicyError, ensure_read_only_command


def test_policy_allows_known_read_only_commands():
    ensure_read_only_command("cat /etc/os-release")
    ensure_read_only_command("command -v awg")
    ensure_read_only_command("systemctl is-active awg-quick@awg0")
    ensure_read_only_command("ss -lun")


@pytest.mark.parametrize(
    "command",
    [
        "apt install amneziawg",
        "systemctl start awg-quick@awg0",
        "ufw allow 30001/udp",
        "rm /tmp/file",
        "cat /etc/os-release > out.txt",
        "sed -i s/a/b/ file",
    ],
)
def test_policy_rejects_mutating_commands(command):
    with pytest.raises(CommandPolicyError):
        ensure_read_only_command(command)
```

- [x] **Step 2: Run test to verify it fails**

Expected: FAIL because command policy does not exist.

- [x] **Step 3: Implement command policy**

Allow exact commands and prefix-safe `systemctl is-active awg-quick@<interface>`.

Reject mutating tokens and shell redirection.

- [x] **Step 4: Run test to verify it passes**

Expected: PASS.

---

### Task 4: Fake SSH Check Runner

**Files:**
- Create: `app/server/ssh.py`
- Modify: `app/server/checks.py`
- Test: `tests/server/test_checks.py`

- [x] **Step 1: Write failing tests**

```python
# tests/server/test_checks.py
from app.server.checks import run_server_checks
from app.server.ssh import CommandResult
from app.server_config.loader import load_server_config, select_server
from tests.server_config.test_loader import VALID_YAML


class FakeSshClient:
    def __init__(self, outputs):
        self.outputs = outputs
        self.commands = []

    def run(self, command: str) -> CommandResult:
        self.commands.append(command)
        result = self.outputs.get(command)
        if result is None:
            return CommandResult(exit_code=127, stdout="", stderr="missing")
        return result


def _server(tmp_path):
    path = tmp_path / "servers.yml"
    path.write_text(VALID_YAML, encoding="utf-8")
    return select_server(load_server_config(path), "debian-vps-1")


def test_run_server_checks_reports_ready_debian_server(tmp_path):
    server = _server(tmp_path)
    ssh = FakeSshClient(
        {
            "cat /etc/os-release": CommandResult(0, 'ID=debian\\nVERSION_ID=\"12\"\\n', ""),
            "command -v systemctl": CommandResult(0, "/usr/bin/systemctl\\n", ""),
            "command -v awg": CommandResult(0, "/usr/bin/awg\\n", ""),
            "command -v awg-quick": CommandResult(0, "/usr/bin/awg-quick\\n", ""),
            "command -v ufw": CommandResult(0, "/usr/sbin/ufw\\n", ""),
            "systemctl is-active awg-quick@awg0": CommandResult(0, "active\\n", ""),
            "ss -lun": CommandResult(0, "udp UNCONN 0 0 0.0.0.0:30001 0.0.0.0:*\\n", ""),
        }
    )

    report = run_server_checks(server, ssh)

    assert report.ok is True
    assert all(command in ssh.commands for command in ["cat /etc/os-release", "ss -lun"])


def test_run_server_checks_marks_missing_awg_as_warning(tmp_path):
    server = _server(tmp_path)
    ssh = FakeSshClient(
        {
            "cat /etc/os-release": CommandResult(0, "ID=debian\\n", ""),
            "command -v systemctl": CommandResult(0, "/usr/bin/systemctl\\n", ""),
            "command -v awg": CommandResult(1, "", "not found"),
            "command -v awg-quick": CommandResult(1, "", "not found"),
            "command -v ufw": CommandResult(0, "/usr/sbin/ufw\\n", ""),
            "systemctl is-active awg-quick@awg0": CommandResult(3, "inactive\\n", ""),
            "ss -lun": CommandResult(0, "", ""),
        }
    )

    report = run_server_checks(server, ssh)

    statuses = {result.name: result.status for result in report.results}
    assert statuses["awg"] == "warning"
    assert statuses["awg-quick"] == "warning"
```

- [x] **Step 2: Run test to verify it fails**

Expected: FAIL because SSH/check runner does not exist.

- [x] **Step 3: Implement fake-friendly checks**

`CommandResult` dataclass:

```python
@dataclass(frozen=True)
class CommandResult:
    exit_code: int
    stdout: str
    stderr: str
```

`SshClient` protocol:

```python
class SshClient(Protocol):
    def run(self, command: str) -> CommandResult: ...
```

`run_server_checks(server, ssh)`:

- runs only commands through `ensure_read_only_command`;
- checks Debian from `/etc/os-release`;
- systemd missing is error;
- `awg`, `awg-quick`, `ufw` missing are warning;
- inactive interface is warning;
- returns `ServerCheckReport`.

- [x] **Step 4: Run test to verify it passes**

Expected: PASS.

---

### Task 5: CLI Integration

**Files:**
- Modify: `app/cli.py`
- Test: `tests/server/test_cli_server_check.py`

- [x] **Step 1: Write failing CLI parser test**

```python
# tests/server/test_cli_server_check.py
from app.cli import build_parser


def test_cli_accepts_server_check_arguments():
    parser = build_parser()

    args = parser.parse_args(["server", "check", "--config", "servers.yml", "--server", "debian-vps-1"])

    assert args.command == "server"
    assert args.server_command == "check"
    assert args.config == "servers.yml"
    assert args.server == "debian-vps-1"
```

- [x] **Step 2: Run test to verify it fails**

Expected: FAIL because CLI has no `build_parser` or `server check`.

- [x] **Step 3: Refactor CLI parser and add command**

Expose:

```python
def build_parser() -> argparse.ArgumentParser
```

Keep existing backup commands working.

Add:

```powershell
python -m app.cli server check --config servers.yml --server debian-vps-1
```

For this plan, CLI can fail with a clear message if no real SSH backend is configured. The check runner itself is fully tested with fake SSH.

- [x] **Step 4: Run CLI tests and backup tests**

Run:

```powershell
$env:PYTHONPATH='.codex_deps;.'; python -m pytest tests/server/test_cli_server_check.py tests/backup/test_backup_service.py -v
```

Expected: PASS.

---

### Task 6: Documentation and Full Verification

**Files:**
- Modify: `docs/NEXT_STAGE_BEGINNER_GUIDE.md`

- [x] **Step 1: Update guide command**

Add:

```powershell
python -m app.cli server check --config servers.yml --server debian-vps-1
```

Explain that this command is read-only and should not modify the VPS.

- [x] **Step 2: Run full test suite**

Run:

```powershell
$env:PYTHONPATH='.codex_deps;.'; python -m pytest tests -v
```

Expected: all tests pass.

- [x] **Step 3: Secret scan**

Run:

```powershell
rg --pcre2 -n "BEGIN .*PRIVATE KEY|TELEGRAM_BOT_TOKEN=[^C]|APP_SECRET_KEY=(?!CHANGE_ME)|UNFINISHED_MARKER" README.md docs app tests pyproject.toml .env.example .gitignore
```

Expected: no real secrets. Example/dummy values in tests or docs are acceptable if obviously fake.

---

## Self-Review

Spec coverage:

- Config parsing and server selection: Task 1.
- Report model and redaction: Task 2.
- Read-only command safety: Task 3.
- Fake SSH check runner: Task 4.
- CLI command shape: Task 5.
- Beginner documentation and full verification: Task 6.

Deferred:

- Real SSH backend.
- Provisioning.
- Server backup.
- Live peer apply/revoke.
- Telegram admin integration with real VPS.
