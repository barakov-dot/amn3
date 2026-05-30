import pytest

from app.server.peer_apply import (
    PeerApplyError,
    PeerApplyInput,
    apply_peer,
    build_peer_apply_dry_run,
    build_peer_revoke_dry_run,
    revoke_peer,
)
from app.server.ssh import CommandResult
from app.server_config.loader import load_server_config, select_server
from tests.server_config.test_loader import DOCKER_YAML
from tests.server_config.test_loader import VALID_YAML


def test_build_peer_apply_dry_run_lists_commands_without_secrets(tmp_path):
    server = _server(tmp_path)
    peer = PeerApplyInput(
        public_key="peer-public",
        preshared_key="secret-psk",
        vpn_ip="10.8.0.2",
    )

    report = build_peer_apply_dry_run(server, peer)

    assert "Dry-run peer apply" in report
    assert "awg set awg0 peer peer-public" in report
    assert "allowed-ips 10.8.0.2/32" in report
    assert "systemctl reload awg-quick@awg0" in report
    assert "secret-psk" not in report
    assert "No changes will be made" in report


def test_build_peer_apply_dry_run_marks_docker_runtime_as_pending(tmp_path):
    server = _docker_server(tmp_path)
    peer = PeerApplyInput(
        public_key="peer-public",
        preshared_key="secret-psk",
        vpn_ip="10.8.0.2",
    )

    report = build_peer_apply_dry_run(server, peer)

    assert "Docker peer apply is not implemented yet" in report
    assert "No changes will be made" in report
    assert "systemctl reload" not in report
    assert "secret-psk" not in report


def test_apply_peer_runs_guarded_commands_without_putting_psk_in_command(tmp_path):
    server = _server(tmp_path)
    peer = PeerApplyInput(
        public_key="peer-public",
        preshared_key="secret-psk",
        vpn_ip="10.8.0.2",
    )
    ssh = RecordingSshClient()

    report = apply_peer(server, peer, ssh_client=ssh)

    assert "Peer apply succeeded" in report
    assert len(ssh.calls) == 1
    command, stdin = ssh.calls[0]
    assert "awg set awg0 peer peer-public" in command
    assert "allowed-ips 10.8.0.2/32" in command
    assert "systemctl reload awg-quick@awg0" in command
    assert "secret-psk" not in command
    assert stdin == "secret-psk\n"
    assert "secret-psk" not in report


def test_apply_peer_rejects_docker_runtime_until_persistent_config_is_known(tmp_path):
    server = _docker_server(tmp_path)
    peer = PeerApplyInput(
        public_key="peer-public",
        preshared_key="secret-psk",
        vpn_ip="10.8.0.2",
    )

    with pytest.raises(PeerApplyError, match="Docker peer apply is not implemented"):
        apply_peer(server, peer, ssh_client=RecordingSshClient())


def test_apply_peer_raises_redacted_error_when_remote_command_fails(tmp_path):
    server = _server(tmp_path)
    peer = PeerApplyInput(
        public_key="peer-public",
        preshared_key="secret-psk",
        vpn_ip="10.8.0.2",
    )
    ssh = RecordingSshClient(
        result=CommandResult(
            exit_code=1,
            stdout="",
            stderr="remote failed with secret-psk",
        )
    )

    with pytest.raises(PeerApplyError) as exc_info:
        apply_peer(server, peer, ssh_client=ssh)

    assert "Peer apply failed" in str(exc_info.value)
    assert "secret-psk" not in str(exc_info.value)


def test_build_peer_revoke_dry_run_lists_remove_command(tmp_path):
    server = _server(tmp_path)

    report = build_peer_revoke_dry_run(server, "peer-public")

    assert "Dry-run peer revoke" in report
    assert "awg set awg0 peer peer-public remove" in report
    assert "systemctl reload awg-quick@awg0" in report
    assert "No changes will be made" in report


def test_revoke_peer_runs_guarded_remove_command(tmp_path):
    server = _server(tmp_path)
    ssh = RecordingSshClient()

    report = revoke_peer(server, "peer-public", ssh_client=ssh)

    assert "Peer revoke succeeded" in report
    assert len(ssh.calls) == 1
    command, stdin = ssh.calls[0]
    assert "awg set awg0 peer peer-public remove" in command
    assert "systemctl reload awg-quick@awg0" in command
    assert stdin is None


def _server(tmp_path):
    path = tmp_path / "servers.yml"
    path.write_text(VALID_YAML, encoding="utf-8")
    return select_server(load_server_config(path), "debian-vps-1")


def _docker_server(tmp_path):
    path = tmp_path / "servers.yml"
    path.write_text(DOCKER_YAML, encoding="utf-8")
    return select_server(load_server_config(path), "debian-vps-1")


class RecordingSshClient:
    def __init__(self, *, result=None):
        self.calls = []
        self._result = result or CommandResult(exit_code=0, stdout="ok", stderr="")

    def run(self, command: str, stdin: str | None = None) -> CommandResult:
        self.calls.append((command, stdin))
        return self._result
