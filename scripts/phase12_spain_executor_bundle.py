from __future__ import annotations

import hashlib
import json
import os
import stat
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any


MODULES = (
    "phase12_spain_installer.py",
    "phase12_spain_live_backend.py",
    "phase12_spain_network.py",
    "phase12_spain_forward_compat.py",
    "phase12_spain_package.py",
    "phase12_spain_precondition.py",
)
FIXED_TIMESTAMP = (2026, 7, 21, 0, 0, 0)
MAIN = (
    "from scripts.phase12_spain_installer import main\n"
    "raise SystemExit(main())\n"
).encode("utf-8")


class ExecutorBundleError(RuntimeError):
    pass


def _read_bound_source(path: Path) -> bytes:
    candidate = Path(path)
    if candidate.is_symlink() or not candidate.is_file():
        raise ExecutorBundleError("executor source unavailable")
    try:
        descriptor = os.open(
            candidate,
            os.O_RDONLY
            | getattr(os, "O_NOFOLLOW", 0)
            | getattr(os, "O_BINARY", 0),
        )
        try:
            before = os.fstat(descriptor)
            payload = os.read(descriptor, 16 * 1024 * 1024 + 1)
            after = os.fstat(descriptor)
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise ExecutorBundleError("executor source read failed") from exc
    if (
        not payload
        or len(payload) > 16 * 1024 * 1024
        or not stat.S_ISREG(before.st_mode)
        or (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
        != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
        or b"\x00" in payload
    ):
        raise ExecutorBundleError("executor source changed during read")
    return payload


def _member(name: str, payload: bytes) -> tuple[zipfile.ZipInfo, bytes]:
    info = zipfile.ZipInfo(name, FIXED_TIMESTAMP)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = (0o100644 & 0xFFFF) << 16
    info.flag_bits = 0
    return info, payload


def build_executor_bundle(
    *, workspace_root: Path, output_path: Path
) -> dict[str, Any]:
    root = Path(workspace_root)
    output = Path(output_path)
    scripts = root / "scripts"
    if (
        not root.is_absolute()
        or not output.is_absolute()
        or output.suffix != ".pyz"
        or output.is_symlink()
        or output.parent.is_symlink()
        or not output.parent.is_dir()
    ):
        raise ExecutorBundleError("executor bundle path invalid")
    sources = {
        "__main__.py": MAIN,
        "scripts/__init__.py": b"",
        "scripts/phase12_spain_resource_confirmation_remote.sh": _read_bound_source(
            scripts / "vps" / "phase12_spain_resource_confirmation_remote.sh"
        ),
        "scripts/phase12_spain_run009_preflight_evidence.json": _read_bound_source(
            root
            / "private-artifacts"
            / "phase12-spain-install-package-inputs-20260721"
            / "evidence"
            / "run009-preflight-evidence.json"
        ),
        "scripts/phase12_spain_resource_plan.json": _read_bound_source(
            root / "packaging" / "phase12-spain" / "resource-plan.json"
        ),
        **{
            "scripts/" + name: _read_bound_source(scripts / name)
            for name in MODULES
        },
    }
    temporary: Path | None = None
    descriptor = -1
    try:
        descriptor, raw = tempfile.mkstemp(
            prefix=".phase12-spain-executor-",
            suffix=".pyz",
            dir=output.parent,
        )
        temporary = Path(raw)
        os.close(descriptor)
        descriptor = -1
        with zipfile.ZipFile(
            temporary,
            "w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
            strict_timestamps=True,
        ) as archive:
            for name in sorted(sources):
                info, payload = _member(name, sources[name])
                archive.writestr(info, payload, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        descriptor = os.open(temporary, os.O_RDWR | getattr(os, "O_BINARY", 0))
        try:
            digest = hashlib.sha256()
            size = 0
            while chunk := os.read(descriptor, 1024 * 1024):
                digest.update(chunk)
                size += len(chunk)
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
            descriptor = -1
        if output.exists():
            if output.is_symlink() or output.read_bytes() != temporary.read_bytes():
                raise ExecutorBundleError("executor output collision")
            temporary.unlink()
            temporary = None
        else:
            os.replace(temporary, output)
            temporary = None
        if os.name != "nt":
            os.chmod(output, 0o700)
            parent = os.open(output.parent, os.O_RDONLY)
            try:
                os.fsync(parent)
            finally:
                os.close(parent)
    except (OSError, zipfile.BadZipFile, ExecutorBundleError):
        raise
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if temporary is not None:
            try:
                temporary.unlink()
            except OSError:
                pass
    receipt = {
        "schema": "amn2.spain-bootstrap-executor-bundle.v1",
        "result": "passed",
        "sha256": digest.hexdigest(),
        "size": size,
        "members": [
            {
                "path": name,
                "sha256": hashlib.sha256(sources[name]).hexdigest(),
                "size": len(sources[name]),
            }
            for name in sorted(sources)
        ],
    }
    return receipt


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 2:
        print("executor_bundle_inputs_required", file=sys.stderr)
        return 64
    try:
        receipt = build_executor_bundle(
            workspace_root=Path(args[0]).resolve(),
            output_path=Path(args[1]).resolve(),
        )
    except ExecutorBundleError as exc:
        print(str(exc), file=sys.stderr)
        return 78
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
