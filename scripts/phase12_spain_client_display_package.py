from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
from pathlib import Path
from typing import Any
from zipfile import ZIP_STORED, ZipFile, ZipInfo


INNER_FILENAME = "NEOBYATNAYA.NET.conf"
INNER_MANIFEST = "package-manifest.json"
RECEIPT_SCHEMA = "amn2.phase12-client-display-package-receipt.v1"
PACKAGE_SCHEMA = "amn2.phase12-client-display-package.v1"
SOURCE_RE = re.compile(
    r"^NEOBYATNAYA\.NET-(?P<body>[A-Za-z0-9._-]+)-"
    r"d(?P<device_id>[1-9][0-9]*)\.conf$"
)
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
MAX_CONFIG_BYTES = 1024 * 1024


class PackageError(RuntimeError):
    pass


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8") + b"\n"


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _read_regular(path: Path, *, limit: int) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise PackageError("source config is not a regular file")
    value = path.read_bytes()
    if not value or len(value) > limit:
        raise PackageError("source config size invalid")
    return value


def _load_manifest(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise PackageError("issuance manifest unavailable")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PackageError("issuance manifest malformed") from exc
    if (
        not isinstance(value, dict)
        or set(value) != {"request_id", "server", "items"}
        or not isinstance(value["request_id"], str)
        or not value["request_id"]
        or value["server"] != "spain"
        or not isinstance(value["items"], list)
        or not value["items"]
    ):
        raise PackageError("issuance manifest schema mismatch")
    identities: set[tuple[str, str]] = set()
    for item in value["items"]:
        if (
            not isinstance(item, dict)
            or set(item) != {"recipient_label", "device_label", "platform"}
            or not isinstance(item["recipient_label"], str)
            or not item["recipient_label"]
            or not isinstance(item["device_label"], str)
            or not item["device_label"]
            or not isinstance(item["platform"], str)
        ):
            raise PackageError("issuance item schema mismatch")
        identity = (item["recipient_label"], item["device_label"])
        if identity in identities:
            raise PackageError("duplicate slot identity")
        identities.add(identity)
    return value


def _source_rows(configs_dir: Path) -> list[tuple[Path, re.Match[str]]]:
    if configs_dir.is_symlink() or not configs_dir.is_dir():
        raise PackageError("configs directory unavailable")
    rows: list[tuple[Path, re.Match[str]]] = []
    for path in configs_dir.iterdir():
        if path.name.startswith("."):
            continue
        match = SOURCE_RE.fullmatch(path.name)
        if match is None:
            raise PackageError("unexpected source config")
        if path.is_symlink() or not path.is_file():
            raise PackageError("source config is not a regular file")
        rows.append((path, match))
    rows.sort(key=lambda row: int(row[1].group("device_id")))
    ids = [int(match.group("device_id")) for _path, match in rows]
    if len(ids) != len(set(ids)):
        raise PackageError("duplicate device id")
    return rows


def _zip_info(name: str) -> ZipInfo:
    info = ZipInfo(name, ZIP_TIMESTAMP)
    info.compress_type = ZIP_STORED
    info.create_system = 3
    info.external_attr = (0o100600 << 16)
    return info


def _package_manifest(
    *, request_id: str, item: dict[str, str], source: Path,
    device_slug: str, device_id: int, config: bytes, archive_filename: str,
) -> dict[str, Any]:
    return {
        "schema": PACKAGE_SCHEMA,
        "request_id": request_id,
        "recipient_label": item["recipient_label"],
        "device_label": item["device_label"],
        "device_id": device_id,
        "slot_identity": f'{item["recipient_label"]}/{item["device_label"]}/d{device_id}',
        "source_filename": source.name,
        "inner_filename": INNER_FILENAME,
        "config_sha256": _sha256(config),
        "config_bytes": len(config),
        "archive_filename": archive_filename,
        "device_slug": device_slug,
    }


def build_packages(
    manifest_path: Path, configs_dir: Path, output_dir: Path
) -> dict[str, Any]:
    manifest = _load_manifest(manifest_path)
    rows = _source_rows(configs_dir)
    if len(rows) != len(manifest["items"]):
        raise PackageError("source config count mismatch")
    output_dir.mkdir(parents=False, exist_ok=False)
    receipt_items: list[dict[str, Any]] = []
    archive_names: set[str] = set()
    slot_identities: set[str] = set()
    try:
        for item, (source, match) in zip(manifest["items"], rows, strict=True):
            recipient_prefix = item["recipient_label"] + "-"
            body = match.group("body")
            if not body.startswith(recipient_prefix):
                raise PackageError("recipient source binding mismatch")
            device_id = int(match.group("device_id"))
            device_slug = body[len(recipient_prefix):]
            if not device_slug:
                raise PackageError("device source binding mismatch")
            archive_filename = (
                f'NEOBYATNAYA.NET--{item["recipient_label"]}--{device_slug}--d{device_id}.zip'
            )
            config = _read_regular(source, limit=MAX_CONFIG_BYTES)
            package_manifest = _package_manifest(
                request_id=manifest["request_id"], item=item, source=source,
                device_slug=device_slug, device_id=device_id, config=config,
                archive_filename=archive_filename,
            )
            if archive_filename in archive_names:
                raise PackageError("archive filename collision")
            if package_manifest["slot_identity"] in slot_identities:
                raise PackageError("duplicate slot identity")
            archive_names.add(archive_filename)
            slot_identities.add(package_manifest["slot_identity"])
            archive_path = output_dir / archive_filename
            with ZipFile(archive_path, "x", compression=ZIP_STORED, allowZip64=False) as archive:
                archive.writestr(_zip_info(INNER_FILENAME), config)
                archive.writestr(_zip_info(INNER_MANIFEST), _canonical(package_manifest))
            archive_bytes = archive_path.read_bytes()
            receipt_items.append(
                {
                    **package_manifest,
                    "archive_sha256": _sha256(archive_bytes),
                    "archive_bytes": len(archive_bytes),
                }
            )
        receipt = {
            "schema": RECEIPT_SCHEMA,
            "request_id": manifest["request_id"],
            "server": "spain",
            "display_name": "NEOBYATNAYA.NET",
            "items": receipt_items,
        }
        verify_packages(receipt, configs_dir, output_dir)
        return receipt
    except Exception:
        shutil.rmtree(output_dir)
        raise


def verify_packages(
    receipt: dict[str, Any], configs_dir: Path, output_dir: Path
) -> None:
    if (
        not isinstance(receipt, dict)
        or set(receipt) != {"schema", "request_id", "server", "display_name", "items"}
        or receipt["schema"] != RECEIPT_SCHEMA
        or receipt["server"] != "spain"
        or receipt["display_name"] != "NEOBYATNAYA.NET"
        or not isinstance(receipt["items"], list)
        or not receipt["items"]
    ):
        raise PackageError("receipt schema mismatch")
    expected_archives = {item.get("archive_filename") for item in receipt["items"]}
    if None in expected_archives or len(expected_archives) != len(receipt["items"]):
        raise PackageError("receipt archive collision")
    actual_archives = {path.name for path in output_dir.iterdir() if path.is_file()}
    if actual_archives != expected_archives:
        raise PackageError("output archive set mismatch")
    slots: set[str] = set()
    for item in receipt["items"]:
        required = {
            "schema", "request_id", "recipient_label", "device_label", "device_id",
            "slot_identity", "source_filename", "inner_filename", "config_sha256",
            "config_bytes", "archive_filename", "device_slug", "archive_sha256",
            "archive_bytes",
        }
        if set(item) != required or item["schema"] != PACKAGE_SCHEMA:
            raise PackageError("receipt item schema mismatch")
        if item["inner_filename"] != INNER_FILENAME:
            raise PackageError("inner filename mismatch")
        if item["slot_identity"] in slots:
            raise PackageError("duplicate slot identity")
        slots.add(item["slot_identity"])
        source = configs_dir / item["source_filename"]
        source_bytes = _read_regular(source, limit=MAX_CONFIG_BYTES)
        if _sha256(source_bytes) != item["config_sha256"] or len(source_bytes) != item["config_bytes"]:
            raise PackageError("source config drift")
        archive_path = output_dir / item["archive_filename"]
        archive_bytes = _read_regular(archive_path, limit=MAX_CONFIG_BYTES * 2)
        with ZipFile(archive_path, "r") as archive:
            if archive.namelist() != [INNER_FILENAME, INNER_MANIFEST]:
                raise PackageError("archive member mismatch")
            if _sha256(archive_bytes) != item["archive_sha256"] or len(archive_bytes) != item["archive_bytes"]:
                raise PackageError("archive drift")
            if archive.read(INNER_FILENAME) != source_bytes:
                raise PackageError("inner config drift")
            try:
                embedded = json.loads(archive.read(INNER_MANIFEST).decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise PackageError("package manifest malformed") from exc
            expected_embedded = {
                key: value
                for key, value in item.items()
                if key not in {"archive_sha256", "archive_bytes"}
            }
            if embedded != expected_embedded:
                raise PackageError("package manifest drift")


def _write_create_new(path: Path, value: bytes) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(path)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(value)
        handle.flush()
        os.fsync(handle.fileno())


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="mode", required=True)
    for mode in ("build", "verify"):
        command = subparsers.add_parser(mode)
        command.add_argument("--configs-dir", required=True, type=Path)
        command.add_argument("--output-dir", required=True, type=Path)
        command.add_argument("--receipt", required=True, type=Path)
        if mode == "build":
            command.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args()
    if args.mode == "build":
        receipt = build_packages(args.manifest, args.configs_dir, args.output_dir)
        _write_create_new(args.receipt, _canonical(receipt))
    else:
        receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
        verify_packages(receipt, args.configs_dir, args.output_dir)
    print(json.dumps({"result": "passed", "mode": args.mode}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
