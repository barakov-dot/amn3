#!/usr/bin/env python3
"""Create one checksum-bound AWG3.1 client recovery candidate.

The source profile is never modified. Output contains the same profile plus the
four client-only fields from the official Amnezia AWG troubleshooting recipe.
Only hashes and fixed metadata are emitted; key material is never printed.
"""
from __future__ import annotations

import argparse
import base64
import configparser
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import stat
import sys


I1 = (
    "<r 2><b 0x8580000100010000000004796162730679616e6465780272750000010001"
    "c00c000100010000026d000457fa27d1>"
)
RECOVERY_FIELDS = {"Jc": "6", "Jmin": "10", "Jmax": "50", "I1": I1}
INTERFACE_FIELDS = {
    "PrivateKey", "Address", "DNS", "MTU", "S1", "S2", "S3", "S4",
    "H1", "H2", "H3", "H4", "HeaderProtectionKey",
    "ContentPaddingAddition", "RekeyAfterTime", "RekeyTimeout",
    "RejectAfterTime", "KeepaliveTimeout", "MaxHandshakeAttempts",
    "RandomTrailers", "DisableCookies",
}
PEER_FIELDS = {
    "PublicKey", "PresharedKey", "Endpoint", "AllowedIPs",
    "PersistentKeepalive",
}


class RecoveryError(ValueError):
    """A fail-closed, secret-free validation error."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def valid_key(value: str) -> bool:
    try:
        decoded = base64.b64decode(value, validate=True)
    except (ValueError, TypeError):
        return False
    return (
        len(value) == 44
        and len(decoded) == 32
        and any(decoded)
        and base64.b64encode(decoded).decode("ascii") == value
    )


def parse_and_validate(data: bytes, expected_sha256: str) -> tuple[str, str]:
    if not re.fullmatch(r"[0-9a-f]{64}", expected_sha256) or sha256(data) != expected_sha256:
        raise RecoveryError("input_hash_mismatch")
    if not data or len(data) > 16384 or data.startswith(b"\xef\xbb\xbf"):
        raise RecoveryError("input_encoding_invalid")
    try:
        text = data.decode("ascii")
    except UnicodeError:
        raise RecoveryError("input_encoding_invalid") from None
    if not text.endswith("\n") or "\r" in text.replace("\r\n", ""):
        raise RecoveryError("input_newline_invalid")
    if "\r\n" in text and "\n" in text.replace("\r\n", ""):
        raise RecoveryError("input_newline_invalid")
    newline = "\r\n" if "\r\n" in text else "\n"

    parser = configparser.ConfigParser(interpolation=None, strict=True)
    parser.optionxform = str
    try:
        parser.read_string(text)
    except configparser.Error:
        raise RecoveryError("profile_parse_failed") from None
    if parser.defaults() or parser.sections() != ["Interface", "Peer"]:
        raise RecoveryError("profile_shape_invalid")
    interface = parser["Interface"]
    peer = parser["Peer"]
    if set(interface) != INTERFACE_FIELDS or set(peer) != PEER_FIELDS:
        raise RecoveryError("profile_fields_invalid")
    if any(field in interface for field in (*RECOVERY_FIELDS, "I2", "I3", "I4", "I5")):
        raise RecoveryError("recovery_fields_already_present")

    try:
        dns = [ipaddress.IPv4Address(item.strip()) for item in interface["DNS"].split(",")]
    except ipaddress.AddressValueError:
        raise RecoveryError("dns_invalid") from None
    if [str(item) for item in dns] != ["9.9.9.9", "149.112.112.112"]:
        raise RecoveryError("dns_variant_mismatch")
    expected_interface = {
        "Address": "10.212.13.2/32", "MTU": "1280",
        "S1": "12", "S2": "12", "S3": "12", "S4": "12",
        "H1": "1", "H2": "2", "H3": "3", "H4": "4",
        "ContentPaddingAddition": "0", "RekeyAfterTime": "120",
        "RekeyTimeout": "5", "RejectAfterTime": "180",
        "KeepaliveTimeout": "10", "MaxHandshakeAttempts": "18",
        "RandomTrailers": "on", "DisableCookies": "on",
    }
    expected_peer = {
        "Endpoint": "138.124.181.246:30002",
        "AllowedIPs": "0.0.0.0/0, ::/0",
        "PersistentKeepalive": "25",
    }
    if any(interface[key] != value for key, value in expected_interface.items()):
        raise RecoveryError("interface_binding_mismatch")
    if any(peer[key] != value for key, value in expected_peer.items()):
        raise RecoveryError("peer_binding_mismatch")
    if not all(valid_key(interface[key]) for key in ("PrivateKey", "HeaderProtectionKey")):
        raise RecoveryError("interface_key_invalid")
    if not all(valid_key(peer[key]) for key in ("PublicKey", "PresharedKey")):
        raise RecoveryError("peer_key_invalid")
    return text, newline


def render_candidate(text: str, newline: str) -> bytes:
    lines = text.splitlines(keepends=True)
    locations = [index for index, line in enumerate(lines) if line.rstrip("\r\n") == "MTU = 1280"]
    if len(locations) != 1:
        raise RecoveryError("mtu_anchor_invalid")
    insertion = "".join(f"{key} = {value}{newline}" for key, value in RECOVERY_FIELDS.items())
    lines.insert(locations[0] + 1, insertion)
    candidate = "".join(lines).encode("ascii")

    parser = configparser.ConfigParser(interpolation=None, strict=True)
    parser.optionxform = str
    try:
        parser.read_string(candidate.decode("ascii"))
    except configparser.Error:
        raise RecoveryError("candidate_parse_failed") from None
    if {key: parser["Interface"][key] for key in RECOVERY_FIELDS} != RECOVERY_FIELDS:
        raise RecoveryError("candidate_recovery_fields_invalid")
    return candidate


def exclusive_write(path: Path, data: bytes) -> None:
    if not path.parent.is_dir() or path.parent.is_symlink():
        raise RecoveryError("output_parent_invalid")
    descriptor = None
    created = False
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        created = True
        with os.fdopen(descriptor, "wb") as output:
            descriptor = None
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
    except (FileExistsError, OSError):
        if descriptor is not None:
            os.close(descriptor)
        if created:
            try:
                path.unlink()
            except OSError:
                pass
        raise RecoveryError("output_write_failed") from None


def create_candidate(input_path: Path, output_path: Path, expected_sha256: str) -> dict[str, object]:
    try:
        info = input_path.lstat()
    except OSError:
        raise RecoveryError("input_unavailable") from None
    if not stat.S_ISREG(info.st_mode) or input_path.is_symlink():
        raise RecoveryError("input_unavailable")
    try:
        data = input_path.read_bytes()
    except OSError:
        raise RecoveryError("input_unavailable") from None
    text, newline = parse_and_validate(data, expected_sha256)
    candidate = render_candidate(text, newline)
    exclusive_write(output_path, candidate)
    return {
        "changed_keys": sorted(RECOVERY_FIELDS),
        "input_sha256": sha256(data),
        "output_sha256": sha256(candidate),
        "result": "client_recovery_candidate_created",
        "secret_output": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--expected-input-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = create_candidate(args.input, args.output, args.expected_input_sha256)
    except RecoveryError:
        print(json.dumps({"result": "client_recovery_failed", "secret_output": False}, sort_keys=True))
        return 65
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
