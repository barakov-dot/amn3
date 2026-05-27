from dataclasses import dataclass
import subprocess
from typing import Protocol

from app.server_config.models import ServerConfig


@dataclass(frozen=True)
class CommandResult:
    exit_code: int
    stdout: str
    stderr: str


class SshClient(Protocol):
    def run(self, command: str) -> CommandResult:
        pass


class SystemSshClient:
    def __init__(self, server: ServerConfig, *, timeout_seconds: int = 20) -> None:
        self._server = server
        self._timeout_seconds = timeout_seconds

    def run(self, command: str) -> CommandResult:
        if self._server.ssh.auth.type == "password":
            return CommandResult(
                exit_code=125,
                stdout="",
                stderr=(
                    "Password auth is configured. Store the password in "
                    "VPS_SSH_PASSWORD, but a non-interactive password SSH backend "
                    "is not enabled yet. Use SSH key auth for live checks or add "
                    "a password backend before running this check."
                ),
            )
        args = [
            "ssh",
            "-p",
            str(self._server.ssh.port),
            "-o",
            "BatchMode=yes",
            "-o",
            f"ConnectTimeout={self._timeout_seconds}",
        ]
        if self._server.ssh.auth.private_key_path:
            args.extend(["-i", self._server.ssh.auth.private_key_path])
        args.extend([f"{self._server.ssh.user}@{self._server.ssh.host}", command])
        try:
            completed = subprocess.run(
                args,
                capture_output=True,
                check=False,
                text=True,
                timeout=self._timeout_seconds,
            )
        except FileNotFoundError:
            return CommandResult(
                exit_code=127,
                stdout="",
                stderr="ssh executable was not found in PATH",
            )
        except subprocess.TimeoutExpired:
            return CommandResult(
                exit_code=124,
                stdout="",
                stderr=f"ssh command timed out after {self._timeout_seconds} seconds",
            )
        return CommandResult(
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
