from dataclasses import dataclass

from app.security.redaction import redact
from app.server_config.models import ServerConfig


@dataclass(frozen=True)
class PeerApplyInput:
    public_key: str
    preshared_key: str
    vpn_ip: str


def build_peer_apply_dry_run(server: ServerConfig, peer: PeerApplyInput) -> str:
    commands = [
        (
            f"awg set {server.vpn.interface} "
            f"peer {peer.public_key} "
            "preshared-key <redacted-psk-file> "
            f"allowed-ips {peer.vpn_ip}/32"
        ),
        f"systemctl reload {server.runtime.service_name}",
    ]
    lines = [
        f"Dry-run peer apply: {redact(server.name)}",
        "No changes will be made.",
        f"Target: ssh {server.ssh.user}@{redact(server.ssh.host)} -p {server.ssh.port}",
        "Planned commands:",
    ]
    lines.extend(f"- {redact(command)}" for command in commands)
    return "\n".join(lines)
