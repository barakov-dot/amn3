# Local Agent Production Wiring Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the pushed read-only Local Amnezia Agent foundation in `amn2` into an opt-in runnable production component with settings, token provisioning, CLI serve command, and real read-only runtime detection.

**Architecture:** The agent remains disabled by default and exposes only the first-slice read-only routes. `.env` stores only token hashes and non-secret runtime settings; raw tokens are displayed once by an operator-owned CLI command. Runtime detection uses existing `servers.yml` metadata and local read-only commands through a small adapter with fake runner tests.

**Tech Stack:** Python 3.12+, FastAPI, uvicorn, pydantic-settings, argparse, pytest, existing `app.agent`, `app.server_config`, and `app.server.checks` patterns.

---

## Preconditions

- Production repo: `C:\Users\SooL\Documents\Amneziya`
- Coordination repo: `C:\Users\SooL\Documents\VPS-OPS-LAB`
- Start only after the existing `amn2` stacked PR is opened or merged:

```text
base: codex-vps-test-prep
head: codex/local-agent-first-slice
manual PR URL: https://github.com/barakov-dot/amn2/pull/new/codex/local-agent-first-slice
```

If the PR is not merged yet, implement this plan on top of `codex/local-agent-first-slice`. If it is merged, create a fresh branch from updated `codex-vps-test-prep`:

```powershell
git switch codex-vps-test-prep
git pull
git switch -c codex/local-agent-production-wiring
```

## File Structure

Production repo `amn2`:

- Modify `app/config/settings.py`: add disabled-by-default Local Agent settings and validation.
- Create `app/agent/config.py`: parse scopes/expiry and build `AgentToken` values from settings.
- Modify `app/agent/runtime.py`: add command-runner protocol and real read-only runtime adapter.
- Modify `app/cli.py`: add `agent hash-token` and `agent serve`.
- Modify `docs/LOCAL_AGENT.ru.md`: document `.env`, token provisioning, serve command, and route boundary.
- Modify `docs/PRODUCTION_VPS_CHECKLIST.ru.md`: add a short Local Agent deployment checklist.
- Add tests in `tests/agent/test_config.py`, `tests/agent/test_runtime.py`, and `tests/agent/test_cli.py`.
- Modify `tests/config/test_settings.py`: cover settings parsing and startup refusal when enabled without token hash.

Coordination repo AMN3:

- Modify `docs/PROJECT_STATUS_CURRENT.ru.md` after implementation with branch, commits, tests, PR URL.
- Modify `research/amn2/transfer-backlog.md` after implementation with Local Agent status.

## Task 0: Integration Checkpoint

**Files:**

- Read-only check: `C:\Users\SooL\Documents\Amneziya`
- No file edits in this task.

- [ ] **Step 1: Confirm the current branch and clean tree**

Run:

```powershell
git status --short --branch
git log -3 --oneline --decorate
```

Expected when continuing the current stacked branch:

```text
## codex/local-agent-first-slice...origin/codex/local-agent-first-slice
ac2baa8 (HEAD -> codex/local-agent-first-slice, origin/codex/local-agent-first-slice) Add typed local agent auth errors
3119ee6 Add local Amnezia agent first slice
8ecb0b4 (origin/codex-vps-test-prep, codex-vps-test-prep) Add configurable client config defaults
```

- [ ] **Step 2: Confirm the existing first slice tests**

Run:

```powershell
pytest tests/agent tests/server/test_operation_runner.py tests/server/test_checks.py tests/web/test_servers.py -v
```

Expected:

```text
70 passed
```

The existing `StarletteDeprecationWarning` from `httpx`/`starlette.testclient` can remain.

- [ ] **Step 3: Commit checkpoint only if a new branch was created**

If no files changed, do not commit. If the branch was created, push the branch:

```powershell
git push -u origin codex/local-agent-production-wiring
```

## Task 1: Local Agent Settings

**Files:**

- Modify: `app/config/settings.py`
- Modify: `tests/config/test_settings.py`

- [ ] **Step 1: Write settings tests**

Add these tests to `tests/config/test_settings.py`:

```python
def test_settings_reads_local_agent_settings():
    settings = Settings(
        _env_file=None,
        telegram_bot_token="TEST_TOKEN",
        app_secret_key="test-secret",
        local_agent_enabled=True,
        local_agent_host="127.0.0.1",
        local_agent_port=3041,
        local_agent_token_id="agent-token-1",
        local_agent_token_hash=(
            "sha256:"
            "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
        ),
        local_agent_token_owner="local-controller",
        local_agent_token_scopes="agent:health,agent:read,agent:protocols:read",
        local_agent_token_expires_at="2030-01-02T03:04:05+00:00",
    )

    assert settings.local_agent_enabled is True
    assert settings.local_agent_host == "127.0.0.1"
    assert settings.local_agent_port == 3041
    assert settings.local_agent_token_id == "agent-token-1"
    assert settings.local_agent_token_owner == "local-controller"
    assert settings.local_agent_scopes == [
        "agent:health",
        "agent:read",
        "agent:protocols:read",
    ]


def test_settings_defaults_local_agent_to_disabled():
    settings = Settings(
        _env_file=None,
        telegram_bot_token="TEST_TOKEN",
        app_secret_key="test-secret",
    )

    assert settings.local_agent_enabled is False
    assert settings.local_agent_host == "127.0.0.1"
    assert settings.local_agent_port == 3031
    assert settings.local_agent_token_hash == ""


def test_settings_requires_token_hash_when_local_agent_enabled():
    with pytest.raises(ValidationError, match="LOCAL_AGENT_TOKEN_HASH"):
        Settings(
            _env_file=None,
            telegram_bot_token="TEST_TOKEN",
            app_secret_key="test-secret",
            local_agent_enabled=True,
            local_agent_token_hash="",
        )


def test_settings_rejects_write_scope_for_local_agent_first_slice():
    with pytest.raises(ValidationError, match="LOCAL_AGENT_TOKEN_SCOPES"):
        Settings(
            _env_file=None,
            telegram_bot_token="TEST_TOKEN",
            app_secret_key="test-secret",
            local_agent_enabled=True,
            local_agent_token_hash=(
                "sha256:"
                "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
            ),
            local_agent_token_scopes="agent:health,agent:clients:write",
        )
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```powershell
pytest tests/config/test_settings.py -v
```

Expected: the new tests fail because `Settings` has no Local Agent fields yet.

- [ ] **Step 3: Add settings fields**

Add these fields to `Settings` in `app/config/settings.py` near the web/admin settings:

```python
    local_agent_enabled: bool = Field(default=False, alias="LOCAL_AGENT_ENABLED")
    local_agent_host: str = Field(default="127.0.0.1", alias="LOCAL_AGENT_HOST")
    local_agent_port: int = Field(default=3031, alias="LOCAL_AGENT_PORT")
    local_agent_token_id: str = Field(
        default="local-controller",
        alias="LOCAL_AGENT_TOKEN_ID",
    )
    local_agent_token_hash: str = Field(default="", alias="LOCAL_AGENT_TOKEN_HASH")
    local_agent_token_owner: str = Field(
        default="local-controller",
        alias="LOCAL_AGENT_TOKEN_OWNER",
    )
    local_agent_token_scopes: str = Field(
        default="agent:health,agent:read,agent:protocols:read",
        alias="LOCAL_AGENT_TOKEN_SCOPES",
    )
    local_agent_token_expires_at: str = Field(
        default="",
        alias="LOCAL_AGENT_TOKEN_EXPIRES_AT",
    )
```

In `validate_vpn_port_bounds()`, add this validation block before `return self`:

```python
        if not 1 <= self.local_agent_port <= 65535:
            raise ValueError("LOCAL_AGENT_PORT must be in 1..65535")
        allowed_agent_scopes = {
            "agent:health",
            "agent:read",
            "agent:protocols:read",
        }
        unknown_agent_scopes = set(self.local_agent_scopes) - allowed_agent_scopes
        if unknown_agent_scopes:
            raise ValueError(
                "LOCAL_AGENT_TOKEN_SCOPES contains unsupported first-slice scope(s): "
                + ", ".join(sorted(unknown_agent_scopes))
            )
        token_hash = self.local_agent_token_hash.strip()
        if self.local_agent_enabled:
            if not token_hash:
                raise ValueError(
                    "LOCAL_AGENT_TOKEN_HASH must be set when LOCAL_AGENT_ENABLED=true"
                )
            if not token_hash.startswith("sha256:") or len(token_hash) != 71:
                raise ValueError("LOCAL_AGENT_TOKEN_HASH must be a sha256 token hash")
```

Add this cached property below `panel_auth_methods`:

```python
    @cached_property
    def local_agent_scopes(self) -> list[str]:
        return [
            part.strip()
            for part in self.local_agent_token_scopes.split(",")
            if part.strip()
        ]
```

- [ ] **Step 4: Run settings tests**

Run:

```powershell
pytest tests/config/test_settings.py -v
```

Expected: all settings tests pass.

- [ ] **Step 5: Commit**

Run:

```powershell
git add app/config/settings.py tests/config/test_settings.py
git commit -m "Add Local Agent settings"
```

## Task 2: Token Config Builder

**Files:**

- Create: `app/agent/config.py`
- Create: `tests/agent/test_config.py`

- [ ] **Step 1: Write token config tests**

Create `tests/agent/test_config.py`:

```python
from datetime import datetime, timezone

import pytest

from app.agent.auth import AgentToken
from app.agent.config import (
    build_agent_tokens,
    parse_agent_expiry,
    parse_agent_scopes,
    require_agent_enabled,
)
from app.config.settings import Settings


TOKEN_HASH = (
    "sha256:"
    "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
)


def _settings(**overrides):
    values = {
        "_env_file": None,
        "telegram_bot_token": "TEST_TOKEN",
        "app_secret_key": "test-secret",
        "local_agent_enabled": True,
        "local_agent_token_hash": TOKEN_HASH,
        "local_agent_token_id": "agent-token-1",
        "local_agent_token_owner": "controller",
        "local_agent_token_scopes": "agent:health,agent:read",
    }
    values.update(overrides)
    return Settings(**values)


def test_parse_agent_scopes_strips_empty_parts():
    assert parse_agent_scopes("agent:health, agent:read,") == frozenset(
        {"agent:health", "agent:read"}
    )


def test_parse_agent_expiry_accepts_blank_value():
    assert parse_agent_expiry("") is None
    assert parse_agent_expiry("   ") is None


def test_parse_agent_expiry_accepts_z_suffix():
    assert parse_agent_expiry("2030-01-02T03:04:05Z") == datetime(
        2030,
        1,
        2,
        3,
        4,
        5,
        tzinfo=timezone.utc,
    )


def test_build_agent_tokens_returns_hash_only_token():
    token = build_agent_tokens(_settings())[0]

    assert token == AgentToken(
        token_id="agent-token-1",
        token_hash=TOKEN_HASH,
        scopes=frozenset({"agent:health", "agent:read"}),
        expires_at=None,
        owner="controller",
    )


def test_build_agent_tokens_rejects_disabled_agent():
    with pytest.raises(ValueError, match="LOCAL_AGENT_ENABLED"):
        build_agent_tokens(
            _settings(local_agent_enabled=False, local_agent_token_hash="")
        )


def test_require_agent_enabled_rejects_disabled_agent():
    with pytest.raises(ValueError, match="LOCAL_AGENT_ENABLED"):
        require_agent_enabled(
            _settings(local_agent_enabled=False, local_agent_token_hash="")
        )
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```powershell
pytest tests/agent/test_config.py -v
```

Expected: fail because `app.agent.config` does not exist.

- [ ] **Step 3: Create config builder**

Create `app/agent/config.py`:

```python
from __future__ import annotations

from datetime import datetime, timezone

from app.agent.auth import AgentToken
from app.config.settings import Settings


def require_agent_enabled(settings: Settings) -> None:
    if not settings.local_agent_enabled:
        raise ValueError("LOCAL_AGENT_ENABLED must be true to start the Local Agent")


def parse_agent_scopes(value: str) -> frozenset[str]:
    return frozenset(part.strip() for part in value.split(",") if part.strip())


def parse_agent_expiry(value: str) -> datetime | None:
    stripped = value.strip()
    if not stripped:
        return None
    normalized = stripped[:-1] + "+00:00" if stripped.endswith("Z") else stripped
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def build_agent_tokens(settings: Settings) -> tuple[AgentToken, ...]:
    require_agent_enabled(settings)
    return (
        AgentToken(
            token_id=settings.local_agent_token_id.strip(),
            token_hash=settings.local_agent_token_hash.strip(),
            scopes=parse_agent_scopes(settings.local_agent_token_scopes),
            expires_at=parse_agent_expiry(settings.local_agent_token_expires_at),
            owner=settings.local_agent_token_owner.strip(),
        ),
    )
```

- [ ] **Step 4: Run token config tests**

Run:

```powershell
pytest tests/agent/test_config.py -v
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

Run:

```powershell
git add app/agent/config.py tests/agent/test_config.py
git commit -m "Build Local Agent tokens from settings"
```

## Task 3: Read-Only Runtime Detection

**Files:**

- Modify: `app/agent/runtime.py`
- Modify: `tests/agent/test_runtime.py`

- [ ] **Step 1: Add runtime adapter tests**

Append to `tests/agent/test_runtime.py`:

```python
from app.agent.runtime import (
    CommandResult,
    LocalCommandRuntimeAdapter,
)
from app.server_config.models import (
    FirewallConfig,
    RuntimeConfig,
    ServerConfig,
    SshAuthConfig,
    SshConfig,
    VpnConfig,
)


class FakeCommandRunner:
    def __init__(self, results):
        self.results = results
        self.calls = []

    def run(self, args):
        self.calls.append(args)
        return self.results[args]


def _server(runtime):
    return ServerConfig(
        name="debian-vps-1",
        enabled=True,
        location="default",
        ssh=SshConfig(
            host="127.0.0.1",
            port=22,
            user="root",
            auth=SshAuthConfig(type="key", private_key_path=None),
        ),
        vpn=VpnConfig(
            endpoint_host="127.0.0.1",
            port=30001,
            interface="awg0",
            network_cidr="10.8.1.0/24",
            server_address="10.8.1.1/24",
            dns="1.1.1.1",
            allowed_ips="0.0.0.0/0",
            max_devices=254,
            server_public_key="server-public-key",
        ),
        firewall=FirewallConfig(provider="ufw", open_vpn_port=True),
        runtime=runtime,
    )


def test_local_command_runtime_adapter_detects_running_docker_awg():
    runner = FakeCommandRunner(
        {
            ("docker", "ps", "--format", "{{.Names}}"): CommandResult(
                exit_code=0,
                stdout="amnezia-awg2\n",
                stderr="",
            ),
            ("docker", "exec", "amnezia-awg2", "awg", "show", "awg0", "dump"): CommandResult(
                exit_code=0,
                stdout=(
                    "awg0\tserver-public-key\tprivate\t30001\toff\n"
                    "peer-1\tpsk\tendpoint\t10.8.1.2/32\tlatest\t1\t2\t25\n"
                    "peer-2\tpsk\tendpoint\t10.8.1.3/32\tlatest\t1\t2\t25\n"
                ),
                stderr="",
            ),
        }
    )

    snapshot = LocalCommandRuntimeAdapter(
        _server(RuntimeConfig(type="docker", container_name="amnezia-awg2")),
        runner=runner,
    ).snapshot()

    assert snapshot.server_name == "debian-vps-1"
    assert snapshot.runtime_type == "docker"
    assert snapshot.status == "running"
    assert snapshot.protocols[0].status == "running"
    assert snapshot.protocols[0].container_name == "amnezia-awg2"
    assert snapshot.protocols[0].interface == "awg0"
    assert snapshot.protocols[0].client_count == 2


def test_local_command_runtime_adapter_reports_stopped_docker_container():
    runner = FakeCommandRunner(
        {
            ("docker", "ps", "--format", "{{.Names}}"): CommandResult(
                exit_code=0,
                stdout="other-container\n",
                stderr="",
            ),
        }
    )

    snapshot = LocalCommandRuntimeAdapter(
        _server(RuntimeConfig(type="docker", container_name="amnezia-awg2")),
        runner=runner,
    ).snapshot()

    assert snapshot.status == "stopped"
    assert snapshot.protocols[0].status == "stopped"
    assert snapshot.protocols[0].client_count is None


def test_local_command_runtime_adapter_detects_running_host_systemd():
    runner = FakeCommandRunner(
        {
            ("systemctl", "is-active", "awg-quick@awg0"): CommandResult(
                exit_code=0,
                stdout="active\n",
                stderr="",
            ),
            ("awg", "show", "awg0", "dump"): CommandResult(
                exit_code=0,
                stdout="awg0\tserver-public-key\tprivate\t30001\toff\n",
                stderr="",
            ),
        }
    )

    snapshot = LocalCommandRuntimeAdapter(
        _server(RuntimeConfig(type="host_systemd", service_name="awg-quick@awg0")),
        runner=runner,
    ).snapshot()

    assert snapshot.runtime_type == "host_systemd"
    assert snapshot.status == "running"
    assert snapshot.protocols[0].status == "running"
    assert snapshot.protocols[0].client_count == 0
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```powershell
pytest tests/agent/test_runtime.py -v
```

Expected: fail because `CommandResult` and `LocalCommandRuntimeAdapter` do not exist.

- [ ] **Step 3: Implement command-runner adapter**

Add to `app/agent/runtime.py` below the existing fake adapter:

```python
import subprocess

from app.server_config.models import ServerConfig


@dataclass(frozen=True)
class CommandResult:
    exit_code: int
    stdout: str
    stderr: str


class CommandRunner(Protocol):
    def run(self, args: tuple[str, ...]) -> CommandResult:
        pass


class LocalSystemCommandRunner:
    def run(self, args: tuple[str, ...]) -> CommandResult:
        completed = subprocess.run(
            args,
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return CommandResult(
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )


class LocalCommandRuntimeAdapter:
    def __init__(
        self,
        server: ServerConfig,
        *,
        runner: CommandRunner | None = None,
    ) -> None:
        self._server = server
        self._runner = runner or LocalSystemCommandRunner()

    def snapshot(self) -> RuntimeSnapshot:
        if self._server.runtime.type == "docker":
            return self._docker_snapshot()
        if self._server.runtime.type == "host_systemd":
            return self._host_systemd_snapshot()
        return RuntimeSnapshot(
            server_name=self._server.name,
            runtime_type=self._server.runtime.type,
            status="unknown",
            protocols=(
                ProtocolSnapshot(
                    name="amneziawg",
                    status="unknown",
                    runtime_type=self._server.runtime.type,
                    capabilities=("detect", "status"),
                    interface=self._server.vpn.interface,
                ),
            ),
        )

    def _docker_snapshot(self) -> RuntimeSnapshot:
        container = self._server.runtime.container_name
        if container is None:
            return self._single_protocol_snapshot("unknown", container_name=None)
        ps = self._runner.run(("docker", "ps", "--format", "{{.Names}}"))
        containers = {line.strip() for line in ps.stdout.splitlines() if line.strip()}
        if ps.exit_code != 0 or container not in containers:
            return self._single_protocol_snapshot("stopped", container_name=container)
        dump = self._runner.run(
            ("docker", "exec", container, "awg", "show", self._server.vpn.interface, "dump")
        )
        if dump.exit_code != 0:
            return self._single_protocol_snapshot("degraded", container_name=container)
        return self._single_protocol_snapshot(
            "running",
            container_name=container,
            client_count=_count_dump_peers(dump.stdout),
        )

    def _host_systemd_snapshot(self) -> RuntimeSnapshot:
        service = self._server.runtime.service_name or f"awg-quick@{self._server.vpn.interface}"
        active = self._runner.run(("systemctl", "is-active", service))
        if active.exit_code != 0 or active.stdout.strip() != "active":
            return self._single_protocol_snapshot("stopped", container_name=None)
        dump = self._runner.run(("awg", "show", self._server.vpn.interface, "dump"))
        if dump.exit_code != 0:
            return self._single_protocol_snapshot("degraded", container_name=None)
        return self._single_protocol_snapshot(
            "running",
            container_name=None,
            client_count=_count_dump_peers(dump.stdout),
        )

    def _single_protocol_snapshot(
        self,
        status: ProtocolStatus,
        *,
        container_name: str | None,
        client_count: int | None = None,
    ) -> RuntimeSnapshot:
        return RuntimeSnapshot(
            server_name=self._server.name,
            runtime_type=self._server.runtime.type,
            status=status,
            protocols=(
                ProtocolSnapshot(
                    name="amneziawg",
                    status=status,
                    runtime_type=self._server.runtime.type,
                    capabilities=("detect", "status"),
                    container_name=container_name,
                    interface=self._server.vpn.interface,
                    client_count=client_count,
                ),
            ),
        )


def _count_dump_peers(output: str) -> int:
    lines = [line for line in output.splitlines() if line.strip()]
    if not lines:
        return 0
    return max(0, len(lines) - 1)
```

- [ ] **Step 4: Run runtime tests**

Run:

```powershell
pytest tests/agent/test_runtime.py -v
```

Expected: all runtime tests pass.

- [ ] **Step 5: Commit**

Run:

```powershell
git add app/agent/runtime.py tests/agent/test_runtime.py
git commit -m "Detect Local Agent runtime status"
```

## Task 4: Agent CLI Commands

**Files:**

- Modify: `app/cli.py`
- Create: `tests/agent/test_cli.py`

- [ ] **Step 1: Write CLI tests**

Create `tests/agent/test_cli.py`:

```python
from pathlib import Path

import pytest

from app.agent.auth import hash_agent_token
from app.cli import build_parser, run_agent_server, run_agent_token_hash
from app.config.settings import Settings


TOKEN_HASH = hash_agent_token("raw-agent-token")


def test_cli_accepts_agent_hash_token_argument():
    parser = build_parser()

    args = parser.parse_args(["agent", "hash-token", "--token", "raw-agent-token"])

    assert args.command == "agent"
    assert args.agent_command == "hash-token"
    assert args.token == "raw-agent-token"


def test_cli_accepts_agent_serve_arguments():
    parser = build_parser()

    args = parser.parse_args(["agent", "serve", "--host", "127.0.0.1", "--port", "3041"])

    assert args.command == "agent"
    assert args.agent_command == "serve"
    assert args.host == "127.0.0.1"
    assert args.port == 3041


def test_run_agent_token_hash_outputs_hash_only_value():
    result = run_agent_token_hash("raw-agent-token")

    assert result == TOKEN_HASH
    assert "raw-agent-token" not in result


def test_run_agent_token_hash_rejects_blank_token():
    with pytest.raises(ValueError, match="token cannot be blank"):
        run_agent_token_hash("   ")


def test_run_agent_server_requires_enabled_agent(tmp_path: Path):
    settings = Settings(
        _env_file=None,
        telegram_bot_token="TEST_TOKEN",
        app_secret_key="test-secret",
        database_path=str(tmp_path / "amneziya.sqlite3"),
        local_agent_enabled=False,
    )

    with pytest.raises(ValueError, match="LOCAL_AGENT_ENABLED"):
        run_agent_server(host=None, port=None, settings=settings)


def test_run_agent_server_invokes_uvicorn_with_selected_host_and_port(tmp_path: Path):
    server_config = tmp_path / "servers.yml"
    server_config.write_text(
        """
servers:
  - name: debian-vps-1
    enabled: true
    location: default
    ssh:
      host: 127.0.0.1
      port: 22
      user: root
      auth:
        type: key
    vpn:
      endpoint_host: 127.0.0.1
      port: 30001
      interface: awg0
      network_cidr: 10.8.1.0/24
      server_address: 10.8.1.1/24
      dns: 1.1.1.1
      allowed_ips: 0.0.0.0/0
      max_devices: 254
      server_public_key: server-public-key
    firewall:
      provider: ufw
      open_vpn_port: true
    runtime:
      type: docker
      container_name: amnezia-awg2
      config_path: /opt/amnezia/awg/awg0.conf
""",
        encoding="utf-8",
    )
    settings = Settings(
        _env_file=None,
        telegram_bot_token="TEST_TOKEN",
        app_secret_key="test-secret",
        database_path=str(tmp_path / "amneziya.sqlite3"),
        server_config_path=str(server_config),
        server_name="debian-vps-1",
        local_agent_enabled=True,
        local_agent_host="127.0.0.1",
        local_agent_port=3031,
        local_agent_token_hash=TOKEN_HASH,
    )
    calls = []

    def fake_uvicorn_run(app, *, host: str, port: int) -> None:
        calls.append({"docs_url": app.docs_url, "host": host, "port": port})

    run_agent_server(
        host="127.0.0.2",
        port=3041,
        settings=settings,
        uvicorn_run=fake_uvicorn_run,
    )

    assert calls == [{"docs_url": None, "host": "127.0.0.2", "port": 3041}]
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```powershell
pytest tests/agent/test_cli.py -v
```

Expected: fail because CLI commands and functions do not exist yet.

- [ ] **Step 3: Add parser entries and CLI helpers**

In `app/cli.py`, add imports:

```python
from app.agent.api import create_agent_app
from app.agent.auth import hash_agent_token
from app.agent.config import build_agent_tokens
from app.agent.runtime import LocalCommandRuntimeAdapter
```

In `build_parser()`, after the `server` parser block and before `web`, add:

```python
    agent = sub.add_parser("agent")
    agent_sub = agent.add_subparsers(dest="agent_command", required=True)

    agent_hash_token = agent_sub.add_parser("hash-token")
    agent_hash_token.add_argument(
        "--token",
        default=None,
        help="Optional; omit to enter the token without shell history.",
    )

    agent_serve = agent_sub.add_parser("serve")
    agent_serve.add_argument("--host", default=None)
    agent_serve.add_argument("--port", type=int, default=None)
```

In `main()`, before the web command branches, add:

```python
    elif args.command == "agent" and args.agent_command == "hash-token":
        print(run_agent_token_hash(_read_agent_token(args.token)))
    elif args.command == "agent" and args.agent_command == "serve":
        run_agent_server(host=args.host, port=args.port)
```

Add helper functions near `run_web_server()`:

```python
def run_agent_token_hash(raw_token: str) -> str:
    if not raw_token.strip():
        raise ValueError("token cannot be blank")
    return hash_agent_token(raw_token.strip())


def run_agent_server(
    *,
    host: str | None,
    port: int | None,
    settings: Settings | None = None,
    uvicorn_run: Callable[..., Any] | None = None,
) -> None:
    import uvicorn

    actual_settings = settings or Settings()
    server_config = select_server(
        load_server_config(actual_settings.server_config_path),
        actual_settings.server_name,
    )
    app = create_agent_app(
        adapter=LocalCommandRuntimeAdapter(server_config),
        tokens=build_agent_tokens(actual_settings),
        build_version=__version__,
    )
    runner = uvicorn_run or uvicorn.run
    runner(
        app,
        host=host or actual_settings.local_agent_host,
        port=port or actual_settings.local_agent_port,
    )


def _read_agent_token(token: str | None) -> str:
    if token is not None:
        return token
    first = getpass.getpass("Local Agent token: ")
    second = getpass.getpass("Repeat Local Agent token: ")
    if first != second:
        raise ValueError("tokens do not match")
    return first
```

- [ ] **Step 4: Run CLI tests**

Run:

```powershell
pytest tests/agent/test_cli.py -v
```

Expected: all CLI tests pass.

- [ ] **Step 5: Run focused regression**

Run:

```powershell
pytest tests/agent tests/config/test_settings.py tests/server/test_operation_runner.py tests/server/test_checks.py tests/web/test_cli_web.py -v
```

Expected: all selected tests pass.

- [ ] **Step 6: Commit**

Run:

```powershell
git add app/cli.py tests/agent/test_cli.py
git commit -m "Add Local Agent CLI commands"
```

## Task 5: Production Docs

**Files:**

- Modify: `docs/LOCAL_AGENT.ru.md`
- Modify: `docs/PRODUCTION_VPS_CHECKLIST.ru.md`

- [ ] **Step 1: Update Local Agent docs**

Add this section to `docs/LOCAL_AGENT.ru.md`:

````markdown
## Production wiring

Agent disabled by default:

```text
LOCAL_AGENT_ENABLED=false
```

Минимальный production режим:

```text
LOCAL_AGENT_ENABLED=true
LOCAL_AGENT_HOST=127.0.0.1
LOCAL_AGENT_PORT=3031
LOCAL_AGENT_TOKEN_ID=local-controller
LOCAL_AGENT_TOKEN_OWNER=local-controller
LOCAL_AGENT_TOKEN_SCOPES=agent:health,agent:read,agent:protocols:read
LOCAL_AGENT_TOKEN_EXPIRES_AT=
LOCAL_AGENT_TOKEN_HASH=sha256:<generated-hash>
```

Raw token не хранится в `.env`. Сгенерировать hash:

```powershell
python -m app.cli agent hash-token
```

Запуск:

```powershell
python -m app.cli agent serve
```

Для первого production режима держать `LOCAL_AGENT_HOST=127.0.0.1` и открывать доступ только через SSH tunnel, reverse proxy с auth или будущий controller-side transport. Публично наружу agent не выставлять.
````

- [ ] **Step 2: Update production checklist**

Add this section to `docs/PRODUCTION_VPS_CHECKLIST.ru.md` near the web/admin environment settings:

````markdown
## Local Agent

- По умолчанию `LOCAL_AGENT_ENABLED=false`.
- Включать только после создания hash через `python -m app.cli agent hash-token`.
- В `.env` хранить только `LOCAL_AGENT_TOKEN_HASH`, raw token не сохранять.
- Первый адрес bind: `LOCAL_AGENT_HOST=127.0.0.1`.
- Первый порт: `LOCAL_AGENT_PORT=3031`.
- Первый scope-набор: `agent:health,agent:read,agent:protocols:read`.
- Проверить локально: `python -m app.cli agent serve`.
- Проверить routes только с Bearer token: `/agent/health`, `/agent/version`, `/agent/runtime`, `/agent/protocols`.
- Не добавлять write/config/backup routes без отдельного policy gate.
````

- [ ] **Step 3: Run docs-adjacent tests**

Run:

```powershell
pytest tests/agent tests/config/test_settings.py tests/agent/test_cli.py -v
```

Expected: all tests pass.

- [ ] **Step 4: Commit**

Run:

```powershell
git add docs/LOCAL_AGENT.ru.md docs/PRODUCTION_VPS_CHECKLIST.ru.md
git commit -m "Document Local Agent production wiring"
```

## Task 6: Final Verification and AMN3 Return

**Files:**

- Modify in AMN3: `docs/PROJECT_STATUS_CURRENT.ru.md`
- Modify in AMN3: `research/amn2/transfer-backlog.md`

- [ ] **Step 1: Run full focused verification in `amn2`**

Run:

```powershell
git diff --check
pytest tests/agent tests/config/test_settings.py tests/server/test_operation_runner.py tests/server/test_checks.py tests/web/test_cli_web.py -v
```

Expected:

```text
0 whitespace errors
all selected tests passed
```

- [ ] **Step 2: Push the implementation branch**

Run:

```powershell
git status --short --branch
git push -u origin codex/local-agent-production-wiring
```

If implementation stayed on `codex/local-agent-first-slice`, push that branch instead:

```powershell
git push origin codex/local-agent-first-slice
```

- [ ] **Step 3: Update AMN3 status**

In `C:\Users\SooL\Documents\VPS-OPS-LAB`, update:

```text
docs/PROJECT_STATUS_CURRENT.ru.md
research/amn2/transfer-backlog.md
```

Record:

```text
amn2 branch:
amn2 commits:
tests:
manual PR URL:
remaining risk:
next slice:
```

- [ ] **Step 4: Commit AMN3 return note**

Run in AMN3:

```powershell
git add docs/PROJECT_STATUS_CURRENT.ru.md research/amn2/transfer-backlog.md
git commit -m "Update Local Agent production wiring status"
git push
```

## Non-Goals

- No client create/update/delete routes.
- No config, QR, `vpn://`, backup, import, restore, reboot, Docker mutation, or write operations.
- No public bind by default.
- No raw token storage in `.env`, logs, docs, tests, or AMN3.

## Self-Review

Spec coverage:

- AMN3 remains coordination repo; production code changes happen only in `amn2`.
- Local Agent stays read-only and disabled by default.
- Token provisioning uses hash-only storage.
- Runtime detection is read-only and covered by fake command runner tests.
- AMN3 receives branch/commit/test evidence after implementation.

Placeholder scan:

- No task depends on unfilled details.
- Every code-changing task includes exact files, code blocks, commands, and expected results.

Type consistency:

- `AgentToken` fields match `app.agent.auth.AgentToken`.
- `RuntimeSnapshot` and `ProtocolSnapshot` fields match `app.agent.runtime`.
- CLI helper names are consistently `run_agent_token_hash()` and `run_agent_server()`.
