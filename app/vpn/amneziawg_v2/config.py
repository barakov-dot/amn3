from dataclasses import dataclass


@dataclass(frozen=True)
class ClientConfigInput:
    private_key: str
    address: str
    dns: str
    server_public_key: str
    preshared_key: str
    endpoint: str
    allowed_ips: str
    persistent_keepalive: int
    jc: int
    jmin: int
    jmax: int
    s1: int
    s2: int
    h1: int
    h2: int
    h3: int
    h4: int


def render_client_config(config: ClientConfigInput) -> str:
    lines = [
        "[Interface]",
        f"PrivateKey = {config.private_key}",
        f"Address = {config.address}",
        f"DNS = {config.dns}",
        f"Jc = {config.jc}",
        f"Jmin = {config.jmin}",
        f"Jmax = {config.jmax}",
        f"S1 = {config.s1}",
        f"S2 = {config.s2}",
        f"H1 = {config.h1}",
        f"H2 = {config.h2}",
        f"H3 = {config.h3}",
        f"H4 = {config.h4}",
        "",
        "[Peer]",
        f"PublicKey = {config.server_public_key}",
        f"PresharedKey = {config.preshared_key}",
        f"Endpoint = {config.endpoint}",
        f"AllowedIPs = {config.allowed_ips}",
        f"PersistentKeepalive = {config.persistent_keepalive}",
    ]
    return "\n".join(lines) + "\n"
