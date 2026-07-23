from __future__ import annotations

import copy
import base64
import hashlib
import importlib.resources
import ipaddress
import json
import os
import re
import sqlite3
import stat
import sys
import tempfile
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, ContextManager, Mapping

try:
    from scripts import phase12_spain_live_backend as live_backend
    from scripts import phase12_spain_network as network_backend
    from scripts import phase12_spain_package as package_backend
    from scripts.phase12_spain_package import (
        PackageVerificationError,
        extract_verified_package_fd,
        plan_verified_package_extraction_fd,
        plan_verified_package_source,
        expand_verified_package_source,
        sha256_canonical,
        verify_package_fd,
    )
    from scripts.phase12_spain_precondition import (
        FIREWALL_SEMANTIC_REBASELINE,
        PreconditionError,
        build_precondition_receipt,
        observation_from_resource_confirmation_evidence,
        validate_preconditions,
        verify_precondition_receipt,
    )
    from scripts.phase12_spain_network import expected_table_document
    from scripts.phase12_spain_live_backend import (
        BackendError,
        LinuxBackend,
        PRODUCTION_INSTALL_MUTATING_STAGES,
        ProductionInstallActionPlan,
        SystemOwnedAdapter,
    )
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from scripts import phase12_spain_live_backend as live_backend
    from scripts import phase12_spain_network as network_backend
    from scripts import phase12_spain_package as package_backend
    from scripts.phase12_spain_package import (
        PackageVerificationError,
        extract_verified_package_fd,
        plan_verified_package_extraction_fd,
        plan_verified_package_source,
        expand_verified_package_source,
        sha256_canonical,
        verify_package_fd,
    )
    from scripts.phase12_spain_precondition import (
        FIREWALL_SEMANTIC_REBASELINE,
        PreconditionError,
        build_precondition_receipt,
        observation_from_resource_confirmation_evidence,
        validate_preconditions,
        verify_precondition_receipt,
    )
    from scripts.phase12_spain_network import expected_table_document
    from scripts.phase12_spain_live_backend import (
        BackendError,
        LinuxBackend,
        PRODUCTION_INSTALL_MUTATING_STAGES,
        ProductionInstallActionPlan,
        SystemOwnedAdapter,
    )


class InstallError(RuntimeError):
    pass


def _preparation_failure_message(exc: Exception) -> str:
    """Expose only a bounded, non-sensitive pre-write failure label."""
    detail = str(exc)
    if re.fullmatch(r"[a-z][a-z0-9_ ./-]{0,159}", detail):
        return "production installation preparation failed:" + detail
    kind = re.sub(r"(?<!^)(?=[A-Z])", "_", type(exc).__name__).lower()
    return "production installation preparation failed:" + kind


def _runtime_failure_message(exc: Exception) -> str:
    """Expose only the Docker image-load diagnostic allowlist after rollback."""
    detail = str(exc)
    if re.fullmatch(
        r"docker_image_load_(?:no_space|archive|permission|daemon_unavailable|layer_apply|unsupported|exit_(?:[1-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]|unknown))",
        detail,
    ):
        return "production runtime rollback failed:" + detail
    return "production runtime rollback failed"


def _embedded_resource_collector_bytes() -> bytes:
    """Return the resource collector shipped inside the standalone executor.

    The production boundary must recheck resources without first writing a
    separate collector to the target. Source-tree tests use the checked-in
    shell script; the standalone executor reads the identically bound member
    from its ``scripts`` package.
    """
    try:
        payload = (
            importlib.resources.files("scripts")
            .joinpath("phase12_spain_resource_confirmation_remote.sh")
            .read_bytes()
        )
    except (FileNotFoundError, ModuleNotFoundError, TypeError):
        path = Path(__file__).resolve().parent / "vps" / "phase12_spain_resource_confirmation_remote.sh"
        try:
            payload = path.read_bytes()
        except OSError as exc:
            raise InstallError("embedded resource collector unavailable") from exc
    if not payload or len(payload) > ChecksumBoundResourceObserver.MAX_COLLECTOR_BYTES:
        raise InstallError("embedded resource collector size invalid")
    return payload


def _embedded_run009_baseline() -> dict[str, Any]:
    """Load the sealed run009 baseline from the executor, never from SSH stdin."""
    try:
        payload = (
            importlib.resources.files("scripts")
            .joinpath("phase12_spain_run009_preflight_evidence.json")
            .read_bytes()
        )
    except (FileNotFoundError, ModuleNotFoundError, TypeError):
        path = (
            Path(__file__).resolve().parents[1]
            / "private-artifacts"
            / "phase12-spain-install-package-inputs-20260721"
            / "evidence"
            / "run009-preflight-evidence.json"
        )
        try:
            payload = path.read_bytes()
        except OSError as exc:
            raise InstallError("embedded run009 baseline unavailable") from exc
    if hashlib.sha256(payload).hexdigest() != package_backend.DEFAULT_RUN009_EVIDENCE_SHA256:
        raise InstallError("embedded run009 baseline checksum mismatch")
    try:
        evidence = json.loads(payload)
        fingerprint = evidence["unrelated_service_fingerprint"]
        firewall = evidence["firewall"]
    except (KeyError, TypeError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InstallError("embedded run009 baseline invalid") from exc
    if (
        not isinstance(fingerprint, list)
        or hashlib.sha256(
            package_backend.compact_json_bytes_preserving_object_order(fingerprint)
        ).hexdigest()
        != package_backend.DEFAULT_RUN009_FINGERPRINT_SHA256
        or not isinstance(firewall, dict)
    ):
        raise InstallError("embedded run009 baseline binding mismatch")
    return {
        "run009_evidence_sha256": package_backend.DEFAULT_RUN009_EVIDENCE_SHA256,
        "fingerprint_array_sha256": package_backend.DEFAULT_RUN009_FINGERPRINT_SHA256,
        "systemd_projection": fingerprint,
        "firewall": firewall,
        "firewall_semantic_rebaseline": copy.deepcopy(FIREWALL_SEMANTIC_REBASELINE),
        "run009_evidence_hex": payload.hex(),
    }


def _embedded_resource_plan() -> dict[str, Any]:
    expected_sha256 = "8bc5375f244f7cdd77a12bd4173ca19be7430c35e49756d7b846906719369f43"
    try:
        payload = (
            importlib.resources.files("scripts")
            .joinpath("phase12_spain_resource_plan.json")
            .read_bytes()
        )
    except (FileNotFoundError, ModuleNotFoundError, TypeError):
        try:
            payload = (
                Path(__file__).resolve().parents[1]
                / "packaging"
                / "phase12-spain"
                / "resource-plan.json"
            ).read_bytes()
        except OSError as exc:
            raise InstallError("embedded resource plan unavailable") from exc
    try:
        plan = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InstallError("embedded resource plan invalid") from exc
    if not isinstance(plan, dict) or sha256_canonical(plan) != expected_sha256:
        raise InstallError("embedded resource plan checksum mismatch")
    return plan


def _read_boot_id(path: Path = Path("/proc/sys/kernel/random/boot_id"), *, expected_uid: int | None = 0) -> str:
    candidate = Path(path)
    if not candidate.is_absolute() or candidate.is_symlink():
        raise InstallError("boot identity source invalid")
    descriptor = -1
    try:
        descriptor = os.open(
            candidate,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0),
        )
        before = os.fstat(descriptor)
        payload = os.read(descriptor, 64)
        after = os.fstat(descriptor)
    except OSError as exc:
        raise InstallError("boot identity unavailable") from exc
    finally:
        if descriptor >= 0:
            os.close(descriptor)
    if (
        not stat.S_ISREG(before.st_mode)
        or (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
        != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
        or (
            os.name != "nt"
            and (
                (stat.S_IMODE(before.st_mode) & 0o022) != 0
                or (expected_uid is not None and before.st_uid != expected_uid)
            )
        )
    ):
        raise InstallError("boot identity owner/mode/type drift")
    try:
        value = payload.decode("ascii").strip()
    except UnicodeDecodeError as exc:
        raise InstallError("boot identity invalid") from exc
    if re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", value) is None:
        raise InstallError("boot identity invalid")
    return value


class ChecksumBoundResourceObserver:
    MAX_COLLECTOR_BYTES = 1024 * 1024
    MAX_EVIDENCE_BYTES = 1024 * 1024

    def __init__(
        self,
        *,
        collector_path: Path | None = None,
        collector_bytes: bytes | None = None,
        collector_sha256: str,
        runner: Callable[..., bytes] | None = None,
        expected_uid: int | None = 0,
    ) -> None:
        if (collector_path is None) == (collector_bytes is None):
            raise InstallError("resource observer dependency invalid")
        path = Path(collector_path) if collector_path is not None else None
        if (
            (path is not None and (not path.is_absolute() or path.is_symlink() or not path.is_file()))
            or (
                collector_bytes is not None
                and (
                    not isinstance(collector_bytes, bytes)
                    or not collector_bytes
                    or len(collector_bytes) > self.MAX_COLLECTOR_BYTES
                )
            )
            or not isinstance(collector_sha256, str)
            or re.fullmatch(r"[0-9a-f]{64}", collector_sha256) is None
            or (runner is not None and not callable(runner))
        ):
            raise InstallError("resource observer dependency invalid")
        self.collector_path = path
        self.collector_bytes = bytes(collector_bytes) if collector_bytes is not None else None
        self.collector_sha256 = collector_sha256
        self.expected_uid = expected_uid
        self._runner = runner or live_backend.FixedCommandRunner(
            allowed_argv={("/usr/bin/bash", "-s")},
            timeout_seconds=60.0,
            max_output=self.MAX_EVIDENCE_BYTES,
        )

    def _open_verified_collector(self) -> tuple[int, os.stat_result]:
        if self.collector_bytes is not None:
            return self._open_verified_in_memory_collector()
        if self.collector_path is None:
            raise InstallError("resource observer dependency invalid")
        descriptor = -1
        try:
            descriptor = os.open(
                self.collector_path,
                os.O_RDONLY
                | getattr(os, "O_NOFOLLOW", 0)
                | getattr(os, "O_BINARY", 0),
            )
            info = os.fstat(descriptor)
            payload = os.read(descriptor, self.MAX_COLLECTOR_BYTES + 1)
            after = os.fstat(descriptor)
        except OSError as exc:
            if descriptor >= 0:
                os.close(descriptor)
            raise InstallError("resource observer collector unavailable") from exc
        if (
            len(payload) > self.MAX_COLLECTOR_BYTES
            or not stat.S_ISREG(info.st_mode)
            or (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns)
            != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
            or hashlib.sha256(payload).hexdigest() != self.collector_sha256
            or (
                os.name != "nt"
                and (
                    stat.S_IMODE(info.st_mode) & 0o022 != 0
                    or (
                        self.expected_uid is not None
                        and info.st_uid != self.expected_uid
                    )
                )
            )
        ):
            os.close(descriptor)
            raise InstallError("resource observer collector checksum/owner drift")
        try:
            os.lseek(descriptor, 0, os.SEEK_SET)
        except OSError as exc:
            os.close(descriptor)
            raise InstallError("resource observer collector cannot be pinned") from exc
        return descriptor, info

    def _open_verified_in_memory_collector(self) -> tuple[int, os.stat_result]:
        payload = self.collector_bytes
        if payload is None or hashlib.sha256(payload).hexdigest() != self.collector_sha256:
            raise InstallError("resource observer collector checksum/owner drift")
        if not hasattr(os, "memfd_create"):
            raise InstallError("resource observer in-memory collector unavailable")
        descriptor = -1
        try:
            descriptor = os.memfd_create(
                "amn2-spain-resource-collector",
                getattr(os, "MFD_CLOEXEC", 0),
            )
            offset = 0
            while offset < len(payload):
                written = os.write(descriptor, payload[offset:])
                if written <= 0:
                    raise InstallError("resource observer in-memory collector write failed")
                offset += written
            os.fchmod(descriptor, 0o600)
            os.lseek(descriptor, 0, os.SEEK_SET)
            info = os.fstat(descriptor)
        except InstallError:
            if descriptor >= 0:
                os.close(descriptor)
            raise
        except OSError as exc:
            if descriptor >= 0:
                os.close(descriptor)
            raise InstallError("resource observer in-memory collector unavailable") from exc
        if (
            not stat.S_ISREG(info.st_mode)
            or info.st_size != len(payload)
            or (
                os.name != "nt"
                and (
                    (stat.S_IMODE(info.st_mode) & 0o022) != 0
                    or (self.expected_uid is not None and info.st_uid != self.expected_uid)
                )
            )
        ):
            os.close(descriptor)
            raise InstallError("resource observer collector checksum/owner drift")
        return descriptor, info

    def collect_evidence(self) -> dict[str, Any]:
        descriptor, before = self._open_verified_collector()
        try:
            try:
                payload = self._runner(
                    ("/usr/bin/bash", "-s"),
                    input_fd=descriptor,
                    input_size=before.st_size,
                    timeout=60.0,
                    max_output=self.MAX_EVIDENCE_BYTES,
                )
                after = os.fstat(descriptor)
            finally:
                os.close(descriptor)
        except InstallError:
            raise
        except Exception as exc:
            raise InstallError("resource observer execution failed") from exc
        if (
            before.st_dev,
            before.st_ino,
            before.st_size,
            before.st_mtime_ns,
        ) != (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
        ):
            raise InstallError("resource observer collector changed during execution")
        if (
            not isinstance(payload, bytes)
            or not payload.endswith(b"\n")
            or len(payload) > self.MAX_EVIDENCE_BYTES
        ):
            raise InstallError("resource observer output envelope invalid")
        try:
            value = json.loads(payload)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise InstallError("resource observer output JSON invalid") from exc
        if (
            json.dumps(value, separators=(",", ":"), ensure_ascii=True).encode(
                "ascii"
            )
            + b"\n"
            != payload
        ):
            raise InstallError("resource observer output canonical mismatch")
        return value

    def collect_observation(self) -> dict[str, Any]:
        try:
            return observation_from_resource_confirmation_evidence(
                self.collect_evidence()
            )
        except PreconditionError as exc:
            raise InstallError("resource observer evidence invalid") from exc


class ProductionPostinstallObserver:
    """Read-only runtime and closed-delta proof; never restarts or stops AWG."""

    MAX_DATABASE_TABLES = 512
    OWNED_UNITS = (
        "amn2-spain-web.service",
        "amn2-spain-bot.service",
        "amn2-spain-docker.service",
        "amn2-spain-network.service",
    )
    RUNTIME_COMMANDS = frozenset(
        {
            (
                "/opt/amn2-spain/docker/bin/docker",
                "--host=unix:///run/amn2-spain-docker/docker.sock",
                "inspect",
                "--format={{.RestartCount}}",
                "amn2-spain-awg",
            ),
            (
                "/opt/amn2-spain/docker/bin/docker",
                "--host=unix:///run/amn2-spain-docker/docker.sock",
                "network",
                "inspect",
                "--format={{.Name}}",
                "amn2-spain-net",
            ),
            (
                "/opt/amn2-spain/docker/bin/docker",
                "--host=unix:///run/amn2-spain-docker/docker.sock",
                "exec",
                "amn2-spain-awg",
                "awg",
                "show",
                "awgsp0",
                "peers",
            ),
            (
                "/usr/bin/systemctl",
                "show",
                "amn2-spain-bot.service",
                "--property=UnitFileState",
                "--value",
            ),
            (
                "/usr/bin/systemctl",
                "show",
                "amn2-spain-bot.service",
                "--property=ActiveState",
                "--value",
            ),
        }
    )

    def __init__(
        self,
        *,
        resource_observer: ChecksumBoundResourceObserver,
        resource_plan: Mapping[str, Any],
        baseline_observation: Mapping[str, Any],
        created_objects: Callable[[], list[str]],
        runner: Callable[..., bytes] | None = None,
        database_path: Path = Path("/var/lib/amn2-spain/amn2.sqlite3"),
        runtime_env_path: Path = Path("/etc/amn2-spain/runtime.env"),
    ) -> None:
        if (
            not isinstance(resource_observer, ChecksumBoundResourceObserver)
            or not isinstance(resource_plan, Mapping)
            or not isinstance(baseline_observation, Mapping)
            or not callable(created_objects)
        ):
            raise InstallError("postinstall observer dependency invalid")
        self.resource_observer = resource_observer
        self.resource_plan = copy.deepcopy(dict(resource_plan))
        self.baseline = copy.deepcopy(dict(baseline_observation))
        self.created_objects = created_objects
        self.runner = runner or live_backend.FixedCommandRunner(
            allowed_argv=set(self.RUNTIME_COMMANDS),
            timeout_seconds=30.0,
            max_output=1024 * 1024,
        )
        self.database_path = Path(database_path)
        self.runtime_env_path = Path(runtime_env_path)

    @staticmethod
    def _one_line(payload: bytes, label: str) -> str:
        if (
            not isinstance(payload, bytes)
            or len(payload) > 1024 * 1024
            or not payload.endswith(b"\n")
            or b"\x00" in payload
        ):
            raise InstallError(f"postinstall {label} output invalid")
        lines = payload.decode("utf-8", "strict").splitlines()
        if len(lines) != 1:
            raise InstallError(f"postinstall {label} output invalid")
        return lines[0]

    def _run(
        self, argv: tuple[str, ...], label: str, *, allow_empty: bool = False
    ) -> str:
        try:
            payload = self.runner(
                argv, timeout=30.0, max_output=1024 * 1024
            )
            if allow_empty and payload == b"":
                return ""
            return self._one_line(payload, label)
        except InstallError:
            raise
        except Exception as exc:
            raise InstallError(f"postinstall {label} observation failed") from exc

    def _database_is_clean(self) -> bool:
        path = self.database_path
        if not path.is_absolute() or path.is_symlink():
            raise InstallError("postinstall database unavailable")
        descriptor = -1
        try:
            descriptor = os.open(
                path,
                os.O_RDONLY
                | getattr(os, "O_NOFOLLOW", 0)
                | getattr(os, "O_BINARY", 0),
            )
            before = os.fstat(descriptor)
            if (
                not stat.S_ISREG(before.st_mode)
                or (
                    os.name != "nt"
                    and stat.S_IMODE(before.st_mode) != 0o600
                )
            ):
                raise InstallError("postinstall database owner/mode/type invalid")
            database_uri = (
                f"file:/proc/self/fd/{descriptor}?mode=ro&immutable=1"
                if os.name != "nt"
                else f"file:{path.as_posix()}?mode=ro&immutable=1"
            )
            connection = sqlite3.connect(
                database_uri,
                uri=True,
                timeout=2.0,
            )
            try:
                integrity = connection.execute("PRAGMA integrity_check").fetchall()
                foreign = connection.execute("PRAGMA foreign_key_check").fetchall()
                connection.execute("PRAGMA foreign_keys=ON")
                foreign_keys = connection.execute("PRAGMA foreign_keys").fetchone()
                names = [
                    row[0]
                    for row in connection.execute(
                        "SELECT name FROM sqlite_master "
                        "WHERE type='table' AND name NOT LIKE 'sqlite_%' "
                        "ORDER BY name"
                    ).fetchall()
                ]
                if not names or len(names) > self.MAX_DATABASE_TABLES:
                    raise InstallError("postinstall database schema invalid")
                nonempty = [
                    name
                    for name in names
                    if connection.execute(
                        'SELECT 1 FROM "' + name.replace('"', '""') + '" LIMIT 1'
                    ).fetchone()
                    is not None
                ]
            finally:
                connection.close()
            after = os.fstat(descriptor)
            if (
                before.st_dev,
                before.st_ino,
                before.st_size,
                before.st_mtime_ns,
            ) != (
                after.st_dev,
                after.st_ino,
                after.st_size,
                after.st_mtime_ns,
            ):
                raise InstallError("postinstall database changed during observation")
        except (sqlite3.Error, OSError) as exc:
            raise InstallError("postinstall database observation failed") from exc
        finally:
            if descriptor >= 0:
                os.close(descriptor)
        if integrity != [("ok",)] or foreign != [] or foreign_keys != (1,) or nonempty:
            raise InstallError("postinstall database is not clean")
        return True

    def _runtime_env_vps_apply_disabled(self) -> bool:
        descriptor = -1
        try:
            descriptor = os.open(
                self.runtime_env_path,
                os.O_RDONLY
                | getattr(os, "O_NOFOLLOW", 0)
                | getattr(os, "O_BINARY", 0),
            )
            before = os.fstat(descriptor)
            payload = os.read(descriptor, 1024 * 1024 + 1)
            after = os.fstat(descriptor)
        except OSError as exc:
            raise InstallError("postinstall runtime settings unavailable") from exc
        finally:
            if descriptor >= 0:
                os.close(descriptor)
        if (
            len(payload) > 1024 * 1024
            or b"\x00" in payload
            or not stat.S_ISREG(before.st_mode)
            or (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
            != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
            or (
                os.name != "nt"
                and stat.S_IMODE(before.st_mode) != 0o600
            )
        ):
            raise InstallError("postinstall runtime settings invalid")
        values: dict[str, str] = {}
        try:
            for line in payload.decode("utf-8", "strict").splitlines():
                if not line or line.startswith("#"):
                    continue
                key, separator, value = line.partition("=")
                if separator != "=" or not key or key in values:
                    raise InstallError("postinstall runtime settings invalid")
                values[key] = value
        except UnicodeDecodeError as exc:
            raise InstallError("postinstall runtime settings invalid") from exc
        if values.get("VPS_APPLY_ENABLED") != "false":
            raise InstallError("postinstall vps_apply is enabled")
        return True

    def _assert_closed_candidates(self, observation: Mapping[str, Any]) -> None:
        existing = observation.get("existing")
        resources = self.resource_plan.get("resources")
        if not isinstance(existing, Mapping) or not isinstance(resources, Mapping):
            raise InstallError("postinstall candidate inventory invalid")
        expected = {
            "paths": set(resources["paths"]) - {"/run/amn2-spain-docker"},
            "retained_paths": set(resources["retained_paths"]),
            "users": set(resources["users"]),
            "groups": set(resources["groups"]),
            "units": set(resources["units"]),
            "containers": set(),
            "networks": set(),
            "bridges": set(resources["bridges"]),
            "interfaces": set(resources["interfaces"]),
            "uids": set(resources["uids"]),
            "gids": set(resources["gids"]),
            "sockets": set(resources["sockets"]),
            "runtime_dirs": set(resources["runtime_dirs"]),
            "firewall_objects": {"inet:amn2_spain"},
            "owned_routes": {"10.212.12.0/24"},
            "sysctls": set(),
        }
        if set(existing) != set(expected) or any(
            set(existing[key]) != values for key, values in expected.items()
        ):
            raise InstallError("postinstall closed candidate delta mismatch")
        baseline_listeners = set(self.baseline.get("listeners", []))
        if set(observation.get("listeners", [])) != baseline_listeners | set(
            self.resource_plan.get("listeners", [])
        ):
            raise InstallError("postinstall listener delta mismatch")
        try:
            docker_network = ipaddress.ip_network(
                self.resource_plan["docker_cidr"], strict=True
            )
            bridge_address = str(
                ipaddress.ip_interface(
                    f"{docker_network.network_address + 1}/{docker_network.prefixlen}"
                )
            )
            vpn_address = str(
                ipaddress.ip_interface(self.resource_plan["server_vpn_address"])
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise InstallError("postinstall network plan invalid") from exc
        if set(observation.get("addresses", [])) != set(
            self.baseline.get("addresses", [])
        ) | {bridge_address, vpn_address}:
            raise InstallError("postinstall address delta mismatch")
        if set(observation.get("routes", [])) != set(
            self.baseline.get("routes", [])
        ) | {str(docker_network), str(ipaddress.ip_interface(vpn_address).network)}:
            raise InstallError("postinstall route delta mismatch")

    def observe(self) -> dict[str, object]:
        observation = self.resource_observer.collect_observation()
        self._assert_closed_candidates(observation)
        owned_hashes = {
            hashlib.sha256(name.encode("utf-8")).hexdigest()
            for name in self.OWNED_UNITS
        }
        foreign_systemd = [
            copy.deepcopy(item)
            for item in observation["systemd_projection"]
            if item.get("name_sha256") not in owned_hashes
        ]
        restart_count = self._run(
            next(
                item for item in self.RUNTIME_COMMANDS
                if "--format={{.RestartCount}}" in item
            ),
            "container restart count",
        )
        peers = self._run(
            next(item for item in self.RUNTIME_COMMANDS if "exec" in item),
            "AWG peers",
            allow_empty=True,
        )
        network_name = self._run(
            next(
                item for item in self.RUNTIME_COMMANDS
                if "network" in item and "inspect" in item
            ),
            "Docker network",
        )
        bot_enabled = self._run(
            next(
                item for item in self.RUNTIME_COMMANDS
                if "--property=UnitFileState" in item
            ),
            "bot enabled state",
        )
        bot_active = self._run(
            next(
                item for item in self.RUNTIME_COMMANDS
                if "--property=ActiveState" in item
            ),
            "bot active state",
        )
        if (
            restart_count != "0"
            or peers
            or network_name != "amn2-spain-net"
            or bot_enabled != "disabled"
            or bot_active != "inactive"
        ):
            raise InstallError("postinstall runtime state mismatch")
        self._database_is_clean()
        self._runtime_env_vps_apply_disabled()
        return {
            "runtime": {
                "database": "clean",
                "peer_count": 0,
                "vps_apply_enabled": False,
                "bot_enabled": False,
                "bot_running": False,
                "web_listener": "127.0.0.1:3031",
                "container_restart_count": int(restart_count),
            },
            "systemd_projection": foreign_systemd,
            "foreign_firewall": copy.deepcopy(observation["firewall"]["nft_json"]),
            "owned_objects": list(self.created_objects()),
            "unexpected_objects": [],
        }


class SharedInstallLockLease:
    """One non-reentrant lease shared by bootstrap, runtime, and recovery."""

    def __init__(self, lock_factory: Callable[[], ContextManager[Any]]) -> None:
        if not callable(lock_factory):
            raise InstallError("shared install lock dependency invalid")
        self._lock_factory = lock_factory
        self._held = False
        self._active_identity: object | None = None

    @property
    def active_identity(self) -> object | None:
        return self._active_identity

    def assert_held(self) -> None:
        if not self._held or self._active_identity is None:
            raise InstallError("shared install lock not held")

    @contextmanager
    def acquire(self):
        if self._held or self._active_identity is not None:
            raise InstallError("shared install lock already held")
        try:
            context = self._lock_factory()
            with context:
                identity = object()
                self._active_identity = identity
                self._held = True
                try:
                    yield self
                finally:
                    if self._active_identity is not identity or not self._held:
                        raise InstallError("shared install lock lease corrupted")
                    self._held = False
                    self._active_identity = None
        except InstallError:
            raise
        except Exception as exc:
            raise InstallError("shared install lock acquisition failed") from exc


@dataclass(frozen=True)
class PackageVerificationReport:
    archive_sha256: str
    archive_size: int
    manifest_sha256: str
    resource_plan_sha256: str
    run009_evidence_sha256: str
    fingerprint_array_sha256: str
    fingerprint_entry_count: int

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "PackageVerificationReport":
        expected = {
            "schema",
            "result",
            "archive_sha256",
            "archive_size",
            "manifest_sha256",
            "resource_plan_sha256",
            "run009_evidence_sha256",
            "fingerprint_array_sha256",
            "fingerprint_entry_count",
        }
        if not isinstance(value, dict) or set(value) != expected:
            raise InstallError("verified package report schema mismatch")
        if value["schema"] != "amn2.spain-package-verification.v1" or value["result"] != "passed":
            raise InstallError("verified package report result mismatch")
        for key in (
            "archive_sha256",
            "manifest_sha256",
            "resource_plan_sha256",
            "run009_evidence_sha256",
            "fingerprint_array_sha256",
        ):
            if not isinstance(value[key], str) or re.fullmatch(r"[0-9a-f]{64}", value[key]) is None:
                raise InstallError(f"verified package report {key} invalid")
        if value["fingerprint_entry_count"] != 148:
            raise InstallError("verified package report fingerprint count mismatch")
        if (
            not isinstance(value["archive_size"], int)
            or isinstance(value["archive_size"], bool)
            or value["archive_size"] <= 0
            or value["archive_size"] > ChecksumBoundPackageStager.MAX_ARCHIVE_BYTES
        ):
            raise InstallError("verified package report archive size invalid")
        return cls(
            archive_sha256=value["archive_sha256"],
            archive_size=value["archive_size"],
            manifest_sha256=value["manifest_sha256"],
            resource_plan_sha256=value["resource_plan_sha256"],
            run009_evidence_sha256=value["run009_evidence_sha256"],
            fingerprint_array_sha256=value["fingerprint_array_sha256"],
            fingerprint_entry_count=value["fingerprint_entry_count"],
        )


@dataclass(frozen=True)
class StagedPackage:
    path: Path
    size: int
    report: PackageVerificationReport
    directory_identity: tuple[int, int] = field(repr=False)
    file_identity: tuple[int, int] = field(repr=False)
    content_inventory: Mapping[str, Mapping[str, object]] = field(repr=False)
    prepared_source_path: Path
    prepared_source_inventory: Mapping[str, Mapping[str, object]] = field(repr=False)
    source_binding_sha256: str

    def __post_init__(self) -> None:
        if (
            not self.path.is_absolute()
            or not isinstance(self.size, int)
            or self.size <= 0
            or not isinstance(self.report, PackageVerificationReport)
            or len(self.directory_identity) != 2
            or len(self.file_identity) != 2
            or not isinstance(self.content_inventory, Mapping)
            or not self.content_inventory
            or not self.prepared_source_path.is_absolute()
            or not isinstance(self.prepared_source_inventory, Mapping)
            or not self.prepared_source_inventory
            or re.fullmatch(r"[0-9a-f]{64}", self.source_binding_sha256) is None
        ):
            raise InstallError("staged package result invalid")


class ChecksumBoundPackageStager:
    MAX_ARCHIVE_BYTES = 2 * 1024 * 1024 * 1024

    def __init__(
        self,
        *,
        host_root: Path = Path("/"),
        expected_uid: int | None = 0,
        expected_gid: int | None = 0,
    ) -> None:
        root = Path(host_root)
        parent = root / "opt"
        if (
            not root.is_absolute()
            or root.is_symlink()
            or not root.is_dir()
            or parent.is_symlink()
            or not parent.is_dir()
        ):
            raise InstallError("package staging root invalid")
        for value in (expected_uid, expected_gid):
            if value is not None and (
                not isinstance(value, int) or isinstance(value, bool) or value < 0
            ):
                raise InstallError("package staging owner invalid")
        self.package_root = parent / "amn2-spain-package"
        self.package_path = self.package_root / "package.tar"
        self.expected_uid = expected_uid
        self.expected_gid = expected_gid

    @staticmethod
    def _identity(info: os.stat_result) -> tuple[int, int]:
        return (int(info.st_dev), int(info.st_ino))

    def _cleanup_created(
        self,
        *,
        directory_identity: tuple[int, int],
        file_identity: tuple[int, int] | None,
        content_inventory: Mapping[str, Mapping[str, object]] | None = None,
        prepared_source_inventory: Mapping[str, Mapping[str, object]] | None = None,
    ) -> None:
        prepared_source = self.package_root / "prepared-source"
        if prepared_source.exists() or prepared_source.is_symlink():
            if prepared_source_inventory is None:
                raise InstallError("package staging cleanup CAS drift")
            self._remove_inventory_tree(
                prepared_source,
                prepared_source_inventory,
                label="prepared source",
            )
        content = self.package_root / "content"
        if content.exists() or content.is_symlink():
            if content_inventory is None:
                raise InstallError("package staging cleanup CAS drift")
            self._remove_inventory_tree(content, content_inventory, label="package content")
        if self.package_path.exists() or self.package_path.is_symlink():
            info = os.lstat(self.package_path)
            if (
                file_identity is None
                or self._identity(info) != file_identity
                or not stat.S_ISREG(info.st_mode)
            ):
                raise InstallError("package staging cleanup CAS drift")
            os.unlink(self.package_path)
        info = os.lstat(self.package_root)
        if (
            self._identity(info) != directory_identity
            or not stat.S_ISDIR(info.st_mode)
            or any(self.package_root.iterdir())
        ):
            raise InstallError("package staging cleanup CAS drift")
        os.rmdir(self.package_root)

    def _remove_inventory_tree(
        self,
        root: Path,
        inventory: Mapping[str, Mapping[str, object]],
        *,
        label: str,
    ) -> None:
        if root.is_symlink() or not root.is_dir():
            raise InstallError(f"{label} rollback CAS drift")
        expected_files = set(inventory)
        expected_directories: set[str] = set()
        for name in expected_files:
            path = Path(name)
            for parent in path.parents:
                if parent == Path("."):
                    break
                expected_directories.add(parent.as_posix())
        actual_files: set[str] = set()
        actual_directories: set[str] = set()
        for candidate in root.rglob("*"):
            relative = candidate.relative_to(root).as_posix()
            if candidate.is_symlink():
                raise InstallError(f"{label} rollback CAS drift")
            info = os.lstat(candidate)
            if stat.S_ISDIR(info.st_mode):
                actual_directories.add(relative)
                continue
            if not stat.S_ISREG(info.st_mode):
                raise InstallError(f"{label} rollback CAS drift")
            actual_files.add(relative)
            expected = inventory.get(relative)
            if not isinstance(expected, Mapping):
                raise InstallError(f"{label} rollback CAS drift")
            descriptor = os.open(
                candidate,
                os.O_RDONLY
                | getattr(os, "O_NOFOLLOW", 0)
                | getattr(os, "O_BINARY", 0),
            )
            try:
                digest = hashlib.sha256()
                size = 0
                while chunk := os.read(descriptor, 1024 * 1024):
                    digest.update(chunk)
                    size += len(chunk)
            finally:
                os.close(descriptor)
            if (
                size != expected.get("size")
                or digest.hexdigest() != expected.get("sha256")
                or (
                    os.name != "nt"
                    and stat.S_IMODE(info.st_mode) != 0o644
                )
            ):
                raise InstallError(f"{label} rollback CAS drift")
        if actual_files != expected_files or actual_directories != expected_directories:
            raise InstallError(f"{label} rollback CAS drift")
        for name in sorted(expected_files, key=lambda value: value.count("/"), reverse=True):
            os.unlink(root.joinpath(*Path(name).parts))
        for name in sorted(
            expected_directories,
            key=lambda value: value.count("/"),
            reverse=True,
        ):
            os.rmdir(root.joinpath(*Path(name).parts))
        os.rmdir(root)

    def stage(
        self,
        input_fd: int,
        *,
        expected_sha256: str,
        expected_size: int,
        transaction_ledger: "BootstrapTransactionLedger | None" = None,
    ) -> StagedPackage:
        if (
            not isinstance(input_fd, int)
            or isinstance(input_fd, bool)
            or not isinstance(expected_sha256, str)
            or re.fullmatch(r"[0-9a-f]{64}", expected_sha256) is None
            or not isinstance(expected_size, int)
            or isinstance(expected_size, bool)
            or expected_size <= 0
            or expected_size > self.MAX_ARCHIVE_BYTES
        ):
            raise InstallError("package staging input invalid")
        try:
            os.fstat(input_fd)
        except OSError as exc:
            raise InstallError("package staging input invalid") from exc
        if self.package_root.exists() or self.package_root.is_symlink():
            raise InstallError("package staging collision")
        if transaction_ledger is not None:
            if not isinstance(transaction_ledger, BootstrapTransactionLedger):
                raise InstallError("package staging transaction invalid")
            transaction = transaction_ledger.snapshot()
            if (
                transaction["status"] != "package_root_intent"
                or transaction["package"]["root"] != str(self.package_root)
                or transaction["package"]["path"] != str(self.package_path)
                or transaction["package"]["expected_sha256"] != expected_sha256
                or transaction["package"]["expected_size"] != expected_size
            ):
                raise InstallError("package staging transaction binding mismatch")
        descriptor = -1
        directory_identity: tuple[int, int] | None = None
        file_identity: tuple[int, int] | None = None
        content_inventory: Mapping[str, Mapping[str, object]] | None = None
        prepared_source_inventory: Mapping[str, Mapping[str, object]] | None = None
        source_binding_sha256: str | None = None
        try:
            os.mkdir(self.package_root, 0o700)
            if os.name != "nt" and (
                self.expected_uid is not None or self.expected_gid is not None
            ):
                os.chown(
                    self.package_root,
                    -1 if self.expected_uid is None else self.expected_uid,
                    -1 if self.expected_gid is None else self.expected_gid,
                    follow_symlinks=False,
                )
            directory_info = os.lstat(self.package_root)
            directory_identity = self._identity(directory_info)
            if transaction_ledger is not None:
                transaction_ledger.record_package_root(directory_identity)
                transaction_ledger.record_package_file_intent()
            descriptor = os.open(
                self.package_path,
                os.O_CREAT
                | os.O_EXCL
                | os.O_RDWR
                | getattr(os, "O_NOFOLLOW", 0)
                | getattr(os, "O_BINARY", 0),
                0o600,
            )
            file_identity = self._identity(os.fstat(descriptor))
            if transaction_ledger is not None:
                transaction_ledger.record_package_file(file_identity)
            digest = hashlib.sha256()
            size = 0
            while chunk := os.read(input_fd, 1024 * 1024):
                size += len(chunk)
                if size > expected_size:
                    raise InstallError("package staging size budget exceeded")
                digest.update(chunk)
                offset = 0
                while offset < len(chunk):
                    written = os.write(descriptor, chunk[offset:])
                    if written <= 0:
                        raise InstallError("short package staging write")
                    offset += written
            if size != expected_size or digest.hexdigest() != expected_sha256:
                raise InstallError("package staging checksum mismatch")
            if os.name != "nt":
                os.fchmod(descriptor, 0o600)
            if os.name != "nt" and (
                self.expected_uid is not None or self.expected_gid is not None
            ):
                os.fchown(
                    descriptor,
                    -1 if self.expected_uid is None else self.expected_uid,
                    -1 if self.expected_gid is None else self.expected_gid,
                )
            os.fsync(descriptor)
            if transaction_ledger is not None:
                transaction_ledger.record_package_bytes(
                    observed_size=size,
                    observed_sha256=digest.hexdigest(),
                )
            file_info = os.fstat(descriptor)
            file_identity = self._identity(file_info)
            if not stat.S_ISREG(file_info.st_mode) or file_info.st_size != size:
                raise InstallError("package staging file identity mismatch")
            os.lseek(descriptor, 0, os.SEEK_SET)
            try:
                report = PackageVerificationReport.from_mapping(
                    verify_package_fd(descriptor)
                )
            except (PackageVerificationError, InstallError) as exc:
                raise InstallError("staged package verification failed") from exc
            if report.archive_sha256 != expected_sha256:
                raise InstallError("staged package approval binding mismatch")
            if transaction_ledger is not None:
                transaction_ledger.record_package_verified(report)
            extraction_plan = plan_verified_package_extraction_fd(descriptor)
            planned_inventory = extraction_plan.get("inventory")
            if not isinstance(planned_inventory, Mapping):
                raise InstallError("staged package extraction plan invalid")
            content_inventory = planned_inventory
            if transaction_ledger is not None:
                transaction_ledger.record_extraction_plan(planned_inventory)
            extraction = extract_verified_package_fd(
                descriptor,
                self.package_root / "content",
                expected_uid=self.expected_uid,
                expected_gid=self.expected_gid,
                expected_inventory=planned_inventory,
            )
            if extraction.get("report") != {
                "schema": "amn2.spain-package-verification.v1",
                "result": "passed",
                "archive_sha256": report.archive_sha256,
                "archive_size": report.archive_size,
                "manifest_sha256": report.manifest_sha256,
                "resource_plan_sha256": report.resource_plan_sha256,
                "run009_evidence_sha256": report.run009_evidence_sha256,
                "fingerprint_array_sha256": report.fingerprint_array_sha256,
                "fingerprint_entry_count": report.fingerprint_entry_count,
            } or not isinstance(extraction.get("inventory"), Mapping):
                raise InstallError("staged package extraction binding mismatch")
            content_inventory = extraction["inventory"]
            if transaction_ledger is not None:
                transaction_ledger.record_package_extracted()
            source_binding = plan_verified_package_source(
                self.package_root / "content"
            )
            source_binding_sha256 = sha256_canonical(source_binding)
            prepared_source_inventory = source_binding.get("inventory")
            if not isinstance(prepared_source_inventory, Mapping):
                raise InstallError("staged package source plan invalid")
            if transaction_ledger is not None:
                transaction_ledger.record_source_preparation_plan(
                    source_binding_sha256=source_binding_sha256,
                    inventory=prepared_source_inventory,
                )
            source_result = expand_verified_package_source(
                self.package_root / "content",
                self.package_root / "prepared-source",
                expected_binding=source_binding,
            )
            if source_result.get("inventory") != prepared_source_inventory:
                raise InstallError("staged package prepared source binding mismatch")
            if transaction_ledger is not None:
                transaction_ledger.record_source_prepared()
            os.fsync(descriptor)
            if os.name != "nt":
                directory = os.open(self.package_root, os.O_RDONLY)
                try:
                    os.fsync(directory)
                finally:
                    os.close(directory)
            return StagedPackage(
                path=self.package_path,
                size=size,
                report=report,
                directory_identity=directory_identity,
                file_identity=file_identity,
                content_inventory=content_inventory,
                prepared_source_path=self.package_root / "prepared-source",
                prepared_source_inventory=prepared_source_inventory,
                source_binding_sha256=source_binding_sha256,
            )
        except Exception:
            if descriptor >= 0:
                os.close(descriptor)
                descriptor = -1
            if directory_identity is not None:
                try:
                    self._cleanup_created(
                        directory_identity=directory_identity,
                        file_identity=file_identity,
                        content_inventory=content_inventory,
                        prepared_source_inventory=prepared_source_inventory,
                    )
                except Exception:
                    if transaction_ledger is not None:
                        transaction_ledger.record_manual_recovery_required()
                    raise
            if transaction_ledger is not None:
                transaction_ledger.record_rolled_back()
            raise
        finally:
            if descriptor >= 0:
                os.close(descriptor)

    def rollback(self, staged: StagedPackage) -> None:
        if not isinstance(staged, StagedPackage) or staged.path != self.package_path:
            raise InstallError("staged package rollback binding mismatch")
        try:
            info = os.lstat(self.package_path)
            if (
                self._identity(info) != staged.file_identity
                or not stat.S_ISREG(info.st_mode)
                or info.st_size != staged.size
            ):
                raise InstallError("staged package rollback CAS drift")
            descriptor = os.open(
                self.package_path,
                os.O_RDONLY
                | getattr(os, "O_NOFOLLOW", 0)
                | getattr(os, "O_BINARY", 0),
            )
            try:
                digest = hashlib.sha256()
                while chunk := os.read(descriptor, 1024 * 1024):
                    digest.update(chunk)
            finally:
                os.close(descriptor)
            if digest.hexdigest() != staged.report.archive_sha256:
                raise InstallError("staged package rollback CAS drift")
            self._cleanup_created(
                directory_identity=staged.directory_identity,
                file_identity=staged.file_identity,
                content_inventory=staged.content_inventory,
                prepared_source_inventory=staged.prepared_source_inventory,
            )
        except InstallError:
            raise
        except OSError as exc:
            raise InstallError("staged package rollback failed") from exc

    def _recover_inventory_tree(
        self,
        root: Path,
        inventory: Mapping[str, Mapping[str, object]],
        *,
        require_complete: bool,
        label: str,
    ) -> None:
        if root.is_symlink() or not root.is_dir():
            raise InstallError(f"package recovery {label} CAS drift")
        actual_files: set[str] = set()
        actual_directories: set[str] = set()
        allowed_directories: set[str] = set()
        for name in inventory:
            for parent in Path(name).parents:
                if parent == Path("."):
                    break
                allowed_directories.add(parent.as_posix())
        for candidate in root.rglob("*"):
            relative = candidate.relative_to(root).as_posix()
            if candidate.is_symlink():
                raise InstallError(f"package recovery {label} CAS drift")
            info = os.lstat(candidate)
            if stat.S_ISDIR(info.st_mode):
                actual_directories.add(relative)
                continue
            if not stat.S_ISREG(info.st_mode) or relative not in inventory:
                raise InstallError(f"package recovery {label} CAS drift")
            actual_files.add(relative)
            if os.name != "nt" and stat.S_IMODE(info.st_mode) != 0o644:
                raise InstallError(f"package recovery {label} CAS drift")
            if require_complete:
                descriptor = os.open(
                    candidate,
                    os.O_RDONLY
                    | getattr(os, "O_NOFOLLOW", 0)
                    | getattr(os, "O_BINARY", 0),
                )
                try:
                    digest = hashlib.sha256()
                    size = 0
                    while chunk := os.read(descriptor, 1024 * 1024):
                        digest.update(chunk)
                        size += len(chunk)
                finally:
                    os.close(descriptor)
                expected = inventory[relative]
                if (
                    size != expected.get("size")
                    or digest.hexdigest() != expected.get("sha256")
                ):
                    raise InstallError(f"package recovery {label} CAS drift")
        if (
            not actual_files.issubset(set(inventory))
            or not actual_directories.issubset(allowed_directories)
            or (require_complete and actual_files != set(inventory))
        ):
            raise InstallError(f"package recovery {label} CAS drift")
        for name in sorted(
            actual_files, key=lambda value: value.count("/"), reverse=True
        ):
            os.unlink(root.joinpath(*Path(name).parts))
        for name in sorted(
            actual_directories, key=lambda value: value.count("/"), reverse=True
        ):
            os.rmdir(root.joinpath(*Path(name).parts))
        os.rmdir(root)

    def recover_or_rollback(
        self,
        transaction_ledger: "BootstrapTransactionLedger",
        lock_lease: SharedInstallLockLease,
        *,
        allow_manual_cleanup: bool = False,
    ) -> None:
        if (
            not isinstance(transaction_ledger, BootstrapTransactionLedger)
            or not isinstance(lock_lease, SharedInstallLockLease)
        ):
            raise InstallError("package recovery dependency invalid")
        lock_lease.assert_held()
        state = transaction_ledger.snapshot()
        package = state["package"]
        if (
            package["root"] != str(self.package_root)
            or package["path"] != str(self.package_path)
        ):
            raise InstallError("package recovery transaction binding mismatch")
        if state["status"] == "rolled_back":
            if self.package_root.exists() or self.package_root.is_symlink():
                raise InstallError("package recovery rolled-back state drift")
            return
        if state["status"] == "manual_recovery_required" and not allow_manual_cleanup:
            raise InstallError("package recovery requires manual intervention")
        try:
            if not self.package_root.exists() and not self.package_root.is_symlink():
                if state["status"] != "manual_recovery_required":
                    transaction_ledger.record_rolled_back()
                return
            root_info = os.lstat(self.package_root)
            recorded_root = package["root_identity"]
            if (
                self.package_root.is_symlink()
                or not stat.S_ISDIR(root_info.st_mode)
                or (
                    recorded_root is not None
                    and self._identity(root_info) != tuple(recorded_root)
                )
                or (
                    os.name != "nt"
                    and (
                        stat.S_IMODE(root_info.st_mode) != 0o700
                        or (
                            self.expected_uid is not None
                            and root_info.st_uid != self.expected_uid
                        )
                    )
                )
            ):
                raise InstallError("package recovery root CAS drift")
            children = {item.name for item in self.package_root.iterdir()}
            if not children.issubset({"package.tar", "content", "prepared-source"}):
                raise InstallError("package recovery unexpected object")
            prepared_source = self.package_root / "prepared-source"
            if prepared_source.exists() or prepared_source.is_symlink():
                source_inventory = package["prepared_source_inventory"]
                if not isinstance(source_inventory, Mapping):
                    raise InstallError("package recovery source intent missing")
                self._recover_inventory_tree(
                    prepared_source,
                    source_inventory,
                    require_complete=state["status"]
                    not in {"source_preparation_planned"},
                    label="prepared source",
                )
            content = self.package_root / "content"
            if content.exists() or content.is_symlink():
                inventory = package["extraction_inventory"]
                if not isinstance(inventory, Mapping):
                    raise InstallError("package recovery extraction intent missing")
                if content.is_symlink() or not content.is_dir():
                    raise InstallError("package recovery content CAS drift")
                actual_files: set[str] = set()
                actual_directories: set[str] = set()
                for candidate in content.rglob("*"):
                    relative = candidate.relative_to(content).as_posix()
                    if candidate.is_symlink():
                        raise InstallError("package recovery content CAS drift")
                    info = os.lstat(candidate)
                    if stat.S_ISDIR(info.st_mode):
                        actual_directories.add(relative)
                        continue
                    if not stat.S_ISREG(info.st_mode) or relative not in inventory:
                        raise InstallError("package recovery content CAS drift")
                    actual_files.add(relative)
                    if os.name != "nt" and stat.S_IMODE(info.st_mode) != 0o644:
                        raise InstallError("package recovery content CAS drift")
                    if state["status"] in {"package_extracted", "manual_recovery_required"}:
                        descriptor = os.open(
                            candidate,
                            os.O_RDONLY
                            | getattr(os, "O_NOFOLLOW", 0)
                            | getattr(os, "O_BINARY", 0),
                        )
                        try:
                            digest = hashlib.sha256()
                            size = 0
                            while chunk := os.read(descriptor, 1024 * 1024):
                                digest.update(chunk)
                                size += len(chunk)
                        finally:
                            os.close(descriptor)
                        expected = inventory[relative]
                        if (
                            size != expected.get("size")
                            or digest.hexdigest() != expected.get("sha256")
                        ):
                            raise InstallError("package recovery content CAS drift")
                allowed_directories: set[str] = set()
                for name in inventory:
                    for parent in Path(name).parents:
                        if parent == Path("."):
                            break
                        allowed_directories.add(parent.as_posix())
                if (
                    not actual_files.issubset(set(inventory))
                    or not actual_directories.issubset(allowed_directories)
                    or (
                        state["status"] in {"package_extracted", "manual_recovery_required"}
                        and actual_files != set(inventory)
                    )
                ):
                    raise InstallError("package recovery content CAS drift")
                for name in sorted(
                    actual_files, key=lambda value: value.count("/"), reverse=True
                ):
                    os.unlink(content.joinpath(*Path(name).parts))
                for name in sorted(
                    actual_directories,
                    key=lambda value: value.count("/"),
                    reverse=True,
                ):
                    os.rmdir(content.joinpath(*Path(name).parts))
                os.rmdir(content)
            if self.package_path.exists() or self.package_path.is_symlink():
                file_info = os.lstat(self.package_path)
                recorded_file = package["file_identity"]
                if (
                    self.package_path.is_symlink()
                    or not stat.S_ISREG(file_info.st_mode)
                    or (
                        recorded_file is not None
                        and self._identity(file_info) != tuple(recorded_file)
                    )
                    or (
                        os.name != "nt"
                        and (
                            stat.S_IMODE(file_info.st_mode) != 0o600
                            or (
                                self.expected_uid is not None
                                and file_info.st_uid != self.expected_uid
                            )
                        )
                    )
                ):
                    raise InstallError("package recovery file CAS drift")
                if package["observed_sha256"] is not None:
                    descriptor = os.open(
                        self.package_path,
                        os.O_RDONLY
                        | getattr(os, "O_NOFOLLOW", 0)
                        | getattr(os, "O_BINARY", 0),
                    )
                    try:
                        digest = hashlib.sha256()
                        size = 0
                        while chunk := os.read(descriptor, 1024 * 1024):
                            digest.update(chunk)
                            size += len(chunk)
                    finally:
                        os.close(descriptor)
                    if (
                        size != package["observed_size"]
                        or digest.hexdigest() != package["observed_sha256"]
                    ):
                        raise InstallError("package recovery file CAS drift")
                os.unlink(self.package_path)
            if any(self.package_root.iterdir()):
                raise InstallError("package recovery root not empty")
            os.rmdir(self.package_root)
            if state["status"] != "manual_recovery_required":
                transaction_ledger.record_rolled_back()
        except InstallError:
            if transaction_ledger.snapshot()["status"] != "manual_recovery_required":
                transaction_ledger.record_manual_recovery_required()
            raise
        except OSError as exc:
            if transaction_ledger.snapshot()["status"] != "manual_recovery_required":
                transaction_ledger.record_manual_recovery_required()
            raise InstallError("package recovery failed") from exc

    def manual_cleanup_terminal(
        self,
        transaction_ledger: "BootstrapTransactionLedger",
        lock_lease: SharedInstallLockLease,
    ) -> None:
        """Remove only a fully verified retained package from a terminal manual state."""
        if transaction_ledger.snapshot()["status"] != "manual_recovery_required":
            raise InstallError("manual cleanup terminal state required")
        self.recover_or_rollback(
            transaction_ledger,
            lock_lease,
            allow_manual_cleanup=True,
        )

@dataclass(frozen=True)
class InstallBoundaryIntent:
    """Hash-only operator intent consumed inside the remote executor.

    The raw boot identifier never crosses SSH or is persisted before the
    one-time authorization tombstone; it is read and verified on the target.
    """

    approval_id: str
    package_archive_sha256: str
    package_archive_size: int
    package_manifest_sha256: str
    resource_plan_sha256: str
    collector_sha256: str
    executor_sha256: str
    run009_evidence_sha256: str
    fingerprint_array_sha256: str
    expected_host_identity_sha256: str
    expected_boot_id_sha256: str
    endpoint_host: str
    nonce: str
    approved_at_epoch: int
    expires_at_epoch: int

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "InstallBoundaryIntent":
        fields = {
            "schema", "mutation_authorized", "approval_id", "package_archive_sha256",
            "package_archive_size", "package_manifest_sha256", "resource_plan_sha256",
            "collector_sha256", "executor_sha256", "run009_evidence_sha256",
            "fingerprint_array_sha256", "expected_host_identity_sha256",
            "expected_boot_id_sha256", "endpoint_host", "nonce", "approved_at_epoch",
            "expires_at_epoch",
        }
        if (
            not isinstance(value, dict)
            or set(value) != fields
            or value.get("schema") != "amn2.spain-install-boundary-intent.v1"
            or value.get("mutation_authorized") is not True
        ):
            raise InstallError("install boundary intent schema/result mismatch")
        for key in (
            "package_archive_sha256", "package_manifest_sha256", "resource_plan_sha256",
            "collector_sha256", "executor_sha256", "run009_evidence_sha256",
            "fingerprint_array_sha256", "expected_host_identity_sha256",
            "expected_boot_id_sha256", "nonce",
        ):
            if not isinstance(value[key], str) or re.fullmatch(r"[0-9a-f]{64}", value[key]) is None:
                raise InstallError(f"install boundary intent {key} invalid")
        if not isinstance(value["approval_id"], str) or not value["approval_id"]:
            raise InstallError("install boundary intent approval invalid")
        if (
            not isinstance(value["endpoint_host"], str)
            or re.fullmatch(
                r"(?=.{1,253}\Z)[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?",
                value["endpoint_host"],
            ) is None
            or ".." in value["endpoint_host"]
        ):
            raise InstallError("install boundary intent endpoint invalid")
        if (
            not isinstance(value["package_archive_size"], int)
            or isinstance(value["package_archive_size"], bool)
            or value["package_archive_size"] <= 0
            or value["package_archive_size"] > ChecksumBoundPackageStager.MAX_ARCHIVE_BYTES
        ):
            raise InstallError("install boundary intent package size invalid")
        if (
            not isinstance(value["approved_at_epoch"], int)
            or isinstance(value["approved_at_epoch"], bool)
            or not isinstance(value["expires_at_epoch"], int)
            or isinstance(value["expires_at_epoch"], bool)
            or value["expires_at_epoch"] <= value["approved_at_epoch"]
        ):
            raise InstallError("install boundary intent time window invalid")
        return cls(**{key: value[key] for key in fields - {"schema", "mutation_authorized"}})

    def to_authorization(
        self, precondition_receipt_sha256: str, boot_id: str
    ) -> "InstallAuthorization":
        if (
            not isinstance(precondition_receipt_sha256, str)
            or re.fullmatch(r"[0-9a-f]{64}", precondition_receipt_sha256) is None
            or not isinstance(boot_id, str)
            or re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", boot_id) is None
            or hashlib.sha256(boot_id.encode("ascii")).hexdigest()
            != self.expected_boot_id_sha256
        ):
            raise InstallError("install boundary intent boot identity mismatch")
        return InstallAuthorization.from_mapping(
            {
                "schema": "amn2.spain-install-authorization.v1",
                "mutation_authorized": True,
                "approval_id": self.approval_id,
                "precondition_receipt_sha256": precondition_receipt_sha256,
                "package_archive_sha256": self.package_archive_sha256,
                "package_archive_size": self.package_archive_size,
                "package_manifest_sha256": self.package_manifest_sha256,
                "resource_plan_sha256": self.resource_plan_sha256,
                "collector_sha256": self.collector_sha256,
                "executor_sha256": self.executor_sha256,
                "run009_evidence_sha256": self.run009_evidence_sha256,
                "fingerprint_array_sha256": self.fingerprint_array_sha256,
                "host_identity_sha256": self.expected_host_identity_sha256,
                "endpoint_host": self.endpoint_host,
                "boot_id": boot_id,
                "nonce": self.nonce,
                "approved_at_epoch": self.approved_at_epoch,
                "expires_at_epoch": self.expires_at_epoch,
            }
        )


@dataclass(frozen=True)
class ManualCleanupIntent:
    """One-use authorization for verified removal of a terminal package tree."""

    approval_id: str
    executor_sha256: str
    nonce: str
    approved_at_epoch: int
    expires_at_epoch: int

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "ManualCleanupIntent":
        fields = {
            "schema",
            "mutation_authorized",
            "approval_id",
            "executor_sha256",
            "nonce",
            "approved_at_epoch",
            "expires_at_epoch",
        }
        if (
            not isinstance(value, dict)
            or set(value) != fields
            or value.get("schema") != "amn2.spain-manual-cleanup-intent.v1"
            or value.get("mutation_authorized") is not True
        ):
            raise InstallError("manual cleanup intent schema/result mismatch")
        for key in ("executor_sha256", "nonce"):
            if (
                not isinstance(value[key], str)
                or re.fullmatch(r"[0-9a-f]{64}", value[key]) is None
            ):
                raise InstallError(f"manual cleanup intent {key} invalid")
        if not isinstance(value["approval_id"], str) or not value["approval_id"]:
            raise InstallError("manual cleanup intent approval invalid")
        if (
            not isinstance(value["approved_at_epoch"], int)
            or isinstance(value["approved_at_epoch"], bool)
            or not isinstance(value["expires_at_epoch"], int)
            or isinstance(value["expires_at_epoch"], bool)
            or value["expires_at_epoch"] <= value["approved_at_epoch"]
            or value["expires_at_epoch"] - value["approved_at_epoch"] > 300
        ):
            raise InstallError("manual cleanup intent time window invalid")
        return cls(
            approval_id=value["approval_id"],
            executor_sha256=value["executor_sha256"],
            nonce=value["nonce"],
            approved_at_epoch=value["approved_at_epoch"],
            expires_at_epoch=value["expires_at_epoch"],
        )


@dataclass(frozen=True)
class TerminalRecoveryIntent:
    """One-use authorization to replay a sealed terminal AMN2 rollback."""

    approval_id: str
    executor_sha256: str
    nonce: str
    transaction_sha256: str
    capsule_sha256: str
    docker_tree_sha256: str
    docker_tree_entry_count: int
    docker_tree_total_bytes: int
    approved_at_epoch: int
    expires_at_epoch: int

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "TerminalRecoveryIntent":
        fields = {
            "schema",
            "mutation_authorized",
            "approval_id",
            "executor_sha256",
            "nonce",
            "transaction_sha256",
            "capsule_sha256",
            "docker_tree_sha256",
            "docker_tree_entry_count",
            "docker_tree_total_bytes",
            "approved_at_epoch",
            "expires_at_epoch",
        }
        if (
            not isinstance(value, dict)
            or set(value) != fields
            or value.get("schema") != "amn2.spain-terminal-recovery-intent.v1"
            or value.get("mutation_authorized") is not True
        ):
            raise InstallError("terminal recovery intent schema/result mismatch")
        for key in (
            "executor_sha256",
            "nonce",
            "transaction_sha256",
            "capsule_sha256",
            "docker_tree_sha256",
        ):
            if (
                not isinstance(value[key], str)
                or re.fullmatch(r"[0-9a-f]{64}", value[key]) is None
            ):
                raise InstallError(f"terminal recovery intent {key} invalid")
        if not isinstance(value["approval_id"], str) or not value["approval_id"]:
            raise InstallError("terminal recovery intent approval invalid")
        for key, upper in (
            ("docker_tree_entry_count", 10_000),
            ("docker_tree_total_bytes", 2 * 1024 * 1024 * 1024),
        ):
            if (
                not isinstance(value[key], int)
                or isinstance(value[key], bool)
                or not 0 < value[key] <= upper
            ):
                raise InstallError(f"terminal recovery intent {key} invalid")
        if (
            not isinstance(value["approved_at_epoch"], int)
            or isinstance(value["approved_at_epoch"], bool)
            or not isinstance(value["expires_at_epoch"], int)
            or isinstance(value["expires_at_epoch"], bool)
            or value["expires_at_epoch"] <= value["approved_at_epoch"]
            or value["expires_at_epoch"] - value["approved_at_epoch"] > 300
        ):
            raise InstallError("terminal recovery intent time window invalid")
        return cls(
            approval_id=value["approval_id"],
            executor_sha256=value["executor_sha256"],
            nonce=value["nonce"],
            transaction_sha256=value["transaction_sha256"],
            capsule_sha256=value["capsule_sha256"],
            docker_tree_sha256=value["docker_tree_sha256"],
            docker_tree_entry_count=value["docker_tree_entry_count"],
            docker_tree_total_bytes=value["docker_tree_total_bytes"],
            approved_at_epoch=value["approved_at_epoch"],
            expires_at_epoch=value["expires_at_epoch"],
        )


@dataclass(frozen=True)
class InstallAuthorization:
    approval_id: str
    precondition_receipt_sha256: str
    package_archive_sha256: str
    package_archive_size: int
    package_manifest_sha256: str
    resource_plan_sha256: str
    collector_sha256: str
    executor_sha256: str
    run009_evidence_sha256: str
    fingerprint_array_sha256: str
    host_identity_sha256: str
    endpoint_host: str
    boot_id: str
    nonce: str
    approved_at_epoch: int
    expires_at_epoch: int

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "InstallAuthorization":
        fields = {
            "schema", "mutation_authorized", "approval_id", "precondition_receipt_sha256",
            "package_archive_sha256", "package_archive_size", "package_manifest_sha256", "resource_plan_sha256",
            "collector_sha256", "executor_sha256",
            "run009_evidence_sha256", "fingerprint_array_sha256", "host_identity_sha256",
            "endpoint_host", "boot_id", "nonce", "approved_at_epoch", "expires_at_epoch"
        }
        if not isinstance(value, dict) or set(value) != fields or value.get("schema") != "amn2.spain-install-authorization.v1" or value.get("mutation_authorized") is not True:
            raise InstallError("install authorization schema/result mismatch")
        for key in (
            "precondition_receipt_sha256", "package_archive_sha256", "package_manifest_sha256",
            "resource_plan_sha256", "collector_sha256", "executor_sha256",
            "run009_evidence_sha256", "fingerprint_array_sha256",
            "host_identity_sha256", "nonce"
        ):
            if not isinstance(value[key], str) or re.fullmatch(r"[0-9a-f]{64}", value[key]) is None:
                raise InstallError(f"install authorization {key} invalid")
        if not isinstance(value["approval_id"], str) or not value["approval_id"] or re.fullmatch(
            r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", value["boot_id"]
        ) is None:
            raise InstallError("install authorization identity invalid")
        if (
            not isinstance(value["endpoint_host"], str)
            or re.fullmatch(
                r"(?=.{1,253}\Z)[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?",
                value["endpoint_host"],
            )
            is None
            or ".." in value["endpoint_host"]
        ):
            raise InstallError("install authorization endpoint invalid")
        if not isinstance(value["approved_at_epoch"], int) or not isinstance(value["expires_at_epoch"], int) or value["expires_at_epoch"] <= value["approved_at_epoch"]:
            raise InstallError("install authorization time window invalid")
        if (
            not isinstance(value["package_archive_size"], int)
            or isinstance(value["package_archive_size"], bool)
            or value["package_archive_size"] <= 0
            or value["package_archive_size"] > ChecksumBoundPackageStager.MAX_ARCHIVE_BYTES
        ):
            raise InstallError("install authorization package size invalid")
        return cls(**{key: value[key] for key in fields - {"schema", "mutation_authorized"}})

    @classmethod
    def from_tombstone_mapping(
        cls, value: dict[str, Any]
    ) -> "InstallAuthorization":
        if (
            not isinstance(value, dict)
            or value.get("schema")
            != "amn2.spain-install-authorization-tombstone.v1"
            or value.get("mutation_authorized") is not True
        ):
            raise InstallError("install authorization tombstone invalid")
        restored = copy.deepcopy(value)
        restored["schema"] = "amn2.spain-install-authorization.v1"
        try:
            return cls.from_mapping(restored)
        except InstallError as exc:
            raise InstallError("install authorization tombstone invalid") from exc

    def tombstone_mapping(self) -> dict[str, Any]:
        return {
            "schema": "amn2.spain-install-authorization-tombstone.v1",
            "mutation_authorized": True,
            "approval_id": self.approval_id,
            "precondition_receipt_sha256": self.precondition_receipt_sha256,
            "package_archive_sha256": self.package_archive_sha256,
            "package_archive_size": self.package_archive_size,
            "package_manifest_sha256": self.package_manifest_sha256,
            "resource_plan_sha256": self.resource_plan_sha256,
            "collector_sha256": self.collector_sha256,
            "executor_sha256": self.executor_sha256,
            "run009_evidence_sha256": self.run009_evidence_sha256,
            "fingerprint_array_sha256": self.fingerprint_array_sha256,
            "host_identity_sha256": self.host_identity_sha256,
            "endpoint_host": self.endpoint_host,
            "boot_id": self.boot_id,
            "nonce": self.nonce,
            "approved_at_epoch": self.approved_at_epoch,
            "expires_at_epoch": self.expires_at_epoch,
        }


def _build_in_memory_install_inputs(
    *,
    intent: InstallBoundaryIntent,
    observation: dict[str, Any],
    host_identity_sha256: str,
    boot_id: str,
    resource_plan: dict[str, Any],
    baseline_value: dict[str, Any],
    now_epoch: int,
) -> tuple[dict[str, object], str, dict[str, Any], InstallAuthorization]:
    if (
        not isinstance(intent, InstallBoundaryIntent)
        or not isinstance(observation, dict)
        or not isinstance(resource_plan, dict)
        or not isinstance(baseline_value, dict)
        or not isinstance(now_epoch, int)
        or host_identity_sha256 != intent.expected_host_identity_sha256
    ):
        raise InstallError("install boundary input binding mismatch")
    try:
        report = validate_preconditions(observation, resource_plan, baseline_value)
        receipt, detached = build_precondition_receipt(
            report,
            package_manifest_sha256=intent.package_manifest_sha256,
            resource_plan_sha256=intent.resource_plan_sha256,
            host_identity_sha256=host_identity_sha256,
            boot_id=boot_id,
            collector_sha256=intent.collector_sha256,
            executor_sha256=intent.executor_sha256,
            package_archive_sha256=intent.package_archive_sha256,
            package_archive_size=intent.package_archive_size,
            issued_at_epoch=now_epoch,
            ttl_seconds=300,
            nonce=intent.nonce,
        )
    except PreconditionError as exc:
        raise InstallError("install boundary precondition failed") from exc
    authorization = intent.to_authorization(detached, boot_id)
    return receipt, detached, copy.deepcopy(baseline_value), authorization


def _build_in_memory_install_inputs_from_evidence(
    *, intent: InstallBoundaryIntent, evidence: dict[str, Any], boot_id: str, now_epoch: int
) -> tuple[dict[str, object], str, dict[str, Any], InstallAuthorization]:
    if not isinstance(intent, InstallBoundaryIntent) or not isinstance(evidence, dict):
        raise InstallError("install boundary evidence invalid")
    try:
        host_identity = evidence["host_identity"]
        host_identity_sha256 = host_identity["machine_id_sha256"]
        boot_id_sha256 = host_identity["boot_id_sha256"]
    except (KeyError, TypeError) as exc:
        raise InstallError("install boundary evidence invalid") from exc
    if (
        host_identity_sha256 != intent.expected_host_identity_sha256
        or boot_id_sha256 != hashlib.sha256(boot_id.encode("ascii")).hexdigest()
        or boot_id_sha256 != intent.expected_boot_id_sha256
    ):
        raise InstallError("install boundary host identity mismatch")
    try:
        observation = observation_from_resource_confirmation_evidence(evidence)
    except PreconditionError as exc:
        raise InstallError("install boundary evidence invalid") from exc
    return _build_in_memory_install_inputs(
        intent=intent,
        observation=observation,
        host_identity_sha256=host_identity_sha256,
        boot_id=boot_id,
        resource_plan=_embedded_resource_plan(),
        baseline_value=_embedded_run009_baseline(),
        now_epoch=now_epoch,
    )


class RetainedAuthorizationStore:
    """Atomic no-replace tombstones retained outside the rollback tree."""

    def __init__(self, audit_root: Path, *, expected_uid: int | None = 0) -> None:
        root = Path(audit_root)
        if not root.is_absolute() or root.name != "phase12-audit" and root.name != "amn2-spain-phase12-audit":
            raise InstallError("retained authorization root invalid")
        if expected_uid is not None and (
            not isinstance(expected_uid, int) or isinstance(expected_uid, bool) or expected_uid < 0
        ):
            raise InstallError("retained authorization owner invalid")
        if root.parent.is_symlink() or not root.parent.is_dir():
            raise InstallError("retained authorization parent invalid")
        if root.is_symlink():
            raise InstallError("retained authorization root unsafe")
        self.root = root
        self.expected_uid = expected_uid
        if root.exists():
            self._validate_root()

    def _validate_root(self) -> None:
        try:
            info = os.lstat(self.root)
        except OSError as exc:
            raise InstallError("retained authorization root unavailable") from exc
        if (
            not stat.S_ISDIR(info.st_mode)
            or (
                os.name != "nt"
                and (
                    stat.S_IMODE(info.st_mode) != 0o700
                    or (
                        self.expected_uid is not None
                        and info.st_uid != self.expected_uid
                    )
                )
            )
        ):
            raise InstallError("retained authorization root owner/mode/type mismatch")

    def _ensure_root(self) -> None:
        if self.root.is_symlink():
            raise InstallError("retained authorization root unsafe")
        if not self.root.exists():
            try:
                os.mkdir(self.root, 0o700)
            except OSError as exc:
                raise InstallError("retained authorization root creation failed") from exc
            if os.name != "nt":
                directory = os.open(self.root.parent, os.O_RDONLY)
                try:
                    os.fsync(directory)
                finally:
                    os.close(directory)
        self._validate_root()

    def _fsync_root(self) -> None:
        if os.name == "nt":
            return
        descriptor = os.open(self.root, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)

    def consume(self, authorization: InstallAuthorization) -> Path:
        if not isinstance(authorization, InstallAuthorization):
            raise InstallError("retained authorization value invalid")
        self._ensure_root()
        final = self.root / ("authorization-" + authorization.nonce + ".json")
        temporary = self.root / ("." + final.name + ".tmp")
        if final.is_symlink() or temporary.is_symlink():
            raise InstallError("retained authorization tombstone unsafe")
        payload = (
            json.dumps(
                authorization.tombstone_mapping(),
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
            + b"\n"
        )
        final_preexisted = final.exists()
        if temporary.exists():
            self._verify_payload_file(temporary, payload)
            if final_preexisted:
                self._verify_payload_file(final, payload)
                try:
                    os.unlink(temporary)
                except OSError as exc:
                    raise InstallError(
                        "retained authorization stale temporary cleanup failed"
                    ) from exc
                self._fsync_root()
                raise InstallError("install authorization nonce already consumed")
            try:
                os.link(temporary, final)
            except FileExistsError:
                final_preexisted = True
            except OSError as exc:
                raise InstallError(
                    "retained authorization temporary promotion failed"
                ) from exc
            self._fsync_root()
            self._verify_payload_file(final, payload)
            try:
                os.unlink(temporary)
            except OSError as exc:
                raise InstallError(
                    "retained authorization temporary cleanup failed"
                ) from exc
            self._fsync_root()
            if final_preexisted:
                raise InstallError("install authorization nonce already consumed")
            return final
        if final_preexisted:
            self._verify_payload_file(final, payload)
            raise InstallError("install authorization nonce already consumed")
        descriptor = -1
        try:
            descriptor = os.open(
                temporary,
                os.O_WRONLY
                | os.O_CREAT
                | os.O_EXCL
                | getattr(os, "O_NOFOLLOW", 0)
                | getattr(os, "O_BINARY", 0),
                0o600,
            )
            if os.name != "nt":
                os.fchmod(descriptor, 0o600)
            offset = 0
            while offset < len(payload):
                written = os.write(descriptor, payload[offset:])
                if written <= 0:
                    raise InstallError("short retained authorization write")
                offset += written
            os.fsync(descriptor)
            os.close(descriptor)
            descriptor = -1
            try:
                os.link(temporary, final)
            except FileExistsError as exc:
                raise InstallError("install authorization nonce already consumed") from exc
            self._fsync_root()
            os.unlink(temporary)
            self._fsync_root()
        except InstallError:
            raise
        except OSError as exc:
            raise InstallError("retained authorization tombstone write failed") from exc
        finally:
            if descriptor >= 0:
                os.close(descriptor)
            if temporary.exists():
                try:
                    os.unlink(temporary)
                except OSError:
                    pass
        self._verify_payload_file(final, payload)
        return final

    def _verify_payload_file(self, path: Path, payload: bytes) -> None:
        flags = (
            os.O_RDONLY
            | getattr(os, "O_NOFOLLOW", 0)
            | getattr(os, "O_BINARY", 0)
        )
        try:
            descriptor = os.open(path, flags)
            try:
                info = os.fstat(descriptor)
                observed = os.read(descriptor, len(payload) + 1)
            finally:
                os.close(descriptor)
        except OSError as exc:
            raise InstallError("retained authorization tombstone verification failed") from exc
        if (
            observed != payload
            or not stat.S_ISREG(info.st_mode)
            or (
                os.name != "nt"
                and (
                    stat.S_IMODE(info.st_mode) != 0o600
                    or (self.expected_uid is not None and info.st_uid != self.expected_uid)
                )
            )
        ):
            raise InstallError("retained authorization tombstone verification failed")

    def open_consumed(self, authorization: InstallAuthorization) -> Path:
        if not isinstance(authorization, InstallAuthorization):
            raise InstallError("retained authorization value invalid")
        final = self.root / ("authorization-" + authorization.nonce + ".json")
        payload = (
            json.dumps(
                authorization.tombstone_mapping(),
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
            + b"\n"
        )
        if final.is_symlink() or not final.is_file():
            raise InstallError("retained authorization tombstone unavailable")
        self._verify_payload_file(final, payload)
        return final


class BootstrapTransactionLedger:
    """Durable bootstrap intents and identities used by fresh-process recovery."""

    SCHEMA = "amn2.spain-bootstrap-transaction.v1"
    MAX_STATE_BYTES = 16 * 1024 * 1024

    def __init__(
        self,
        *,
        path: Path,
        state: dict[str, Any],
        expected_uid: int | None,
    ) -> None:
        self.path = Path(path)
        self._state = copy.deepcopy(state)
        self.expected_uid = expected_uid
        self._validate_state(self._state)

    @staticmethod
    def _canonical(value: Mapping[str, Any]) -> bytes:
        return (
            json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
            + b"\n"
        )

    @classmethod
    def open_or_create_for_authorization(
        cls,
        *,
        authorization_store: RetainedAuthorizationStore,
        authorization: InstallAuthorization,
        package_root: Path,
        lock_lease: SharedInstallLockLease,
    ) -> tuple[Path, "BootstrapTransactionLedger", bool]:
        if (
            not isinstance(authorization_store, RetainedAuthorizationStore)
            or not isinstance(authorization, InstallAuthorization)
            or not isinstance(lock_lease, SharedInstallLockLease)
        ):
            raise InstallError("bootstrap transaction recovery dependency invalid")
        lock_lease.assert_held()
        expected_tombstone = authorization_store.root / (
            "authorization-" + authorization.nonce + ".json"
        )
        if expected_tombstone.exists() or expected_tombstone.is_symlink():
            tombstone = authorization_store.open_consumed(authorization)
        else:
            tombstone = authorization_store.consume(authorization)
        transaction_path = authorization_store.root / (
            "transaction-" + authorization.nonce + ".json"
        )
        if transaction_path.exists() or transaction_path.is_symlink() or (
            transaction_path.parent / ("." + transaction_path.name + ".tmp")
        ).exists():
            ledger = cls.open_existing(
                audit_root=authorization_store.root,
                nonce=authorization.nonce,
                expected_uid=authorization_store.expected_uid,
            )
            state = ledger.snapshot()
            if (
                state["package"]["root"] != str(Path(package_root))
                or state["package"]["expected_sha256"]
                != authorization.package_archive_sha256
                or state["package"]["expected_size"]
                != authorization.package_archive_size
            ):
                raise InstallError("bootstrap transaction recovery binding mismatch")
            return tombstone, ledger, True
        ledger = cls.create(
            authorization=authorization,
            tombstone=tombstone,
            package_root=Path(package_root),
            expected_uid=authorization_store.expected_uid,
        )
        return tombstone, ledger, False

    @classmethod
    def create(
        cls,
        *,
        authorization: InstallAuthorization,
        tombstone: Path,
        package_root: Path,
        expected_uid: int | None = 0,
    ) -> "BootstrapTransactionLedger":
        if not isinstance(authorization, InstallAuthorization):
            raise InstallError("bootstrap transaction authorization invalid")
        tombstone = Path(tombstone)
        package_root = Path(package_root)
        if (
            not tombstone.is_absolute()
            or tombstone.name != "authorization-" + authorization.nonce + ".json"
            or not package_root.is_absolute()
            or package_root.name != "amn2-spain-package"
            or package_root.parent.name != "opt"
        ):
            raise InstallError("bootstrap transaction binding invalid")
        expected_tombstone = cls._canonical(authorization.tombstone_mapping())
        try:
            observed_tombstone = tombstone.read_bytes()
        except OSError as exc:
            raise InstallError("bootstrap transaction tombstone unavailable") from exc
        if observed_tombstone != expected_tombstone:
            raise InstallError("bootstrap transaction tombstone mismatch")
        path = tombstone.parent / ("transaction-" + authorization.nonce + ".json")
        if path.exists() or path.is_symlink():
            raise InstallError("bootstrap transaction already exists")
        state: dict[str, Any] = {
            "schema": cls.SCHEMA,
            "generation": 0,
            "previous_state_sha256": "0" * 64,
            "nonce": authorization.nonce,
            "authorization_tombstone": tombstone.name,
            "authorization_tombstone_sha256": hashlib.sha256(
                observed_tombstone
            ).hexdigest(),
            "status": "package_root_intent",
            "package": {
                "root": str(package_root),
                "path": str(package_root / "package.tar"),
                "expected_sha256": authorization.package_archive_sha256,
                "expected_size": authorization.package_archive_size,
                "root_identity": None,
                "file_identity": None,
                "observed_sha256": None,
                "observed_size": None,
                "verification_report": None,
                "extraction_inventory": None,
                "prepared_source_inventory": None,
                "prepared_source_binding_sha256": None,
            },
            "action_blueprint_sha256": None,
            "recovery_capsule_sha256": None,
        }
        ledger = cls(path=path, state=state, expected_uid=expected_uid)
        ledger._write_state(state, create=True)
        return ledger

    @classmethod
    def open_existing(
        cls,
        *,
        audit_root: Path,
        nonce: str,
        expected_uid: int | None = 0,
    ) -> "BootstrapTransactionLedger":
        root = Path(audit_root)
        if (
            not root.is_absolute()
            or root.is_symlink()
            or not root.is_dir()
            or not isinstance(nonce, str)
            or re.fullmatch(r"[0-9a-f]{64}", nonce) is None
        ):
            raise InstallError("bootstrap transaction lookup invalid")
        path = root / ("transaction-" + nonce + ".json")
        cls._reconcile_temporary(
            path,
            nonce=nonce,
            expected_uid=expected_uid,
        )
        state = cls._read_state_file(path, expected_uid=expected_uid)
        if state.get("nonce") != nonce:
            raise InstallError("bootstrap transaction nonce mismatch")
        tombstone = root / str(state.get("authorization_tombstone", ""))
        try:
            tombstone_bytes = tombstone.read_bytes()
        except OSError as exc:
            raise InstallError("bootstrap transaction tombstone unavailable") from exc
        if hashlib.sha256(tombstone_bytes).hexdigest() != state.get(
            "authorization_tombstone_sha256"
        ):
            raise InstallError("bootstrap transaction tombstone mismatch")
        return cls(path=path, state=state, expected_uid=expected_uid)

    @classmethod
    def _reconcile_temporary(
        cls,
        path: Path,
        *,
        nonce: str,
        expected_uid: int | None,
    ) -> None:
        temporary = path.parent / ("." + path.name + ".tmp")
        if not temporary.exists() and not temporary.is_symlink():
            return
        temporary_state = cls._read_state_file(
            temporary,
            expected_uid=expected_uid,
        )
        if temporary_state.get("nonce") != nonce:
            raise InstallError("bootstrap transaction temporary nonce mismatch")
        if not path.exists() and not path.is_symlink():
            try:
                os.replace(temporary, path)
            except OSError as exc:
                raise InstallError(
                    "bootstrap transaction temporary promotion failed"
                ) from exc
            cls._fsync_directory(path.parent)
            return
        current_state = cls._read_state_file(path, expected_uid=expected_uid)
        if current_state.get("nonce") != nonce:
            raise InstallError("bootstrap transaction nonce mismatch")
        temporary_generation = temporary_state["generation"]
        current_generation = current_state["generation"]
        if (
            temporary_generation == current_generation + 1
            and temporary_state["previous_state_sha256"]
            == hashlib.sha256(cls._canonical(current_state)).hexdigest()
        ):
            try:
                os.replace(temporary, path)
            except OSError as exc:
                raise InstallError(
                    "bootstrap transaction temporary promotion failed"
                ) from exc
            cls._fsync_directory(path.parent)
            return
        if temporary_generation <= current_generation:
            try:
                os.unlink(temporary)
            except OSError as exc:
                raise InstallError(
                    "bootstrap transaction stale temporary cleanup failed"
                ) from exc
            cls._fsync_directory(path.parent)
            return
        raise InstallError("bootstrap transaction temporary chain mismatch")

    @staticmethod
    def _fsync_directory(path: Path) -> None:
        if os.name == "nt":
            return
        descriptor = os.open(path, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)

    @classmethod
    def _read_state_file(
        cls, path: Path, *, expected_uid: int | None
    ) -> dict[str, Any]:
        flags = (
            os.O_RDONLY
            | getattr(os, "O_NOFOLLOW", 0)
            | getattr(os, "O_BINARY", 0)
        )
        try:
            descriptor = os.open(path, flags)
            try:
                info = os.fstat(descriptor)
                payload = os.read(descriptor, cls.MAX_STATE_BYTES + 1)
            finally:
                os.close(descriptor)
        except OSError as exc:
            raise InstallError("bootstrap transaction unavailable") from exc
        if (
            len(payload) > cls.MAX_STATE_BYTES
            or not stat.S_ISREG(info.st_mode)
            or (
                os.name != "nt"
                and (
                    stat.S_IMODE(info.st_mode) != 0o600
                    or (expected_uid is not None and info.st_uid != expected_uid)
                )
            )
        ):
            raise InstallError("bootstrap transaction file invalid")
        try:
            state = json.loads(payload)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise InstallError("bootstrap transaction JSON invalid") from exc
        if not isinstance(state, dict) or cls._canonical(state) != payload:
            raise InstallError("bootstrap transaction canonical form invalid")
        cls._validate_state(state)
        return state

    @classmethod
    def _validate_state(cls, state: Mapping[str, Any]) -> None:
        if set(state) != {
            "schema",
            "generation",
            "previous_state_sha256",
            "nonce",
            "authorization_tombstone",
            "authorization_tombstone_sha256",
            "status",
            "package",
            "action_blueprint_sha256",
            "recovery_capsule_sha256",
        }:
            raise InstallError("bootstrap transaction schema mismatch")
        if (
            state.get("schema") != cls.SCHEMA
            or not isinstance(state.get("generation"), int)
            or isinstance(state.get("generation"), bool)
            or state["generation"] < 0
            or not isinstance(state.get("nonce"), str)
            or re.fullmatch(r"[0-9a-f]{64}", state["nonce"]) is None
            or any(
                not isinstance(state.get(key), str)
                or re.fullmatch(r"[0-9a-f]{64}", state[key]) is None
                for key in (
                    "previous_state_sha256",
                    "authorization_tombstone_sha256",
                )
            )
        ):
            raise InstallError("bootstrap transaction identity invalid")
        if state.get("authorization_tombstone") != (
            "authorization-" + state["nonce"] + ".json"
        ):
            raise InstallError("bootstrap transaction tombstone binding invalid")
        package = state.get("package")
        if not isinstance(package, Mapping) or set(package) != {
            "root",
            "path",
            "expected_sha256",
            "expected_size",
            "root_identity",
            "file_identity",
            "observed_sha256",
            "observed_size",
            "verification_report",
            "extraction_inventory",
            "prepared_source_inventory",
            "prepared_source_binding_sha256",
        }:
            raise InstallError("bootstrap transaction package schema mismatch")
        root = Path(str(package.get("root", "")))
        path = Path(str(package.get("path", "")))
        if (
            not root.is_absolute()
            or root.name != "amn2-spain-package"
            or root.parent.name != "opt"
            or path != root / "package.tar"
            or not isinstance(package.get("expected_sha256"), str)
            or re.fullmatch(r"[0-9a-f]{64}", package["expected_sha256"]) is None
            or not isinstance(package.get("expected_size"), int)
            or isinstance(package.get("expected_size"), bool)
            or package["expected_size"] <= 0
            or package["expected_size"] > ChecksumBoundPackageStager.MAX_ARCHIVE_BYTES
        ):
            raise InstallError("bootstrap transaction package binding invalid")
        allowed_statuses = {
            "package_root_intent",
            "package_root_created",
            "package_file_intent",
            "package_file_created",
            "package_bytes_staged",
            "package_verified",
            "extraction_planned",
            "package_extracted",
            "source_preparation_planned",
            "source_prepared",
            "capsule_committed",
            "runtime_started",
            "rollback_required",
            "rolled_back",
            "manual_recovery_required",
        }
        if state.get("status") not in allowed_statuses:
            raise InstallError("bootstrap transaction status invalid")
        for key in ("root_identity", "file_identity"):
            identity = package.get(key)
            if identity is not None and (
                not isinstance(identity, list)
                or len(identity) != 2
                or any(
                    not isinstance(value, int) or isinstance(value, bool) or value < 0
                    for value in identity
                )
            ):
                raise InstallError("bootstrap transaction inode identity invalid")
        for key in ("action_blueprint_sha256", "recovery_capsule_sha256"):
            value = state.get(key)
            if value is not None and (
                not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None
            ):
                raise InstallError("bootstrap transaction digest invalid")

    def _write_state(self, state: dict[str, Any], *, create: bool = False) -> None:
        payload = self._canonical(state)
        if len(payload) > self.MAX_STATE_BYTES:
            raise InstallError("bootstrap transaction state too large")
        temporary = self.path.parent / ("." + self.path.name + ".tmp")
        descriptor = -1
        try:
            descriptor = os.open(
                temporary,
                os.O_WRONLY
                | os.O_CREAT
                | os.O_EXCL
                | getattr(os, "O_NOFOLLOW", 0)
                | getattr(os, "O_BINARY", 0),
                0o600,
            )
            if os.name != "nt":
                os.fchmod(descriptor, 0o600)
            offset = 0
            while offset < len(payload):
                written = os.write(descriptor, payload[offset:])
                if written <= 0:
                    raise InstallError("short bootstrap transaction write")
                offset += written
            os.fsync(descriptor)
            os.close(descriptor)
            descriptor = -1
            if create:
                try:
                    os.link(temporary, self.path)
                except FileExistsError as exc:
                    raise InstallError("bootstrap transaction already exists") from exc
                os.unlink(temporary)
            else:
                os.replace(temporary, self.path)
            if os.name != "nt":
                directory = os.open(self.path.parent, os.O_RDONLY)
                try:
                    os.fsync(directory)
                finally:
                    os.close(directory)
        except InstallError:
            raise
        except OSError as exc:
            raise InstallError("bootstrap transaction write failed") from exc
        finally:
            if descriptor >= 0:
                os.close(descriptor)
            if temporary.exists():
                try:
                    temporary.unlink()
                except OSError:
                    pass

    def snapshot(self) -> dict[str, Any]:
        return copy.deepcopy(self._state)

    def _advance(
        self,
        expected_status: str,
        next_status: str,
        mutate: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        if self._state["status"] != expected_status:
            raise InstallError("bootstrap transaction transition invalid")
        next_state = copy.deepcopy(self._state)
        next_state["generation"] += 1
        next_state["previous_state_sha256"] = hashlib.sha256(
            self._canonical(self._state)
        ).hexdigest()
        next_state["status"] = next_status
        if mutate is not None:
            mutate(next_state)
        self._validate_state(next_state)
        self._write_state(next_state)
        self._state = next_state

    @staticmethod
    def _valid_identity(identity: tuple[int, int]) -> list[int]:
        if (
            not isinstance(identity, tuple)
            or len(identity) != 2
            or any(
                not isinstance(value, int) or isinstance(value, bool) or value < 0
                for value in identity
            )
        ):
            raise InstallError("bootstrap transaction inode identity invalid")
        return [identity[0], identity[1]]

    def record_package_root(self, identity: tuple[int, int]) -> None:
        value = self._valid_identity(identity)
        self._advance(
            "package_root_intent",
            "package_root_created",
            lambda state: state["package"].__setitem__("root_identity", value),
        )

    def record_package_file_intent(self) -> None:
        self._advance("package_root_created", "package_file_intent")

    def record_package_file(self, identity: tuple[int, int]) -> None:
        value = self._valid_identity(identity)
        self._advance(
            "package_file_intent",
            "package_file_created",
            lambda state: state["package"].__setitem__("file_identity", value),
        )

    def record_package_bytes(
        self, *, observed_size: int, observed_sha256: str
    ) -> None:
        package = self._state["package"]
        if (
            observed_size != package["expected_size"]
            or observed_sha256 != package["expected_sha256"]
        ):
            raise InstallError("bootstrap transaction package bytes mismatch")

        def mutate(state: dict[str, Any]) -> None:
            state["package"]["observed_size"] = observed_size
            state["package"]["observed_sha256"] = observed_sha256

        self._advance("package_file_created", "package_bytes_staged", mutate)

    @staticmethod
    def _report_mapping(report: PackageVerificationReport) -> dict[str, Any]:
        return {
            "schema": "amn2.spain-package-verification.v1",
            "result": "passed",
            "archive_sha256": report.archive_sha256,
            "archive_size": report.archive_size,
            "manifest_sha256": report.manifest_sha256,
            "resource_plan_sha256": report.resource_plan_sha256,
            "run009_evidence_sha256": report.run009_evidence_sha256,
            "fingerprint_array_sha256": report.fingerprint_array_sha256,
            "fingerprint_entry_count": report.fingerprint_entry_count,
        }

    def record_package_verified(self, report: PackageVerificationReport) -> None:
        if (
            not isinstance(report, PackageVerificationReport)
            or report.archive_sha256 != self._state["package"]["expected_sha256"]
            or report.archive_size != self._state["package"]["expected_size"]
        ):
            raise InstallError("bootstrap transaction package report mismatch")
        mapping = self._report_mapping(report)
        self._advance(
            "package_bytes_staged",
            "package_verified",
            lambda state: state["package"].__setitem__(
                "verification_report", mapping
            ),
        )

    @staticmethod
    def _validate_inventory(
        inventory: Mapping[str, Mapping[str, object]],
    ) -> dict[str, dict[str, object]]:
        if not isinstance(inventory, Mapping) or not inventory:
            raise InstallError("bootstrap transaction extraction inventory invalid")
        sealed: dict[str, dict[str, object]] = {}
        for name, item in inventory.items():
            if (
                not isinstance(name, str)
                or not name
                or name.startswith(("/", "\\"))
                or "\\" in name
                or ".." in Path(name).parts
                or not isinstance(item, Mapping)
                or set(item) != {"sha256", "size", "mode"}
                or not isinstance(item.get("sha256"), str)
                or re.fullmatch(r"[0-9a-f]{64}", str(item["sha256"])) is None
                or not isinstance(item.get("size"), int)
                or isinstance(item.get("size"), bool)
                or item["size"] < 0
                or item.get("mode") != "0644"
            ):
                raise InstallError("bootstrap transaction extraction inventory invalid")
            sealed[name] = dict(item)
        return sealed

    def record_extraction_plan(
        self, inventory: Mapping[str, Mapping[str, object]]
    ) -> None:
        sealed = self._validate_inventory(inventory)
        self._advance(
            "package_verified",
            "extraction_planned",
            lambda state: state["package"].__setitem__(
                "extraction_inventory", sealed
            ),
        )

    def record_package_extracted(self) -> None:
        self._advance("extraction_planned", "package_extracted")

    def record_source_preparation_plan(
        self,
        *,
        source_binding_sha256: str,
        inventory: Mapping[str, Mapping[str, object]],
    ) -> None:
        if (
            not isinstance(source_binding_sha256, str)
            or re.fullmatch(r"[0-9a-f]{64}", source_binding_sha256) is None
        ):
            raise InstallError("bootstrap transaction source binding invalid")
        sealed = self._validate_inventory(inventory)

        def mutate(state: dict[str, Any]) -> None:
            state["package"]["prepared_source_inventory"] = sealed
            state["package"]["prepared_source_binding_sha256"] = source_binding_sha256

        self._advance(
            "package_extracted",
            "source_preparation_planned",
            mutate,
        )

    def record_source_prepared(self) -> None:
        self._advance("source_preparation_planned", "source_prepared")

    def record_capsule_committed(
        self,
        *,
        capsule_sha256: str,
        blueprint_sha256: str,
        prepared_source_inventory: Mapping[str, Mapping[str, object]],
    ) -> None:
        if any(
            not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None
            for value in (capsule_sha256, blueprint_sha256)
        ):
            raise InstallError("bootstrap transaction capsule digest invalid")
        inventory = self._validate_inventory(prepared_source_inventory)

        def mutate(state: dict[str, Any]) -> None:
            state["recovery_capsule_sha256"] = capsule_sha256
            state["action_blueprint_sha256"] = blueprint_sha256
            state["package"]["prepared_source_inventory"] = inventory

        self._advance("source_prepared", "capsule_committed", mutate)

    def record_runtime_started(self) -> None:
        self._advance("capsule_committed", "runtime_started")

    def _terminal_transition(self, status: str) -> None:
        if self._state["status"] in {"rolled_back", "manual_recovery_required"}:
            raise InstallError("bootstrap transaction transition invalid")
        next_state = copy.deepcopy(self._state)
        next_state["generation"] += 1
        next_state["previous_state_sha256"] = hashlib.sha256(
            self._canonical(self._state)
        ).hexdigest()
        next_state["status"] = status
        self._validate_state(next_state)
        self._write_state(next_state)
        self._state = next_state

    def record_rolled_back(self) -> None:
        self._terminal_transition("rolled_back")

    def record_manual_recovery_required(self) -> None:
        self._terminal_transition("manual_recovery_required")


@dataclass(frozen=True, repr=False)
class InstallActionBlueprint:
    assembly_context: Mapping[str, Any]
    actions: tuple[Mapping[str, Any], ...]

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "InstallActionBlueprint":
        if (
            not isinstance(value, Mapping)
            or set(value) != {"schema", "assembly_context", "actions"}
            or value.get("schema") != "amn2.spain-install-action-blueprint.v1"
            or not isinstance(value.get("assembly_context"), Mapping)
            or not isinstance(value.get("actions"), list)
            or not value["actions"]
        ):
            raise InstallError("install action blueprint schema invalid")
        try:
            assembly_context = json.loads(
                json.dumps(
                    value["assembly_context"],
                    sort_keys=True,
                    separators=(",", ":"),
                )
            )
        except (TypeError, ValueError) as exc:
            raise InstallError("install action blueprint assembly context invalid") from exc
        if (
            not isinstance(assembly_context, dict)
            or assembly_context.get("schema")
            != "amn2.spain-production-assembly-context.v1"
            or len(assembly_context) < 2
            or any(
                marker in key.casefold()
                for key in assembly_context
                for marker in ("password", "token", "secret", "private_key")
            )
        ):
            raise InstallError("install action blueprint assembly context invalid")
        sealed: list[Mapping[str, Any]] = []
        stages: list[str] = []
        objects: set[str] = set()
        for raw in value["actions"]:
            if not isinstance(raw, Mapping) or set(raw) != {
                "stage",
                "owned_object",
                "desired_identity",
                "builder",
                "parameters",
            }:
                raise InstallError("install action blueprint entry invalid")
            stage = raw.get("stage")
            owned_object = raw.get("owned_object")
            desired_identity = raw.get("desired_identity")
            builder = raw.get("builder")
            parameters = raw.get("parameters")
            if (
                stage not in PRODUCTION_INSTALL_MUTATING_STAGES
                or not isinstance(owned_object, str)
                or not owned_object
                or owned_object in objects
                or not isinstance(desired_identity, str)
                or re.fullmatch(r"(?:sha256:)?[0-9a-f]{64}", desired_identity) is None
                or not isinstance(builder, str)
                or re.fullmatch(r"[a-z][a-z0-9_]{2,63}", builder) is None
                or not isinstance(parameters, Mapping)
            ):
                raise InstallError("install action blueprint entry invalid")
            try:
                parameters_copy = json.loads(
                    json.dumps(parameters, sort_keys=True, separators=(",", ":"))
                )
            except (TypeError, ValueError) as exc:
                raise InstallError("install action blueprint parameters invalid") from exc
            if not isinstance(parameters_copy, dict):
                raise InstallError("install action blueprint parameters invalid")
            stages.append(stage)
            objects.add(owned_object)
            sealed.append(
                {
                    "stage": stage,
                    "owned_object": owned_object,
                    "desired_identity": desired_identity,
                    "builder": builder,
                    "parameters": parameters_copy,
                }
            )
        expected_rank = {
            stage: index for index, stage in enumerate(PRODUCTION_INSTALL_MUTATING_STAGES)
        }
        if (
            set(stages) != set(PRODUCTION_INSTALL_MUTATING_STAGES)
            or stages != sorted(stages, key=expected_rank.__getitem__)
        ):
            raise InstallError("install action blueprint stage contract invalid")
        return cls(
            assembly_context=assembly_context,
            actions=tuple(sealed),
        )

    def mapping(self) -> dict[str, Any]:
        return {
            "schema": "amn2.spain-install-action-blueprint.v1",
            "assembly_context": copy.deepcopy(dict(self.assembly_context)),
            "actions": [copy.deepcopy(dict(action)) for action in self.actions],
        }

    @property
    def digest(self) -> str:
        return hashlib.sha256(
            json.dumps(
                self.mapping(), sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()

    @classmethod
    def from_production_action_plan(
        cls,
        action_plan: ProductionInstallActionPlan,
        *,
        assembly_context: Mapping[str, Any],
        operation_logical_contract: Mapping[str, str],
    ) -> "InstallActionBlueprint":
        if (
            not isinstance(action_plan, ProductionInstallActionPlan)
            or not isinstance(operation_logical_contract, Mapping)
            or set(operation_logical_contract)
            != {operation.owned_object for operation in action_plan.operations}
            or any(
                not isinstance(value, str) or not value
                for value in operation_logical_contract.values()
            )
        ):
            raise InstallError("production blueprint logical contract invalid")
        return cls.from_mapping(
            {
                "schema": "amn2.spain-install-action-blueprint.v1",
                "assembly_context": assembly_context,
                "actions": [
                    {
                        "stage": operation.stage,
                        "owned_object": operation.owned_object,
                        "desired_identity": operation.desired_identity,
                        "builder": "sealed_system_action",
                        "parameters": {
                            "logical_object": operation_logical_contract[
                                operation.owned_object
                            ]
                        },
                    }
                    for operation in action_plan.operations
                ],
            }
        )


class RecoveryCapsuleStore:
    SCHEMA = "amn2.spain-recovery-capsule.v1"
    MAX_BYTES = 16 * 1024 * 1024
    FILE_SECURITY = {
        "etc/amn2-spain/runtime.env": ("0600", "root", "root"),
        "etc/amn2-spain/awgsp0.conf": ("0600", "root", "root"),
        "etc/amn2-spain/servers.yml": ("0640", "root", "service"),
        "etc/amn2-spain/docker-daemon.json": ("0644", "root", "root"),
        "opt/amn2-spain/runtime/awg-start.sh": ("0755", "root", "root"),
    }

    def __init__(
        self,
        *,
        path: Path,
        state: dict[str, Any],
        sha256: str,
        expected_uid: int | None,
    ) -> None:
        self._validate_state(state)
        self.path = Path(path)
        self._state = copy.deepcopy(state)
        self.sha256 = sha256
        self.expected_uid = expected_uid
        self.blueprint = InstallActionBlueprint.from_mapping(state["blueprint"])
        if self.blueprint.digest != state["blueprint_sha256"]:
            raise InstallError("recovery capsule blueprint digest mismatch")

    @classmethod
    def _validate_state(cls, state: Mapping[str, Any]) -> None:
        if set(state) != {
            "schema",
            "nonce",
            "transaction_generation",
            "transaction_sha256",
            "blueprint",
            "blueprint_sha256",
            "prepared_source_inventory",
            "prepared_source_inventory_sha256",
            "rendered_payloads",
        }:
            raise InstallError("recovery capsule schema invalid")
        if (
            state.get("schema") != cls.SCHEMA
            or re.fullmatch(r"[0-9a-f]{64}", str(state.get("nonce", ""))) is None
            or not isinstance(state.get("transaction_generation"), int)
            or isinstance(state.get("transaction_generation"), bool)
            or state["transaction_generation"] < 0
            or any(
                re.fullmatch(r"[0-9a-f]{64}", str(state.get(key, ""))) is None
                for key in (
                    "transaction_sha256",
                    "blueprint_sha256",
                    "prepared_source_inventory_sha256",
                )
            )
        ):
            raise InstallError("recovery capsule identity invalid")
        prepared = BootstrapTransactionLedger._validate_inventory(
            state.get("prepared_source_inventory")
        )
        prepared_sha256 = hashlib.sha256(
            json.dumps(prepared, sort_keys=True, separators=(",", ":")).encode(
                "utf-8"
            )
        ).hexdigest()
        if prepared_sha256 != state["prepared_source_inventory_sha256"]:
            raise InstallError("recovery capsule source inventory digest mismatch")

    @staticmethod
    def _canonical(state: Mapping[str, Any]) -> bytes:
        return (
            json.dumps(state, sort_keys=True, separators=(",", ":")).encode("utf-8")
            + b"\n"
        )

    @classmethod
    def create(
        cls,
        *,
        transaction_ledger: BootstrapTransactionLedger,
        blueprint: InstallActionBlueprint,
        rendered_payloads: Mapping[str, Mapping[str, object]],
        prepared_source_inventory: Mapping[str, Mapping[str, object]],
        expected_uid: int | None = 0,
    ) -> "RecoveryCapsuleStore":
        if (
            not isinstance(transaction_ledger, BootstrapTransactionLedger)
            or not isinstance(blueprint, InstallActionBlueprint)
            or transaction_ledger.snapshot()["status"] != "source_prepared"
            or not isinstance(rendered_payloads, Mapping)
            or set(rendered_payloads) != set(cls.FILE_SECURITY)
        ):
            raise InstallError("recovery capsule dependency invalid")
        sealed_payloads: dict[str, dict[str, object]] = {}
        for path, expected_security in cls.FILE_SECURITY.items():
            spec = rendered_payloads[path]
            if not isinstance(spec, Mapping) or set(spec) != {
                "payload",
                "mode",
                "uid_role",
                "gid_role",
            }:
                raise InstallError("recovery capsule payload schema invalid")
            payload = spec.get("payload")
            security = (
                spec.get("mode"),
                spec.get("uid_role"),
                spec.get("gid_role"),
            )
            if (
                not isinstance(payload, bytes)
                or not payload
                or len(payload) > 2 * 1024 * 1024
                or security != expected_security
                or b"temporary_password" in payload.lower()
            ):
                raise InstallError("recovery capsule payload invalid")
            sealed_payloads[path] = {
                "content_b64": base64.b64encode(payload).decode("ascii"),
                "sha256": hashlib.sha256(payload).hexdigest(),
                "size": len(payload),
                "mode": security[0],
                "uid_role": security[1],
                "gid_role": security[2],
            }
        prepared = BootstrapTransactionLedger._validate_inventory(
            prepared_source_inventory
        )
        transaction = transaction_ledger.snapshot()
        state = {
            "schema": cls.SCHEMA,
            "nonce": transaction["nonce"],
            "transaction_generation": transaction["generation"],
            "transaction_sha256": hashlib.sha256(
                BootstrapTransactionLedger._canonical(transaction)
            ).hexdigest(),
            "blueprint": blueprint.mapping(),
            "blueprint_sha256": blueprint.digest,
            "prepared_source_inventory": prepared,
            "prepared_source_inventory_sha256": hashlib.sha256(
                json.dumps(prepared, sort_keys=True, separators=(",", ":")).encode(
                    "utf-8"
                )
            ).hexdigest(),
            "rendered_payloads": sealed_payloads,
        }
        path = transaction_ledger.path.parent / (
            "recovery-capsule-" + transaction["nonce"] + ".json"
        )
        payload = cls._canonical(state)
        if len(payload) > cls.MAX_BYTES or path.exists() or path.is_symlink():
            raise InstallError("recovery capsule path/size invalid")
        temporary = path.parent / ("." + path.name + ".tmp")
        descriptor = -1
        try:
            descriptor = os.open(
                temporary,
                os.O_WRONLY
                | os.O_CREAT
                | os.O_EXCL
                | getattr(os, "O_NOFOLLOW", 0)
                | getattr(os, "O_BINARY", 0),
                0o600,
            )
            if os.name != "nt":
                os.fchmod(descriptor, 0o600)
            offset = 0
            while offset < len(payload):
                written = os.write(descriptor, payload[offset:])
                if written <= 0:
                    raise InstallError("short recovery capsule write")
                offset += written
            os.fsync(descriptor)
            os.close(descriptor)
            descriptor = -1
            os.link(temporary, path)
            BootstrapTransactionLedger._fsync_directory(path.parent)
            os.unlink(temporary)
            BootstrapTransactionLedger._fsync_directory(path.parent)
        except InstallError:
            raise
        except OSError as exc:
            raise InstallError("recovery capsule write failed") from exc
        finally:
            if descriptor >= 0:
                os.close(descriptor)
            if temporary.exists():
                try:
                    os.unlink(temporary)
                except OSError:
                    pass
        digest = hashlib.sha256(payload).hexdigest()
        capsule = cls(
            path=path,
            state=state,
            sha256=digest,
            expected_uid=expected_uid,
        )
        transaction_ledger.record_capsule_committed(
            capsule_sha256=digest,
            blueprint_sha256=blueprint.digest,
            prepared_source_inventory=prepared,
        )
        return capsule

    @classmethod
    def _read_file(
        cls,
        path: Path,
        *,
        expected_uid: int | None,
    ) -> tuple[bytes, dict[str, Any]]:
        flags = (
            os.O_RDONLY
            | getattr(os, "O_NOFOLLOW", 0)
            | getattr(os, "O_BINARY", 0)
        )
        try:
            descriptor = os.open(path, flags)
            try:
                info = os.fstat(descriptor)
                payload = os.read(descriptor, cls.MAX_BYTES + 1)
            finally:
                os.close(descriptor)
        except OSError as exc:
            raise InstallError("recovery capsule unavailable") from exc
        if (
            len(payload) > cls.MAX_BYTES
            or not stat.S_ISREG(info.st_mode)
            or (
                os.name != "nt"
                and (
                    stat.S_IMODE(info.st_mode) != 0o600
                    or (expected_uid is not None and info.st_uid != expected_uid)
                )
            )
        ):
            raise InstallError("recovery capsule file invalid")
        try:
            state = json.loads(payload)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise InstallError("recovery capsule JSON invalid") from exc
        if not isinstance(state, dict) or cls._canonical(state) != payload:
            raise InstallError("recovery capsule canonical binding invalid")
        return payload, state

    @classmethod
    def open_existing(
        cls,
        *,
        audit_root: Path,
        nonce: str,
        expected_uid: int | None = 0,
    ) -> "RecoveryCapsuleStore":
        root = Path(audit_root)
        if (
            not root.is_absolute()
            or not root.is_dir()
            or root.is_symlink()
            or not isinstance(nonce, str)
            or re.fullmatch(r"[0-9a-f]{64}", nonce) is None
        ):
            raise InstallError("recovery capsule lookup invalid")
        path = root / ("recovery-capsule-" + nonce + ".json")
        temporary = path.parent / ("." + path.name + ".tmp")
        if temporary.exists() or temporary.is_symlink():
            temporary_payload, temporary_state = cls._read_file(
                temporary,
                expected_uid=expected_uid,
            )
            if temporary_state.get("nonce") != nonce:
                raise InstallError("recovery capsule temporary nonce mismatch")
            if not path.exists() and not path.is_symlink():
                try:
                    os.replace(temporary, path)
                except OSError as exc:
                    raise InstallError(
                        "recovery capsule temporary promotion failed"
                    ) from exc
                BootstrapTransactionLedger._fsync_directory(path.parent)
            else:
                current_payload, current_state = cls._read_file(
                    path,
                    expected_uid=expected_uid,
                )
                if (
                    current_state.get("nonce") != nonce
                    or current_payload != temporary_payload
                ):
                    raise InstallError("recovery capsule temporary mismatch")
                try:
                    os.unlink(temporary)
                except OSError as exc:
                    raise InstallError(
                        "recovery capsule stale temporary cleanup failed"
                    ) from exc
                BootstrapTransactionLedger._fsync_directory(path.parent)
        payload, state = cls._read_file(path, expected_uid=expected_uid)
        if (
            state.get("schema") != cls.SCHEMA
            or state.get("nonce") != nonce
        ):
            raise InstallError("recovery capsule canonical binding invalid")
        capsule = cls(
            path=path,
            state=state,
            sha256=hashlib.sha256(payload).hexdigest(),
            expected_uid=expected_uid,
        )
        capsule.rendered_payloads()
        return capsule

    @classmethod
    def remove_uncommitted(
        cls,
        *,
        transaction_ledger: BootstrapTransactionLedger,
        lock_lease: SharedInstallLockLease,
    ) -> bool:
        if (
            not isinstance(transaction_ledger, BootstrapTransactionLedger)
            or not isinstance(lock_lease, SharedInstallLockLease)
        ):
            raise InstallError("uncommitted capsule cleanup dependency invalid")
        lock_lease.assert_held()
        transaction = transaction_ledger.snapshot()
        path = transaction_ledger.path.parent / (
            "recovery-capsule-" + transaction["nonce"] + ".json"
        )
        temporary = path.parent / ("." + path.name + ".tmp")
        candidates = [
            candidate
            for candidate in (path, temporary)
            if candidate.exists() or candidate.is_symlink()
        ]
        if not candidates:
            return False
        try:
            if (
                transaction["status"] not in {"source_prepared", "rolled_back"}
                or transaction.get("recovery_capsule_sha256") is not None
                or transaction.get("action_blueprint_sha256") is not None
            ):
                raise InstallError("uncommitted capsule transaction state mismatch")
            observed = [
                cls._read_file(candidate, expected_uid=transaction_ledger.expected_uid)
                for candidate in candidates
            ]
            if any(payload != observed[0][0] for payload, _state in observed[1:]):
                raise InstallError("uncommitted capsule copies mismatch")
            capsule_state = observed[0][1]
            capsule = cls(
                path=path,
                state=capsule_state,
                sha256=hashlib.sha256(observed[0][0]).hexdigest(),
                expected_uid=transaction_ledger.expected_uid,
            )
            capsule.rendered_payloads()
            prepared = transaction["package"].get("prepared_source_inventory")
            if transaction["status"] == "source_prepared":
                expected_generation = transaction["generation"]
                expected_transaction_sha256 = hashlib.sha256(
                    BootstrapTransactionLedger._canonical(transaction)
                ).hexdigest()
            else:
                expected_generation = transaction["generation"] - 1
                expected_transaction_sha256 = transaction["previous_state_sha256"]
            if (
                capsule_state["nonce"] != transaction["nonce"]
                or capsule_state["transaction_generation"] != expected_generation
                or capsule_state["transaction_sha256"]
                != expected_transaction_sha256
                or capsule_state["prepared_source_inventory"] != prepared
            ):
                raise InstallError("uncommitted capsule transaction binding mismatch")
            for candidate in reversed(candidates):
                os.unlink(candidate)
            BootstrapTransactionLedger._fsync_directory(path.parent)
            return True
        except InstallError:
            if transaction["status"] not in {
                "rolled_back",
                "manual_recovery_required",
            }:
                try:
                    transaction_ledger.record_manual_recovery_required()
                except InstallError:
                    pass
            raise
        except OSError as exc:
            if transaction["status"] != "rolled_back":
                try:
                    transaction_ledger.record_manual_recovery_required()
                except InstallError:
                    pass
            raise InstallError("uncommitted capsule cleanup failed") from exc

    def rendered_payloads(self) -> dict[str, bytes]:
        raw = self._state.get("rendered_payloads")
        if not isinstance(raw, Mapping) or set(raw) != set(self.FILE_SECURITY):
            raise InstallError("recovery capsule payload schema invalid")
        result: dict[str, bytes] = {}
        for path, expected_security in self.FILE_SECURITY.items():
            spec = raw[path]
            if not isinstance(spec, Mapping) or set(spec) != {
                "content_b64",
                "sha256",
                "size",
                "mode",
                "uid_role",
                "gid_role",
            }:
                raise InstallError("recovery capsule payload schema invalid")
            try:
                payload = base64.b64decode(spec["content_b64"], validate=True)
            except Exception as exc:
                raise InstallError("recovery capsule payload encoding invalid") from exc
            if (
                (spec["mode"], spec["uid_role"], spec["gid_role"])
                != expected_security
                or spec["size"] != len(payload)
                or spec["sha256"] != hashlib.sha256(payload).hexdigest()
                or b"temporary_password" in payload.lower()
            ):
                raise InstallError("recovery capsule payload binding invalid")
            result[path] = payload
        return result

    def remove_after_rollback(
        self,
        *,
        transaction_ledger: BootstrapTransactionLedger,
        lock_lease: SharedInstallLockLease,
    ) -> None:
        if (
            not isinstance(transaction_ledger, BootstrapTransactionLedger)
            or not isinstance(lock_lease, SharedInstallLockLease)
        ):
            raise InstallError("recovery capsule cleanup dependency invalid")
        lock_lease.assert_held()
        transaction = transaction_ledger.snapshot()
        if (
            transaction["status"] != "rolled_back"
            or transaction.get("recovery_capsule_sha256") != self.sha256
            or transaction.get("action_blueprint_sha256") != self.blueprint.digest
            or self.path.parent != transaction_ledger.path.parent
            or self.path.name
            != "recovery-capsule-" + transaction["nonce"] + ".json"
        ):
            raise InstallError("recovery capsule cleanup state mismatch")
        reopened = self.open_existing(
            audit_root=self.path.parent,
            nonce=transaction["nonce"],
            expected_uid=self.expected_uid,
        )
        if reopened.sha256 != self.sha256:
            raise InstallError("recovery capsule cleanup CAS drift")
        temporary = self.path.parent / ("." + self.path.name + ".tmp")
        if temporary.exists() or temporary.is_symlink():
            raise InstallError("recovery capsule cleanup temporary collision")
        try:
            os.unlink(self.path)
            BootstrapTransactionLedger._fsync_directory(self.path.parent)
        except OSError as exc:
            raise InstallError("recovery capsule cleanup failed") from exc


@dataclass(frozen=True)
class BootstrapResult:
    tombstone: Path
    staged_package: StagedPackage
    transaction_ledger: BootstrapTransactionLedger
    recovery_capsule: RecoveryCapsuleStore | None = None

    def __post_init__(self) -> None:
        if (
            not self.tombstone.is_absolute()
            or not isinstance(self.staged_package, StagedPackage)
            or not isinstance(self.transaction_ledger, BootstrapTransactionLedger)
            or (
                self.recovery_capsule is not None
                and not isinstance(self.recovery_capsule, RecoveryCapsuleStore)
            )
        ):
            raise InstallError("bootstrap result invalid")


@dataclass(frozen=True, repr=False)
class PreparedProductionInstallation:
    capsule: RecoveryCapsuleStore
    assembly: live_backend.ProductionInstallAssembly
    prepared_payloads: live_backend.PreparedProductionFilesystemPayloads = field(
        repr=False
    )


def _production_runtime_dependencies(
    nft_config: bytes,
) -> tuple[
    live_backend.FixedCommandRunner,
    live_backend.FixedCommandRunner,
    network_backend.NetworkManager,
]:
    return (
        live_backend.FixedCommandRunner(
            allowed_argv=live_backend.SYSTEMCTL_COMMAND_ALLOWLIST
        ),
        live_backend.FixedCommandRunner(
            allowed_argv=live_backend.DOCKER_COMMAND_ALLOWLIST
        ),
        network_backend.NetworkManager(nft_config=nft_config.decode("utf-8")),
    )


def _production_assembly_context(
    *,
    host_root: Path,
    staged_package: StagedPackage,
    authorization: InstallAuthorization,
    runtime_binding: Mapping[str, Any],
    source_tree_identity: str,
    transaction_ledger: BootstrapTransactionLedger,
) -> dict[str, Any]:
    return {
        "schema": "amn2.spain-production-assembly-context.v1",
        "host_root": str(Path(host_root)),
        "package_content_root": str(staged_package.path.parent / "content"),
        "prepared_source_root": str(staged_package.prepared_source_path),
        "endpoint_host": authorization.endpoint_host,
        "boot_id": authorization.boot_id,
        "runtime_binding": copy.deepcopy(dict(runtime_binding)),
        "source_tree_identity": source_tree_identity,
        "mutation_ledger_path": str(
            transaction_ledger.path.parent
            / ("mutation-ledger-" + authorization.nonce + ".json")
        ),
    }


def prepare_production_installation(
    *,
    staged_package: StagedPackage,
    transaction_ledger: BootstrapTransactionLedger,
    authorization: InstallAuthorization,
    host_root: Path = Path("/"),
    expected_uid: int | None = 0,
) -> PreparedProductionInstallation:
    if (
        not isinstance(staged_package, StagedPackage)
        or not isinstance(transaction_ledger, BootstrapTransactionLedger)
        or not isinstance(authorization, InstallAuthorization)
        or transaction_ledger.snapshot()["status"] != "source_prepared"
    ):
        raise InstallError("production installation preparation dependency invalid")
    try:
        content = staged_package.path.parent / "content"
        runtime_binding = package_backend.plan_verified_runtime_artifacts(content)
        prepared = live_backend.prepare_production_filesystem_payloads(
            source_root=staged_package.prepared_source_path,
            endpoint_host=authorization.endpoint_host,
            package_content_root=content,
        )
        systemd_runner, docker_runner, network_manager = (
            _production_runtime_dependencies(
                prepared.package_bound_payloads[
                    "opt/amn2-spain/current/packaging/phase12-spain/templates/nftables.conf"
                ]
            )
        )
        assembly = live_backend.assemble_production_install_actions(
            host_root=Path(host_root),
            package_content_root=content,
            prepared_source_root=staged_package.prepared_source_path,
            endpoint_host=authorization.endpoint_host,
            boot_id=authorization.boot_id,
            runtime_binding=runtime_binding,
            prepared_payloads=prepared,
            systemd_runner=systemd_runner,
            docker_runner=docker_runner,
            network_manager=network_manager,
        )
        context = _production_assembly_context(
            host_root=Path(host_root),
            staged_package=staged_package,
            authorization=authorization,
            runtime_binding=runtime_binding,
            source_tree_identity=prepared.source_tree_identity,
            transaction_ledger=transaction_ledger,
        )
        blueprint = InstallActionBlueprint.from_production_action_plan(
            assembly.action_plan,
            assembly_context=context,
            operation_logical_contract=assembly.operation_logical_contract,
        )
        capsule = RecoveryCapsuleStore.create(
            transaction_ledger=transaction_ledger,
            blueprint=blueprint,
            rendered_payloads=live_backend.recovery_capsule_payload_specs(prepared),
            prepared_source_inventory=staged_package.prepared_source_inventory,
            expected_uid=expected_uid,
        )
    except InstallError:
        raise
    except (BackendError, PackageVerificationError) as exc:
        raise InstallError(_preparation_failure_message(exc)) from exc
    return PreparedProductionInstallation(
        capsule=capsule,
        assembly=assembly,
        prepared_payloads=prepared,
    )


def reconstruct_production_installation(
    *,
    capsule: RecoveryCapsuleStore,
    transaction_ledger: BootstrapTransactionLedger,
    authorization: InstallAuthorization,
) -> PreparedProductionInstallation:
    if (
        not isinstance(capsule, RecoveryCapsuleStore)
        or not isinstance(transaction_ledger, BootstrapTransactionLedger)
        or not isinstance(authorization, InstallAuthorization)
    ):
        raise InstallError("production reconstruction dependency invalid")
    transaction = transaction_ledger.snapshot()
    context = copy.deepcopy(dict(capsule.blueprint.assembly_context))
    required = {
        "schema",
        "host_root",
        "package_content_root",
        "prepared_source_root",
        "endpoint_host",
        "boot_id",
        "runtime_binding",
        "source_tree_identity",
        "mutation_ledger_path",
    }
    package_root = Path(transaction["package"]["root"])
    expected_host_root = package_root.parent.parent
    expected_ledger = transaction_ledger.path.parent / (
        "mutation-ledger-" + authorization.nonce + ".json"
    )
    if (
        set(context) != required
        or context["schema"] != "amn2.spain-production-assembly-context.v1"
        or not Path(context["host_root"]).is_absolute()
        or Path(context["host_root"]) != expected_host_root
        or Path(context["package_content_root"]) != package_root / "content"
        or Path(context["prepared_source_root"]) != package_root / "prepared-source"
        or context["endpoint_host"] != authorization.endpoint_host
        or context["boot_id"] != authorization.boot_id
        or Path(context["mutation_ledger_path"]) != expected_ledger
        or transaction.get("recovery_capsule_sha256") != capsule.sha256
        or transaction.get("action_blueprint_sha256") != capsule.blueprint.digest
    ):
        raise InstallError("production reconstruction context mismatch")
    try:
        runtime_binding = package_backend.plan_verified_runtime_artifacts(
            Path(context["package_content_root"])
        )
        if runtime_binding != context["runtime_binding"]:
            raise InstallError("production reconstruction artifact drift")
        prepared = live_backend.recover_production_filesystem_payloads(
            source_root=Path(context["prepared_source_root"]),
            endpoint_host=context["endpoint_host"],
            expected_source_tree_identity=context["source_tree_identity"],
            rendered_payloads=capsule.rendered_payloads(),
            package_content_root=Path(context["package_content_root"]),
        )
        systemd_runner, docker_runner, network_manager = (
            _production_runtime_dependencies(
                prepared.package_bound_payloads[
                    "opt/amn2-spain/current/packaging/phase12-spain/templates/nftables.conf"
                ]
            )
        )
        assembly = live_backend.assemble_production_install_actions(
            host_root=Path(context["host_root"]),
            package_content_root=Path(context["package_content_root"]),
            prepared_source_root=Path(context["prepared_source_root"]),
            endpoint_host=context["endpoint_host"],
            boot_id=context["boot_id"],
            runtime_binding=runtime_binding,
            prepared_payloads=prepared,
            systemd_runner=systemd_runner,
            docker_runner=docker_runner,
            network_manager=network_manager,
        )
        rebuilt = InstallActionBlueprint.from_production_action_plan(
            assembly.action_plan,
            assembly_context=context,
            operation_logical_contract=assembly.operation_logical_contract,
        )
        if rebuilt.digest != capsule.blueprint.digest:
            raise InstallError("production reconstruction blueprint drift")
    except InstallError:
        raise
    except (BackendError, PackageVerificationError) as exc:
        raise InstallError("production reconstruction failed") from exc
    return PreparedProductionInstallation(
        capsule=capsule,
        assembly=assembly,
        prepared_payloads=prepared,
    )


def _persist_or_open_rollback_equality_receipt(
    *,
    audit_root: Path,
    receipt: dict[str, Any],
    expected_uid: int | None,
) -> Path:
    validated = validate_rollback_equality_receipt(receipt)
    root = Path(audit_root)
    path = root / ("rollback-equality-" + validated["nonce"] + ".json")
    temporary = root / ("." + path.name + ".tmp")
    payload = (
        json.dumps(validated, sort_keys=True, separators=(",", ":")).encode("utf-8")
        + b"\n"
    )

    def verify(candidate: Path) -> None:
        try:
            descriptor = os.open(
                candidate,
                os.O_RDONLY
                | getattr(os, "O_NOFOLLOW", 0)
                | getattr(os, "O_BINARY", 0),
            )
            try:
                info = os.fstat(descriptor)
                observed = os.read(descriptor, len(payload) + 1)
            finally:
                os.close(descriptor)
        except OSError as exc:
            raise InstallError("rollback equality receipt unavailable") from exc
        if (
            observed != payload
            or not stat.S_ISREG(info.st_mode)
            or (
                os.name != "nt"
                and (
                    stat.S_IMODE(info.st_mode) != 0o600
                    or (expected_uid is not None and info.st_uid != expected_uid)
                )
            )
        ):
            raise InstallError("rollback equality receipt CAS mismatch")

    if path.exists() or path.is_symlink():
        if path.is_symlink():
            raise InstallError("rollback equality receipt symlink rejected")
        verify(path)
        return path
    if temporary.exists() or temporary.is_symlink():
        if temporary.is_symlink():
            raise InstallError("rollback equality receipt temporary unsafe")
        verify(temporary)
    else:
        descriptor = os.open(
            temporary,
            os.O_WRONLY
            | os.O_CREAT
            | os.O_EXCL
            | getattr(os, "O_NOFOLLOW", 0)
            | getattr(os, "O_BINARY", 0),
            0o600,
        )
        try:
            if os.name != "nt":
                os.fchmod(descriptor, 0o600)
            offset = 0
            while offset < len(payload):
                written = os.write(descriptor, payload[offset:])
                if written <= 0:
                    raise InstallError("rollback equality receipt short write")
                offset += written
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    try:
        os.link(temporary, path)
        BootstrapTransactionLedger._fsync_directory(root)
        os.unlink(temporary)
        BootstrapTransactionLedger._fsync_directory(root)
    except FileExistsError:
        verify(path)
    except OSError as exc:
        raise InstallError("rollback equality receipt promotion failed") from exc
    verify(path)
    return path


def _read_rollback_equality_receipt(
    path: Path,
    *,
    expected_uid: int | None,
) -> dict[str, Any]:
    candidate = Path(path)
    try:
        descriptor = os.open(
            candidate,
            os.O_RDONLY
            | getattr(os, "O_NOFOLLOW", 0)
            | getattr(os, "O_BINARY", 0),
        )
        try:
            info = os.fstat(descriptor)
            payload = os.read(descriptor, 64 * 1024 + 1)
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise InstallError("rollback equality receipt unavailable") from exc
    if (
        len(payload) > 64 * 1024
        or not stat.S_ISREG(info.st_mode)
        or (
            os.name != "nt"
            and (
                stat.S_IMODE(info.st_mode) != 0o600
                or (expected_uid is not None and info.st_uid != expected_uid)
            )
        )
    ):
        raise InstallError("rollback equality receipt owner/mode/type mismatch")
    try:
        value = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InstallError("rollback equality receipt JSON invalid") from exc
    if (
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
        + b"\n"
        != payload
    ):
        raise InstallError("rollback equality receipt canonical mismatch")
    return validate_rollback_equality_receipt(value)


def finalize_rolled_back_recovery(
    *,
    audit_root: Path,
    nonce: str,
    lock_lease: SharedInstallLockLease,
    expected_uid: int | None = 0,
) -> dict[str, Any]:
    if not isinstance(lock_lease, SharedInstallLockLease):
        raise InstallError("rolled-back recovery lock invalid")
    with lock_lease.acquire():
        transaction = BootstrapTransactionLedger.open_existing(
            audit_root=Path(audit_root),
            nonce=nonce,
            expected_uid=expected_uid,
        )
        state = transaction.snapshot()
        package_root = Path(state["package"]["root"])
        if (
            state["status"] != "rolled_back"
            or package_root.exists()
            or package_root.is_symlink()
            or not isinstance(state.get("action_blueprint_sha256"), str)
            or not isinstance(state.get("recovery_capsule_sha256"), str)
        ):
            raise InstallError("rolled-back recovery state mismatch")
        receipt = _read_rollback_equality_receipt(
            transaction.path.parent / ("rollback-equality-" + nonce + ".json"),
            expected_uid=expected_uid,
        )
        _assert_rollback_equality_transaction_binding(
            receipt,
            transaction,
            blueprint_sha256=state["action_blueprint_sha256"],
        )
        capsule_path = transaction.path.parent / (
            "recovery-capsule-" + nonce + ".json"
        )
        temporary = capsule_path.parent / ("." + capsule_path.name + ".tmp")
        if capsule_path.exists() or capsule_path.is_symlink() or temporary.exists():
            capsule = RecoveryCapsuleStore.open_existing(
                audit_root=transaction.path.parent,
                nonce=nonce,
                expected_uid=expected_uid,
            )
            capsule.remove_after_rollback(
                transaction_ledger=transaction,
                lock_lease=lock_lease,
            )
        return receipt


class ProductionRecoveryCoordinator:
    """Rollback runtime, prove foreign equality, then remove package and capsule."""

    def __init__(
        self,
        *,
        prepared: PreparedProductionInstallation,
        transaction_ledger: BootstrapTransactionLedger,
        package_stager: ChecksumBoundPackageStager,
        lock_lease: SharedInstallLockLease,
        equality_observer: Callable[[dict[str, str]], dict[str, Any]],
    ) -> None:
        if (
            not isinstance(prepared, PreparedProductionInstallation)
            or not isinstance(transaction_ledger, BootstrapTransactionLedger)
            or not isinstance(package_stager, ChecksumBoundPackageStager)
            or not isinstance(lock_lease, SharedInstallLockLease)
            or not callable(equality_observer)
        ):
            raise InstallError("production recovery coordinator dependency invalid")
        self.prepared = prepared
        self.transaction_ledger = transaction_ledger
        self.package_stager = package_stager
        self.lock_lease = lock_lease
        self.equality_observer = equality_observer

    def rollback(self) -> dict[str, Any]:
        assembly = self.prepared.assembly
        context = self.prepared.capsule.blueprint.assembly_context
        ledger_path = Path(context["mutation_ledger_path"])
        allowed = {
            operation.owned_object for operation in assembly.action_plan.operations
        }
        with self.lock_lease.acquire():
            try:
                store = live_backend.DurableMutationLedgerStore(
                    ledger_path,
                    expected_uid=self.transaction_ledger.expected_uid,
                )
                mutation_ledger = store.load_or_create(allowed)
                backend = live_backend.LinuxBackend(
                    adapter=live_backend.SystemOwnedAdapter(
                        actions={
                            action.operation.owned_object: action
                            for action in assembly.action_plan.actions
                        }
                    ),
                    ledger=mutation_ledger,
                )
                backend.rollback(assembly.action_plan.operations)
            except (InstallError, BackendError) as exc:
                if (
                    self.transaction_ledger.snapshot()["status"]
                    != "manual_recovery_required"
                ):
                    self.transaction_ledger.record_manual_recovery_required()
                if isinstance(exc, InstallError):
                    raise
                raise InstallError(_runtime_failure_message(exc)) from exc
            try:
                self.package_stager.recover_or_rollback(
                    self.transaction_ledger,
                    self.lock_lease,
                )
                transaction = self.transaction_ledger.snapshot()
                binding = {
                    "nonce": transaction["nonce"],
                    "transaction_sha256": hashlib.sha256(
                        BootstrapTransactionLedger._canonical(transaction)
                    ).hexdigest(),
                    "blueprint_sha256": self.prepared.capsule.blueprint.digest,
                }
                receipt = validate_rollback_equality_receipt(
                    self.equality_observer(copy.deepcopy(binding))
                )
                if any(receipt[key] != value for key, value in binding.items()):
                    raise InstallError("rollback equality receipt binding mismatch")
                _persist_or_open_rollback_equality_receipt(
                    audit_root=self.transaction_ledger.path.parent,
                    receipt=receipt,
                    expected_uid=self.transaction_ledger.expected_uid,
                )
                self.prepared.capsule.remove_after_rollback(
                    transaction_ledger=self.transaction_ledger,
                    lock_lease=self.lock_lease,
                )
            except InstallError:
                raise
        return receipt


class ChecksumBoundBootstrap:
    INITIAL_STAGES = (
        "authorization_validated",
        "critical_recheck_passed",
        "authorization_consumed",
        "package_staged",
        "package_verified_remote",
    )

    def __init__(
        self,
        *,
        authorization: InstallAuthorization,
        receipt: dict[str, Any],
        detached_receipt_sha256: str,
        now_epoch: int,
        lock_lease: SharedInstallLockLease,
        critical_observer: Callable[[], dict[str, str]],
        authorization_store: RetainedAuthorizationStore,
        package_stager: ChecksumBoundPackageStager,
        append_stage: Callable[[str], None],
        capsule_preparer: Callable[
            [StagedPackage, BootstrapTransactionLedger, InstallAuthorization],
            RecoveryCapsuleStore,
        ]
        | None = None,
    ) -> None:
        if (
            not isinstance(authorization, InstallAuthorization)
            or not isinstance(receipt, dict)
            or not isinstance(detached_receipt_sha256, str)
            or re.fullmatch(r"[0-9a-f]{64}", detached_receipt_sha256) is None
            or not isinstance(now_epoch, int)
            or isinstance(now_epoch, bool)
            or not isinstance(authorization_store, RetainedAuthorizationStore)
            or not isinstance(package_stager, ChecksumBoundPackageStager)
            or not isinstance(lock_lease, SharedInstallLockLease)
            or any(
                not callable(value)
                for value in (critical_observer, append_stage)
            )
            or (capsule_preparer is not None and not callable(capsule_preparer))
        ):
            raise InstallError("bootstrap dependency invalid")
        try:
            verify_precondition_receipt(
                receipt,
                detached_receipt_sha256,
                package_manifest_sha256=authorization.package_manifest_sha256,
                resource_plan_sha256=authorization.resource_plan_sha256,
                host_identity_sha256=authorization.host_identity_sha256,
                boot_id=authorization.boot_id,
                collector_sha256=authorization.collector_sha256,
                executor_sha256=authorization.executor_sha256,
                package_archive_sha256=authorization.package_archive_sha256,
                package_archive_size=authorization.package_archive_size,
            )
        except PreconditionError as exc:
            raise InstallError("bootstrap precondition receipt invalid") from exc
        if (
            authorization.precondition_receipt_sha256
            != detached_receipt_sha256
            or receipt.get("run009_evidence_sha256")
            != authorization.run009_evidence_sha256
            or receipt.get("fingerprint_array_sha256")
            != authorization.fingerprint_array_sha256
            or receipt.get("nonce") != authorization.nonce
            or authorization.approved_at_epoch > receipt.get("issued_at_epoch", -1)
            or authorization.expires_at_epoch > receipt.get("expires_at_epoch", -1)
            or now_epoch < authorization.approved_at_epoch
            or now_epoch > authorization.expires_at_epoch
        ):
            raise InstallError("bootstrap authorization binding/expiry mismatch")
        self.authorization = authorization
        self.receipt = copy.deepcopy(receipt)
        self.detached_receipt_sha256 = detached_receipt_sha256
        self.now_epoch = now_epoch
        self._lock_lease = lock_lease
        self._critical_observer = critical_observer
        self.authorization_store = authorization_store
        self.package_stager = package_stager
        self._append_stage = append_stage
        self._capsule_preparer = capsule_preparer

    def execute(
        self,
        input_fd: int,
        *,
        continuation: Callable[[BootstrapResult], Any] | None = None,
    ) -> Any:
        if continuation is not None and not callable(continuation):
            raise InstallError("bootstrap continuation invalid")
        staged: StagedPackage | None = None
        transaction_ledger: BootstrapTransactionLedger | None = None
        continuation_started = False
        try:
            with self._lock_lease.acquire():
                try:
                    critical = self._critical_observer()
                except Exception as exc:
                    raise InstallError("bootstrap critical recheck failed") from exc
                expected_critical = {
                    "host_identity_sha256": self.receipt["host_identity_sha256"],
                    "boot_id": self.receipt["boot_id"],
                }
                if critical != expected_critical:
                    raise InstallError("bootstrap critical recheck mismatch")
                (
                    tombstone,
                    transaction_ledger,
                    transaction_existed,
                ) = BootstrapTransactionLedger.open_or_create_for_authorization(
                    authorization_store=self.authorization_store,
                    authorization=self.authorization,
                    package_root=self.package_stager.package_root,
                    lock_lease=self._lock_lease,
                )
                if transaction_existed:
                    raise InstallError("bootstrap recovery required")
                for stage in self.INITIAL_STAGES[:3]:
                    self._append_stage(stage)
                staged = self.package_stager.stage(
                    input_fd,
                    expected_sha256=self.authorization.package_archive_sha256,
                    expected_size=self.authorization.package_archive_size,
                    transaction_ledger=transaction_ledger,
                )
                self._append_stage("package_staged")
                report = staged.report
                if (
                    report.archive_sha256
                    != self.authorization.package_archive_sha256
                    or report.archive_size != self.authorization.package_archive_size
                    or report.manifest_sha256
                    != self.authorization.package_manifest_sha256
                    or report.resource_plan_sha256
                    != self.authorization.resource_plan_sha256
                    or report.run009_evidence_sha256
                    != self.authorization.run009_evidence_sha256
                    or report.fingerprint_array_sha256
                    != self.authorization.fingerprint_array_sha256
                    or report.fingerprint_entry_count != 148
                ):
                    raise InstallError("bootstrap package report binding mismatch")
                self._append_stage("package_verified_remote")
                recovery_capsule = None
                if self._capsule_preparer is not None:
                    try:
                        recovery_capsule = self._capsule_preparer(
                            staged,
                            transaction_ledger,
                            self.authorization,
                        )
                    except InstallError:
                        raise
                    except Exception as exc:
                        raise InstallError(
                            "bootstrap recovery capsule preparation failed"
                        ) from exc
                    transaction = transaction_ledger.snapshot()
                    if (
                        not isinstance(recovery_capsule, RecoveryCapsuleStore)
                        or transaction["status"] != "capsule_committed"
                        or transaction["recovery_capsule_sha256"]
                        != recovery_capsule.sha256
                    ):
                        raise InstallError(
                            "bootstrap recovery capsule binding mismatch"
                        )
                result = BootstrapResult(
                    tombstone=tombstone,
                    staged_package=staged,
                    transaction_ledger=transaction_ledger,
                    recovery_capsule=recovery_capsule,
                )
                if continuation is None:
                    return result
                continuation_started = True
                return continuation(result)
        except InstallError:
            if staged is not None and not continuation_started:
                self.package_stager.rollback(staged)
                if transaction_ledger is not None:
                    transaction_ledger.record_rolled_back()
            raise
        except Exception as exc:
            if staged is not None and not continuation_started:
                self.package_stager.rollback(staged)
                if transaction_ledger is not None:
                    transaction_ledger.record_rolled_back()
            raise InstallError("bootstrap execution failed") from exc


class FsyncLedger:
    _ACTIVE_LOCKS: set[str] = set()

    def __init__(
        self,
        path: Path,
        stages: tuple[str, ...],
        *,
        sealed_allowlist: set[str],
    ) -> None:
        self.path = Path(path)
        self.stages = stages
        self.sealed_allowlist = frozenset(sealed_allowlist)
        self._lock_depth = 0
        if self.path.parent.is_symlink() or self.path.is_symlink():
            raise InstallError("ledger path must not contain symlink")
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        if not self.path.exists():
            descriptor = self._open(os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.fsync(descriptor)
            os.close(descriptor)
            if os.name != "nt":
                directory = os.open(self.path.parent, os.O_RDONLY)
                try:
                    os.fsync(directory)
                finally:
                    os.close(directory)
        self._identity = self._validate_file_identity()

    def _open(self, flags: int, mode: int = 0o600) -> int:
        flags |= getattr(os, "O_NOFOLLOW", 0)
        return os.open(self.path, flags, mode)

    def _validate_file_identity(self) -> tuple[int, int]:
        descriptor = self._open(os.O_RDONLY)
        try:
            info = os.fstat(descriptor)
        finally:
            os.close(descriptor)
        if not stat.S_ISREG(info.st_mode) or (
            os.name != "nt" and stat.S_IMODE(info.st_mode) != 0o600
        ):
            raise InstallError("ledger owner/mode/type mismatch")
        if os.name != "nt" and info.st_uid != 0:
            raise InstallError("ledger must be root-owned")
        return (info.st_dev, info.st_ino)

    def _read_bytes(self) -> bytes:
        descriptor = self._open(os.O_RDONLY)
        try:
            info = os.fstat(descriptor)
            if (info.st_dev, info.st_ino) != self._identity:
                raise InstallError("ledger inode changed")
            chunks = []
            while chunk := os.read(descriptor, 1024 * 1024):
                chunks.append(chunk)
            return b"".join(chunks)
        finally:
            os.close(descriptor)

    def _decoded_events(self) -> tuple[list[dict[str, str]], int]:
        raw = self._read_bytes()
        complete_length = len(raw) if raw.endswith(b"\n") or not raw else raw.rfind(b"\n") + 1
        complete = raw[:complete_length]
        events: list[dict[str, str]] = []
        for line in complete.splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError as exc:
                raise InstallError("corrupt mutation ledger") from exc
            if not isinstance(event, dict) or not all(
                isinstance(key, str) and isinstance(value, str) for key, value in event.items()
            ):
                raise InstallError("corrupt mutation ledger")
            events.append(event)
        return events, complete_length

    def events(self) -> list[dict[str, str]]:
        events, _complete_length = self._decoded_events()
        completed: list[str] = []
        states: dict[str, tuple[str, str | None, str]] = {}
        for event in events:
            kind = event.get("event")
            if kind == "stage":
                if set(event) != {"event", "stage"}:
                    raise InstallError("forged ledger stage event")
                stage = event["stage"]
                if stage == "rolled_back":
                    if not completed or completed[-1] == "rolled_back":
                        raise InstallError("out-of-order ledger rollback stage")
                elif len(completed) >= len(self.stages) or self.stages[len(completed)] != stage:
                    raise InstallError("out-of-order ledger stage")
                completed.append(stage)
            elif kind == "object":
                if set(event) != {
                    "event", "stage", "object", "state", "identity", "expected_identity"
                }:
                    raise InstallError("forged ledger object event")
                owned = event["object"]
                if owned not in self.sealed_allowlist:
                    raise InstallError("ledger object outside sealed allowlist")
                stage = event["stage"]
                state = event["state"]
                identity = event["identity"] or None
                expected_identity = event["expected_identity"]
                if not expected_identity:
                    raise InstallError("forged ledger expected identity")
                current = states.get(owned)
                if state == "pending" and current is None and identity is None:
                    pass
                elif (
                    state == "created"
                    and current == ("pending", None, expected_identity, stage)
                    and identity == expected_identity
                ):
                    pass
                elif (
                    state == "removed"
                    and current is not None
                    and current[0] in {"pending", "created"}
                    and expected_identity == current[2]
                    and stage == current[3]
                    and (identity == current[1] or (current[0] == "pending" and identity is None))
                ):
                    pass
                else:
                    raise InstallError("invalid duplicate/out-of-order ledger object transition")
                states[owned] = (state, identity, expected_identity, stage)
            else:
                raise InstallError("unknown ledger event type")
        return events

    @contextmanager
    def exclusive(self):
        key = str(self.path.resolve())
        if self._lock_depth:
            self._lock_depth += 1
            try:
                yield
            finally:
                self._lock_depth -= 1
            return
        if key in self._ACTIVE_LOCKS:
            raise InstallError("ledger lock is already held")
        lock_path = self.path.with_suffix(self.path.suffix + ".lock")
        if lock_path.is_symlink():
            raise InstallError("ledger lock path must not be symlink")
        lock_fd = os.open(
            lock_path,
            os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0),
            0o600,
        )
        try:
            if os.name != "nt":
                import fcntl

                try:
                    fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError as exc:
                    raise InstallError("ledger lock is already held") from exc
            self._ACTIVE_LOCKS.add(key)
            self._lock_depth = 1
            yield
        finally:
            self._lock_depth = 0
            self._ACTIVE_LOCKS.discard(key)
            if os.name != "nt":
                import fcntl

                fcntl.flock(lock_fd, fcntl.LOCK_UN)
            os.close(lock_fd)

    def _append(self, event: dict[str, str]) -> None:
        if not self._lock_depth:
            with self.exclusive():
                self._append(event)
            return
        _events, complete_length = self._decoded_events()
        body = json.dumps(event, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"
        descriptor = self._open(os.O_WRONLY)
        try:
            info = os.fstat(descriptor)
            if (info.st_dev, info.st_ino) != self._identity:
                raise InstallError("ledger inode changed")
            os.ftruncate(descriptor, complete_length)
            os.lseek(descriptor, 0, os.SEEK_END)
            offset = 0
            while offset < len(body):
                written = os.write(descriptor, body[offset:])
                if written <= 0:
                    raise InstallError("short mutation ledger write")
                offset += written
            os.fsync(descriptor)
        finally:
            os.close(descriptor)

    def _completed_stages(self) -> list[str]:
        return [event["stage"] for event in self.events() if event.get("event") == "stage"]

    def append_stage(self, stage: str) -> None:
        completed = self._completed_stages()
        if stage == "rolled_back":
            if not completed or completed[-1] == "rolled_back":
                raise InstallError("non-monotonic journal stage")
        else:
            expected_index = len(completed)
            if expected_index >= len(self.stages) or self.stages[expected_index] != stage:
                raise InstallError("non-monotonic journal stage")
        self._append({"event": "stage", "stage": stage})

    def _object_states(self) -> dict[str, tuple[str, str | None, str, str]]:
        states: dict[str, tuple[str, str | None, str, str]] = {}
        for event in self.events():
            if event.get("event") == "object":
                states[event["object"]] = (
                    event["state"], event["identity"] or None,
                    event["expected_identity"], event["stage"]
                )
        return states

    def record_pending(self, stage: str, owned_object: str, expected_identity: str) -> None:
        completed = self._completed_stages()
        if completed and completed[-1] == "rolled_back":
            raise InstallError("cannot add owned object after rollback")
        next_index = len(completed)
        if next_index >= len(self.stages) or self.stages[next_index] != stage:
            raise InstallError("owned object stage is not current monotonic stage")
        if owned_object not in self.sealed_allowlist:
            raise InstallError("owned object outside sealed allowlist")
        if not isinstance(expected_identity, str) or not expected_identity:
            raise InstallError("owned object expected identity required before mutation")
        if owned_object in self._object_states():
            raise InstallError("duplicate owned object transition")
        self._append({
            "event": "object", "stage": stage, "object": owned_object,
            "state": "pending", "identity": "", "expected_identity": expected_identity,
        })

    def record_created(self, stage: str, owned_object: str, identity: str) -> None:
        current = self._object_states().get(owned_object)
        if (
            not identity
            or current is None
            or current[0] != "pending"
            or current[1] is not None
            or current[3] != stage
            or identity != current[2]
        ):
            raise InstallError("created transition requires matching pending object")
        self._append({
            "event": "object", "stage": stage, "object": owned_object,
            "state": "created", "identity": identity, "expected_identity": current[2],
        })

    def rollback(self, observe_identity, remove_owned) -> None:
        completed = self._completed_stages()
        if completed and completed[-1] == "rolled_back":
            return
        intent_order = []
        for event in self.events():
            if event.get("event") == "object" and event["state"] == "pending":
                intent_order.append(event["object"])
        with self.exclusive():
            for owned_object in reversed(intent_order):
                state, actual_identity, expected_identity, stage = self._object_states()[owned_object]
                if state == "removed":
                    continue
                actual_identity = observe_identity(owned_object)
                if state == "pending" and actual_identity is None:
                    self._append({
                        "event": "object", "stage": stage, "object": owned_object,
                        "state": "removed", "identity": "",
                        "expected_identity": expected_identity,
                    })
                    continue
                if state == "pending" and actual_identity == expected_identity:
                    self._append({
                        "event": "object", "stage": stage, "object": owned_object,
                        "state": "created", "identity": actual_identity,
                        "expected_identity": expected_identity,
                    })
                    state = "created"
                elif state == "pending":
                    raise InstallError(f"owned object identity drift: {owned_object}")
                if actual_identity is None:
                    self._append({
                        "event": "object", "stage": stage, "object": owned_object,
                        "state": "removed", "identity": expected_identity,
                        "expected_identity": expected_identity,
                    })
                    continue
                if actual_identity != expected_identity:
                    raise InstallError(f"owned object identity drift: {owned_object}")
                remove_owned(owned_object, expected_identity)
                if observe_identity(owned_object) is not None:
                    raise InstallError(f"owned object removal not observable: {owned_object}")
                self._append({
                    "event": "object", "stage": stage, "object": owned_object,
                    "state": "removed", "identity": expected_identity,
                    "expected_identity": expected_identity,
                })
            self.append_stage("rolled_back")


def build_rollback_equality_receipt(
    *,
    baseline_observation: Mapping[str, Any],
    current_observation: Mapping[str, Any],
    binding: Mapping[str, str],
) -> dict[str, Any]:
    required_observation = {
        "schema",
        "os",
        "capacity",
        "existing",
        "listeners",
        "addresses",
        "routes",
        "docker_present",
        "package_root",
        "systemd_projection",
        "firewall",
    }
    if (
        not isinstance(baseline_observation, Mapping)
        or not isinstance(current_observation, Mapping)
        or set(baseline_observation) != required_observation
        or set(current_observation) != required_observation
        or baseline_observation.get("schema")
        != "amn2.spain-precondition-observation.v1"
        or current_observation.get("schema")
        != "amn2.spain-precondition-observation.v1"
        or not isinstance(binding, Mapping)
        or set(binding) != {"nonce", "transaction_sha256", "blueprint_sha256"}
        or any(
            not isinstance(binding[key], str)
            or re.fullmatch(r"[0-9a-f]{64}", binding[key]) is None
            for key in binding
        )
    ):
        raise InstallError("rollback equality observation schema invalid")
    before_existing = copy.deepcopy(dict(baseline_observation["existing"]))
    after_existing = copy.deepcopy(dict(current_observation["existing"]))
    before_existing.pop("retained_paths", None)
    after_existing.pop("retained_paths", None)
    package_root = current_observation["package_root"]
    if (
        baseline_observation["os"] != current_observation["os"]
        or baseline_observation["docker_present"]
        != current_observation["docker_present"]
        or before_existing != after_existing
        or not isinstance(package_root, Mapping)
        or package_root.get("exists") is not False
        or package_root.get("is_symlink") is not False
    ):
        raise InstallError("rollback baseline projection mismatch")
    if baseline_observation["firewall"] != current_observation["firewall"]:
        raise InstallError("rollback firewall projection mismatch")
    if any(
        baseline_observation[key] != current_observation[key]
        for key in ("listeners", "routes", "addresses")
    ):
        raise InstallError("rollback listeners/routes/addresses mismatch")
    def stable_foreign_item(item: Mapping[str, object]) -> dict[str, object]:
        stable = dict(item)
        stable.pop("bound_port_set", None)
        stable.pop("restart_count", None)
        return stable
    before_items = {
        str(item.get("name_sha256")): stable_foreign_item(item)
        for item in baseline_observation["systemd_projection"]
    }
    after_items = {
        str(item.get("name_sha256")): stable_foreign_item(item)
        for item in current_observation["systemd_projection"]
    }
    persistent = sorted(set(before_items) & set(after_items))
    if any(before_items[key] != after_items[key] for key in persistent):
        raise InstallError("rollback persistent foreign projection mismatch")
    before_fingerprint = sha256_canonical([before_items[key] for key in persistent])
    after_fingerprint = sha256_canonical([after_items[key] for key in persistent])
    return validate_rollback_equality_receipt(
        {
            "schema": "amn2.spain-rollback-equality.v1",
            "result": "passed",
            "baseline_projection_equal": True,
            "firewall_projection_equal": True,
            "listeners_routes_addresses_equal": True,
            **dict(binding),
            "foreign_service_fingerprint_before_sha256": before_fingerprint,
            "foreign_service_fingerprint_after_sha256": after_fingerprint,
            "foreign_service_persistent_equal": True,
            "foreign_service_volatile_before_count": len(set(before_items) - set(after_items)),
            "foreign_service_volatile_after_count": len(set(after_items) - set(before_items)),
        }
    )


def build_terminal_recovery_equality_receipt(
    *,
    baseline_observation: Mapping[str, Any],
    current_observation: Mapping[str, Any],
    binding: Mapping[str, str],
) -> dict[str, Any]:
    """Prove foreign equality while permitting only the owned recovery delta."""
    if not isinstance(current_observation, Mapping):
        raise InstallError("terminal recovery equality observation invalid")
    existing = current_observation.get("existing")
    expected_existing = {
        "paths", "retained_paths", "users", "groups", "units", "containers",
        "networks", "bridges", "interfaces", "uids", "gids", "sockets",
        "runtime_dirs", "firewall_objects", "owned_routes", "sysctls",
    }
    if (
        not isinstance(existing, Mapping)
        or set(existing) != expected_existing
        or any(
            not isinstance(existing[key], list) or existing[key]
            for key in expected_existing - {"retained_paths"}
        )
        or existing["retained_paths"] != ["/var/lib/amn2-spain-phase12-audit"]
    ):
        raise InstallError("terminal recovery owned inventory remains")
    normalized_baseline = copy.deepcopy(dict(baseline_observation))
    normalized_baseline["existing"] = copy.deepcopy(dict(existing))
    return build_rollback_equality_receipt(
        baseline_observation=normalized_baseline,
        current_observation=current_observation,
        binding=binding,
    )


def validate_rollback_equality_receipt(value: Any) -> dict[str, Any]:
    expected = {
        "schema",
        "result",
        "baseline_projection_equal",
        "firewall_projection_equal",
        "listeners_routes_addresses_equal",
        "nonce",
        "transaction_sha256",
        "blueprint_sha256",
        "foreign_service_fingerprint_before_sha256",
        "foreign_service_fingerprint_after_sha256",
        "foreign_service_persistent_equal",
        "foreign_service_volatile_before_count",
        "foreign_service_volatile_after_count",
    }
    if (
        not isinstance(value, dict)
        or set(value) != expected
        or value.get("schema") != "amn2.spain-rollback-equality.v1"
        or value.get("result") != "passed"
        or value.get("baseline_projection_equal") is not True
        or value.get("firewall_projection_equal") is not True
        or value.get("listeners_routes_addresses_equal") is not True
        or value.get("foreign_service_persistent_equal") is not True
        or not isinstance(value.get("foreign_service_volatile_before_count"), int)
        or not isinstance(value.get("foreign_service_volatile_after_count"), int)
    ):
        raise InstallError("rollback equality receipt invalid")
    before = value["foreign_service_fingerprint_before_sha256"]
    after = value["foreign_service_fingerprint_after_sha256"]
    if (
        any(
            not isinstance(value[key], str)
            or re.fullmatch(r"[0-9a-f]{64}", value[key]) is None
            for key in ("nonce", "transaction_sha256", "blueprint_sha256")
        )
        or
        not isinstance(before, str)
        or re.fullmatch(r"[0-9a-f]{64}", before) is None
        or after != before
    ):
        raise InstallError("rollback foreign service fingerprint mismatch")
    return copy.deepcopy(value)


def assert_systemd_projection(expected: object, current: object) -> None:
    if not isinstance(expected, list) or not isinstance(current, list):
        raise InstallError("systemd projection mismatch")
    def by_identity(entries: list[object]) -> dict[str, dict[str, Any]]:
        result: dict[str, dict[str, Any]] = {}
        for entry in entries:
            if not isinstance(entry, dict) or not isinstance(entry.get("name_sha256"), str):
                raise InstallError("systemd projection mismatch")
            identity = entry["name_sha256"]
            if identity in result:
                raise InstallError("systemd projection mismatch")
            stable = dict(entry)
            stable.pop("bound_port_set", None)
            stable.pop("restart_count", None)
            result[identity] = stable
        return result
    expected_by_identity = by_identity(expected)
    current_by_identity = by_identity(current)
    persistent = set(expected_by_identity) & set(current_by_identity)
    if not persistent or any(
        expected_by_identity[identity] != current_by_identity[identity]
        for identity in persistent
    ):
        raise InstallError("systemd projection mismatch")


def assert_firewall_projection(
    baseline_nft: object,
    current_nft: object,
    *,
    sealed_namespace: object,
    expected_owned_nft: object,
) -> None:
    if not isinstance(sealed_namespace, dict) or set(sealed_namespace) != {
        "family", "table", "chains", "sets"
    } or sealed_namespace["family"] != "inet" or sealed_namespace["table"] != "amn2_spain" or not isinstance(sealed_namespace["chains"], list) or not isinstance(sealed_namespace["sets"], list):
        raise InstallError("invalid sealed firewall projection namespace")

    try:
        from scripts.phase12_spain_network import _owned_semantics
    except Exception as exc:
        raise InstallError("exact owned firewall model unavailable") from exc
    try:
        expected_semantics = _owned_semantics(expected_owned_nft)
    except Exception as exc:
        raise InstallError("invalid exact owned firewall model") from exc

    def classify(model: object) -> tuple[list[bytes], list[dict[str, Any]]]:
        if not isinstance(model, dict) or set(model) != {"nftables"} or not isinstance(model["nftables"], list):
            raise InstallError("invalid structured nft firewall projection")
        foreign: list[bytes] = []
        owned: list[dict[str, Any]] = []
        for item in model["nftables"]:
            if not isinstance(item, dict) or len(item) != 1:
                raise InstallError("invalid structured nft object")
            object_type, value = next(iter(item.items()))
            if object_type == "metainfo":
                continue
            if not isinstance(value, dict):
                raise InstallError("invalid structured nft object payload")
            family = value.get("family")
            table = value.get("table") if object_type != "table" else value.get("name")
            is_owned = family == sealed_namespace["family"] and table == sealed_namespace["table"]
            if is_owned:
                owned.append(copy.deepcopy(item))
                continue
            if object_type == "rule" and str(value.get("comment", "")).startswith(
                sealed_namespace["table"] + ":"
            ):
                raise InstallError("firewall projection package rule injected into foreign chain")
            if isinstance(table, str) and table.startswith("amn2_"):
                raise InstallError("firewall projection unsealed AMN2 namespace observed")
            foreign.append(
                json.dumps(item, sort_keys=True, separators=(",", ":")).encode("utf-8")
            )
        return sorted(foreign), owned

    baseline_foreign, baseline_owned = classify(baseline_nft)
    current_foreign, current_owned = classify(current_nft)
    if baseline_owned:
        raise InstallError("firewall projection baseline already contains owned namespace")
    if current_foreign != baseline_foreign:
        raise InstallError("firewall projection contains foreign change")
    try:
        current_semantics = _owned_semantics({"nftables": current_owned})
    except Exception as exc:
        raise InstallError("firewall projection exact owned model malformed") from exc
    if current_semantics != expected_semantics:
        raise InstallError("firewall projection exact owned model mismatch")


class ProductionBackend:
    """Installer-facing adapter over one immutable production action plan."""

    def __init__(
        self,
        *,
        action_plan: ProductionInstallActionPlan,
        blueprint: InstallActionBlueprint,
        linux_backend: LinuxBackend,
        stage_object_contract: Mapping[str, list[str]],
        append_stage: Callable[[str], None],
        lock_lease: SharedInstallLockLease,
        critical_observer: Callable[[], dict[str, str]],
        authorization_consumer: Callable[[str], None],
        postinstall_observer: Callable[[], dict[str, object]],
    ) -> None:
        if (
            not isinstance(action_plan, ProductionInstallActionPlan)
            or not isinstance(blueprint, InstallActionBlueprint)
            or not isinstance(linux_backend, LinuxBackend)
            or not isinstance(linux_backend.adapter, SystemOwnedAdapter)
            or not isinstance(lock_lease, SharedInstallLockLease)
            or any(
                not callable(value)
                for value in (
                    append_stage,
                    critical_observer,
                    authorization_consumer,
                    postinstall_observer,
                )
            )
        ):
            raise InstallError("production backend dependency invalid")
        expected_objects = {operation.owned_object for operation in action_plan.operations}
        blueprint_actions = blueprint.actions
        if tuple(
            (
                action["stage"],
                action["owned_object"],
                action["desired_identity"],
            )
            for action in blueprint_actions
        ) != tuple(
            (operation.stage, operation.owned_object, operation.desired_identity)
            for operation in action_plan.operations
        ):
            raise InstallError("production blueprint/action plan mismatch")
        adapter_actions = getattr(linux_backend.adapter, "_actions", None)
        if (
            linux_backend.ledger.allowed_objects != expected_objects
            or not isinstance(adapter_actions, Mapping)
            or set(adapter_actions) != expected_objects
            or any(
                adapter_actions[action.operation.owned_object] is not action
                for action in action_plan.actions
            )
        ):
            raise InstallError("production backend sealed registry mismatch")
        expected_stages = tuple(action_plan.operations_by_stage)
        if (
            not isinstance(stage_object_contract, Mapping)
            or tuple(stage_object_contract) != expected_stages
        ):
            raise InstallError("production stage object contract invalid")
        sealed_contract: dict[str, tuple[str, ...]] = {}
        logical_objects: list[str] = []
        for stage in expected_stages:
            values = stage_object_contract[stage]
            if (
                not isinstance(values, (list, tuple))
                or not values
                or any(not isinstance(value, str) or not value for value in values)
                or len(values) != len(set(values))
            ):
                raise InstallError("production stage object contract invalid")
            sealed_contract[stage] = tuple(values)
            logical_objects.extend(values)
            blueprint_logical = {
                action["parameters"].get("logical_object")
                for action in blueprint_actions
                if action["stage"] == stage
            }
            if blueprint_logical != set(values) or None in blueprint_logical:
                raise InstallError("production blueprint logical contract mismatch")
        if len(logical_objects) != len(set(logical_objects)):
            raise InstallError("production logical object contract overlaps")
        self.action_plan = action_plan
        self.blueprint = blueprint
        self.linux_backend = linux_backend
        self._stage_object_contract = sealed_contract
        self._logical_objects = tuple(logical_objects)
        self._append_stage = append_stage
        self._lock_lease = lock_lease
        self._critical_observer = critical_observer
        self._authorization_consumer = authorization_consumer
        self._postinstall_observer = postinstall_observer
        self._runtime_invariants: dict[str, object] | None = None

    def stage_object_contract(self) -> dict[str, list[str]]:
        return {
            stage: list(values)
            for stage, values in self._stage_object_contract.items()
        }

    @property
    def created_objects(self) -> list[str]:
        return [
            operation.owned_object
            for operation in self.action_plan.operations
            if (
                (event := self.linux_backend.ledger.event_for(operation.owned_object))
                is not None
                and event["event"] == "committed"
            )
        ]

    def append_journal(self, stage: str) -> None:
        self._require_lock("production journal append requires install lock")
        try:
            self._append_stage(stage)
        except Exception as exc:
            raise InstallError("production journal append failed") from exc

    def assert_no_collisions(self, planned_objects: list[str]) -> None:
        if tuple(planned_objects) != self._logical_objects:
            raise InstallError("production planned object contract mismatch")

    def apply_stage(self, stage: str, objects: list[str]) -> None:
        self._require_lock("production mutation requires install lock")
        expected = self._stage_object_contract.get(stage)
        if expected is None or tuple(objects) != expected:
            raise InstallError("production stage object contract mismatch")
        try:
            self.linux_backend.apply(self.action_plan.operations_by_stage[stage])
        except BackendError as exc:
            raise InstallError(f"production stage failed: {stage}") from exc

    def set_runtime_state(self, state: dict[str, object]) -> None:
        self._require_lock("production runtime invariant contract invalid")
        if not isinstance(state, dict):
            raise InstallError("production runtime invariant contract invalid")
        self._runtime_invariants = copy.deepcopy(state)

    def rollback(self) -> None:
        self._require_lock("production rollback requires install lock")
        try:
            self.linux_backend.rollback(self.action_plan.operations)
        except BackendError as exc:
            raise InstallError("production rollback failed") from exc
        self._runtime_invariants = None

    def observe_postinstall(self) -> dict[str, object]:
        self._require_lock("production postinstall observation unavailable")
        if self._runtime_invariants is None:
            raise InstallError("production postinstall observation unavailable")
        try:
            value = self._postinstall_observer()
        except Exception as exc:
            raise InstallError("production postinstall observation failed") from exc
        if not isinstance(value, dict):
            raise InstallError("production postinstall observation invalid")
        return copy.deepcopy(value)

    @contextmanager
    def install_lock(self):
        with self._lock_lease.acquire():
            yield

    def _require_lock(self, message: str) -> None:
        try:
            self._lock_lease.assert_held()
        except InstallError as exc:
            raise InstallError(message) from exc

    def observe_critical(self) -> dict[str, str]:
        self._require_lock("critical recheck requires install lock")
        try:
            value = self._critical_observer()
        except Exception as exc:
            raise InstallError("critical recheck failed") from exc
        if not isinstance(value, dict) or any(
            not isinstance(key, str) or not isinstance(item, str)
            for key, item in value.items()
        ):
            raise InstallError("critical recheck observation invalid")
        return copy.deepcopy(value)

    def consume_authorization(self, nonce: str) -> None:
        self._require_lock("authorization consume requires install lock")
        if not isinstance(nonce, str) or re.fullmatch(r"[0-9a-f]{64}", nonce) is None:
            raise InstallError("authorization nonce invalid")
        try:
            self._authorization_consumer(nonce)
        except Exception as exc:
            raise InstallError("authorization consume failed") from exc


@dataclass
class MemoryBackend:
    fault_stage: str | None = None
    preexisting: set[str] = field(default_factory=set)
    objects: set[str] = field(init=False)
    created_objects: list[str] = field(default_factory=list)
    rollback_objects: list[str] = field(default_factory=list)
    journal: list[str] = field(default_factory=list)
    mutations: list[str] = field(default_factory=list)
    runtime_state: dict[str, object] = field(default_factory=dict)
    systemd_projection: object = None
    foreign_firewall: object = None
    runtime_overrides: dict[str, object] = field(default_factory=dict)
    unexpected_objects: list[str] = field(default_factory=list)
    critical_observation: dict[str, str] | None = None
    consumed_nonces: set[str] = field(default_factory=set)
    lock_held: bool = False

    def __post_init__(self) -> None:
        self.objects = set(self.preexisting)

    def append_journal(self, stage: str) -> None:
        self.journal.append(stage)

    def assert_no_collisions(self, planned_objects: list[str]) -> None:
        collision = self.objects.intersection(planned_objects)
        if collision:
            raise InstallError(f"pre-existing resource collision: {sorted(collision)[0]}")

    def apply_stage(self, stage: str, objects: list[str]) -> None:
        if self.fault_stage == stage:
            raise InstallError(f"fault injection at {stage}")
        for value in objects:
            if value in self.objects:
                raise InstallError(f"pre-existing resource collision: {value}")
            self.objects.add(value)
            self.created_objects.append(value)
            self.mutations.append(f"create:{value}")

    def set_runtime_state(self, state: dict[str, object]) -> None:
        self.runtime_state = copy.deepcopy(state)

    def rollback(self) -> None:
        for value in reversed(self.created_objects):
            if value not in self.objects:
                raise InstallError(f"owned rollback object disappeared: {value}")
            self.objects.remove(value)
            self.rollback_objects.append(value)
            self.mutations.append(f"remove:{value}")
        self.runtime_state = {}

    def observe_postinstall(self) -> dict[str, object]:
        runtime = copy.deepcopy(self.runtime_state)
        runtime.update(self.runtime_overrides)
        return {
            "runtime": runtime,
            "systemd_projection": copy.deepcopy(self.systemd_projection),
            "foreign_firewall": copy.deepcopy(self.foreign_firewall),
            "owned_objects": list(self.created_objects),
            "unexpected_objects": list(self.unexpected_objects),
        }

    @contextmanager
    def install_lock(self):
        if self.lock_held:
            raise InstallError("install lock already held")
        self.lock_held = True
        try:
            yield
        finally:
            self.lock_held = False

    def observe_critical(self) -> dict[str, str]:
        if not self.lock_held:
            raise InstallError("critical recheck requires install lock")
        if self.critical_observation is None:
            raise InstallError("critical recheck observation unavailable")
        return copy.deepcopy(self.critical_observation)

    def consume_authorization(self, nonce: str) -> None:
        if not self.lock_held:
            raise InstallError("authorization consume requires install lock")
        if nonce in self.consumed_nonces:
            raise InstallError("install authorization nonce already consumed")
        self.consumed_nonces.add(nonce)


class InstallStateMachine:
    STAGES = (
        "authorization_validated",
        "critical_recheck_passed",
        "authorization_consumed",
        "package_staged",
        "package_verified_remote",
        "identity_created",
        "filesystem_staged",
        "secrets_configs_rendered",
        "clean_db_initialized",
        "units_installed",
        "docker_started",
        "awg_image_loaded",
        "network_container_started",
        "host_network_applied",
        "web_started",
        "postinstall_verified",
    )
    MUTATING_STAGES = STAGES[5:-1]

    def __init__(
        self,
        backend: MemoryBackend,
        resource_plan: dict[str, Any],
        baseline: dict[str, Any],
    ) -> None:
        self.backend = backend
        self.resource_plan = resource_plan
        self.baseline = baseline

    def _stage_objects(self) -> dict[str, list[str]]:
        if isinstance(self.backend, ProductionBackend):
            return self.backend.stage_object_contract()
        resources = self.resource_plan["resources"]
        return {
            "identity_created": [
                *[f"group:{value}" for value in resources["groups"]],
                *[f"user:{value}" for value in resources["users"]],
                *[f"gid:{value}" for value in resources["gids"]],
                *[f"uid:{value}" for value in resources["uids"]],
            ],
            "filesystem_staged": [
                *[f"path:{value}" for value in resources["paths"]],
                *[f"runtime-dir:{value}" for value in resources["runtime_dirs"]],
                "runtime:docker-static",
                "runtime:source-tree",
                "runtime:site-packages",
            ],
            "secrets_configs_rendered": [
                "secret:server-private-key",
                "secret:app-runtime",
                "file:/etc/amn2-spain/awgsp0.conf",
                "file:/etc/amn2-spain/runtime.env",
                "file:/etc/amn2-spain/servers.yml",
                "file:/etc/amn2-spain/docker-daemon.json",
                "file:/opt/amn2-spain/runtime/awg-start.sh",
            ],
            "clean_db_initialized": ["database:/var/lib/amn2-spain/amn2.sqlite3"],
            "units_installed": [f"unit:{value}" for value in resources["units"]],
            "docker_started": [
                "service-state:amn2-spain-docker.service:active",
                *[f"socket:{value}" for value in resources["sockets"]],
            ],
            "awg_image_loaded": [
                "image:sha256:0f21ddfb3313affe3a336693886ced918301335815e4b7db3d15b5a0a5da6afb"
            ],
            "network_container_started": [
                *[f"network:{value}" for value in resources["networks"]],
                *[f"bridge:{value}" for value in resources["bridges"]],
                *[f"interface:{value}" for value in resources["interfaces"]],
                *[f"container:{value}" for value in resources["containers"]],
                "runtime:awgsp0",
            ],
            "host_network_applied": [
                "network-contour:amn2-spain",
                *[f"firewall:{value}" for value in resources["firewall_objects"]],
                *[f"route:{value}" for value in resources["owned_routes"]],
                *[f"sysctl:{value}" for value in resources["sysctls"]],
                *[
                    f"listener:{value}"
                    for value in self.resource_plan["listeners"]
                    if value.startswith("udp|")
                ],
            ],
            "web_started": [
                "service-state:amn2-spain-web.service:active",
                *[
                    f"listener:{value}"
                    for value in self.resource_plan["listeners"]
                    if value.startswith("tcp|")
                ],
            ],
        }

    def _apply_runtime_under_held_lock(self) -> dict[str, object]:
        stage_objects = self._stage_objects()
        all_objects = [
            value
            for stage in self.MUTATING_STAGES
            for value in stage_objects[stage]
        ]
        self.backend.assert_no_collisions(all_objects)
        stage = "runtime_initialization"
        try:
            for stage in self.MUTATING_STAGES:
                self.backend.apply_stage(stage, stage_objects[stage])
                self.backend.append_journal(stage)
            invariants = self.resource_plan["runtime_invariants"]
            self.backend.set_runtime_state(invariants)
            observation = self.backend.observe_postinstall()
            if not isinstance(observation, dict) or set(observation) != {
                "runtime",
                "systemd_projection",
                "foreign_firewall",
                "owned_objects",
                "unexpected_objects",
            }:
                raise InstallError("backend postinstall observation schema mismatch")
            runtime = observation["runtime"]
            if not isinstance(runtime, dict):
                raise InstallError("backend runtime observation invalid")
            for key, expected in invariants.items():
                if runtime.get(key) != expected:
                    raise InstallError(f"runtime invariant mismatch: {key}")
            assert_systemd_projection(
                self.baseline["systemd_projection"],
                observation["systemd_projection"],
            )
            assert_firewall_projection(
                self.baseline["firewall"]["nft_json"],
                observation["foreign_firewall"],
                sealed_namespace=self.resource_plan["firewall_namespace"],
                expected_owned_nft=expected_table_document(),
            )
            if set(observation["owned_objects"]) != set(self.backend.created_objects):
                raise InstallError("closed owned delta mismatch")
            if observation["unexpected_objects"] != []:
                raise InstallError("unexpected unowned objects observed")
            self.backend.append_journal("postinstall_verified")
        except Exception as exc:
            try:
                self.backend.rollback()
                self.backend.append_journal("rolled_back")
            except Exception as rollback_exc:
                raise InstallError(
                    f"partial rollback failure after {stage}: {rollback_exc}"
                ) from exc
            if isinstance(exc, InstallError):
                raise
            raise InstallError(f"install failed at {stage}") from exc
        return {
            "schema": "amn2.spain-install-result.v1",
            "result": "passed",
            "stage": "postinstall_verified",
            "owned_objects": list(self.backend.created_objects),
        }

    def install_after_bootstrap(
        self,
        bootstrap_result: BootstrapResult,
        *,
        authorization: InstallAuthorization,
    ) -> dict[str, object]:
        if (
            not isinstance(bootstrap_result, BootstrapResult)
            or not isinstance(authorization, InstallAuthorization)
            or bootstrap_result.staged_package.report.archive_sha256
            != authorization.package_archive_sha256
            or bootstrap_result.staged_package.report.manifest_sha256
            != authorization.package_manifest_sha256
            or bootstrap_result.staged_package.report.resource_plan_sha256
            != authorization.resource_plan_sha256
            or authorization.resource_plan_sha256
            != sha256_canonical(self.resource_plan)
            or bootstrap_result.staged_package.report.run009_evidence_sha256
            != authorization.run009_evidence_sha256
            or bootstrap_result.staged_package.report.fingerprint_array_sha256
            != authorization.fingerprint_array_sha256
            or bootstrap_result.tombstone.name
            != "authorization-" + authorization.nonce + ".json"
        ):
            raise InstallError("bootstrap continuation binding mismatch")
        if isinstance(self.backend, ProductionBackend):
            capsule = bootstrap_result.recovery_capsule
            transaction = bootstrap_result.transaction_ledger.snapshot()
            if (
                not isinstance(capsule, RecoveryCapsuleStore)
                or transaction["status"] != "capsule_committed"
                or transaction["recovery_capsule_sha256"] != capsule.sha256
                or transaction["action_blueprint_sha256"]
                != capsule.blueprint.digest
                or transaction["package"]["prepared_source_inventory"]
                != bootstrap_result.staged_package.prepared_source_inventory
            ):
                raise InstallError("production recovery capsule binding mismatch")
            reopened_capsule = RecoveryCapsuleStore.open_existing(
                audit_root=bootstrap_result.transaction_ledger.path.parent,
                nonce=authorization.nonce,
                expected_uid=bootstrap_result.transaction_ledger.expected_uid,
            )
            if reopened_capsule.sha256 != capsule.sha256:
                raise InstallError("production recovery capsule changed")
        try:
            descriptor = os.open(
                bootstrap_result.tombstone,
                os.O_RDONLY
                | getattr(os, "O_NOFOLLOW", 0)
                | getattr(os, "O_BINARY", 0),
            )
            try:
                info = os.fstat(descriptor)
                raw = os.read(descriptor, 64 * 1024 + 1)
            finally:
                os.close(descriptor)
            if (
                not stat.S_ISREG(info.st_mode)
                or len(raw) > 64 * 1024
                or (
                    os.name != "nt"
                    and (stat.S_IMODE(info.st_mode) != 0o600 or info.st_uid != 0)
                )
            ):
                raise InstallError("bootstrap tombstone owner/mode/type mismatch")
            tombstone = json.loads(raw)
        except (OSError, json.JSONDecodeError) as exc:
            raise InstallError("bootstrap tombstone unavailable") from exc
        if (
            raw
            != json.dumps(tombstone, sort_keys=True, separators=(",", ":")).encode(
                "utf-8"
            )
            + b"\n"
            or tombstone != authorization.tombstone_mapping()
        ):
            raise InstallError("bootstrap tombstone binding mismatch")
        if isinstance(self.backend, ProductionBackend):
            bootstrap_result.transaction_ledger.record_runtime_started()
        return self._apply_runtime_under_held_lock()

    def install(
        self,
        receipt: dict[str, Any] | None,
        detached_sha256: str | None,
        *,
        package_manifest_sha256: str,
        package_report: PackageVerificationReport | None = None,
        authorization: InstallAuthorization | None = None,
        now_epoch: int | None = None,
    ) -> dict[str, object]:
        if not isinstance(package_report, PackageVerificationReport):
            raise InstallError("immutable verified package report is required")
        if (
            package_report.manifest_sha256 != package_manifest_sha256
            or package_report.resource_plan_sha256 != sha256_canonical(self.resource_plan)
            or package_report.fingerprint_entry_count != 148
        ):
            raise InstallError("verified package report binding mismatch")
        if not isinstance(authorization, InstallAuthorization):
            raise InstallError("separate install authorization is required")
        if not isinstance(now_epoch, int) or isinstance(now_epoch, bool):
            raise InstallError("trusted current time is required")
        if receipt is None or detached_sha256 is None:
            raise InstallError("valid precondition receipt is required before mutation")
        try:
            verify_precondition_receipt(
                receipt,
                detached_sha256,
                package_manifest_sha256=package_manifest_sha256,
                resource_plan_sha256=sha256_canonical(self.resource_plan),
                host_identity_sha256=authorization.host_identity_sha256,
                boot_id=authorization.boot_id,
                collector_sha256=authorization.collector_sha256,
                executor_sha256=authorization.executor_sha256,
                package_archive_sha256=package_report.archive_sha256,
                package_archive_size=package_report.archive_size,
            )
        except PreconditionError as exc:
            raise InstallError("invalid precondition receipt") from exc
        if (
            authorization.precondition_receipt_sha256 != detached_sha256
            or authorization.package_archive_sha256 != package_report.archive_sha256
            or authorization.package_archive_size != package_report.archive_size
            or authorization.package_manifest_sha256 != package_report.manifest_sha256
            or authorization.resource_plan_sha256 != package_report.resource_plan_sha256
            or receipt["collector_sha256"] != authorization.collector_sha256
            or receipt["executor_sha256"] != authorization.executor_sha256
            or receipt["run009_evidence_sha256"] != package_report.run009_evidence_sha256
            or receipt["fingerprint_array_sha256"] != package_report.fingerprint_array_sha256
            or authorization.run009_evidence_sha256 != package_report.run009_evidence_sha256
            or authorization.fingerprint_array_sha256 != package_report.fingerprint_array_sha256
            or authorization.nonce != receipt["nonce"]
            or authorization.approved_at_epoch > receipt["issued_at_epoch"]
            or authorization.expires_at_epoch > receipt["expires_at_epoch"]
            or now_epoch > authorization.expires_at_epoch
            or now_epoch < authorization.approved_at_epoch
        ):
            raise InstallError("install authorization binding/expiry mismatch")
        with self.backend.install_lock():
            critical = self.backend.observe_critical()
            if critical != {
                "host_identity_sha256": receipt["host_identity_sha256"],
                "boot_id": receipt["boot_id"],
                "observation_sha256": receipt["observation_sha256"],
            }:
                raise InstallError("critical under-lock recheck mismatch")
            self.backend.consume_authorization(authorization.nonce)
            for stage in self.STAGES[:5]:
                self.backend.append_journal(stage)
            return self._apply_runtime_under_held_lock()


def _read_json_file(
    path: Path,
    *,
    label: str,
    expected_uid: int | None,
    require_canonical: bool = True,
    max_bytes: int = 16 * 1024 * 1024,
) -> dict[str, Any]:
    candidate = Path(path)
    if not candidate.is_absolute() or candidate.is_symlink():
        raise InstallError(f"{label} path invalid")
    try:
        descriptor = os.open(
            candidate,
            os.O_RDONLY
            | getattr(os, "O_NOFOLLOW", 0)
            | getattr(os, "O_BINARY", 0),
        )
        try:
            before = os.fstat(descriptor)
            payload = os.read(descriptor, max_bytes + 1)
            after = os.fstat(descriptor)
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise InstallError(f"{label} unavailable") from exc
    if (
        len(payload) > max_bytes
        or not stat.S_ISREG(before.st_mode)
        or (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
        != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
        or (
            os.name != "nt"
            and (
                stat.S_IMODE(before.st_mode) & 0o022 != 0
                or (expected_uid is not None and before.st_uid != expected_uid)
            )
        )
    ):
        raise InstallError(f"{label} owner/mode/type drift")
    try:
        value = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InstallError(f"{label} JSON invalid") from exc
    canonical = (
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
        + b"\n"
    )
    if not isinstance(value, dict) or (require_canonical and payload != canonical):
        raise InstallError(f"{label} canonical form invalid")
    return value


def _read_authorization_payload(payload: bytes) -> InstallAuthorization:
    if (
        not isinstance(payload, bytes)
        or not payload
        or len(payload) > 64 * 1024
        or not payload.endswith(b"\n")
    ):
        raise InstallError("install authorization stdin envelope invalid")
    try:
        value = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InstallError("install authorization stdin JSON invalid") from exc
    if (
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
        + b"\n"
        != payload
    ):
        raise InstallError("install authorization stdin canonical form invalid")
    return InstallAuthorization.from_mapping(value)


def _read_install_boundary_intent_payload(payload: bytes) -> InstallBoundaryIntent:
    if (
        not isinstance(payload, bytes)
        or not payload
        or len(payload) > 64 * 1024
        or not payload.endswith(b"\n")
    ):
        raise InstallError("install_bound_inputs_required")
    try:
        value = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InstallError("install_bound_inputs_required") from exc
    if (
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
        + b"\n"
        != payload
    ):
        raise InstallError("install_bound_inputs_required")
    try:
        return InstallBoundaryIntent.from_mapping(value)
    except InstallError as exc:
        raise InstallError("install_bound_inputs_required") from exc


def _read_manual_cleanup_intent_payload(payload: bytes) -> ManualCleanupIntent:
    if (
        not isinstance(payload, bytes)
        or not payload
        or len(payload) > 64 * 1024
        or not payload.endswith(b"\n")
    ):
        raise InstallError("manual_cleanup_bound_inputs_required")
    try:
        value = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InstallError("manual_cleanup_bound_inputs_required") from exc
    if (
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
        + b"\n"
        != payload
    ):
        raise InstallError("manual_cleanup_bound_inputs_required")
    try:
        return ManualCleanupIntent.from_mapping(value)
    except InstallError as exc:
        raise InstallError("manual_cleanup_bound_inputs_required") from exc


def _read_terminal_recovery_intent_payload(payload: bytes) -> TerminalRecoveryIntent:
    if (
        not isinstance(payload, bytes)
        or not payload
        or len(payload) > 64 * 1024
        or not payload.endswith(b"\n")
    ):
        raise InstallError("terminal_recovery_bound_inputs_required")
    try:
        value = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InstallError("terminal_recovery_bound_inputs_required") from exc
    if (
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
        + b"\n"
        != payload
    ):
        raise InstallError("terminal_recovery_bound_inputs_required")
    try:
        return TerminalRecoveryIntent.from_mapping(value)
    except InstallError as exc:
        raise InstallError("terminal_recovery_bound_inputs_required") from exc


def _sha256_regular_file(
    path: Path,
    *,
    expected_uid: int | None,
    max_bytes: int = 2 * 1024 * 1024 * 1024,
) -> tuple[str, int]:
    candidate = Path(path)
    if not candidate.is_absolute() or candidate.is_symlink():
        raise InstallError("checksum-bound file path invalid")
    try:
        descriptor = os.open(
            candidate,
            os.O_RDONLY
            | getattr(os, "O_NOFOLLOW", 0)
            | getattr(os, "O_BINARY", 0),
        )
        try:
            before = os.fstat(descriptor)
            digest = hashlib.sha256()
            size = 0
            while chunk := os.read(descriptor, 1024 * 1024):
                size += len(chunk)
                if size > max_bytes:
                    raise InstallError("checksum-bound file exceeds size limit")
                digest.update(chunk)
            after = os.fstat(descriptor)
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise InstallError("checksum-bound file unavailable") from exc
    if (
        not stat.S_ISREG(before.st_mode)
        or (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
        != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
        or (
            os.name != "nt"
            and (
                stat.S_IMODE(before.st_mode) & 0o022 != 0
                or (expected_uid is not None and before.st_uid != expected_uid)
            )
        )
    ):
        raise InstallError("checksum-bound file owner/mode/type drift")
    return digest.hexdigest(), size


def _assert_running_executor(
    executor_path: Path,
    expected_sha256: str,
    *,
    expected_uid: int | None,
) -> None:
    candidate = Path(executor_path)
    running = Path(sys.argv[0])
    if (
        re.fullmatch(r"[0-9a-f]{64}", expected_sha256) is None
        or not candidate.is_absolute()
        or not running.is_absolute()
        or candidate.is_symlink()
        or running.is_symlink()
    ):
        raise InstallError("running executor identity invalid")
    try:
        if not os.path.samefile(candidate, running):
            raise InstallError("running executor path mismatch")
    except OSError as exc:
        raise InstallError("running executor identity unavailable") from exc
    observed_sha256, _size = _sha256_regular_file(
        running,
        expected_uid=expected_uid,
        max_bytes=64 * 1024 * 1024,
    )
    if observed_sha256 != expected_sha256:
        raise InstallError("running executor checksum mismatch")


def _host_path(host_root: Path, live_path: str) -> Path:
    path = Path(live_path)
    root = Path(host_root)
    if not path.is_absolute() or not root.is_absolute():
        raise InstallError("production live path invalid")
    if root == Path("/"):
        return path
    return root.joinpath(*path.parts[1:])


@contextmanager
def _existing_opt_directory_lock(host_root: Path):
    target = _host_path(host_root, "/opt")
    try:
        descriptor = os.open(
            target,
            os.O_RDONLY
            | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_NOFOLLOW", 0),
        )
    except OSError as exc:
        raise InstallError("global install lock directory unavailable") from exc
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISDIR(info.st_mode):
            raise InstallError("global install lock target invalid")
        if os.name == "nt":
            raise InstallError("production install lock requires POSIX flock")
        import fcntl

        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise InstallError("global install lock already held") from exc
        try:
            yield (info.st_dev, info.st_ino)
        finally:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
    finally:
        os.close(descriptor)


def _critical_resource_binding(
    observer: ChecksumBoundResourceObserver,
    authorization: InstallAuthorization,
    *,
    resource_plan: dict[str, Any],
    baseline: dict[str, Any],
) -> tuple[dict[str, str], dict[str, Any]]:
    evidence = observer.collect_evidence()
    try:
        observation = observation_from_resource_confirmation_evidence(evidence)
        host_identity = evidence["host_identity"]
    except (PreconditionError, KeyError, TypeError) as exc:
        raise InstallError("critical resource evidence invalid") from exc
    if (
        host_identity.get("machine_id_sha256")
        != authorization.host_identity_sha256
        or host_identity.get("boot_id_sha256")
        != hashlib.sha256(authorization.boot_id.encode("ascii")).hexdigest()
    ):
        raise InstallError("critical host identity drift")
    try:
        validate_preconditions(observation, resource_plan, baseline)
    except PreconditionError as exc:
        raise InstallError("critical resource precondition drift") from exc
    return (
        {
            "host_identity_sha256": authorization.host_identity_sha256,
            "boot_id": authorization.boot_id,
        },
        observation,
    )


def _production_equality_observer(
    *,
    resource_observer: ChecksumBoundResourceObserver,
    baseline: Mapping[str, Any],
) -> Callable[[dict[str, str]], dict[str, Any]]:
    def observe(binding: dict[str, str]) -> dict[str, Any]:
        return build_rollback_equality_receipt(
            baseline_observation=baseline,
            current_observation=resource_observer.collect_observation(),
            binding=binding,
        )

    return observe


def _load_resource_plan(staged: StagedPackage) -> dict[str, Any]:
    plan = _read_json_file(
        staged.path.parent / "content" / "metadata" / "resource-plan.json",
        label="staged resource plan",
        expected_uid=None,
        require_canonical=False,
    )
    if sha256_canonical(plan) != staged.report.resource_plan_sha256:
        raise InstallError("staged resource plan binding mismatch")
    return plan


def _production_install(
    args: list[str],
    *,
    authorization_payload: bytes,
    host_root: Path = Path("/"),
    expected_uid: int | None = 0,
    receipt_override: dict[str, Any] | None = None,
    baseline_override: dict[str, Any] | None = None,
    authorization_override: InstallAuthorization | None = None,
) -> dict[str, Any]:
    if len(args) != 7:
        raise InstallError("install_inputs_required")
    receipt_path, detached, baseline_path, collector_path, executor_path, package_path, now_text = args
    if re.fullmatch(r"[0-9a-f]{64}", detached) is None:
        raise InstallError("install receipt digest invalid")
    try:
        now_epoch = int(now_text)
    except ValueError as exc:
        raise InstallError("install trusted time invalid") from exc
    overrides = (receipt_override, baseline_override, authorization_override)
    if any(value is None for value in overrides) and any(value is not None for value in overrides):
        raise InstallError("install in-memory input set incomplete")
    if all(value is not None for value in overrides):
        receipt = copy.deepcopy(receipt_override)
        baseline = copy.deepcopy(baseline_override)
        authorization = authorization_override
        if not isinstance(receipt, dict) or not isinstance(baseline, dict) or not isinstance(authorization, InstallAuthorization):
            raise InstallError("install in-memory input set invalid")
    else:
        authorization = _read_authorization_payload(authorization_payload)
        receipt = _read_json_file(
            Path(receipt_path), label="precondition receipt", expected_uid=expected_uid
        )
        baseline = _read_json_file(
            Path(baseline_path), label="baseline observation", expected_uid=expected_uid
        )
    if (
        hashlib.sha256(package_backend.canonical_json_bytes(receipt)).hexdigest()
        != detached
        or sha256_canonical(baseline) != receipt.get("baseline_sha256")
    ):
        raise InstallError("install receipt/baseline binding mismatch")
    critical_resource_plan = _embedded_resource_plan()
    if sha256_canonical(critical_resource_plan) != authorization.resource_plan_sha256:
        raise InstallError("critical resource plan binding mismatch")
    executor_sha256, _executor_size = _sha256_regular_file(
        Path(executor_path), expected_uid=expected_uid, max_bytes=64 * 1024 * 1024
    )
    if executor_sha256 != authorization.executor_sha256:
        raise InstallError("install executor checksum mismatch")
    _assert_running_executor(
        Path(executor_path),
        authorization.executor_sha256,
        expected_uid=expected_uid,
    )
    resource_observer = ChecksumBoundResourceObserver(
        collector_bytes=_embedded_resource_collector_bytes(),
        collector_sha256=authorization.collector_sha256,
        expected_uid=expected_uid,
    )
    lock_lease = SharedInstallLockLease(
        lambda: _existing_opt_directory_lock(Path(host_root))
    )
    audit_root = _host_path(host_root, "/var/lib/amn2-spain-phase12-audit")
    authorization_store = RetainedAuthorizationStore(
        audit_root, expected_uid=expected_uid
    )
    stager = ChecksumBoundPackageStager(
        host_root=Path(host_root),
        expected_uid=expected_uid,
        expected_gid=0 if expected_uid is not None else None,
    )
    journal: FsyncLedger | None = None

    def append_stage(stage: str) -> None:
        nonlocal journal
        if journal is None:
            journal = FsyncLedger(
                audit_root / ("install-journal-" + authorization.nonce + ".jsonl"),
                InstallStateMachine.STAGES,
                sealed_allowlist=set(),
            )
        journal.append_stage(stage)

    critical_cache: dict[str, str] | None = None

    def critical_observer() -> dict[str, str]:
        nonlocal critical_cache
        critical_cache, _observation = _critical_resource_binding(
            resource_observer,
            authorization,
            resource_plan=critical_resource_plan,
            baseline=baseline,
        )
        return copy.deepcopy(critical_cache)

    prepared_holder: dict[str, PreparedProductionInstallation] = {}

    def prepare_capsule(
        staged: StagedPackage,
        transaction: BootstrapTransactionLedger,
        approved: InstallAuthorization,
    ) -> RecoveryCapsuleStore:
        prepared = prepare_production_installation(
            staged_package=staged,
            transaction_ledger=transaction,
            authorization=approved,
            host_root=Path(host_root),
            expected_uid=expected_uid,
        )
        prepared_holder["value"] = prepared
        return prepared.capsule

    bootstrap = ChecksumBoundBootstrap(
        authorization=authorization,
        receipt=receipt,
        detached_receipt_sha256=detached,
        now_epoch=now_epoch,
        lock_lease=lock_lease,
        critical_observer=critical_observer,
        authorization_store=authorization_store,
        package_stager=stager,
        append_stage=append_stage,
        capsule_preparer=prepare_capsule,
    )

    def continue_install(result: BootstrapResult) -> dict[str, Any]:
        prepared = prepared_holder["value"]
        resource_plan = _load_resource_plan(result.staged_package)
        allowed = {
            operation.owned_object
            for operation in prepared.assembly.action_plan.operations
        }
        store = live_backend.DurableMutationLedgerStore(
            Path(prepared.capsule.blueprint.assembly_context["mutation_ledger_path"]),
            expected_uid=expected_uid,
        )
        mutation_ledger = store.load_or_create(allowed)
        linux = live_backend.LinuxBackend(
            adapter=live_backend.SystemOwnedAdapter(
                actions={
                    action.operation.owned_object: action
                    for action in prepared.assembly.action_plan.actions
                }
            ),
            ledger=mutation_ledger,
        )
        backend_holder: dict[str, ProductionBackend] = {}
        postinstall = ProductionPostinstallObserver(
            resource_observer=resource_observer,
            resource_plan=resource_plan,
            baseline_observation=baseline,
            created_objects=lambda: backend_holder["value"].created_objects,
            database_path=_host_path(
                host_root, "/var/lib/amn2-spain/amn2.sqlite3"
            ),
            runtime_env_path=_host_path(host_root, "/etc/amn2-spain/runtime.env"),
        )
        backend = ProductionBackend(
            action_plan=prepared.assembly.action_plan,
            blueprint=prepared.capsule.blueprint,
            linux_backend=linux,
            stage_object_contract=prepared.assembly.stage_object_contract,
            append_stage=append_stage,
            lock_lease=lock_lease,
            critical_observer=critical_observer,
            authorization_consumer=lambda _nonce: (_ for _ in ()).throw(
                InstallError("authorization already consumed by bootstrap")
            ),
            postinstall_observer=postinstall.observe,
        )
        backend_holder["value"] = backend
        return InstallStateMachine(backend, resource_plan, baseline).install_after_bootstrap(
            result,
            authorization=authorization,
        )

    descriptor = -1
    transaction: BootstrapTransactionLedger | None = None
    try:
        descriptor = os.open(
            Path(package_path),
            os.O_RDONLY
            | getattr(os, "O_NOFOLLOW", 0)
            | getattr(os, "O_BINARY", 0),
        )
        outcome = bootstrap.execute(descriptor, continuation=continue_install)
        return copy.deepcopy(outcome)
    except InstallError:
        prepared = prepared_holder.get("value")
        if prepared is not None:
            transaction = BootstrapTransactionLedger.open_existing(
                audit_root=audit_root,
                nonce=authorization.nonce,
                expected_uid=expected_uid,
            )
            ProductionRecoveryCoordinator(
                prepared=prepared,
                transaction_ledger=transaction,
                package_stager=stager,
                lock_lease=lock_lease,
                equality_observer=_production_equality_observer(
                    resource_observer=resource_observer,
                    baseline=baseline,
                ),
            ).rollback()
        raise
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def _recovery_inputs(
    args: list[str],
    *,
    host_root: Path,
    expected_uid: int | None,
) -> tuple[
    str,
    InstallAuthorization,
    dict[str, Any],
    ChecksumBoundResourceObserver,
    Path,
]:
    if len(args) != 5:
        raise InstallError("recovery_inputs_required")
    nonce, receipt_path, baseline_path, collector_path, executor_path = args
    if re.fullmatch(r"[0-9a-f]{64}", nonce) is None:
        raise InstallError("recovery nonce invalid")
    audit_root = _host_path(host_root, "/var/lib/amn2-spain-phase12-audit")
    tombstone = _read_json_file(
        audit_root / ("authorization-" + nonce + ".json"),
        label="retained authorization tombstone",
        expected_uid=expected_uid,
    )
    authorization = InstallAuthorization.from_tombstone_mapping(tombstone)
    receipt = _read_json_file(
        Path(receipt_path),
        label="recovery precondition receipt",
        expected_uid=expected_uid,
    )
    baseline = _read_json_file(
        Path(baseline_path),
        label="recovery baseline observation",
        expected_uid=expected_uid,
    )
    if (
        authorization.nonce != nonce
        or hashlib.sha256(package_backend.canonical_json_bytes(receipt)).hexdigest()
        != authorization.precondition_receipt_sha256
        or sha256_canonical(baseline) != receipt.get("baseline_sha256")
    ):
        raise InstallError("recovery receipt/baseline binding mismatch")
    try:
        verify_precondition_receipt(
            receipt,
            authorization.precondition_receipt_sha256,
            package_manifest_sha256=authorization.package_manifest_sha256,
            resource_plan_sha256=authorization.resource_plan_sha256,
            host_identity_sha256=authorization.host_identity_sha256,
            boot_id=authorization.boot_id,
            collector_sha256=authorization.collector_sha256,
            executor_sha256=authorization.executor_sha256,
            package_archive_sha256=authorization.package_archive_sha256,
            package_archive_size=authorization.package_archive_size,
        )
    except PreconditionError as exc:
        raise InstallError("recovery precondition receipt invalid") from exc
    executor_sha256, _executor_size = _sha256_regular_file(
        Path(executor_path), expected_uid=expected_uid, max_bytes=64 * 1024 * 1024
    )
    if executor_sha256 != authorization.executor_sha256:
        raise InstallError("recovery executor checksum mismatch")
    _assert_running_executor(
        Path(executor_path),
        authorization.executor_sha256,
        expected_uid=expected_uid,
    )
    observer = ChecksumBoundResourceObserver(
        collector_bytes=_embedded_resource_collector_bytes(),
        collector_sha256=authorization.collector_sha256,
        expected_uid=expected_uid,
    )
    return nonce, authorization, baseline, observer, audit_root


def _rollback_binding(
    transaction: BootstrapTransactionLedger,
    *,
    blueprint_sha256: str,
) -> dict[str, str]:
    state = transaction.snapshot()
    if re.fullmatch(r"[0-9a-f]{64}", blueprint_sha256) is None:
        raise InstallError("recovery blueprint binding invalid")
    return {
        "nonce": state["nonce"],
        "transaction_sha256": hashlib.sha256(
            BootstrapTransactionLedger._canonical(state)
        ).hexdigest(),
        "blueprint_sha256": blueprint_sha256,
    }


def _assert_rollback_equality_transaction_binding(
    receipt: Mapping[str, Any],
    transaction: BootstrapTransactionLedger,
    *,
    blueprint_sha256: str,
) -> None:
    if not isinstance(transaction, BootstrapTransactionLedger):
        raise InstallError("rollback equality transaction dependency invalid")
    expected = _rollback_binding(
        transaction,
        blueprint_sha256=blueprint_sha256,
    )
    if any(receipt.get(key) != value for key, value in expected.items()):
        raise InstallError("rolled-back recovery equality binding mismatch")


def _persist_current_equality(
    *,
    transaction: BootstrapTransactionLedger,
    baseline: Mapping[str, Any],
    observer: ChecksumBoundResourceObserver,
    blueprint_sha256: str,
) -> dict[str, Any]:
    receipt = build_rollback_equality_receipt(
        baseline_observation=baseline,
        current_observation=observer.collect_observation(),
        binding=_rollback_binding(
            transaction,
            blueprint_sha256=blueprint_sha256,
        ),
    )
    _persist_or_open_rollback_equality_receipt(
        audit_root=transaction.path.parent,
        receipt=receipt,
        expected_uid=transaction.expected_uid,
    )
    return receipt


def _production_recover(
    args: list[str],
    *,
    mode: str,
    host_root: Path = Path("/"),
    expected_uid: int | None = 0,
) -> dict[str, Any]:
    nonce, authorization, baseline, observer, audit_root = _recovery_inputs(
        args,
        host_root=host_root,
        expected_uid=expected_uid,
    )
    lock_lease = SharedInstallLockLease(
        lambda: _existing_opt_directory_lock(Path(host_root))
    )
    transaction = BootstrapTransactionLedger.open_existing(
        audit_root=audit_root,
        nonce=nonce,
        expected_uid=expected_uid,
    )
    status = transaction.snapshot()["status"]
    stager = ChecksumBoundPackageStager(
        host_root=Path(host_root),
        expected_uid=expected_uid,
        expected_gid=0 if expected_uid is not None else None,
    )
    if mode == "manual-cleanup":
        if status != "manual_recovery_required":
            raise InstallError("manual cleanup terminal state required")
        with lock_lease.acquire():
            stager.manual_cleanup_terminal(transaction, lock_lease)
        return {
            "schema": "amn2.spain-manual-cleanup-receipt.v1",
            "result": "passed",
            "nonce": nonce,
            "transaction_status": transaction.snapshot()["status"],
        }
    if status == "manual_recovery_required":
        raise InstallError("recovery requires manual intervention")
    capsule_statuses = {
        "capsule_committed",
        "runtime_started",
        "rollback_required",
    }
    if mode == "rollback" and status not in capsule_statuses:
        raise InstallError("rollback runtime state unavailable")
    equality_path = audit_root / ("rollback-equality-" + nonce + ".json")
    capsule_path = audit_root / ("recovery-capsule-" + nonce + ".json")
    capsule_temporary = capsule_path.parent / ("." + capsule_path.name + ".tmp")
    if status not in capsule_statuses and (
        capsule_path.exists()
        or capsule_path.is_symlink()
        or capsule_temporary.exists()
        or capsule_temporary.is_symlink()
    ):
        with lock_lease.acquire():
            RecoveryCapsuleStore.remove_uncommitted(
                transaction_ledger=transaction,
                lock_lease=lock_lease,
            )
        status = transaction.snapshot()["status"]
    if status == "rolled_back":
        state = transaction.snapshot()
        blueprint = state.get("action_blueprint_sha256") or "0" * 64
        if equality_path.exists() or equality_path.is_symlink():
            receipt = _read_rollback_equality_receipt(
                equality_path,
                expected_uid=expected_uid,
            )
        else:
            receipt = _persist_current_equality(
                transaction=transaction,
                baseline=baseline,
                observer=observer,
                blueprint_sha256=blueprint,
            )
        _assert_rollback_equality_transaction_binding(
            receipt,
            transaction,
            blueprint_sha256=blueprint,
        )
        if state.get("recovery_capsule_sha256") is not None and (
            capsule_path.exists() or capsule_path.is_symlink()
        ):
            finalized = finalize_rolled_back_recovery(
                audit_root=audit_root,
                nonce=nonce,
                lock_lease=lock_lease,
                expected_uid=expected_uid,
            )
            if finalized != receipt:
                raise InstallError("rolled-back equality receipt drift")
        return receipt
    if status in capsule_statuses:
        capsule = RecoveryCapsuleStore.open_existing(
            audit_root=audit_root,
            nonce=nonce,
            expected_uid=expected_uid,
        )
        prepared = reconstruct_production_installation(
            capsule=capsule,
            transaction_ledger=transaction,
            authorization=authorization,
        )
        return ProductionRecoveryCoordinator(
            prepared=prepared,
            transaction_ledger=transaction,
            package_stager=stager,
            lock_lease=lock_lease,
            equality_observer=_production_equality_observer(
                resource_observer=observer,
                baseline=baseline,
            ),
        ).rollback()
    with lock_lease.acquire():
        stager.recover_or_rollback(transaction, lock_lease)
    return _persist_current_equality(
        transaction=transaction,
        baseline=baseline,
        observer=observer,
        blueprint_sha256="0" * 64,
    )


def _production_manual_cleanup_bound(
    intent: ManualCleanupIntent,
    *,
    host_root: Path = Path("/"),
    expected_uid: int | None = 0,
    now_epoch: int | None = None,
) -> dict[str, Any]:
    now = int(time.time()) if now_epoch is None else now_epoch
    if not isinstance(now, int) or isinstance(now, bool):
        raise InstallError("manual cleanup clock invalid")
    if now < intent.approved_at_epoch or now > intent.expires_at_epoch:
        raise InstallError("manual cleanup intent expired")
    running_executor = Path(sys.argv[0]).resolve()
    _assert_running_executor(
        running_executor,
        intent.executor_sha256,
        expected_uid=expected_uid,
    )
    audit_root = _host_path(host_root, "/var/lib/amn2-spain-phase12-audit")
    transaction = BootstrapTransactionLedger.open_existing(
        audit_root=audit_root,
        nonce=intent.nonce,
        expected_uid=expected_uid,
    )
    tombstone = _read_json_file(
        audit_root / ("authorization-" + intent.nonce + ".json"),
        label="retained authorization tombstone",
        expected_uid=expected_uid,
    )
    if InstallAuthorization.from_tombstone_mapping(tombstone).nonce != intent.nonce:
        raise InstallError("manual cleanup authorization binding mismatch")
    if transaction.snapshot()["status"] != "manual_recovery_required":
        raise InstallError("manual cleanup terminal state required")
    transaction_sha256 = hashlib.sha256(
        BootstrapTransactionLedger._canonical(transaction.snapshot())
    ).hexdigest()
    lock_lease = SharedInstallLockLease(
        lambda: _existing_opt_directory_lock(Path(host_root))
    )
    stager = ChecksumBoundPackageStager(
        host_root=Path(host_root),
        expected_uid=expected_uid,
        expected_gid=0 if expected_uid is not None else None,
    )
    with lock_lease.acquire():
        stager.manual_cleanup_terminal(transaction, lock_lease)
    return {
        "schema": "amn2.spain-manual-cleanup-receipt.v1",
        "result": "passed",
        "approval_id": intent.approval_id,
        "nonce": intent.nonce,
        "transaction_sha256": transaction_sha256,
        "transaction_status": transaction.snapshot()["status"],
    }


def _classify_terminal_recovery_ledger(
    *,
    ledger: Any,
    blueprint: Mapping[str, Any],
    expected_objects: set[str],
) -> str:
    if any(
        (event := ledger.event_for(name)) is not None and event["event"] == "intent"
        for name in blueprint
    ):
        raise InstallError("terminal recovery mutation ledger mismatch")
    committed = {
        name for name in expected_objects
        if (event := ledger.event_for(name)) is not None and event["event"] == "committed"
    }
    removed = {
        name for name in expected_objects
        if (event := ledger.event_for(name)) is not None and event["event"] == "removed"
    }
    if committed == expected_objects and not removed:
        return "removed_verified_owned_objects"
    if removed == expected_objects and not committed:
        return "verified_previously_removed_owned_objects"
    raise InstallError("terminal recovery mutation ledger mismatch")


def _production_terminal_recovery_bound(
    intent: TerminalRecoveryIntent, *, host_root: Path = Path("/"), expected_uid: int | None = 0,
    now_epoch: int | None = None, receipt_only: bool = False,
) -> dict[str, Any]:
    now = int(time.time()) if now_epoch is None else now_epoch
    if now < intent.approved_at_epoch or now > intent.expires_at_epoch:
        raise InstallError("terminal recovery intent expired")
    _assert_running_executor(Path(sys.argv[0]).resolve(), intent.executor_sha256, expected_uid=expected_uid)
    audit_root = _host_path(host_root, "/var/lib/amn2-spain-phase12-audit")
    transaction = BootstrapTransactionLedger.open_existing(audit_root=audit_root, nonce=intent.nonce, expected_uid=expected_uid)
    state = transaction.snapshot()
    transaction_sha256 = hashlib.sha256(BootstrapTransactionLedger._canonical(state)).hexdigest()
    if state["status"] != "manual_recovery_required" or transaction_sha256 != intent.transaction_sha256:
        raise InstallError("terminal recovery transaction binding mismatch")
    capsule = RecoveryCapsuleStore.open_existing(audit_root=audit_root, nonce=intent.nonce, expected_uid=expected_uid)
    if capsule.sha256 != intent.capsule_sha256 or state.get("recovery_capsule_sha256") != capsule.sha256:
        raise InstallError("terminal recovery capsule binding mismatch")
    package_root = _host_path(host_root, "/opt/amn2-spain-package")
    if package_root.exists() or package_root.is_symlink():
        raise InstallError("terminal recovery package tree must be absent")
    root = Path(host_root)
    root_fs = live_backend.SafeFs(root=root, expected_uid=0, expected_gid=0)
    config_fs = live_backend.SafeFs(root=root, expected_uid=0, expected_gid=61212)
    service_fs = live_backend.SafeFs(root=root, expected_uid=61212, expected_gid=61212)
    directories = (
        (root_fs, "opt/amn2-spain", 0o755),
        (root_fs, "opt/amn2-spain/runtime", 0o755),
        (config_fs, "etc/amn2-spain", 0o750),
        (service_fs, "var/lib/amn2-spain", 0o750),
        (service_fs, "var/lib/amn2-spain/logs", 0o750),
        (service_fs, "var/lib/amn2-spain/config-templates", 0o750),
    )
    actions = {action.operation.owned_object: action for action in live_backend.build_production_identity_bundle().actions}
    for fs, relative, mode in directories:
        action = live_backend.build_directory_action(fs, "filesystem_staged", relative, mode)
        actions[action.operation.owned_object] = action
    docker_base = live_backend.build_directory_action(root_fs, "filesystem_staged", "var/lib/amn2-spain-docker", 0o700)
    def observe_docker_rollback() -> str | None:
        return None if root_fs.identity("var/lib/amn2-spain-docker") is None else docker_base.operation.desired_identity
    docker_action = live_backend.SystemAction(
        operation=docker_base.operation,
        observe_identity=docker_base.observe_identity,
        observe_rollback_identity=observe_docker_rollback,
        create_exact=docker_base.create_exact,
        remove_exact=lambda identity: live_backend.cleanup_terminal_docker_data_root(
            fs=root_fs, relative="var/lib/amn2-spain-docker", expected_identity=identity,
            expected_tree_sha256=intent.docker_tree_sha256,
            expected_tree_entry_count=intent.docker_tree_entry_count,
            expected_tree_total_bytes=intent.docker_tree_total_bytes,
        ),
    )
    actions[docker_action.operation.owned_object] = docker_action
    blueprint = {entry["owned_object"]: entry for entry in capsule.blueprint.actions}
    expected_objects = set(actions)
    if set(blueprint) & expected_objects != expected_objects or any(
        live_backend.OwnedOperation(entry["stage"], entry["owned_object"], entry["desired_identity"]) != actions[name].operation
        for name, entry in blueprint.items() if name in actions
    ):
        raise InstallError("terminal recovery action blueprint mismatch")
    ledger_path = Path(capsule.blueprint.assembly_context["mutation_ledger_path"])
    ledger = live_backend.DurableMutationLedgerStore(ledger_path, expected_uid=expected_uid).load_or_create(set(blueprint))
    recovery_action = _classify_terminal_recovery_ledger(
        ledger=ledger,
        blueprint=blueprint,
        expected_objects=expected_objects,
    )
    if receipt_only and recovery_action != "verified_previously_removed_owned_objects":
        raise InstallError("terminal recovery receipt requires removed contour")
    observer = ChecksumBoundResourceObserver(collector_bytes=_embedded_resource_collector_bytes(), collector_sha256=hashlib.sha256(_embedded_resource_collector_bytes()).hexdigest(), expected_uid=expected_uid)
    before = observation_from_resource_confirmation_evidence(observer.collect_evidence())
    if recovery_action == "removed_verified_owned_objects":
        ordered = [actions[entry["owned_object"]].operation for entry in capsule.blueprint.actions if entry["owned_object"] in actions]
        lease = SharedInstallLockLease(lambda: _existing_opt_directory_lock(root))
        with lease.acquire():
            live_backend.LinuxBackend(adapter=live_backend.SystemOwnedAdapter(actions=actions), ledger=ledger).rollback(ordered)
    after = observation_from_resource_confirmation_evidence(observer.collect_evidence())
    equality = build_terminal_recovery_equality_receipt(
        baseline_observation=before, current_observation=after,
        binding={"nonce": intent.nonce, "transaction_sha256": transaction_sha256, "blueprint_sha256": capsule.blueprint.digest},
    )
    return {"schema": "amn2.spain-terminal-recovery-receipt.v1", "result": "passed", "recovery_action": recovery_action, "approval_id": intent.approval_id, "nonce": intent.nonce, "transaction_sha256": transaction_sha256, "capsule_sha256": capsule.sha256, "docker_tree_sha256": intent.docker_tree_sha256, "foreign_service_persistent_equal": equality["foreign_service_persistent_equal"], "foreign_service_volatile_before_count": equality["foreign_service_volatile_before_count"], "foreign_service_volatile_after_count": equality["foreign_service_volatile_after_count"]}


def run_production_command(
    argv: list[str],
    *,
    authorization_payload: bytes | None = None,
    host_root: Path = Path("/"),
    expected_uid: int | None = 0,
) -> dict[str, Any]:
    args = list(argv)
    if not args or args[0] not in {"install", "install-bound", "manual-cleanup", "manual-cleanup-bound", "terminal-recovery-bound", "terminal-recovery-receipt-bound", "recover", "rollback", "verify"}:
        raise InstallError("unsupported_mode")
    mode = args.pop(0)
    if mode == "install-bound":
        if args:
            raise InstallError("install_bound_inputs_required")
        payload = authorization_payload
        if payload is None:
            payload = sys.stdin.buffer.read(64 * 1024 + 1)
        intent = _read_install_boundary_intent_payload(payload)
        try:
            observer = ChecksumBoundResourceObserver(
                collector_bytes=_embedded_resource_collector_bytes(),
                collector_sha256=intent.collector_sha256,
                expected_uid=expected_uid,
            )
            evidence = observer.collect_evidence()
        except (InstallError, BackendError) as exc:
            raise InstallError("install_bound_precondition_failed") from exc
        boot_id = _read_boot_id(expected_uid=expected_uid)
        receipt, detached, baseline, authorization = _build_in_memory_install_inputs_from_evidence(
            intent=intent,
            evidence=evidence,
            boot_id=boot_id,
            now_epoch=int(time.time()),
        )
        return _production_install(
            [
                "/in-memory/receipt",
                detached,
                "/in-memory/baseline",
                "/in-memory/collector",
                str(Path(sys.argv[0]).resolve()),
                "/root/amn2-spain-phase12-install.tar",
                str(int(time.time())),
            ],
            authorization_payload=b"",
            host_root=host_root,
            expected_uid=expected_uid,
            receipt_override=receipt,
            baseline_override=baseline,
            authorization_override=authorization,
        )
    if mode == "manual-cleanup-bound":
        if args:
            raise InstallError("manual_cleanup_bound_inputs_required")
        payload = authorization_payload
        if payload is None:
            payload = sys.stdin.buffer.read(64 * 1024 + 1)
        intent = _read_manual_cleanup_intent_payload(payload)
        return _production_manual_cleanup_bound(
            intent,
            host_root=host_root,
            expected_uid=expected_uid,
        )
    if mode in {"terminal-recovery-bound", "terminal-recovery-receipt-bound"}:
        if args:
            raise InstallError("terminal_recovery_bound_inputs_required")
        payload = authorization_payload
        if payload is None:
            payload = sys.stdin.buffer.read(64 * 1024 + 1)
        intent = _read_terminal_recovery_intent_payload(payload)
        return _production_terminal_recovery_bound(
            intent,
            host_root=host_root,
            expected_uid=expected_uid,
            receipt_only=mode == "terminal-recovery-receipt-bound",
        )
    if mode == "install":
        if len(args) != 7:
            raise InstallError("install_inputs_required")
        payload = authorization_payload
        if payload is None:
            payload = sys.stdin.buffer.read(64 * 1024 + 1)
        return _production_install(
            args,
            authorization_payload=payload,
            host_root=host_root,
            expected_uid=expected_uid,
        )
    if mode == "verify":
        if len(args) != 2:
            raise InstallError("verify_inputs_required")
        collector_path, collector_sha256 = args
        observation = ChecksumBoundResourceObserver(
            collector_bytes=_embedded_resource_collector_bytes(),
            collector_sha256=collector_sha256,
            expected_uid=expected_uid,
        ).collect_observation()
        return {
            "schema": "amn2.spain-live-verify-result.v1",
            "result": "passed",
            "observation_sha256": sha256_canonical(observation),
        }
    if len(args) != 5:
        raise InstallError(f"{mode}_inputs_required")
    return _production_recover(
        args,
        mode=mode,
        host_root=host_root,
        expected_uid=expected_uid,
    )


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    try:
        result = run_production_command(args)
    except InstallError as exc:
        message = str(exc)
        print(message if message else "install_failed", file=sys.stderr)
        if message in {
            "unsupported_mode",
            "install_bound_inputs_required",
            "install_inputs_required",
            "recover_inputs_required",
            "rollback_inputs_required",
            "recovery_inputs_required",
            "verify_inputs_required",
        }:
            return 64
        return 78
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
