import re

from app.server.report import CheckResult, ServerCheckReport
from app.server.ssh import CommandResult, SshClient
from app.server_config.models import ServerConfig


class CommandPolicyError(ValueError):
    pass


_EXACT_READ_ONLY_COMMANDS = {
    "cat /etc/os-release",
    "command -v systemctl",
    "command -v awg",
    "command -v awg-quick",
    "command -v ufw",
    "ss -lun",
}
_SYSTEMD_ACTIVE_RE = re.compile(r"^systemctl is-active awg-quick@[A-Za-z0-9_.:-]+$")
_SHELL_CONTROL_TOKENS = ("|", "&", ";", ">", "<", "`", "$(", "\n", "\r")
_MUTATING_WORDS = {
    "apt",
    "apt-get",
    "chmod",
    "chown",
    "cp",
    "curl",
    "dd",
    "docker",
    "install",
    "iptables",
    "mkdir",
    "mv",
    "reboot",
    "rm",
    "rsync",
    "scp",
    "sed",
    "service",
    "start",
    "stop",
    "systemctl start",
    "systemctl stop",
    "systemctl enable",
    "tee",
    "ufw",
    "wget",
}

READ_ONLY_CHECK_COMMANDS = (
    "cat /etc/os-release",
    "command -v systemctl",
    "command -v awg",
    "command -v awg-quick",
    "command -v ufw",
    "systemctl is-active awg-quick@{interface}",
    "ss -lun",
)


def planned_check_commands(server: ServerConfig) -> list[str]:
    return [
        command.format(interface=server.vpn.interface)
        for command in READ_ONLY_CHECK_COMMANDS
    ]


def ensure_read_only_command(command: str) -> None:
    normalized = " ".join(command.strip().split())
    if not normalized:
        raise CommandPolicyError("Empty command is not allowed")
    if any(token in command for token in _SHELL_CONTROL_TOKENS):
        raise CommandPolicyError(f"Shell control token is not allowed: {normalized}")
    if normalized in _EXACT_READ_ONLY_COMMANDS or _SYSTEMD_ACTIVE_RE.match(normalized):
        return
    lowered = normalized.lower()
    for word in _MUTATING_WORDS:
        if lowered == word or lowered.startswith(f"{word} "):
            raise CommandPolicyError(f"Mutating command is not allowed: {normalized}")
    raise CommandPolicyError(f"Command is not in the read-only allowlist: {normalized}")


def run_server_checks(server: ServerConfig, ssh: SshClient) -> ServerCheckReport:
    results = [
        _check_debian(_run(ssh, planned_check_commands(server)[0])),
        _check_command("systemd", _run(ssh, planned_check_commands(server)[1]), missing_status="error"),
        _check_command("awg", _run(ssh, planned_check_commands(server)[2]), missing_status="warning"),
        _check_command("awg-quick", _run(ssh, planned_check_commands(server)[3]), missing_status="warning"),
        _check_command("ufw", _run(ssh, planned_check_commands(server)[4]), missing_status="warning"),
        _check_interface(server, _run(ssh, planned_check_commands(server)[5])),
        _check_udp_port(server, _run(ssh, planned_check_commands(server)[6])),
    ]
    return ServerCheckReport(server_name=server.name, results=results)


def _run(ssh: SshClient, command: str) -> CommandResult:
    ensure_read_only_command(command)
    return ssh.run(command)


def _check_debian(result: CommandResult) -> CheckResult:
    if result.exit_code != 0:
        return CheckResult("debian", "error", "Could not read /etc/os-release", result.stderr)
    if "ID=debian" not in result.stdout:
        return CheckResult("debian", "error", "Server OS is not Debian", result.stdout)
    return CheckResult("debian", "ok", "Debian detected", result.stdout)


def _check_command(name: str, result: CommandResult, *, missing_status: str) -> CheckResult:
    if result.exit_code == 0:
        return CheckResult(name, "ok", f"{name} is installed", result.stdout.strip())
    return CheckResult(name, missing_status, f"{name} is not installed", result.stderr or result.stdout)


def _check_interface(server: ServerConfig, result: CommandResult) -> CheckResult:
    service = server.runtime.service_name
    active_text = result.stdout.strip() or result.stderr.strip()
    if result.exit_code == 0 and active_text == "active":
        return CheckResult("interface", "ok", f"{service} is active", active_text)
    return CheckResult("interface", "warning", f"{service} is not active", active_text)


def _check_udp_port(server: ServerConfig, result: CommandResult) -> CheckResult:
    if result.exit_code != 0:
        return CheckResult("udp-port", "warning", "Could not inspect UDP sockets", result.stderr)
    port = str(server.vpn.port)
    if port in result.stdout:
        return CheckResult("udp-port", "ok", f"UDP port {port} is visible", result.stdout)
    return CheckResult("udp-port", "warning", f"UDP port {port} is not visible", result.stdout)
