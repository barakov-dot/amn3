from pathlib import Path
from typing import Any

import yaml

from app.server_config.models import (
    FirewallConfig,
    RuntimeConfig,
    ServerConfig,
    ServersConfig,
    SshAuthConfig,
    SshConfig,
    VpnConfig,
)


class ConfigError(ValueError):
    pass


def load_server_config(path: str | Path) -> ServersConfig:
    config_path = Path(path)
    if not config_path.is_file():
        raise ConfigError(f"Server config not found: {config_path}")
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("servers"), list):
        raise ConfigError("servers.yml must contain a servers list")
    _reject_placeholders(data)
    return ServersConfig(servers=[_parse_server(item) for item in data["servers"]])


def select_server(config: ServersConfig, name: str) -> ServerConfig:
    for server in config.servers:
        if server.name == name:
            return server
    available = ", ".join(server.name for server in config.servers) or "<none>"
    raise ConfigError(f"Server '{name}' not found. Available: {available}")


def _parse_server(item: Any) -> ServerConfig:
    if not isinstance(item, dict):
        raise ConfigError("Each server entry must be an object")
    ssh = _required_dict(item, "ssh")
    auth = _required_dict(ssh, "auth")
    vpn = _required_dict(item, "vpn")
    firewall = _required_dict(item, "firewall")
    runtime = _required_dict(item, "runtime")
    return ServerConfig(
        name=str(_required(item, "name")),
        enabled=bool(_required(item, "enabled")),
        location=str(_required(item, "location")),
        ssh=SshConfig(
            host=str(_required(ssh, "host")),
            port=int(_required(ssh, "port")),
            user=str(_required(ssh, "user")),
            auth=SshAuthConfig(
                type=str(_required(auth, "type")),
                private_key_path=None if auth.get("private_key_path") is None else str(auth["private_key_path"]),
            ),
        ),
        vpn=VpnConfig(
            endpoint_host=str(_required(vpn, "endpoint_host")),
            port=_parse_port(_required(vpn, "port")),
            interface=str(_required(vpn, "interface")),
            network_cidr=str(_required(vpn, "network_cidr")),
            server_address=str(_required(vpn, "server_address")),
            dns=str(_required(vpn, "dns")),
            allowed_ips=str(_required(vpn, "allowed_ips")),
            max_devices=int(_required(vpn, "max_devices")),
        ),
        firewall=FirewallConfig(
            provider=str(_required(firewall, "provider")),
            open_vpn_port=bool(_required(firewall, "open_vpn_port")),
        ),
        runtime=RuntimeConfig(
            type=str(_required(runtime, "type")),
            service_name=str(_required(runtime, "service_name")),
        ),
    )


def _parse_port(value: Any) -> int | str:
    if value == "auto":
        return "auto"
    return int(value)


def _required(data: dict[str, Any], key: str) -> Any:
    if key not in data:
        raise ConfigError(f"Missing required field: {key}")
    return data[key]


def _required_dict(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = _required(data, key)
    if not isinstance(value, dict):
        raise ConfigError(f"Field must be an object: {key}")
    return value


def _reject_placeholders(value: Any) -> None:
    if isinstance(value, dict):
        for child in value.values():
            _reject_placeholders(child)
    elif isinstance(value, list):
        for child in value:
            _reject_placeholders(child)
    elif isinstance(value, str) and value.startswith("CHANGE_ME"):
        raise ConfigError("Server config contains placeholder values")
