from app.cli import build_parser


def test_cli_accepts_server_check_arguments():
    parser = build_parser()

    args = parser.parse_args(["server", "check", "--config", "servers.yml", "--server", "debian-vps-1"])

    assert args.command == "server"
    assert args.server_command == "check"
    assert args.config == "servers.yml"
    assert args.server == "debian-vps-1"
