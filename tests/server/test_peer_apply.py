from app.server.peer_apply import PeerApplyInput, build_peer_apply_dry_run
from app.server_config.loader import load_server_config, select_server
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


def _server(tmp_path):
    path = tmp_path / "servers.yml"
    path.write_text(VALID_YAML, encoding="utf-8")
    return select_server(load_server_config(path), "debian-vps-1")
