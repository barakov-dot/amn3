import argparse
from pathlib import Path

from app import __version__
from app.backup.service import BackupService
from app.db.connection import connect
from app.db.repositories import Repository
from app.db.schema import initialize_schema
from app.server.checks import planned_check_commands, run_server_checks
from app.server.peer_apply import (
    PeerApplyInput,
    apply_peer,
    build_peer_apply_dry_run,
    build_peer_revoke_dry_run,
    revoke_peer,
)
from app.server.ssh import SystemSshClient
from app.server_config.loader import load_server_config, select_server
from app.server_config.models import ServerConfig
from app.services.traffic import AwgDumpTrafficCollector, TrafficService


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
    apply_mode = apply_peer.add_mutually_exclusive_group(required=True)
    apply_mode.add_argument("--dry-run", action="store_true")
    apply_mode.add_argument("--apply", action="store_true")

    revoke_peer_parser = server_sub.add_parser("revoke-peer")
    revoke_peer_parser.add_argument("--config", default="servers.yml")
    revoke_peer_parser.add_argument("--server", required=True)
    revoke_peer_parser.add_argument("--public-key", required=True)
    revoke_mode = revoke_peer_parser.add_mutually_exclusive_group(required=True)
    revoke_mode.add_argument("--dry-run", action="store_true")
    revoke_mode.add_argument("--apply", action="store_true")

    collect_traffic = server_sub.add_parser("collect-traffic")
    collect_traffic.add_argument("--config", default="servers.yml")
    collect_traffic.add_argument("--server", required=True)
    collect_traffic.add_argument("--db", default="data/amneziya.sqlite3")
    collect_traffic.add_argument("--dry-run", action="store_true")

    preflight = server_sub.add_parser("preflight")
    preflight.add_argument("--config", default="servers.yml")
    preflight.add_argument("--server", required=True)
    preflight.add_argument("--db", default="data/amneziya.sqlite3")

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
        if args.dry_run:
            print(build_peer_apply_dry_run(server, peer))
        else:
            print(apply_peer(server, peer, ssh_client=SystemSshClient(server)))
    elif args.command == "server" and args.server_command == "revoke-peer":
        config = load_server_config(Path(args.config))
        server = select_server(config, args.server)
        if args.dry_run:
            print(build_peer_revoke_dry_run(server, args.public_key))
        else:
            print(revoke_peer(server, args.public_key, ssh_client=SystemSshClient(server)))
    elif args.command == "server" and args.server_command == "collect-traffic":
        config = load_server_config(Path(args.config))
        server = select_server(config, args.server)
        if args.dry_run:
            print(run_server_traffic_collection_dry_run(server))
        else:
            print(run_server_traffic_collection(server, db_path=Path(args.db)))
    elif args.command == "server" and args.server_command == "preflight":
        print(
            run_server_preflight(
                config_path=Path(args.config),
                server_name=args.server,
                db_path=Path(args.db),
            )
        )


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


def run_server_traffic_collection_dry_run(server: ServerConfig) -> str:
    return "\n".join(
        [
            f"Dry-run traffic collection: {server.name}",
            "No changes will be made.",
            f"Target: ssh {server.ssh.user}@{server.ssh.host} -p {server.ssh.port}",
            f"Read-only command: awg show {server.vpn.interface} dump",
        ]
    )


def run_server_traffic_collection(server: ServerConfig, *, db_path: Path) -> str:
    conn = connect(db_path)
    initialize_schema(conn)
    repo = Repository(conn)
    server_id = repo.upsert_server_config(
        name=server.name,
        host=server.ssh.host,
        ssh_port=server.ssh.port,
        endpoint_host=server.vpn.endpoint_host,
        vpn_port=int(server.vpn.port),
        vpn_network_cidr=server.vpn.network_cidr,
        server_address=server.vpn.server_address,
        server_public_key=server.vpn.server_public_key or "",
        runtime=server.runtime.type,
        firewall=server.firewall.provider,
        max_devices=server.vpn.max_devices,
    )
    report = TrafficService(repo).collect_and_store(
        server_id,
        AwgDumpTrafficCollector(
            interface=server.vpn.interface,
            source=f"awg:{server.name}",
            ssh_client=SystemSshClient(server),
        ),
    )
    return (
        f"Traffic collection stored snapshots: {report.stored_count}\n"
        f"Unknown peers: {len(report.unknown_peers)}"
    )


def run_server_preflight(
    *,
    config_path: Path,
    server_name: str,
    db_path: Path,
) -> str:
    config = load_server_config(config_path)
    server = select_server(config, server_name)
    _validate_preflight_server(server)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = connect(db_path)
    initialize_schema(conn)
    repo = Repository(conn)
    repo.upsert_server_config(
        name=server.name,
        host=server.ssh.host,
        ssh_port=server.ssh.port,
        endpoint_host=server.vpn.endpoint_host,
        vpn_port=int(server.vpn.port),
        vpn_network_cidr=server.vpn.network_cidr,
        server_address=server.vpn.server_address,
        server_public_key=server.vpn.server_public_key or "",
        runtime=server.runtime.type,
        firewall=server.firewall.provider,
        max_devices=server.vpn.max_devices,
    )
    apply_dry_run = build_peer_apply_dry_run(
        server,
        PeerApplyInput(
            public_key="PREFLIGHT_PEER_PUBLIC_KEY",
            preshared_key="PREFLIGHT_PSK",
            vpn_ip=_preflight_peer_ip(server),
        ),
    )
    revoke_dry_run = build_peer_revoke_dry_run(
        server,
        "PREFLIGHT_PEER_PUBLIC_KEY",
    )
    traffic_dry_run = run_server_traffic_collection_dry_run(server)
    return "\n".join(
        [
            f"Preflight report: {server.name}",
            "server config: ok",
            "database sync: ok",
            "server check dry-run: ok",
            _indent(run_server_check(server, dry_run=True)),
            "peer apply dry-run: ok",
            _indent(apply_dry_run),
            "peer revoke dry-run: ok",
            _indent(revoke_dry_run),
            "traffic dry-run: ok",
            _indent(traffic_dry_run),
            "backup target: ok",
            "Next: keep VPS_APPLY_ENABLED=false until live checks pass.",
        ]
    )


def _validate_preflight_server(server: ServerConfig) -> None:
    if server.vpn.port == "auto":
        raise ValueError("server preflight requires a fixed vpn.port before live VPS test")
    if not server.vpn.server_public_key:
        raise ValueError("server preflight requires vpn.server_public_key")


def _preflight_peer_ip(server: ServerConfig) -> str:
    import ipaddress

    network = ipaddress.ip_network(server.vpn.network_cidr, strict=False)
    server_ip = ipaddress.ip_interface(server.vpn.server_address).ip
    for address in network.hosts():
        if address != server_ip:
            return str(address)
    raise ValueError("server network has no free preflight peer IP")


def _indent(value: str) -> str:
    return "\n".join(f"  {line}" for line in value.splitlines())


if __name__ == "__main__":
    main()
