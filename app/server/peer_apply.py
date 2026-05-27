from dataclasses import dataclass
import shlex

from app.security.redaction import redact
from app.server.ssh import SshClient, SystemSshClient
from app.server_config.models import ServerConfig


@dataclass(frozen=True)
class PeerApplyInput:
    public_key: str
    preshared_key: str
    vpn_ip: str


class PeerApplyError(RuntimeError):
    pass


class ServerConfigPeerApplier:
    def __init__(
        self,
        server: ServerConfig,
        *,
        ssh_client: SshClient | None = None,
    ) -> None:
        self._server = server
        self._ssh_client = ssh_client or SystemSshClient(server)

    def apply_peer(
        self,
        *,
        server,
        peer_public_key: str,
        preshared_key: str,
        vpn_ip: str,
    ) -> None:
        apply_peer(
            self._server,
            PeerApplyInput(
                public_key=peer_public_key,
                preshared_key=preshared_key,
                vpn_ip=vpn_ip,
            ),
            ssh_client=self._ssh_client,
        )

    def remove_peer(self, *, server, peer_public_key: str) -> None:
        revoke_peer(self._server, peer_public_key, ssh_client=self._ssh_client)


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


def build_peer_revoke_dry_run(server: ServerConfig, peer_public_key: str) -> str:
    commands = [
        (
            f"awg set {server.vpn.interface} "
            f"peer {peer_public_key} "
            "remove"
        ),
        f"systemctl reload {server.runtime.service_name}",
    ]
    lines = [
        f"Dry-run peer revoke: {redact(server.name)}",
        "No changes will be made.",
        f"Target: ssh {server.ssh.user}@{redact(server.ssh.host)} -p {server.ssh.port}",
        "Planned commands:",
    ]
    lines.extend(f"- {redact(command)}" for command in commands)
    return "\n".join(lines)


def apply_peer(server: ServerConfig, peer: PeerApplyInput, *, ssh_client: SshClient) -> str:
    command = _build_apply_command(server, peer)
    result = ssh_client.run(command, stdin=f"{peer.preshared_key}\n")
    if result.exit_code != 0:
        stdout = result.stdout.replace(peer.preshared_key, "[REDACTED]")
        stderr = result.stderr.replace(peer.preshared_key, "[REDACTED]")
        raise PeerApplyError(
            redact(
                "Peer apply failed "
                f"(exit_code={result.exit_code}). "
                f"stdout={stdout!r} stderr={stderr!r}"
            )
        )
    return redact(f"Peer apply succeeded: {server.name} {peer.public_key} {peer.vpn_ip}/32")


def revoke_peer(
    server: ServerConfig,
    peer_public_key: str,
    *,
    ssh_client: SshClient,
) -> str:
    command = _build_revoke_command(server, peer_public_key)
    result = ssh_client.run(command)
    if result.exit_code != 0:
        raise PeerApplyError(
            redact(
                "Peer revoke failed "
                f"(exit_code={result.exit_code}). "
                f"stdout={result.stdout!r} stderr={result.stderr!r}"
            )
        )
    return redact(f"Peer revoke succeeded: {server.name} {peer_public_key}")


def _build_apply_command(server: ServerConfig, peer: PeerApplyInput) -> str:
    interface = shlex.quote(server.vpn.interface)
    public_key = shlex.quote(peer.public_key)
    allowed_ips = shlex.quote(f"{peer.vpn_ip}/32")
    service_name = shlex.quote(server.runtime.service_name)
    return (
        "set -e; "
        'psk_file="$(mktemp)"; '
        'trap \'rm -f "$psk_file"\' EXIT; '
        'chmod 600 "$psk_file"; '
        'cat > "$psk_file"; '
        f"awg set {interface} peer {public_key} "
        'preshared-key "$psk_file" '
        f"allowed-ips {allowed_ips}; "
        f"systemctl reload {service_name}"
    )


def _build_revoke_command(server: ServerConfig, peer_public_key: str) -> str:
    interface = shlex.quote(server.vpn.interface)
    public_key = shlex.quote(peer_public_key)
    service_name = shlex.quote(server.runtime.service_name)
    return (
        "set -e; "
        f"awg set {interface} peer {public_key} remove; "
        f"systemctl reload {service_name}"
    )
