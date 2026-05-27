from app.cli import build_parser
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
