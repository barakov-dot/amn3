from app.cli import build_parser
from app.cli import run_server_traffic_collection_dry_run
from app.cli import run_server_check
from app.server_config.loader import load_server_config, select_server
from tests.server_config.test_loader import VALID_YAML


def test_cli_accepts_server_check_arguments():
    parser = build_parser()

    args = parser.parse_args(["server", "check", "--config", "servers.yml", "--server", "debian-vps-1", "--dry-run"])

    assert args.command == "server"
    assert args.server_command == "check"
    assert args.config == "servers.yml"
    assert args.server == "debian-vps-1"
    assert args.dry_run is True


def test_run_server_check_dry_run_prints_read_only_commands(tmp_path):
    path = tmp_path / "servers.yml"
    path.write_text(VALID_YAML, encoding="utf-8")
    config = load_server_config(path)
    server = select_server(config, "debian-vps-1")

    output = run_server_check(server, dry_run=True)

    assert "Dry-run server check" in output
    assert "ssh root@" in output
    assert "cat /etc/os-release" in output
    assert "systemctl is-active awg-quick@awg0" in output
    assert "No changes will be made" in output


def test_cli_accepts_server_apply_peer_dry_run_arguments():
    parser = build_parser()

    args = parser.parse_args(
        [
            "server",
            "apply-peer",
            "--config",
            "servers.yml",
            "--server",
            "debian-vps-1",
            "--public-key",
            "peer-public",
            "--preshared-key",
            "secret-psk",
            "--vpn-ip",
            "10.8.0.2",
            "--dry-run",
        ]
    )

    assert args.command == "server"
    assert args.server_command == "apply-peer"
    assert args.public_key == "peer-public"
    assert args.preshared_key == "secret-psk"
    assert args.vpn_ip == "10.8.0.2"
    assert args.dry_run is True
    assert args.apply is False


def test_cli_accepts_server_apply_peer_apply_arguments():
    parser = build_parser()

    args = parser.parse_args(
        [
            "server",
            "apply-peer",
            "--config",
            "servers.yml",
            "--server",
            "debian-vps-1",
            "--public-key",
            "peer-public",
            "--preshared-key",
            "secret-psk",
            "--vpn-ip",
            "10.8.0.2",
            "--apply",
        ]
    )

    assert args.command == "server"
    assert args.server_command == "apply-peer"
    assert args.apply is True
    assert args.dry_run is False


def test_cli_requires_explicit_apply_or_dry_run_for_server_apply_peer():
    parser = build_parser()

    try:
        parser.parse_args(
            [
                "server",
                "apply-peer",
                "--config",
                "servers.yml",
                "--server",
                "debian-vps-1",
                "--public-key",
                "peer-public",
                "--preshared-key",
                "secret-psk",
                "--vpn-ip",
                "10.8.0.2",
            ]
        )
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("apply-peer must require --apply or --dry-run")


def test_cli_accepts_server_revoke_peer_dry_run_arguments():
    parser = build_parser()

    args = parser.parse_args(
        [
            "server",
            "revoke-peer",
            "--config",
            "servers.yml",
            "--server",
            "debian-vps-1",
            "--public-key",
            "peer-public",
            "--dry-run",
        ]
    )

    assert args.command == "server"
    assert args.server_command == "revoke-peer"
    assert args.public_key == "peer-public"
    assert args.dry_run is True
    assert args.apply is False


def test_cli_accepts_server_revoke_peer_apply_arguments():
    parser = build_parser()

    args = parser.parse_args(
        [
            "server",
            "revoke-peer",
            "--config",
            "servers.yml",
            "--server",
            "debian-vps-1",
            "--public-key",
            "peer-public",
            "--apply",
        ]
    )

    assert args.command == "server"
    assert args.server_command == "revoke-peer"
    assert args.public_key == "peer-public"
    assert args.apply is True
    assert args.dry_run is False


def test_cli_accepts_server_collect_traffic_arguments():
    parser = build_parser()

    args = parser.parse_args(
        [
            "server",
            "collect-traffic",
            "--config",
            "servers.yml",
            "--server",
            "debian-vps-1",
            "--db",
            "data/amneziya.sqlite3",
            "--dry-run",
        ]
    )

    assert args.command == "server"
    assert args.server_command == "collect-traffic"
    assert args.db == "data/amneziya.sqlite3"
    assert args.dry_run is True


def test_run_server_traffic_collection_dry_run_prints_read_only_command(tmp_path):
    path = tmp_path / "servers.yml"
    path.write_text(VALID_YAML, encoding="utf-8")
    config = load_server_config(path)
    server = select_server(config, "debian-vps-1")

    output = run_server_traffic_collection_dry_run(server)

    assert "Dry-run traffic collection" in output
    assert "awg show awg0 dump" in output
    assert "No changes will be made" in output
