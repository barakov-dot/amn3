from dataclasses import dataclass


@dataclass(frozen=True)
class SshAuthConfig:
    type: str
    private_key_path: str | None = None


@dataclass(frozen=True)
class SshConfig:
    host: str
    port: int
    user: str
    auth: SshAuthConfig


@dataclass(frozen=True)
class VpnConfig:
    endpoint_host: str
    port: int | str
    interface: str
    network_cidr: str
    server_address: str
    dns: str
    allowed_ips: str
    max_devices: int
    server_public_key: str | None = None


@dataclass(frozen=True)
class FirewallConfig:
    provider: str
    open_vpn_port: bool


@dataclass(frozen=True)
class RuntimeConfig:
    type: str
    service_name: str


@dataclass(frozen=True)
class ServerConfig:
    name: str
    enabled: bool
    location: str
    ssh: SshConfig
    vpn: VpnConfig
    firewall: FirewallConfig
    runtime: RuntimeConfig


@dataclass(frozen=True)
class ServersConfig:
    servers: list[ServerConfig]
