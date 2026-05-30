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
        password: str | None = None,
    ) -> None:
        self._server = server
        self._ssh_client = ssh_client or SystemSshClient(server, password=password)

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
    if server.runtime.type == "docker":
        return _build_docker_peer_apply_dry_run(server, peer)

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
    if server.runtime.type == "docker":
        return _build_docker_peer_revoke_dry_run(server, peer_public_key)

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
    if server.runtime.type == "docker":
        return _apply_docker_peer(server, peer, ssh_client=ssh_client)
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
    if server.runtime.type == "docker":
        return _revoke_docker_peer(server, peer_public_key, ssh_client=ssh_client)
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
    service_name = shlex.quote(_require_service_name(server))
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
    service_name = shlex.quote(_require_service_name(server))
    return (
        "set -e; "
        f"awg set {interface} peer {public_key} remove; "
        f"systemctl reload {service_name}"
    )


def _build_docker_peer_apply_dry_run(server: ServerConfig, peer: PeerApplyInput) -> str:
    container = server.runtime.container_name or "<missing-container>"
    config_path = server.runtime.config_path or "<missing-config-path>"
    return "\n".join(
        [
            f"Dry-run peer apply: {redact(server.name)}",
            "No changes will be made.",
            f"Target: ssh {server.ssh.user}@{redact(server.ssh.host)} -p {server.ssh.port}",
            f"Container: {redact(container)}",
            "Peer will be written to persistent config, then the Docker container will be restarted.",
            "Planned commands:",
            f"- docker exec {container} cat {config_path}",
            f"- docker exec -i {container} sh -c 'cat > \"$1\"' sh {config_path}",
            f"- docker restart {container}",
            f"Peer: {redact(peer.public_key)} allowed-ips {redact(peer.vpn_ip)}/32",
        ]
    )


def _build_docker_peer_revoke_dry_run(server: ServerConfig, peer_public_key: str) -> str:
    container = server.runtime.container_name or "<missing-container>"
    config_path = server.runtime.config_path or "<missing-config-path>"
    return "\n".join(
        [
            f"Dry-run peer revoke: {redact(server.name)}",
            "No changes will be made.",
            f"Target: ssh {server.ssh.user}@{redact(server.ssh.host)} -p {server.ssh.port}",
            f"Container: {redact(container)}",
            "Peer will be removed from persistent config, then the Docker container will be restarted.",
            "Planned commands:",
            f"- docker exec {container} cat {config_path}",
            f"- docker exec -i {container} sh -c 'cat > \"$1\"' sh {config_path}",
            f"- docker restart {container}",
            f"Peer: {redact(peer_public_key)}",
        ]
    )


def _require_service_name(server: ServerConfig) -> str:
    if not server.runtime.service_name:
        raise PeerApplyError("host_systemd runtime requires runtime.service_name")
    return server.runtime.service_name


def _apply_docker_peer(
    server: ServerConfig,
    peer: PeerApplyInput,
    *,
    ssh_client: SshClient,
) -> str:
    config_path = _require_docker_config_path(server)
    config_text = _read_docker_config(server, config_path, ssh_client=ssh_client)
    next_config = _upsert_peer_block(config_text, peer)
    _write_docker_config(server, config_path, next_config, ssh_client=ssh_client)
    _restart_docker_container(server, ssh_client=ssh_client)
    return redact(
        f"Peer apply succeeded: {server.name} {peer.public_key} {peer.vpn_ip}/32 "
        f"(Docker container restarted)"
    )


def _revoke_docker_peer(
    server: ServerConfig,
    peer_public_key: str,
    *,
    ssh_client: SshClient,
) -> str:
    config_path = _require_docker_config_path(server)
    config_text = _read_docker_config(server, config_path, ssh_client=ssh_client)
    next_config, _removed = _remove_peer_block(config_text, peer_public_key)
    _write_docker_config(server, config_path, next_config, ssh_client=ssh_client)
    _restart_docker_container(server, ssh_client=ssh_client)
    return redact(
        f"Peer revoke succeeded: {server.name} {peer_public_key} "
        f"(Docker container restarted)"
    )


def _read_docker_config(
    server: ServerConfig,
    config_path: str,
    *,
    ssh_client: SshClient,
) -> str:
    command = f"docker exec {_docker_container(server)} cat {shlex.quote(config_path)}"
    result = ssh_client.run(command)
    if result.exit_code != 0:
        raise PeerApplyError(
            redact(
                "Docker config read failed "
                f"(exit_code={result.exit_code}). "
                f"stdout={_stream_status(result.stdout)} "
                f"stderr={result.stderr!r}"
            )
        )
    return result.stdout


def _write_docker_config(
    server: ServerConfig,
    config_path: str,
    config_text: str,
    *,
    ssh_client: SshClient,
) -> None:
    command = (
        f"docker exec -i {_docker_container(server)} "
        f"sh -c {shlex.quote('cat > \"$1\"')} sh {shlex.quote(config_path)}"
    )
    result = ssh_client.run(command, stdin=_ensure_trailing_newline(config_text))
    if result.exit_code != 0:
        raise PeerApplyError(
            redact(
                "Docker config write failed "
                f"(exit_code={result.exit_code}). "
                f"stdout={_stream_status(result.stdout)} "
                f"stderr={result.stderr!r}"
            )
        )


def _restart_docker_container(server: ServerConfig, *, ssh_client: SshClient) -> None:
    command = f"docker restart {_docker_container(server)}"
    result = ssh_client.run(command)
    if result.exit_code != 0:
        raise PeerApplyError(
            redact(
                "Docker container restart failed "
                f"(exit_code={result.exit_code}). "
                f"stdout={result.stdout!r} stderr={result.stderr!r}"
            )
        )


def _upsert_peer_block(config_text: str, peer: PeerApplyInput) -> str:
    without_peer, _removed = _remove_peer_block(config_text, peer.public_key)
    prefix = without_peer.rstrip()
    if prefix:
        prefix += "\n\n"
    return (
        prefix
        + "[Peer]\n"
        + f"PublicKey = {peer.public_key}\n"
        + f"PresharedKey = {peer.preshared_key}\n"
        + f"AllowedIPs = {peer.vpn_ip}/32\n"
    )


def _remove_peer_block(config_text: str, peer_public_key: str) -> tuple[str, bool]:
    blocks = _split_config_blocks(config_text)
    kept: list[list[str]] = []
    removed = False
    for block in blocks:
        if _is_peer_block(block) and _peer_block_public_key(block) == peer_public_key:
            removed = True
            continue
        kept.append(block)
    return _join_config_blocks(kept), removed


def _split_config_blocks(config_text: str) -> list[list[str]]:
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in config_text.splitlines():
        if line.strip().lower() == "[peer]" and current:
            blocks.append(current)
            current = [line]
            continue
        current.append(line)
    if current:
        blocks.append(current)
    return blocks


def _join_config_blocks(blocks: list[list[str]]) -> str:
    return "\n".join("\n".join(block).rstrip() for block in blocks if block).rstrip() + "\n"


def _is_peer_block(block: list[str]) -> bool:
    return bool(block) and block[0].strip().lower() == "[peer]"


def _peer_block_public_key(block: list[str]) -> str | None:
    for line in block:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        if key.strip().lower() == "publickey":
            return value.strip()
    return None


def _require_docker_config_path(server: ServerConfig) -> str:
    if not server.runtime.config_path:
        raise PeerApplyError(
            "docker runtime requires runtime.config_path for peer apply/revoke"
        )
    return server.runtime.config_path


def _docker_container(server: ServerConfig) -> str:
    if not server.runtime.container_name:
        raise PeerApplyError("docker runtime requires runtime.container_name")
    return shlex.quote(server.runtime.container_name)


def _ensure_trailing_newline(value: str) -> str:
    if value.endswith("\n"):
        return value
    return value + "\n"


def _stream_status(value: str) -> str:
    return "present" if value else "empty"
