from __future__ import annotations

import argparse
import ast
import base64
import binascii
import hashlib
from html.parser import HTMLParser
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import tarfile
import tempfile
from typing import NamedTuple


class PackageContractError(ValueError):
    pass


class PackageReceipt(NamedTuple):
    root: Path
    manifest_path: Path
    package_identity_sha256: str
    file_count: int


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ID = "phase16-awg3-family-3-1-spain-pilot-20260824-005"
SOURCE_BRANCH = "codex/phase16-awg3-family-3-1-spain-pilot"
TOOLING_BRANCH = "codex/phase16-awg3-family-3-1-spain-pilot-005"
MANIFEST_SCHEMA = "amn2.phase16.package-manifest.v1"
PHASE14_RECEIPT_PATH = "research/amn2/phase14-dual-protocol-application-readiness-receipt.md"
PHASE14_RECEIPT_COMMIT = "4e1052c079e1e25031a6c80f4dae1763e457ca48"
PHASE14_RECEIPT_SHA256 = "d33e69b53c7397c567b16c4f1caea12af97969d9436d3e95e6038148054aa982"
PHASE16_SOURCE_RECEIPT_PATH = "research/amn2/phase16-source-readiness-receipt.md"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
HEAD_RE = re.compile(r"^[0-9a-f]{40}$")

RESOURCE_PLAN = {
    "controls": {
        "awg2_untouched": True,
        "general_issuance_enabled": False,
        "rollback_required": True,
        "stage_requires_separate_claim": True,
    },
    "package_id": PACKAGE_ID,
    "pilot_client": {
        "application": "amneziawg",
        "artifact_identity": (
            "github:amnezia-vpn/amneziawg-android/releases/v3.1.20260814/"
            "AmneziaWG-3.1.202060814.apk@"
            "sha256:74f109a948f012e8b90b4055e98bb9bee77bbb8e5d0fe7d5a057dd9698009697"
        ),
        "build": "12",
        "platform": "android",
        "release_kind": "stable",
        "version": "v3.1.20260814",
    },
    "protocol": {
        "config_revision": "amneziawg_v3_1",
        "family": "awg3",
        "revision": "3.1",
    },
    "resources": {
        "bridge": "amn2sp3br0",
        "config_path": "/var/lib/amn2-spain/awg3/awg3.conf",
        "container": "amn2-spain-awg3",
        "container_cidr": "172.29.252.0/28",
        "interface": "awg3",
        "server_address": "10.212.13.1/24",
        "service": "amn2-spain-awg3.service",
        "state_root": "/var/lib/amn2-spain/awg3",
        "udp_port": 30002,
        "vpn_cidr": "10.212.13.0/24",
    },
    "runtime": {
        "artifact_identity": (
            "docker.io/amneziavpn/amneziawg-go@"
            "sha256:4e1fd2840f8d26eb6ec8bc1598e66f2f17f5d0201cd2baadbde560c104d4fc9d"
        ),
        "capabilities": ["disable_cookies", "random_trailers"],
        "source_commit": "1f50ad736ecca22a9bfc7b4606805ec9ca49fe48",
    },
    "schema": "amn2.phase16.resource-plan.v1",
}

SOURCE_ARCHIVE_PATHS = (
    "README.md",
    "app",
    "requirements/phase15-runtime-py312.lock",
    "requirements/phase15-test-py312.lock",
    "scripts/phase15_dependency_lock.py",
)
REQUIRED_SOURCE_SPECS = {
    "README.md": ("operator_documentation", "OPERATOR", "operator"),
    "app/main.py": ("application_snapshot", "APPLICATION_STAGE", "application"),
    "app/db/phase15_bootstrap.py": ("callback_bootstrap", "APPLICATION_STAGE", "application"),
    "app/services/phase15_bootstrap.py": ("callback_bootstrap", "APPLICATION_STAGE", "application"),
    "app/services/telegram_callback_state.py": ("callback_bootstrap", "APPLICATION_STAGE", "application"),
    "requirements/phase15-runtime-py312.lock": ("runtime_dependency_lock", "LOCAL_VERIFY", "application"),
    "requirements/phase15-test-py312.lock": ("test_dependency_lock", "LOCAL_VERIFY", "application"),
    "scripts/phase15_dependency_lock.py": ("dependency_lock_tool", "LOCAL_VERIFY", "application"),
}
REQUIRED_SOURCE_PATHS = set(REQUIRED_SOURCE_SPECS)
TOOLING_SPECS = {
    "docs/superpowers/plans/2026-08-24-amn2-phase16-awg3-family-3-1-spain-pilot.md": ("operator_documentation", "OPERATOR", "operator"),
    "docs/superpowers/specs/2026-08-24-amn2-phase16-awg3-family-3-1-spain-pilot-design.ru.md": ("operator_documentation", "OPERATOR", "operator"),
    "packaging/phase16-awg3-family-3-1-spain-pilot-contract/failure-outcome.schema.json": ("failure_schema", "LOCAL_VERIFY", "preflight"),
    "packaging/phase16-awg3-family-3-1-spain-pilot-contract/package-manifest.schema.json": ("contract_schema", "LOCAL_VERIFY", "none"),
    "packaging/phase16-awg3-family-3-1-spain-pilot-contract/preflight-evidence.schema.json": ("preflight_evidence_schema", "LOCAL_VERIFY", "preflight"),
    "packaging/phase16-awg3-family-3-1-spain-pilot-contract/resource-plan.json": ("resource_plan", "LOCAL_VERIFY", "awg3-runtime"),
    PHASE16_SOURCE_RECEIPT_PATH: ("phase16_source_receipt", "LOCAL_VERIFY", "operator"),
    "scripts/phase16_awg31_package.py": ("package_verifier", "LOCAL_VERIFY", "none"),
    "scripts/phase16_preflight_contract.py": ("preflight_contract", "PREFLIGHT", "preflight"),
    "scripts/vps/phase16_application_stage_remote.sh": ("stage_envelope", "APPLICATION_STAGE", "application"),
    "scripts/vps/phase16_awg31_runtime_stage_remote.sh": ("stage_envelope", "AWG31_RUNTIME_STAGE", "awg3-runtime"),
    "scripts/vps/phase16_spain_readonly_preflight_remote.sh": ("readonly_collector", "PREFLIGHT", "preflight"),
    "scripts/vps/phase16_spain_readonly_preflight_ssh_runner.ps1": ("readonly_collector", "PREFLIGHT", "preflight"),
}
REQUIRED_ENTRY_SPECS = {
    **{"source/" + path: spec for path, spec in REQUIRED_SOURCE_SPECS.items()},
    **{"tooling/" + path: spec for path, spec in TOOLING_SPECS.items()},
    "tooling/" + PHASE14_RECEIPT_PATH: ("phase14_receipt", "LOCAL_VERIFY", "operator"),
}
EXPECTED_LOCK_PATHS = {
    "runtime": "source/requirements/phase15-runtime-py312.lock",
    "test": "source/requirements/phase15-test-py312.lock",
}
APPROVED_BRAND_PNGS = {
    "app/bot/assets/NEOBYATNAYA-AMNZ-BOT.png": (
        2_950_469,
        "40acd9465dc9fda06644d2d829da996e1d9bf6c856e95298b624b31154fec791",
    ),
    "app/bot/assets/NEOBYATNAYA-AMNZ-LANGUAGE-HEADER.png": (
        2_647_131,
        "bbddfa72d1d1fc37e412d2f4a9b4124001ff91fbd641635e31a47e008fc4611f",
    ),
    "app/web/static/brand-full.png": (
        2_950_469,
        "40acd9465dc9fda06644d2d829da996e1d9bf6c856e95298b624b31154fec791",
    ),
}
FORBIDDEN_SOURCE_COMPONENTS = {
    ".cache", "__pycache__", "cache", "caches", "peer", "peers", "secret", "secrets",
}
FORBIDDEN_SOURCE_SUFFIXES = {".conf", ".config", ".db", ".ini", ".key", ".pem", ".p12", ".pfx", ".sqlite", ".sqlite3", ".toml", ".yaml", ".yml", ".json"}
PRIVATE_MATERIAL_PATTERNS = (
    re.compile(rb"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----"),
    re.compile(rb"(?im)^\s*(?:PrivateKey|PresharedKey)\s*=\s*[A-Za-z0-9+/]{42,44}={0,2}\s*$"),
    re.compile(rb"\b[0-9]{6,12}:[A-Za-z0-9_-]{30,}\b"),
    re.compile(rb"(?i)\bBearer[ \t]+(?=[^\s'\"<>{}])"),
)
APPROVED_TEMPLATE_PLACEHOLDERS = {
    b"{{ issued_raw_token }}",
    b"{{ csrf_token }}",
    b"{{ revealed_secrets.private_key }}",
    b"{{ revealed_secrets.preshared_key }}",
}
APPROVED_TEMPLATE_PLACEHOLDER_TEXT = {
    placeholder.decode("ascii") for placeholder in APPROVED_TEMPLATE_PLACEHOLDERS
}
JWT_CANDIDATE_RE = re.compile(
    rb"(?<![A-Za-z0-9_-])([A-Za-z0-9_-]+)\."
    rb"([A-Za-z0-9_-]+)\.([A-Za-z0-9_-]+)(?![A-Za-z0-9_-])"
)
JINJA_EXPRESSION_RE = re.compile(r"\{\{[^{}]*\}\}")
TEXT_ASSIGNMENT_RE = re.compile(
    r"(?m)^\s*(?P<target>[A-Za-z_][A-Za-z0-9_.-]*)"
    r"(?:\s*:\s*[^=\r\n]+)?\s*=\s*(?P<value>[^\r\n]+?)\s*$"
)
JINJA_SET_ASSIGNMENT_RE = re.compile(
    r"(?is)\{%\s*set\s+(?P<target>[A-Za-z_][A-Za-z0-9_.-]*)"
    r"\s*=\s*(?P<value>.*?)\s*%\}"
)
JINJA_BLOCK_SET_ASSIGNMENT_RE = re.compile(
    r"(?is)\{%\s*set\s+(?P<target>[A-Za-z_][A-Za-z0-9_.-]*)\s*%\}"
    r"(?P<value>.*?)\{%\s*endset\s*%\}"
)
INLINE_SCRIPT_ASSIGNMENT_RE = re.compile(
    r"(?im)\b(?:(?:const|let|var)\s+)?"
    r"(?P<target>[A-Za-z_$][A-Za-z0-9_$]*(?:\.[A-Za-z_$][A-Za-z0-9_$]*)*)"
    r"\s*=(?!=|>)\s*(?P<value>[^;\r\n<]+?)\s*(?:;|(?=</script>|$))"
)
CSS_CUSTOM_PROPERTY_RE = re.compile(
    r"(?im)(?P<target>--[A-Za-z_][A-Za-z0-9_-]*)"
    r"\s*:\s*(?P<value>[^;\r\n}]+?)\s*(?:;|(?=\}))"
)
TEXT_SOURCE_SUFFIXES = {".css", ".html", ".py", ".tpl"}
NON_SECRET_CLASSIFICATION_IDENTIFIERS = {"config_secret_class"}
APPROVED_STATIC_SENSITIVE_METADATA_SHA256 = {
    ("app/security/surface_bindings.py", "public_token_form_view"): frozenset({
        "19320c3c6e1302ab0eb1dd47a408ae8a0d167e2f125c19ae236d3aab50e5d382",
    }),
    ("app/services/api_tokens.py", "stored_secret_material"): frozenset({
        "c6c83a3e7fa6995a8d493dccb65718e5c5c3a649cf3926e2a7b73a38c5e4fcc2",
    }),
    ("app/services/device_enrollment.py", "stored_secret_material"): frozenset({
        "c6c83a3e7fa6995a8d493dccb65718e5c5c3a649cf3926e2a7b73a38c5e4fcc2",
    }),
    ("app/services/fresh_install_wizard.py", "secret_handoff_policy_doc"): frozenset({
        "c143fbc9038b6b436ef44bc36a3a4d3ada86baf2f7c6cb4ef9ea13c90c6b8ed1",
    }),
    ("app/services/productization_boundary.py", "token_material"): frozenset({
        "8ad9daf7945517e6ba19a295b4193c92c20a35f5243e037b96ff1c8d1b8e51b7",
    }),
    ("app/services/productization_boundary.py", "raw_token_return_policy"): frozenset({
        "b121ab80ed64c2445e4cd832f9d140e17ab87c90e95dd68d4a7b8f02cc0e9403",
    }),
    ("app/web/app.py", "private_key"): frozenset({
        "10e4bdfa85a95e23e62efa0f28faa17a28c267a30494a49a2b0bc84e0c7559f1",
    }),
    ("app/web/app.py", "preshared_key"): frozenset({
        "a32af243ee5c79d50ab95591d1a992e6ba790e793aaa0e114341c91d81a5ba49",
    }),
    ("app/web/app.py", "token_label"): frozenset({
        "3ee75029c70e284c46b5af29eb87592f923e747f460353b02059a645f332b990",
    }),
    ("app/web/auth.py", "password_hash_error"): frozenset({
        "1f7981c8117bb7cc9c535075d24025a33b987f83293d9e1c4c10f186f22059d7",
    }),
}
APPROVED_RAW_SECRET_CONTEXT_LINE_SHA256 = {
    ("app/security/surface_policy.py", 3): frozenset({
        "4de4b5321d2217e385696e936d321f514eba38d33fb0c24afc726baf5618c105",
    }),
}
MAX_JWT_SEGMENT_BYTES = 8192
MAX_STATIC_EXPRESSION_DEPTH = 64
MAX_STATIC_EXPRESSION_NODES = 512
MAX_STATIC_VALUE_BYTES = 8192
ENTRY_KEYS = {"gate", "mode", "path", "role", "rollback_role", "secret_classification", "sha256", "size"}
ROLES = {spec[0] for spec in TOOLING_SPECS.values()} | {
    "application_snapshot", "callback_bootstrap", "dependency_lock_tool",
    "phase14_receipt", "runtime_dependency_lock", "test_dependency_lock",
}
GATES = {"ACCEPTANCE", "ADMIN_PILOT", "APPLICATION_STAGE", "AWG31_RUNTIME_STAGE", "ENABLE_ISSUANCE", "LOCAL_VERIFY", "OPERATOR", "PREFLIGHT"}
ROLLBACK_ROLES = {"application", "awg3-runtime", "none", "operator", "preflight"}


def canonical_json_bytes(value: object) -> bytes:
    try:
        rendered = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise PackageContractError("value is not canonical JSON") from exc
    return rendered.encode("utf-8") + b"\n"


def load_canonical_json(raw: bytes, *, label: str) -> dict[str, object]:
    if not isinstance(raw, bytes):
        raise PackageContractError(f"{label} must be bytes")

    def no_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise PackageContractError(f"{label} duplicate key")
            result[key] = value
        return result

    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=no_duplicates)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PackageContractError(f"{label} invalid JSON") from exc
    if not isinstance(value, dict) or raw != canonical_json_bytes(value):
        raise PackageContractError(f"{label} is not canonical JSON")
    return value


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _exact_dict(value: object, keys: set[str], label: str) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != keys:
        raise PackageContractError(f"{label} keys")
    return value


def _safe_path(value: object) -> str:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise PackageContractError("entry path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise PackageContractError("entry path")
    if value != path.as_posix() or path.parts[0] not in {"source", "tooling"} or any(":" in part for part in path.parts):
        raise PackageContractError("entry path")
    folded = value.casefold()
    if "phase13" in folded and any(word in folded for word in ("manifest", "outcome", "evidence")):
        raise PackageContractError("stale Phase 13 artifact")
    return value


def validate_manifest(value: object, *, verify_identity: bool = True) -> dict[str, object]:
    manifest = _exact_dict(value, {"dependency_locks", "entries", "package_id", "package_identity_sha256", "receipts", "schema", "source", "tooling"}, "manifest")
    if manifest["schema"] != MANIFEST_SCHEMA or manifest["package_id"] != PACKAGE_ID:
        raise PackageContractError("manifest package identity")
    source = _exact_dict(manifest["source"], {"branch", "head"}, "source")
    if source["branch"] != SOURCE_BRANCH or not isinstance(source["head"], str) or HEAD_RE.fullmatch(source["head"]) is None:
        raise PackageContractError("manifest source")
    tooling = _exact_dict(manifest["tooling"], {"branch", "head"}, "tooling")
    if tooling["branch"] != TOOLING_BRANCH or not isinstance(tooling["head"], str) or HEAD_RE.fullmatch(tooling["head"]) is None:
        raise PackageContractError("tooling identity")
    receipts = _exact_dict(manifest["receipts"], {"phase14", "phase16_source"}, "receipts")
    phase14 = _exact_dict(receipts["phase14"], {"commit", "path", "sha256"}, "phase14 receipt")
    if phase14 != {"commit": PHASE14_RECEIPT_COMMIT, "path": PHASE14_RECEIPT_PATH, "sha256": PHASE14_RECEIPT_SHA256}:
        raise PackageContractError("phase14 receipt identity")
    phase16 = _exact_dict(receipts["phase16_source"], {"path", "sha256"}, "phase16 receipt")
    if phase16["path"] != PHASE16_SOURCE_RECEIPT_PATH or not isinstance(phase16["sha256"], str) or SHA256_RE.fullmatch(phase16["sha256"]) is None:
        raise PackageContractError("phase16 receipt identity")
    locks = _exact_dict(manifest["dependency_locks"], {"runtime", "test"}, "dependency locks")
    for name, expected_path in EXPECTED_LOCK_PATHS.items():
        lock = _exact_dict(locks[name], {"path", "sha256"}, f"{name} lock")
        if lock["path"] != expected_path:
            raise PackageContractError("exact dependency lock binding")
        if not isinstance(lock["sha256"], str) or SHA256_RE.fullmatch(lock["sha256"]) is None:
            raise PackageContractError("dependency lock hash")
    entries = manifest["entries"]
    if not isinstance(entries, list) or not entries:
        raise PackageContractError("manifest entries")
    paths: list[str] = []
    folded_paths: set[str] = set()
    by_path: dict[str, dict[str, object]] = {}
    for value_entry in entries:
        entry = _exact_dict(value_entry, ENTRY_KEYS, "entry")
        path = _safe_path(entry["path"])
        if path.casefold() in folded_paths:
            raise PackageContractError("duplicate or case-colliding entry path")
        folded_paths.add(path.casefold())
        paths.append(path)
        by_path[path] = entry
        if not isinstance(entry["size"], int) or isinstance(entry["size"], bool) or entry["size"] < 0:
            raise PackageContractError("entry size")
        if not isinstance(entry["sha256"], str) or SHA256_RE.fullmatch(entry["sha256"]) is None:
            raise PackageContractError("entry sha256")
        if entry["role"] not in ROLES or entry["mode"] not in {"0644", "0755"}:
            raise PackageContractError("entry classification")
        if entry["secret_classification"] not in {"none", "synthetic-test"}:
            raise PackageContractError("forbidden secret classification")
        if entry["gate"] not in GATES or entry["rollback_role"] not in ROLLBACK_ROLES:
            raise PackageContractError("entry gate or rollback role")
    if paths != sorted(paths):
        raise PackageContractError("manifest entries must be sorted")
    for required_path, expected_spec in REQUIRED_ENTRY_SPECS.items():
        entry = by_path.get(required_path)
        if entry is None:
            raise PackageContractError(f"required package entry missing: {required_path}")
        actual_spec = (entry["role"], entry["gate"], entry["rollback_role"])
        expected_mode = "0755" if required_path.endswith(".sh") else "0644"
        if actual_spec != expected_spec or entry["mode"] != expected_mode or entry["secret_classification"] != "none":
            raise PackageContractError(f"required package entry contract: {required_path}")
    dynamic_spec = ("application_snapshot", "APPLICATION_STAGE", "application")
    for path, entry in by_path.items():
        if path in REQUIRED_ENTRY_SPECS:
            continue
        relative = path.removeprefix("source/")
        actual_spec = (entry["role"], entry["gate"], entry["rollback_role"])
        if (
            not path.startswith("source/app/")
            or _source_spec(relative) != dynamic_spec
            or actual_spec != dynamic_spec
            or entry["secret_classification"] != "none"
        ):
            raise PackageContractError(f"unexpected package entry: {path}")
    for lock_name in ("runtime", "test"):
        lock = locks[lock_name]
        entry = by_path.get(lock["path"])
        if entry is None or entry["sha256"] != lock["sha256"]:
            raise PackageContractError("dependency lock binding")
    expected_receipts = {
        "tooling/" + PHASE14_RECEIPT_PATH: ("phase14_receipt", PHASE14_RECEIPT_SHA256),
        "tooling/" + PHASE16_SOURCE_RECEIPT_PATH: ("phase16_source_receipt", phase16["sha256"]),
    }
    for path, (role, digest) in expected_receipts.items():
        entry = by_path.get(path)
        if entry is None or entry["role"] != role or entry["sha256"] != digest:
            raise PackageContractError("receipt entry binding")
    identity = manifest["package_identity_sha256"]
    if not isinstance(identity, str) or SHA256_RE.fullmatch(identity) is None:
        raise PackageContractError("package identity sha256")
    if verify_identity:
        unsigned = dict(manifest)
        unsigned.pop("package_identity_sha256")
        if identity != _sha256(canonical_json_bytes(unsigned)):
            raise PackageContractError("package identity mismatch")
    return dict(manifest)


def _git_environment() -> dict[str, str]:
    environment = {key: value for key, value in os.environ.items() if not key.upper().startswith("GIT_")}
    environment.update({"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1", "GIT_TERMINAL_PROMPT": "0"})
    return environment


def _git(root: Path, *args: str) -> bytes:
    try:
        result = subprocess.run(
            [
                "git",
                "-c",
                f"safe.directory={Path(root).resolve()}",
                "-c",
                "core.autocrlf=input",
                "-c",
                "core.safecrlf=false",
                *args,
            ],
            cwd=root,
            env=_git_environment(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as exc:
        raise PackageContractError("git unavailable") from exc
    if result.returncode != 0:
        raise PackageContractError("git command failed")
    return result.stdout


def _checked_repo(root: Path, expected_branch: str) -> tuple[Path, str]:
    root = Path(root).resolve()
    if root.is_symlink() or not root.is_dir():
        raise PackageContractError("repository root")
    if _git(root, "status", "--porcelain=v1", "--untracked-files=all"):
        raise PackageContractError("repository must be clean")
    branch = _git(root, "branch", "--show-current").decode("ascii").strip()
    if branch != expected_branch:
        raise PackageContractError("repository branch")
    head = _git(root, "rev-parse", "HEAD").decode("ascii").strip()
    if HEAD_RE.fullmatch(head) is None:
        raise PackageContractError("repository head")
    return root, head


def _git_mode(root: Path, revision: str, relative: str) -> str:
    raw = _git(root, "ls-tree", revision, "--", relative).decode("utf-8")
    rows = [row for row in raw.splitlines() if row]
    if len(rows) != 1 or "\t" not in rows[0]:
        raise PackageContractError("tracked tooling inventory")
    mode, kind, _object = rows[0].split("\t", 1)[0].split(" ", 2)
    if kind != "blob" or mode not in {"100644", "100755"}:
        raise PackageContractError("non-regular tracked file")
    return "0755" if mode == "100755" else "0644"


def _source_spec(relative: str) -> tuple[str, str, str] | None:
    if relative in REQUIRED_SOURCE_SPECS:
        return REQUIRED_SOURCE_SPECS[relative]
    if relative.startswith("app/") and Path(relative).suffix.casefold() in {".css", ".html", ".png", ".py", ".tpl"}:
        return "application_snapshot", "APPLICATION_STAGE", "application"
    return None


def _is_structural_jwt(body: bytes) -> bool:
    for candidate in JWT_CANDIDATE_RE.finditer(body):
        if any(len(segment) > MAX_JWT_SEGMENT_BYTES for segment in candidate.groups()):
            raise PackageContractError("forbidden oversized JWT candidate")
        decoded: list[object] = []
        for segment in candidate.groups()[:2]:
            padded = segment + b"=" * (-len(segment) % 4)
            try:
                raw = base64.b64decode(padded, altchars=b"-_", validate=True)
                decoded.append(json.loads(raw.decode("utf-8")))
            except RecursionError as exc:
                raise PackageContractError(
                    "forbidden recursively nested JWT candidate"
                ) from exc
            except (binascii.Error, UnicodeDecodeError, json.JSONDecodeError):
                break
        if len(decoded) == 2 and all(isinstance(value, dict) for value in decoded):
            return True
    return False


def _normalize_identifier(value: str) -> str:
    separated = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", value)
    return re.sub(r"[^a-z0-9]+", "_", separated.casefold()).strip("_")


def _is_sensitive_identifier(value: str) -> bool:
    normalized = _normalize_identifier(value)
    if not normalized:
        return False
    if normalized in NON_SECRET_CLASSIFICATION_IDENTIFIERS:
        return False
    parts = normalized.split("_")
    if any(
        part in {"authorization", "credential", "password", "secret", "token"}
        for part in parts
    ):
        return True
    joined = "_".join(parts)
    return any(
        marker in joined
        for marker in (
            "access_key", "api_key", "private_key", "preshared_key", "secret_key",
        )
    ) or joined in {"apikey", "privatekey", "presharedkey"}


def _is_approved_static_sensitive_metadata(relative: str, identifier: str, value: str | bytes) -> bool:
    payload = value if isinstance(value, bytes) else value.encode("utf-8")
    allowed_hashes = APPROVED_STATIC_SENSITIVE_METADATA_SHA256.get(
        (relative, _normalize_identifier(identifier)),
        frozenset(),
    )
    return _sha256(payload) in allowed_hashes


def _is_approved_raw_secret_context(relative: str, pattern_index: int, body: bytes, match: re.Match[bytes]) -> bool:
    line_start = body.rfind(b"\n", 0, match.start()) + 1
    line_end = body.find(b"\n", match.start())
    if line_end < 0:
        line_end = len(body)
    else:
        line_end += 1
    allowed_hashes = APPROVED_RAW_SECRET_CONTEXT_LINE_SHA256.get(
        (relative, pattern_index),
        frozenset(),
    )
    return _sha256(body[line_start:line_end]) in allowed_hashes


def _strip_scalar_quotes(value: str) -> str:
    scalar = value.strip()
    if len(scalar) >= 2 and scalar[0] == scalar[-1] and scalar[0] in {"'", '"'}:
        return scalar[1:-1].strip()
    return scalar


def _reject_sensitive_value(relative: str, value: str | bytes) -> None:
    if isinstance(value, bytes):
        try:
            scalar = value.decode("utf-8")
        except UnicodeDecodeError:
            if len(value) >= 16:
                raise PackageContractError(f"forbidden sensitive assignment: {relative}")
            return
    else:
        scalar = value
    scalar = _strip_scalar_quotes(scalar)
    expressions = list(JINJA_EXPRESSION_RE.finditer(scalar))
    if expressions:
        if len(expressions) != 1 or expressions[0].span() != (0, len(scalar)):
            raise PackageContractError(f"forbidden composite sensitive template: {relative}")
        if expressions[0].group(0) not in APPROVED_TEMPLATE_PLACEHOLDER_TEXT:
            raise PackageContractError(f"forbidden sensitive template: {relative}")
        return
    if len(scalar) >= 16:
        raise PackageContractError(f"forbidden sensitive assignment: {relative}")


class _StaticPythonValueLimit(Exception):
    pass


def _static_value_size(value: str | bytes) -> int:
    if isinstance(value, bytes):
        return len(value)
    return len(value.encode("utf-8"))


def _static_python_value(
    node: ast.AST,
    *,
    depth: int = 0,
    budget: list[int] | None = None,
) -> str | bytes | None:
    if budget is None:
        budget = [MAX_STATIC_EXPRESSION_NODES]
    if depth > MAX_STATIC_EXPRESSION_DEPTH or budget[0] <= 0:
        raise _StaticPythonValueLimit
    budget[0] -= 1
    if isinstance(node, ast.Constant) and isinstance(node.value, (str, bytes)):
        if _static_value_size(node.value) > MAX_STATIC_VALUE_BYTES:
            raise _StaticPythonValueLimit
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = _static_python_value(
            node.left,
            depth=depth + 1,
            budget=budget,
        )
        right = _static_python_value(
            node.right,
            depth=depth + 1,
            budget=budget,
        )
        if left is not None and right is not None and type(left) is type(right):
            result = left + right
            if _static_value_size(result) > MAX_STATIC_VALUE_BYTES:
                raise _StaticPythonValueLimit
            return result
    if isinstance(node, ast.JoinedStr):
        pieces: list[str] = []
        for value_node in node.values:
            value = _static_python_value(
                value_node,
                depth=depth + 1,
                budget=budget,
            )
            if not isinstance(value, str):
                return None
            pieces.append(value)
        result = "".join(pieces)
        if _static_value_size(result) > MAX_STATIC_VALUE_BYTES:
            raise _StaticPythonValueLimit
        return result
    return None


def _python_target_identifiers(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Name):
        return [node.id]
    if isinstance(node, ast.Attribute):
        return [node.attr]
    if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str):
        return [node.slice.value]
    if isinstance(node, (ast.List, ast.Tuple)):
        return [name for item in node.elts for name in _python_target_identifiers(item)]
    return []


def _reject_python_sensitive_assignments(relative: str, text: str) -> None:
    try:
        tree = ast.parse(text)
        for node in ast.walk(tree):
            targets: list[ast.AST] = []
            value_node: ast.AST | None = None
            if isinstance(node, ast.Assign):
                targets = list(node.targets)
                value_node = node.value
            elif isinstance(node, ast.AnnAssign):
                targets = [node.target]
                value_node = node.value
            identifiers = [
                name
                for target in targets
                for name in _python_target_identifiers(target)
                if _is_sensitive_identifier(name)
            ]
            if value_node is not None and identifiers:
                value = _static_python_value(value_node)
                if value is not None and not all(
                    _is_approved_static_sensitive_metadata(relative, name, value)
                    for name in identifiers
                ):
                    _reject_sensitive_value(relative, value)
            if isinstance(node, ast.Dict):
                for key, value_node in zip(node.keys, node.values, strict=True):
                    if (
                        isinstance(key, ast.Constant)
                        and isinstance(key.value, str)
                        and _is_sensitive_identifier(key.value)
                    ):
                        value = _static_python_value(value_node)
                        if value is not None and not _is_approved_static_sensitive_metadata(
                            relative, key.value, value
                        ):
                            _reject_sensitive_value(relative, value)
            if isinstance(node, ast.Call):
                for keyword in node.keywords:
                    if keyword.arg and _is_sensitive_identifier(keyword.arg):
                        value = _static_python_value(keyword.value)
                        if value is not None and not _is_approved_static_sensitive_metadata(
                            relative, keyword.arg, value
                        ):
                            _reject_sensitive_value(relative, value)
    except (SyntaxError, RecursionError, _StaticPythonValueLimit) as exc:
        raise PackageContractError(
            f"forbidden unscannable Python source: {relative}"
        ) from exc


class _SensitiveHTMLParser(HTMLParser):
    def __init__(self, relative: str) -> None:
        super().__init__(convert_charrefs=True)
        self.relative = relative

    def handle_starttag(self, _tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name.casefold(): value for name, value in attrs}
        sensitive_context = any(
            value is not None and _is_sensitive_identifier(value)
            for name, value in attrs
            if name.casefold() in {"id", "name"}
        )
        if sensitive_context:
            for name in ("content", "value"):
                value = values.get(name)
                if value is not None:
                    _reject_sensitive_value(self.relative, value)
        for name, value in attrs:
            if value is not None and _is_sensitive_identifier(name):
                _reject_sensitive_value(self.relative, value)


def _reject_contextual_sensitive_values(relative: str, body: bytes) -> None:
    suffix = PurePosixPath(relative).suffix.casefold()
    try:
        text = body.decode("utf-8")
    except UnicodeDecodeError as exc:
        if suffix in TEXT_SOURCE_SUFFIXES:
            raise PackageContractError(
                f"forbidden undecodable source text: {relative}"
            ) from exc
        return
    if suffix == ".py":
        _reject_python_sensitive_assignments(relative, text)
    if suffix == ".html":
        parser = _SensitiveHTMLParser(relative)
        parser.feed(text)
        parser.close()
    if suffix in {".html", ".tpl"}:
        for assignment in TEXT_ASSIGNMENT_RE.finditer(text):
            if _is_sensitive_identifier(assignment.group("target")):
                _reject_sensitive_value(relative, assignment.group("value"))
        for assignment in JINJA_SET_ASSIGNMENT_RE.finditer(text):
            if _is_sensitive_identifier(assignment.group("target")):
                _reject_sensitive_value(relative, assignment.group("value"))
        for assignment in JINJA_BLOCK_SET_ASSIGNMENT_RE.finditer(text):
            if _is_sensitive_identifier(assignment.group("target")):
                _reject_sensitive_value(relative, assignment.group("value"))
        for assignment in INLINE_SCRIPT_ASSIGNMENT_RE.finditer(text):
            if _is_sensitive_identifier(assignment.group("target")):
                _reject_sensitive_value(relative, assignment.group("value"))
    if suffix == ".css":
        for assignment in CSS_CUSTOM_PROPERTY_RE.finditer(text):
            if _is_sensitive_identifier(assignment.group("target")):
                _reject_sensitive_value(relative, assignment.group("value"))


def _reject_forbidden_source(relative: str, body: bytes) -> None:
    path = PurePosixPath(relative)
    folded_parts = {part.casefold() for part in path.parts}
    name = path.name.casefold()
    suffix = path.suffix.casefold()
    if folded_parts & FORBIDDEN_SOURCE_COMPONENTS:
        raise PackageContractError(f"forbidden source material: {relative}")
    if name == ".env" or name.startswith(".env.") or suffix in FORBIDDEN_SOURCE_SUFFIXES:
        raise PackageContractError(f"forbidden source material: {relative}")
    if suffix == ".png":
        expected_brand = APPROVED_BRAND_PNGS.get(relative)
        if expected_brand is None or (len(body), _sha256(body)) != expected_brand:
            raise PackageContractError(f"forbidden source material: {relative}")
    has_unapproved_raw_secret = any(
        match is not None and not _is_approved_raw_secret_context(relative, index, body, match)
        for index, pattern in enumerate(PRIVATE_MATERIAL_PATTERNS)
        for match in (pattern.search(body),)
    )
    if body.startswith(b"SQLite format 3\x00") or has_unapproved_raw_secret or _is_structural_jwt(body):
        raise PackageContractError(f"forbidden raw secret material: {relative}")
    _reject_contextual_sensitive_values(relative, body)


def _source_payloads(root: Path, head: str) -> dict[str, tuple[bytes, str, str, str, str]]:
    archive = _git(root, "archive", "--format=tar", head, "--", *SOURCE_ARCHIVE_PATHS)
    result: dict[str, tuple[bytes, str, str, str, str]] = {}
    try:
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as stream:
            for member in stream.getmembers():
                if member.isdir():
                    continue
                relative = PurePosixPath(member.name)
                if not member.isfile() or relative.is_absolute() or ".." in relative.parts:
                    raise PackageContractError("source archive member")
                extracted = stream.extractfile(member)
                if extracted is None:
                    raise PackageContractError("source archive member unreadable")
                body = extracted.read()
                _reject_forbidden_source(relative.as_posix(), body)
                spec = _source_spec(relative.as_posix())
                if spec is None:
                    raise PackageContractError(f"unclassified source file: {relative.as_posix()}")
                role, gate, rollback = spec
                result[relative.as_posix()] = (body, "0755" if member.mode & 0o111 else "0644", role, gate, rollback)
    except tarfile.TarError as exc:
        raise PackageContractError("invalid git archive") from exc
    if not REQUIRED_SOURCE_PATHS.issubset(result):
        raise PackageContractError("source inventory incomplete")
    return result


def _tooling_payloads(root: Path, head: str) -> dict[str, tuple[bytes, str, str, str, str]]:
    result: dict[str, tuple[bytes, str, str, str, str]] = {}
    for relative, (role, gate, rollback) in TOOLING_SPECS.items():
        body = _git(root, "show", f"{head}:{relative}")
        result[relative] = (body, _git_mode(root, head, relative), role, gate, rollback)
    contract_ids = {
        "failure-outcome.schema.json": "amn2.phase16.readonly-preflight-failure.v1",
        "package-manifest.schema.json": MANIFEST_SCHEMA,
        "preflight-evidence.schema.json": "amn2.phase16.readonly-preflight-evidence.v1",
    }
    prefix = "packaging/phase16-awg3-family-3-1-spain-pilot-contract/"
    for name, schema_id in contract_ids.items():
        value = load_canonical_json(result[prefix + name][0], label=name)
        if value.get("$id") != schema_id or value.get("additionalProperties") is not False:
            raise PackageContractError("contract schema identity")
    resource = load_canonical_json(result[prefix + "resource-plan.json"][0], label="resource plan")
    if resource != RESOURCE_PLAN:
        raise PackageContractError("resource plan identity")
    return result


def _phase14_blob(root: Path) -> bytes:
    body = _git(root, "show", f"{PHASE14_RECEIPT_COMMIT}:{PHASE14_RECEIPT_PATH}")
    if _sha256(body) != PHASE14_RECEIPT_SHA256:
        raise PackageContractError("phase14 receipt hash")
    return body


def _entry(path: str, body: bytes, mode: str, role: str, gate: str, rollback: str) -> dict[str, object]:
    return {"gate": gate, "mode": mode, "path": path, "role": role, "rollback_role": rollback, "secret_classification": "none", "sha256": _sha256(body), "size": len(body)}


def _reject_symlink_or_reparse_path(value: Path, *, label: str) -> Path:
    lexical = Path(os.path.abspath(os.fspath(value)))
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    for candidate in reversed((lexical, *lexical.parents)):
        try:
            info = os.lstat(candidate)
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise PackageContractError(f"{label} path inspection") from exc
        if stat.S_ISLNK(info.st_mode) or (
            reparse_flag and getattr(info, "st_file_attributes", 0) & reparse_flag
        ):
            raise PackageContractError(f"{label} symlink or reparse point")
    return lexical


def materialize_package(*, source_root: Path, source_head: str, package_id: str, output_root: Path, tooling_root: Path = ROOT) -> PackageReceipt:
    if package_id != PACKAGE_ID:
        raise PackageContractError("package id")
    lexical_output = _reject_symlink_or_reparse_path(Path(output_root), label="output")
    output = lexical_output.resolve()
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise PackageContractError("output must not be non-empty")
    source, actual_head = _checked_repo(Path(source_root), SOURCE_BRANCH)
    tooling, tooling_head = _checked_repo(Path(tooling_root), TOOLING_BRANCH)
    if not isinstance(source_head, str) or HEAD_RE.fullmatch(source_head) is None or source_head != actual_head:
        raise PackageContractError("source head mismatch")
    source_items = _source_payloads(source, source_head)
    tooling_items = _tooling_payloads(tooling, tooling_head)
    files: dict[str, tuple[bytes, str, str, str, str]] = {
        "source/" + path: item for path, item in source_items.items()
    }
    files.update({"tooling/" + path: item for path, item in tooling_items.items()})
    phase14_path = "tooling/" + PHASE14_RECEIPT_PATH
    files[phase14_path] = (_phase14_blob(tooling), "0644", "phase14_receipt", "LOCAL_VERIFY", "operator")
    if len({path.casefold() for path in files}) != len(files):
        raise PackageContractError("package path collision")
    entries = [_entry(path, *files[path]) for path in sorted(files)]
    by_path = {entry["path"]: entry for entry in entries}
    runtime_path = "source/requirements/phase15-runtime-py312.lock"
    test_path = "source/requirements/phase15-test-py312.lock"
    phase16_path = "tooling/" + PHASE16_SOURCE_RECEIPT_PATH
    unsigned: dict[str, object] = {
        "dependency_locks": {
            "runtime": {"path": runtime_path, "sha256": by_path[runtime_path]["sha256"]},
            "test": {"path": test_path, "sha256": by_path[test_path]["sha256"]},
        },
        "entries": entries,
        "package_id": PACKAGE_ID,
        "receipts": {
            "phase14": {"commit": PHASE14_RECEIPT_COMMIT, "path": PHASE14_RECEIPT_PATH, "sha256": PHASE14_RECEIPT_SHA256},
            "phase16_source": {"path": PHASE16_SOURCE_RECEIPT_PATH, "sha256": by_path[phase16_path]["sha256"]},
        },
        "schema": MANIFEST_SCHEMA,
        "source": {"branch": SOURCE_BRANCH, "head": source_head},
        "tooling": {"branch": TOOLING_BRANCH, "head": tooling_head},
    }
    manifest = dict(unsigned)
    manifest["package_identity_sha256"] = _sha256(canonical_json_bytes(unsigned))
    validate_manifest(manifest)
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{output.name}.", dir=output.parent))
    try:
        for path, (body, mode, _role, _gate, _rollback) in files.items():
            destination = staging.joinpath(*PurePosixPath(path).parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open("xb") as stream:
                stream.write(body)
            if os.name != "nt":
                os.chmod(destination, int(mode, 8))
        (staging / "manifest.json").write_bytes(canonical_json_bytes(manifest))
        verified = verify_package(staging)
        _reject_symlink_or_reparse_path(lexical_output, label="output")
        if output.exists():
            output.rmdir()
        staging.replace(output)
        return PackageReceipt(output, output / "manifest.json", verified.package_identity_sha256, verified.file_count)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def _regular_files(root: Path) -> set[str]:
    paths: set[str] = set()
    for current, directories, filenames in os.walk(root, followlinks=False):
        current_path = Path(current)
        for name in directories:
            if (current_path / name).is_symlink():
                raise PackageContractError("package symlink")
        for name in filenames:
            path = current_path / name
            info = os.lstat(path)
            if not stat.S_ISREG(info.st_mode):
                raise PackageContractError("package non-regular file")
            paths.add(path.relative_to(root).as_posix())
    return paths


def verify_package(package_root: Path) -> PackageReceipt:
    lexical_root = _reject_symlink_or_reparse_path(Path(package_root), label="package root")
    root = lexical_root.resolve()
    if not root.is_dir():
        raise PackageContractError("package root")
    manifest_path = root / "manifest.json"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise PackageContractError("package manifest")
    manifest = validate_manifest(load_canonical_json(manifest_path.read_bytes(), label="package manifest"))
    expected = {"manifest.json"} | {entry["path"] for entry in manifest["entries"]}
    if _regular_files(root) != expected:
        raise PackageContractError("package inventory mismatch")
    for entry in manifest["entries"]:
        path = root.joinpath(*PurePosixPath(entry["path"]).parts)
        body = path.read_bytes()
        if len(body) != entry["size"] or _sha256(body) != entry["sha256"]:
            raise PackageContractError("package checksum mismatch")
    return PackageReceipt(root, manifest_path, manifest["package_identity_sha256"], len(manifest["entries"]))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    materialize = commands.add_parser("materialize")
    materialize.add_argument("--source-root", required=True, type=Path)
    materialize.add_argument("--source-head", required=True)
    materialize.add_argument("--package-id", required=True)
    materialize.add_argument("--output-root", required=True, type=Path)
    verify = commands.add_parser("verify")
    verify.add_argument("--package-root", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "materialize":
            receipt = materialize_package(source_root=args.source_root, source_head=args.source_head, package_id=args.package_id, output_root=args.output_root, tooling_root=ROOT)
            result = {"file_count": receipt.file_count, "package_identity_sha256": receipt.package_identity_sha256, "result": "materialized"}
        else:
            receipt = verify_package(args.package_root)
            result = {"file_count": receipt.file_count, "package_identity_sha256": receipt.package_identity_sha256, "result": "verified"}
    except PackageContractError as exc:
        parser.error(str(exc))
    print(canonical_json_bytes(result).decode("ascii"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
