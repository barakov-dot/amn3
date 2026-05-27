import argparse
from pathlib import Path

from app import __version__
from app.backup.service import BackupService
from app.server.checks import planned_check_commands, run_server_checks
from app.server.peer_apply import PeerApplyInput, build_peer_apply_dry_run
from app.server.ssh import SystemSshClient
from app.server_config.loader import load_server_config, select_server
from app.server_config.models import ServerConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="amneziya")
    sub = parser.add_subparsers(dest="command", required=True)

    backup = sub.add_parser("backup")
    backup_sub = backup.add_subparsers(dest="backup_command", required=True)

    create = backup_sub.add_parser("create")
    create.add_argument("--db", default="data/amneziya.sqlite3")
    create.add_argument("--output", default="backups")

    verify = backup_sub.add_parser("verify")
    verify.add_argument("--file", required=True)

    restore = backup_sub.add_parser("restore")
    restore.add_argument("--file", required=True)
    restore.add_argument("--target-db", required=True)
    restore.add_argument("--force", action="store_true")

    server = sub.add_parser("server")
    server_sub = server.add_subparsers(dest="server_command", required=True)

    check = server_sub.add_parser("check")
    check.add_argument("--config", default="servers.yml")
    check.add_argument("--server", required=True)
    check.add_argument("--dry-run", action="store_true")

    apply_peer = server_sub.add_parser("apply-peer")
    apply_peer.add_argument("--config", default="servers.yml")
    apply_peer.add_argument("--server", required=True)
    apply_peer.add_argument("--public-key", required=True)
    apply_peer.add_argument("--preshared-key", required=True)
    apply_peer.add_argument("--vpn-ip", required=True)
    apply_peer.add_argument("--dry-run", action="store_true", required=True)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    service = BackupService(app_version=__version__)

    if args.command == "backup" and args.backup_command == "create":
        print(service.create(Path(args.db), Path(args.output)))
    elif args.command == "backup" and args.backup_command == "verify":
        print(service.verify(Path(args.file)))
    elif args.command == "backup" and args.backup_command == "restore":
        print(service.restore(Path(args.file), Path(args.target_db), force=args.force))
    elif args.command == "server" and args.server_command == "check":
        config = load_server_config(Path(args.config))
        server = select_server(config, args.server)
        print(run_server_check(server, dry_run=args.dry_run))
    elif args.command == "server" and args.server_command == "apply-peer":
        config = load_server_config(Path(args.config))
        server = select_server(config, args.server)
        peer = PeerApplyInput(
            public_key=args.public_key,
            preshared_key=args.preshared_key,
            vpn_ip=args.vpn_ip,
        )
        print(build_peer_apply_dry_run(server, peer))


def run_server_check(server: ServerConfig, *, dry_run: bool) -> str:
    if dry_run:
        lines = [
            f"Dry-run server check: {server.name}",
            "No changes will be made.",
            f"Target: ssh {server.ssh.user}@{server.ssh.host} -p {server.ssh.port}",
            "Read-only commands:",
        ]
        lines.extend(f"- {command}" for command in planned_check_commands(server))
        return "\n".join(lines)

    report = run_server_checks(server, SystemSshClient(server))
    return report.to_text()


if __name__ == "__main__":
    main()
