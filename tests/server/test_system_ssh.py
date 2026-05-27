import subprocess

from app.server.ssh import SystemSshClient
from app.server_config.loader import load_server_config, select_server
from tests.server_config.test_loader import VALID_YAML


def test_system_ssh_client_reports_missing_ssh_binary(tmp_path, monkeypatch):
    server = _server(tmp_path)

    def fail_run(*args, **kwargs):
        raise FileNotFoundError("ssh")

    monkeypatch.setattr(subprocess, "run", fail_run)

    result = SystemSshClient(server).run("cat /etc/os-release")

    assert result.exit_code == 127
    assert "ssh executable was not found" in result.stderr


def test_system_ssh_client_reports_timeout(tmp_path, monkeypatch):
    server = _server(tmp_path)

    def fail_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=args[0], timeout=5)

    monkeypatch.setattr(subprocess, "run", fail_run)

    result = SystemSshClient(server, timeout_seconds=5).run("cat /etc/os-release")

    assert result.exit_code == 124
    assert "timed out" in result.stderr


def test_system_ssh_client_reports_password_auth_backend_requirement(tmp_path):
    server = _server(tmp_path, auth_type="password")

    result = SystemSshClient(server).run("cat /etc/os-release")

    assert result.exit_code == 125
    assert "VPS_SSH_PASSWORD" in result.stderr
    assert "non-interactive password SSH backend" in result.stderr


def _server(tmp_path, *, auth_type="key"):
    path = tmp_path / "servers.yml"
    path.write_text(VALID_YAML.replace("type: key", f"type: {auth_type}"), encoding="utf-8")
    return select_server(load_server_config(path), "debian-vps-1")
