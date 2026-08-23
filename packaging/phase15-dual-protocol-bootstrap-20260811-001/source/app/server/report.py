from dataclasses import dataclass, field
from typing import Literal

from app.security.redaction import redact


CheckStatus = Literal["ok", "warning", "error"]


@dataclass(frozen=True)
class CheckResult:
    name: str
    status: CheckStatus
    message: str
    details: str | None = None

    def __post_init__(self) -> None:
        if self.status not in {"ok", "warning", "error"}:
            raise ValueError(f"Unknown check status: {self.status}")


@dataclass(frozen=True)
class ServerCheckReport:
    server_name: str
    results: list[CheckResult] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(result.status == "error" for result in self.results)

    def to_text(self) -> str:
        status = "OK" if self.ok else "FAILED"
        lines = [f"Server check: {redact(self.server_name)}", f"Overall: {status}"]
        for result in self.results:
            lines.append(f"- [{result.status.upper()}] {redact(result.name)}: {redact(result.message)}")
            if result.details:
                lines.append(f"  {redact(result.details)}")
        return "\n".join(lines)
