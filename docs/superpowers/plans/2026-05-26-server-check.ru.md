# План реализации Server Check

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Цель:** добавить безопасную команду `server check`, которая читает `servers.yml`, выбирает VPS и запускает read-only readiness checks без изменения сервера.

**Архитектура:** добавить `server_config` для parsing/validation и `server` для report, command policy и SSH-backed checks. Реальный SSH держать за интерфейсом, чтобы логика проверялась fake clients до подключения к VPS.

**Tech Stack:** Python 3.12+, pytest, PyYAML, argparse CLI, existing security redaction helpers.

---

## File Structure

- Modify `pyproject.toml`: add `PyYAML`.
- Create `app/server_config/__init__.py`.
- Create `app/server_config/models.py`.
- Create `app/server_config/loader.py`.
- Create `app/server/__init__.py`.
- Create `app/server/report.py`.
- Create `app/server/ssh.py`.
- Create `app/server/checks.py`.
- Modify `app/cli.py`.
- Modify `docs/NEXT_STAGE_BEGINNER_GUIDE.md`.
- Add tests under `tests/server_config/` and `tests/server/`.

---

### Task 1: Server Config Loader

**Files:**

- `pyproject.toml`
- `app/server_config/__init__.py`
- `app/server_config/models.py`
- `app/server_config/loader.py`
- `tests/server_config/test_loader.py`

- [x] Write tests for valid `servers.yml`, server selection, and placeholder rejection.
- [x] Run focused tests and confirm initial failure.
- [x] Implement dataclasses: `SshAuthConfig`, `SshConfig`, `VpnConfig`, `FirewallConfig`, `RuntimeConfig`, `ServerConfig`, `ServersConfig`.
- [x] Implement `load_server_config`, `select_server`, `ConfigError`, required field validation, and `CHANGE_ME` rejection.
- [x] Run `pytest tests/server_config/test_loader.py -v`.

### Task 2: Report Model and Safe Formatting

**Files:**

- `app/server/__init__.py`
- `app/server/report.py`
- `tests/server/test_report.py`

- [x] Write tests for overall failure on any `error` and secret redaction in `to_text()`.
- [x] Run focused tests and confirm missing module failure.
- [x] Implement `CheckResult`, `ServerCheckReport`, status validation, `ok` property, and redacted text output.
- [x] Run `pytest tests/server/test_report.py -v`.

### Task 3: Read-Only Command Policy

**Files:**

- `app/server/checks.py`
- `tests/server/test_command_policy.py`

- [x] Write tests for allowed commands:
  - `cat /etc/os-release`;
  - `command -v awg`;
  - `systemctl is-active awg-quick@awg0`;
  - `ss -lun`.
- [x] Write tests rejecting mutating commands:
  - `apt install amneziawg`;
  - `systemctl start awg-quick@awg0`;
  - `ufw allow 30001/udp`;
  - `rm /tmp/file`;
  - shell redirection;
  - `sed -i`.
- [x] Implement `CommandPolicyError` and `ensure_read_only_command`.
- [x] Run `pytest tests/server/test_command_policy.py -v`.

### Task 4: Fake SSH Check Runner

**Files:**

- `app/server/ssh.py`
- `app/server/checks.py`
- `tests/server/test_checks.py`

- [x] Write fake SSH client tests for a ready Debian server.
- [x] Write warning tests for missing `awg` and `awg-quick`.
- [x] Implement `CommandResult` and `SshClient` protocol.
- [x] Implement `run_server_checks(server, ssh)`.
- [x] Ensure all commands pass through `ensure_read_only_command`.
- [x] Run `pytest tests/server/test_checks.py -v`.

### Task 5: CLI Integration

**Files:**

- `app/cli.py`
- `tests/server/test_cli_server_check.py`

- [x] Add parser test for:

```powershell
python -m app.cli server check --config servers.yml --server debian-vps-1
```

- [x] Expose `build_parser()`.
- [x] Keep backup commands working.
- [x] Add `server check` command shape.
- [x] Run CLI and backup tests.

### Task 6: Documentation and Verification

**Files:**

- `docs/NEXT_STAGE_BEGINNER_GUIDE.md`

- [x] Document `server check` command.
- [x] Explain that this command is read-only.
- [x] Run full test suite.
- [x] Run secret scan.

## Verification

Final verification:

```powershell
$env:PYTHONPATH='.codex_deps;.'; python -m pytest tests -v
```

Expected result:

```text
72 passed
```

Secret scan may show only intentional fake test values and regex examples.

## Deferred

- Real SSH backend.
- Provisioning.
- Server config backup.
- Live peer apply/revoke.
- Telegram admin integration with real VPS.
