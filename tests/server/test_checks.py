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
