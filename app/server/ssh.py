from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class CommandResult:
    exit_code: int
    stdout: str
    stderr: str


class SshClient(Protocol):
    def run(self, command: str) -> CommandResult:
        pass
