import subprocess

from app.server.ssh import SystemSshClient
from app.server.ssh import CommandResult
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


def test_system_ssh_client_reports_missing_password_for_password_auth(tmp_path, monkeypatch):
    server = _server(tmp_path, auth_type="password")
    monkeypatch.delenv("VPS_SSH_PASSWORD", raising=False)
    monkeypatch.chdir(tmp_path)

    result = SystemSshClient(server).run("cat /etc/os-release")

    assert result.exit_code == 125
    assert "VPS_SSH_PASSWORD" in result.stderr
    assert "not set" in result.stderr


def test_system_ssh_client_runs_password_auth_with_sshpass_env(tmp_path, monkeypatch):
    server = _server(tmp_path, auth_type="password")
    monkeypatch.setenv("VPS_SSH_PASSWORD", "secret-password")
    calls = []

    def fake_run(args, **kwargs):
        calls.append((args, kwargs))
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = SystemSshClient(server).run("cat /etc/os-release")

    assert result == CommandResult(exit_code=0, stdout="ok", stderr="")
    args, kwargs = calls[0]
    assert args[:3] == ["sshpass", "-e", "ssh"]
    assert "secret-password" not in args
    assert kwargs["env"]["SSHPASS"] == "secret-password"
    assert "-o" in args
    assert "PreferredAuthentications=password" in args
    assert "BatchMode=yes" not in args


def test_system_ssh_client_reads_password_from_dotenv_for_cli(tmp_path, monkeypatch):
    server = _server(tmp_path, auth_type="password")
    monkeypatch.delenv("VPS_SSH_PASSWORD", raising=False)
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("VPS_SSH_PASSWORD=dotenv-password\n", encoding="utf-8")
    calls = []

    def fake_run(args, **kwargs):
        calls.append((args, kwargs))
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = SystemSshClient(server).run("cat /etc/os-release")

    assert result.exit_code == 0
    assert calls[0][1]["env"]["SSHPASS"] == "dotenv-password"


def test_system_ssh_client_reports_missing_sshpass_binary(tmp_path, monkeypatch):
    server = _server(tmp_path, auth_type="password")
    monkeypatch.setenv("VPS_SSH_PASSWORD", "secret-password")

    def fail_run(*args, **kwargs):
        raise FileNotFoundError("sshpass")

    monkeypatch.setattr(subprocess, "run", fail_run)

    result = SystemSshClient(server).run("cat /etc/os-release")

    assert result.exit_code == 127
    assert "sshpass executable was not found" in result.stderr
    assert "secret-password" not in result.stderr


def _server(tmp_path, *, auth_type="key"):
    path = tmp_path / "servers.yml"
    path.write_text(VALID_YAML.replace("type: key", f"type: {auth_type}"), encoding="utf-8")
    return select_server(load_server_config(path), "debian-vps-1")
