from __future__ import annotations

from dataclasses import dataclass
import base64
import hashlib
import hmac


_KEY_TYPE_PREFIXES = ("ssh-", "ecdsa-sha2-", "sk-")


@dataclass(frozen=True)
class SshHostKeyIdentity:
    hosts: tuple[str, ...]
    key_type: str
    key_blob: bytes
    comment: str = ""

    @property
    def fingerprint_sha256(self) -> str:
        digest = hashlib.sha256(self.key_blob).digest()
        encoded = base64.b64encode(digest).decode("ascii").rstrip("=")
        return f"SHA256:{encoded}"

    def safe_metadata(self) -> dict[str, object]:
        return {
            "hosts": list(self.hosts),
            "key_type": self.key_type,
            "fingerprint_sha256": self.fingerprint_sha256,
        }


@dataclass(frozen=True)
class SshHostKeyVerificationResult:
    status: str
    trusted: bool
    key_type: str | None = None
    fingerprint_sha256: str | None = None
    expected_fingerprint_sha256: str | None = None
    host: str | None = None
    host_matched: bool | None = None

    def safe_metadata(self) -> dict[str, object]:
        return {
            "status": self.status,
            "trusted": self.trusted,
            "key_type": self.key_type,
            "fingerprint_sha256": self.fingerprint_sha256,
            "expected_fingerprint_sha256": self.expected_fingerprint_sha256,
            "host": self.host,
            "host_matched": self.host_matched,
        }


def parse_ssh_host_key_line(line: str) -> SshHostKeyIdentity:
    parts = line.strip().split()
    key_index = _find_key_type_index(parts)
    if key_index is None or key_index + 1 >= len(parts):
        raise ValueError("SSH host key line must include key type and base64 key")

    key_blob = _decode_key_blob(parts[key_index + 1])
    hosts = _parse_hosts(parts, key_index)
    comment = " ".join(parts[key_index + 2 :])
    return SshHostKeyIdentity(
        hosts=hosts,
        key_type=parts[key_index],
        key_blob=key_blob,
        comment=comment,
    )


def verify_ssh_host_key_pin(
    line: str,
    *,
    expected_sha256_fingerprint: str,
    expected_host: str | None = None,
) -> SshHostKeyVerificationResult:
    expected = _normalize_sha256_fingerprint(expected_sha256_fingerprint)
    if expected is None:
        return SshHostKeyVerificationResult(
            status="missing-pin",
            trusted=False,
            expected_fingerprint_sha256=None,
            host=expected_host,
        )

    try:
        identity = parse_ssh_host_key_line(line)
    except ValueError:
        return SshHostKeyVerificationResult(
            status="invalid-host-key",
            trusted=False,
            expected_fingerprint_sha256=expected,
            host=expected_host,
        )

    host_matched = _host_matches(expected_host, identity.hosts)
    if not host_matched:
        return _verification_result(
            "host-mismatch",
            False,
            identity,
            expected,
            expected_host,
            host_matched,
        )

    trusted = hmac.compare_digest(identity.fingerprint_sha256, expected)
    return _verification_result(
        "verified" if trusted else "fingerprint-mismatch",
        trusted,
        identity,
        expected,
        expected_host,
        host_matched,
    )


def _find_key_type_index(parts: list[str]) -> int | None:
    for index, part in enumerate(parts):
        if part.startswith(_KEY_TYPE_PREFIXES):
            return index
    return None


def _parse_hosts(parts: list[str], key_index: int) -> tuple[str, ...]:
    if key_index == 0:
        return ()
    host_field = parts[key_index - 1]
    if host_field.startswith("@") and key_index >= 2:
        host_field = parts[key_index - 2]
    return tuple(host for host in host_field.split(",") if host)


def _decode_key_blob(value: str) -> bytes:
    try:
        decoded = base64.b64decode(value.encode("ascii"), validate=True)
    except (UnicodeEncodeError, ValueError) as exc:
        raise ValueError("SSH host key blob must be valid base64") from exc
    if not decoded:
        raise ValueError("SSH host key blob must not be empty")
    return decoded


def _normalize_sha256_fingerprint(value: str) -> str | None:
    stripped = value.strip()
    if not stripped:
        return None
    if stripped.lower().startswith("sha256:"):
        stripped = stripped.split(":", 1)[1]
    if not stripped or ":" in stripped or any(char.isspace() for char in stripped):
        return None
    return f"SHA256:{stripped.rstrip('=')}"


def _host_matches(expected_host: str | None, hosts: tuple[str, ...]) -> bool:
    if expected_host is None or not hosts:
        return True
    return expected_host in hosts


def _verification_result(
    status: str,
    trusted: bool,
    identity: SshHostKeyIdentity,
    expected: str,
    expected_host: str | None,
    host_matched: bool,
) -> SshHostKeyVerificationResult:
    return SshHostKeyVerificationResult(
        status=status,
        trusted=trusted,
        key_type=identity.key_type,
        fingerprint_sha256=identity.fingerprint_sha256,
        expected_fingerprint_sha256=expected,
        host=expected_host,
        host_matched=host_matched,
    )
