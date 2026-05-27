import asyncio
from pathlib import Path

from aiogram import Bot

from app.bot import create_dispatcher
from app.bot.workflows import BotWorkflow
from app.config import Settings
from app.db.connection import connect
from app.db.repositories import Repository
from app.db.schema import initialize_schema
from app.security.crypto import SecretBox
from app.server.peer_apply import ServerConfigPeerApplier
from app.server_config.loader import load_server_config, select_server
from app.server_config.models import ServerConfig
from app.services.access import AccessService


async def run() -> None:
    settings = Settings()
    workflow = create_workflow(
        database_path=settings.database_path,
        app_secret_key=settings.app_secret_key,
        admin_telegram_ids=set(settings.admin_ids),
        default_vpn_network_cidr=settings.default_vpn_network_cidr,
        max_devices_per_user=settings.max_devices_per_user,
        default_plan_days=settings.default_plan_days,
        vps_apply_enabled=settings.vps_apply_enabled,
        server_config_path=settings.server_config_path,
        server_name=settings.server_name,
    )
    bot = Bot(token=settings.telegram_bot_token)
    dispatcher = create_dispatcher(workflow=workflow)
    await dispatcher.start_polling(bot)


def create_workflow(
    *,
    database_path: str | Path,
    app_secret_key: str,
    admin_telegram_ids: set[int],
    default_vpn_network_cidr: str,
    max_devices_per_user: int,
    default_plan_days: int,
    vps_apply_enabled: bool = False,
    server_config_path: str | Path = "servers.yml",
    server_name: str = "debian-vps-1",
) -> BotWorkflow:
    conn = connect(database_path)
    initialize_schema(conn)
    repo = Repository(conn)
    repo.seed_default_plans()
    peer_applier = None
    if vps_apply_enabled:
        server_config = select_server(load_server_config(server_config_path), server_name)
        default_server_id = _sync_server_config(repo, server_config)
        peer_applier = ServerConfigPeerApplier(server_config)
    else:
        default_server_id = repo.ensure_default_server(
            name="local",
            network_cidr=default_vpn_network_cidr,
        )

    access_service = AccessService(
        repo=repo,
        secret_box=SecretBox.from_app_secret(app_secret_key),
        max_devices_per_user=max_devices_per_user,
        duration_days=default_plan_days,
        peer_applier=peer_applier,
    )
    secret_box = SecretBox.from_app_secret(app_secret_key)
    workflow = BotWorkflow(
        repo=repo,
        admin_telegram_ids=admin_telegram_ids,
        access_service=access_service,
        default_server_id=default_server_id,
        secret_box=secret_box,
        peer_remover=peer_applier,
    )
    return workflow


def _sync_server_config(repo: Repository, server: ServerConfig) -> int:
    if server.vpn.port == "auto":
        raise ValueError("VPS_APPLY_ENABLED requires a fixed vpn.port")
    if not server.vpn.server_public_key:
        raise ValueError("VPS_APPLY_ENABLED requires vpn.server_public_key in servers.yml")
    return repo.upsert_server_config(
        name=server.name,
        host=server.ssh.host,
        ssh_port=server.ssh.port,
        endpoint_host=server.vpn.endpoint_host,
        vpn_port=int(server.vpn.port),
        vpn_network_cidr=server.vpn.network_cidr,
        server_address=server.vpn.server_address,
        server_public_key=server.vpn.server_public_key,
        runtime=server.runtime.type,
        firewall=server.firewall.provider,
        max_devices=server.vpn.max_devices,
    )


if __name__ == "__main__":
    asyncio.run(run())
