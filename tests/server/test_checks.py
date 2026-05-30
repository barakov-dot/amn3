from app.server.checks import build_server_check_operation
from app.server.checks import planned_check_commands
from app.server.checks import run_server_checks
from app.server.ssh import CommandResult
from app.server_config.loader import load_server_config, select_server
from tests.server_config.test_loader import DOCKER_YAML
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


def _docker_server(tmp_path):
    path = tmp_path / "servers.yml"
    path.write_text(DOCKER_YAML, encoding="utf-8")
    return select_server(load_server_config(path), "debian-vps-1")


def test_run_server_checks_reports_ready_debian_server(tmp_path):
    server = _server(tmp_path)
    ssh = FakeSshClient(
        {
            "cat /etc/os-release": CommandResult(0, 'ID=debian\nVERSION_ID="12"\n', ""),
            "command -v systemctl": CommandResult(0, "/usr/bin/systemctl\n", ""),
            "command -v awg": CommandResult(0, "/usr/bin/awg\n", ""),
            "command -v awg-quick": CommandResult(0, "/usr/bin/awg-quick\n", ""),
            "command -v ufw": CommandResult(0, "/usr/sbin/ufw\n", ""),
            "systemctl is-active awg-quick@awg0": CommandResult(0, "active\n", ""),
            "ss -lun": CommandResult(0, "udp UNCONN 0 0 0.0.0.0:30001 0.0.0.0:*\n", ""),
        }
    )

    report = run_server_checks(server, ssh)

    assert report.ok is True
    assert all(command in ssh.commands for command in ["cat /etc/os-release", "ss -lun"])


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
    assert (
        "Mutating command" in report.results[0].message
        or "allowlist" in report.results[0].message
    )


def test_run_server_checks_marks_missing_awg_as_warning(tmp_path):
    server = _server(tmp_path)
    ssh = FakeSshClient(
        {
            "cat /etc/os-release": CommandResult(0, "ID=debian\n", ""),
            "command -v systemctl": CommandResult(0, "/usr/bin/systemctl\n", ""),
            "command -v awg": CommandResult(1, "", "not found"),
            "command -v awg-quick": CommandResult(1, "", "not found"),
            "command -v ufw": CommandResult(0, "/usr/sbin/ufw\n", ""),
            "systemctl is-active awg-quick@awg0": CommandResult(3, "inactive\n", ""),
            "ss -lun": CommandResult(0, "", ""),
        }
    )

    report = run_server_checks(server, ssh)

    statuses = {result.name: result.status for result in report.results}
    assert statuses["awg"] == "warning"
    assert statuses["awg-quick"] == "warning"


def test_planned_check_commands_uses_docker_runtime(tmp_path):
    server = _docker_server(tmp_path)

    commands = planned_check_commands(server)

    assert commands == [
        "cat /etc/os-release",
        "command -v docker",
        "docker ps --format {{.Names}}",
        "docker exec amnezia-awg command -v awg",
        "docker exec amnezia-awg awg show awg0",
        "ss -lun",
    ]


def test_build_server_check_operation_describes_host_health_check(tmp_path):
    server = _server(tmp_path)

    operation = build_server_check_operation(
        server,
        actor_id="web-admin",
        actor_auth_method="session",
    )

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

    operation = build_server_check_operation(
        server,
        actor_id="cli",
        actor_auth_method="cli",
    )

    assert operation.id == "server.health.check"
    assert "docker exec amnezia-awg command -v awg" in [
        step.command for step in operation.steps
    ]
    assert operation.inputs == {
        "server_name": "debian-vps-1",
        "runtime": "docker",
    }


def test_run_server_checks_reports_ready_docker_amnezia_node(tmp_path):
    server = _docker_server(tmp_path)
    ssh = FakeSshClient(
        {
            "cat /etc/os-release": CommandResult(0, 'ID=debian\nVERSION_ID="12"\n', ""),
            "command -v docker": CommandResult(0, "/usr/bin/docker\n", ""),
            "docker ps --format {{.Names}}": CommandResult(0, "amnezia-awg\n", ""),
            "docker exec amnezia-awg command -v awg": CommandResult(0, "/usr/bin/awg\n", ""),
            "docker exec amnezia-awg awg show awg0": CommandResult(0, "interface: awg0\n", ""),
            "ss -lun": CommandResult(0, "udp UNCONN 0 0 0.0.0.0:30001 0.0.0.0:*\n", ""),
        }
    )

    report = run_server_checks(server, ssh)

    statuses = {result.name: result.status for result in report.results}
    assert report.ok is True
    assert statuses["docker"] == "ok"
    assert statuses["container"] == "ok"
    assert statuses["awg"] == "ok"
    assert statuses["interface"] == "ok"


def test_run_server_checks_marks_missing_docker_container_as_error(tmp_path):
    server = _docker_server(tmp_path)
    ssh = FakeSshClient(
        {
            "cat /etc/os-release": CommandResult(0, "ID=debian\n", ""),
            "command -v docker": CommandResult(0, "/usr/bin/docker\n", ""),
            "docker ps --format {{.Names}}": CommandResult(0, "other-container\n", ""),
            "docker exec amnezia-awg command -v awg": CommandResult(1, "", "container not found"),
            "docker exec amnezia-awg awg show awg0": CommandResult(1, "", "container not found"),
            "ss -lun": CommandResult(0, "", ""),
        }
    )

    report = run_server_checks(server, ssh)

    statuses = {result.name: result.status for result in report.results}
    assert report.ok is False
    assert statuses["container"] == "error"
