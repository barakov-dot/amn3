import argparse
from pathlib import Path

from app import __version__
from app.backup.service import BackupService
from app.server_config.loader import load_server_config, select_server


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
        select_server(config, args.server)
        parser.error("server check parser is ready, but real SSH backend is not configured yet")


if __name__ == "__main__":
    main()
