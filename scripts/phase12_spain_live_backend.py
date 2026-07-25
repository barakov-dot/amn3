from __future__ import annotations

import copy
import hashlib
import io
import json
import os
import importlib
import importlib.util
import re
import secrets
import stat
import subprocess
import sys
import tarfile
import tempfile
import threading
import zipfile
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from types import MappingProxyType
from typing import Any, Callable, Iterable, Iterator, Mapping, Protocol


MAX_COMMAND_OUTPUT = 1024 * 1024
MAX_COMMAND_INPUT = 4096
MAX_COMMAND_STREAM_INPUT = 256 * 1024 * 1024
DEFAULT_COMMAND_TIMEOUT = 15.0
IDENTITY_PATTERN = "sha256:"
ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = ROOT / "packaging" / "phase12-spain" / "templates"

DOCKER = "/opt/amn2-spain/docker/bin/docker"
DOCKER_SOCKET = "unix:///run/amn2-spain-docker/docker.sock"
AWG_IMAGE_PLATFORM_DIGEST = (
    "sha256:3c78eb57ef5cb44f63aed185e79c104593c854a5ebde3e1075470301bcc77c44"
)
AWG_IMAGE_CONFIG_DIGEST = (
    "sha256:0f21ddfb3313affe3a336693886ced918301335815e4b7db3d15b5a0a5da6afb"
)
AWG_IMAGE_REFERENCE = "amneziavpn/amneziawg-go@" + AWG_IMAGE_PLATFORM_DIGEST
AWG_LOCAL_IMAGE_TAG = "amn2-spain-awg:phase12"
STATIC_DOCKER_RELATIVE_PATHS = (
    "opt/amn2-spain/docker/bin/containerd",
    "opt/amn2-spain/docker/bin/containerd-shim-runc-v2",
    "opt/amn2-spain/docker/bin/ctr",
    "opt/amn2-spain/docker/bin/docker",
    "opt/amn2-spain/docker/bin/docker-init",
    "opt/amn2-spain/docker/bin/docker-proxy",
    "opt/amn2-spain/docker/bin/dockerd",
    "opt/amn2-spain/docker/bin/runc",
)
MAX_STATIC_DOCKER_ARCHIVE_BYTES = 512 * 1024 * 1024
REQUIRED_CLOSED_DELTA_OBJECTS = frozenset(
    {
        "group:amn2-spain",
        "user:amn2-spain",
        "gid:61212",
        "uid:61212",
        "socket:/run/amn2-spain-docker/docker.sock",
        "runtime:docker-static",
        "image:" + AWG_IMAGE_CONFIG_DIGEST,
        "network:amn2-spain-net",
        "bridge:amn2spbr0",
        "container:amn2-spain-awg",
        "interface:awgsp0",
        "firewall:inet:amn2_spain",
        "listener:udp:30001",
        "route:10.212.12.0/24",
        "sysctl:net.ipv4.ip_forward",
        "listener:tcp:127.0.0.1:3031",
        "database:/var/lib/amn2-spain/amn2.sqlite3",
        "unit:amn2-spain-docker.service",
        "unit:amn2-spain-network.service",
        "unit:amn2-spain-web.service",
        "unit:amn2-spain-bot.service",
    }
)

PRODUCTION_FILE_SECURITY = MappingProxyType(
    {
        "etc/amn2-spain/runtime.env": ("root", "root", 0o600),
        "etc/amn2-spain/awgsp0.conf": ("root", "root", 0o600),
        "etc/amn2-spain/servers.yml": ("root", "service", 0o640),
        "etc/amn2-spain/docker-daemon.json": ("root", "root", 0o644),
        "opt/amn2-spain/runtime/awg-start.sh": ("root", "root", 0o755),
        "opt/amn2-spain/current/scripts/phase12_spain_network.py": (
            "root", "root", 0o644,
        ),
        "opt/amn2-spain/current/packaging/phase12-spain/templates/nftables.conf": (
            "root", "root", 0o644,
        ),
    }
)
POSTINSTALL_BINDING_FIELDS = frozenset(
    {
        "collector_sha256",
        "executor_sha256",
        "run009_evidence_sha256",
        "fingerprint_array_sha256",
        "package_archive_sha256",
        "package_manifest_sha256",
        "resource_plan_sha256",
        "approval_sha256",
    }
)


class BackendError(RuntimeError):
    """Fail-closed live-backend boundary error with no command output attached."""


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
        "ascii"
    )


def _digest(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def classify_docker_image_load_failure(stderr: bytes, return_code: int) -> str:
    """Reduce Docker image-load stderr to a fixed, secret-free failure label."""
    text = stderr.decode("utf-8", errors="ignore").casefold()
    if "no space left on device" in text:
        return "docker_image_load_no_space"
    if "invalid tar" in text or "unexpected eof" in text or "unexpected end of file" in text:
        return "docker_image_load_archive"
    if "permission denied" in text or "operation not permitted" in text:
        return "docker_image_load_permission"
    if (
        "cannot connect to the docker daemon" in text
        or "is the docker daemon running" in text
        or "connection refused" in text
    ):
        return "docker_image_load_daemon_unavailable"
    if "failed to register layer" in text or "failed to apply layer" in text:
        return "docker_image_load_layer_apply"
    if "not supported" in text or "unsupported" in text:
        return "docker_image_load_unsupported"
    if isinstance(return_code, int) and not isinstance(return_code, bool) and 1 <= return_code <= 255:
        return "docker_image_load_exit_" + str(return_code)
    return "docker_image_load_exit_unknown"


_DOCKER_IMAGE_LOAD_SAFE_LABEL = re.compile(
    r"docker_image_load_(?:no_space|archive|permission|daemon_unavailable|layer_apply|unsupported|timeout|input_changed|output_exceeded|command_failed|exit_(?:[1-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]|unknown))"
)


def _bounded_docker_image_load_failure_label(error: BackendError) -> str:
    """Map every loader failure to a fixed, non-sensitive diagnostic label."""
    detail = str(error)
    if _DOCKER_IMAGE_LOAD_SAFE_LABEL.fullmatch(detail):
        return detail
    return {
        "command timed out": "docker_image_load_timeout",
        "command stream input changed or truncated": "docker_image_load_input_changed",
        "command output exceeded bound": "docker_image_load_output_exceeded",
    }.get(detail, "docker_image_load_command_failed")


class FixedCommandRunner:
    """Run only exact, pre-registered argv vectors with bounded resources."""

    def __init__(
        self,
        *,
        allowed_argv: Iterable[tuple[str, ...]],
        timeout_seconds: float = DEFAULT_COMMAND_TIMEOUT,
        max_output: int = MAX_COMMAND_OUTPUT,
        redactions: Iterable[str] = (),
    ) -> None:
        self._allowed = frozenset(tuple(value) for value in allowed_argv)
        if not self._allowed:
            raise BackendError("command allowlist must not be empty")
        for argv in self._allowed:
            self._validate_argv(argv)
        if not isinstance(timeout_seconds, (int, float)) or timeout_seconds <= 0:
            raise BackendError("command timeout invalid")
        if not isinstance(max_output, int) or not 0 < max_output <= MAX_COMMAND_OUTPUT:
            raise BackendError("command output bound invalid")
        self._timeout = float(timeout_seconds)
        self._max_output = max_output
        self._redactions = frozenset(
            value for value in redactions if isinstance(value, str) and value
        )

    @staticmethod
    def _validate_argv(argv: tuple[str, ...]) -> None:
        if (
            not isinstance(argv, tuple)
            or not argv
            or any(not isinstance(part, str) or not part or "\x00" in part for part in argv)
        ):
            raise BackendError("command argv invalid")
        if not Path(argv[0]).is_absolute():
            raise BackendError("command executable must be absolute")

    def __call__(
        self,
        argv: tuple[str, ...],
        *,
        input_bytes: bytes | None = None,
        input_fd: int | None = None,
        input_size: int | None = None,
        timeout: float | None = None,
        max_output: int | None = None,
    ) -> bytes:
        self._validate_argv(argv)
        if argv not in self._allowed:
            raise BackendError("command argv outside exact allowlist")
        effective_timeout = self._timeout if timeout is None else timeout
        effective_bound = self._max_output if max_output is None else max_output
        if (
            not isinstance(effective_timeout, (int, float))
            or effective_timeout <= 0
            or not isinstance(effective_bound, int)
            or not 0 < effective_bound <= self._max_output
            or (input_bytes is not None and input_fd is not None)
            or (input_fd is None) != (input_size is None)
            or (
                input_bytes is not None
                and (
                    not isinstance(input_bytes, bytes)
                    or len(input_bytes) > MAX_COMMAND_INPUT
                )
            )
            or (
                input_fd is not None
                and (
                    not isinstance(input_fd, int)
                    or input_fd < 0
                    or not isinstance(input_size, int)
                    or input_size < 0
                    or input_size > MAX_COMMAND_STREAM_INPUT
                )
            )
        ):
            raise BackendError("command execution boundary invalid")
        stream_before: os.stat_result | None = None
        if input_fd is not None:
            try:
                stream_before = os.fstat(input_fd)
                position = os.lseek(input_fd, 0, os.SEEK_CUR)
            except OSError as exc:
                raise BackendError("command execution boundary invalid") from exc
            if (
                not stat.S_ISREG(stream_before.st_mode)
                or stream_before.st_size != input_size
                or position != 0
            ):
                raise BackendError("command execution boundary invalid")
        try:
            process = subprocess.Popen(
                argv,
                stdin=(
                    input_fd
                    if input_fd is not None
                    else subprocess.PIPE if input_bytes is not None else subprocess.DEVNULL
                ),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
                close_fds=True,
            )
        except OSError as exc:
            raise BackendError("command could not be executed") from exc
        if process.stdout is None or process.stderr is None:
            process.kill()
            raise BackendError("command pipes unavailable")

        output = bytearray()
        failure_stderr = bytearray()
        combined_count = 0
        guard = threading.Lock()
        oversized = threading.Event()

        def drain(stream: Any, *, target: bytearray) -> None:
            nonlocal combined_count
            try:
                while chunk := stream.read(64 * 1024):
                    with guard:
                        combined_count += len(chunk)
                        if combined_count > effective_bound:
                            oversized.set()
                    if not oversized.is_set():
                        target.extend(chunk)
                    if oversized.is_set():
                        try:
                            process.kill()
                        except OSError:
                            pass
                        return
            finally:
                stream.close()

        readers = (
            threading.Thread(target=drain, args=(process.stdout,), kwargs={"target": output}, daemon=True),
            threading.Thread(target=drain, args=(process.stderr,), kwargs={"target": failure_stderr}, daemon=True),
        )
        for reader in readers:
            reader.start()
        try:
            if input_bytes is not None:
                if process.stdin is None:
                    raise BackendError("command input pipe unavailable")
                try:
                    process.stdin.write(input_bytes)
                    process.stdin.close()
                except BrokenPipeError:
                    pass
            try:
                return_code = process.wait(timeout=float(effective_timeout))
            except subprocess.TimeoutExpired as exc:
                process.kill()
                process.wait()
                raise BackendError("command timed out") from exc
        finally:
            for reader in readers:
                reader.join()
        if input_fd is not None:
            if stream_before is None or input_size is None:
                raise BackendError("command stream input boundary invalid")
            try:
                stream_after = os.fstat(input_fd)
                stream_position = os.lseek(input_fd, 0, os.SEEK_CUR)
            except OSError as exc:
                raise BackendError("command stream input changed") from exc
            if (
                stream_position != input_size
                or (
                    stream_before.st_dev,
                    stream_before.st_ino,
                    stream_before.st_size,
                    stream_before.st_mtime_ns,
                )
                != (
                    stream_after.st_dev,
                    stream_after.st_ino,
                    stream_after.st_size,
                    stream_after.st_mtime_ns,
                )
            ):
                raise BackendError("command stream input changed or truncated")
        if oversized.is_set():
            raise BackendError("command output exceeded bound")
        if return_code != 0:
            # Deliberately omit argv/stdout/stderr. They can carry generated secrets.
            if argv == DOCKER_IMAGE_LOAD_ARGV:
                raise BackendError(
                    classify_docker_image_load_failure(
                        bytes(failure_stderr), return_code
                    )
                )
            raise BackendError("command failed")
        return bytes(output)


class SafeFs:
    """Root-relative, no-follow filesystem mutations and CAS identities."""

    def __init__(
        self,
        *,
        root: Path = Path("/"),
        expected_uid: int | None = 0,
        expected_gid: int | None = None,
    ) -> None:
        self.root = Path(root)
        self.expected_uid = expected_uid
        self.expected_gid = expected_gid
        if not self.root.is_absolute() or self.root.is_symlink() or not self.root.is_dir():
            raise BackendError("filesystem root invalid")

    @staticmethod
    def _parts(relative: str) -> tuple[str, ...]:
        if not isinstance(relative, str) or not relative or "\x00" in relative:
            raise BackendError("filesystem relative path invalid")
        path = PurePosixPath(relative.replace("\\", "/"))
        parts = path.parts
        if path.is_absolute() or not parts or any(part in {"", ".", ".."} for part in parts):
            raise BackendError("filesystem path must be safe relative path")
        return tuple(parts)

    def _path(self, relative: str, *, allow_missing_leaf: bool = True) -> Path:
        parts = self._parts(relative)
        current = self.root
        for index, part in enumerate(parts):
            current = current / part
            if not current.exists() and not current.is_symlink():
                if allow_missing_leaf and index == len(parts) - 1:
                    break
                raise BackendError("filesystem parent missing")
            if current.is_symlink():
                raise BackendError("filesystem symlink component rejected")
        return current

    def _verify_owner(self, info: os.stat_result) -> None:
        if self.expected_uid is not None and os.name != "nt" and info.st_uid != self.expected_uid:
            raise BackendError("filesystem owner mismatch")
        if self.expected_gid is not None and os.name != "nt" and info.st_gid != self.expected_gid:
            raise BackendError("filesystem group mismatch")

    def _open_directory_parts(self, parts: tuple[str, ...]) -> int:
        descriptor = os.open(
            self.root,
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_NOFOLLOW", 0),
        )
        try:
            for part in parts:
                child = os.open(
                    part,
                    os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                    | getattr(os, "O_NOFOLLOW", 0),
                    dir_fd=descriptor,
                )
                os.close(descriptor)
                descriptor = child
            return descriptor
        except Exception:
            os.close(descriptor)
            raise

    def _identity_descriptor(self, descriptor: int) -> str:
        before = os.fstat(descriptor)
        self._verify_owner(before)
        kind = (
            "dir" if stat.S_ISDIR(before.st_mode)
            else "file" if stat.S_ISREG(before.st_mode)
            else "other"
        )
        payload: dict[str, Any] = {
            "kind": kind,
            "mode": stat.S_IMODE(before.st_mode),
            "uid": before.st_uid if hasattr(before, "st_uid") else None,
            "gid": before.st_gid if hasattr(before, "st_gid") else None,
        }
        if kind == "file":
            os.lseek(descriptor, 0, os.SEEK_SET)
            digest = hashlib.sha256()
            while chunk := os.read(descriptor, 1024 * 1024):
                digest.update(chunk)
            after = os.fstat(descriptor)
            if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
                after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns
            ):
                raise BackendError("filesystem object changed during identity read")
            payload["content_sha256"] = digest.hexdigest()
        return _digest(_canonical(payload))

    def _identity_at(self, parent_descriptor: int, leaf: str) -> str | None:
        try:
            descriptor = os.open(
                leaf,
                os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
                | getattr(os, "O_BINARY", 0),
                dir_fd=parent_descriptor,
            )
        except FileNotFoundError:
            return None
        except OSError as exc:
            raise BackendError("filesystem nofollow identity open failed") from exc
        try:
            return self._identity_descriptor(descriptor)
        finally:
            os.close(descriptor)

    def mkdir(self, relative: str, mode: int) -> str:
        if not isinstance(mode, int) or mode & ~0o777:
            raise BackendError("directory mode invalid")
        parts = self._parts(relative)
        if os.name != "nt":
            descriptor = self._open_directory_parts(())
            try:
                for part in parts:
                    try:
                        child = os.open(
                            part,
                            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                            | getattr(os, "O_NOFOLLOW", 0),
                            dir_fd=descriptor,
                        )
                    except FileNotFoundError:
                        os.mkdir(part, mode, dir_fd=descriptor)
                        os.fsync(descriptor)
                        child = os.open(
                            part,
                            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                            | getattr(os, "O_NOFOLLOW", 0),
                            dir_fd=descriptor,
                        )
                        if self.expected_uid is not None or self.expected_gid is not None:
                            os.fchown(
                                child,
                                -1 if self.expected_uid is None else self.expected_uid,
                                -1 if self.expected_gid is None else self.expected_gid,
                            )
                        os.fchmod(child, mode)
                        os.fsync(child)
                    except OSError as exc:
                        raise BackendError("filesystem mkdir nofollow collision") from exc
                    os.close(descriptor)
                    descriptor = child
                info = os.fstat(descriptor)
                self._verify_owner(info)
                if not stat.S_ISDIR(info.st_mode) or stat.S_IMODE(info.st_mode) != mode:
                    raise BackendError("directory mode/type mismatch")
                identity = self._identity_descriptor(descriptor)
            finally:
                os.close(descriptor)
            return identity
        current = self.root
        for part in parts:
            candidate = current / part
            if candidate.exists() or candidate.is_symlink():
                if candidate.is_symlink() or not candidate.is_dir():
                    raise BackendError("filesystem symlink/type collision")
                current = candidate
                continue
            os.mkdir(candidate, mode=mode)
            if os.name != "nt":
                os.chmod(candidate, mode, follow_symlinks=False)
            current = candidate
        info = os.lstat(current)
        self._verify_owner(info)
        if os.name != "nt" and stat.S_IMODE(info.st_mode) != mode:
            raise BackendError("directory mode mismatch")
        return self.identity(relative) or ""

    def write_file(self, relative: str, payload: bytes, mode: int) -> str:
        if not isinstance(payload, bytes) or not isinstance(mode, int) or mode & ~0o777:
            raise BackendError("file write boundary invalid")
        parts = self._parts(relative)
        parent_relative = "/".join(parts[:-1])
        parent = self.root if not parent_relative else self._path(parent_relative, allow_missing_leaf=False)
        if parent.is_symlink() or not parent.is_dir():
            raise BackendError("filesystem symlink parent rejected")
        target = parent / parts[-1]
        if target.exists() or target.is_symlink():
            raise BackendError("file collision")
        flags = (
            os.O_WRONLY
            | os.O_CREAT
            | os.O_EXCL
            | getattr(os, "O_NOFOLLOW", 0)
            | getattr(os, "O_BINARY", 0)
        )
        parent_descriptor = -1
        try:
            if os.name != "nt":
                parent_descriptor = self._open_directory_parts(tuple(parts[:-1]))
                descriptor = os.open(parts[-1], flags, mode, dir_fd=parent_descriptor)
            else:
                descriptor = os.open(target, flags, mode)
        except OSError as exc:
            if parent_descriptor >= 0:
                os.close(parent_descriptor)
            raise BackendError("filesystem symlink-safe open failed") from exc
        try:
            if os.name != "nt":
                if self.expected_uid is not None or self.expected_gid is not None:
                    os.fchown(
                        descriptor,
                        -1 if self.expected_uid is None else self.expected_uid,
                        -1 if self.expected_gid is None else self.expected_gid,
                    )
                os.fchmod(descriptor, mode)
            offset = 0
            while offset < len(payload):
                written = os.write(descriptor, payload[offset:])
                if written <= 0:
                    raise BackendError("short file write")
                offset += written
            os.fsync(descriptor)
            info = os.fstat(descriptor)
            if not stat.S_ISREG(info.st_mode):
                raise BackendError("file type mismatch")
            self._verify_owner(info)
            if os.name != "nt" and stat.S_IMODE(info.st_mode) != mode:
                raise BackendError("file mode mismatch")
        finally:
            os.close(descriptor)
        if os.name != "nt":
            try:
                os.fsync(parent_descriptor)
            finally:
                os.close(parent_descriptor)
        identity = self.identity(relative)
        if identity is None:
            raise BackendError("file mutation not observable")
        return identity

    def identity(self, relative: str) -> str | None:
        parts = self._parts(relative)
        if os.name != "nt":
            try:
                parent_descriptor = self._open_directory_parts(tuple(parts[:-1]))
            except FileNotFoundError as exc:
                raise BackendError("filesystem parent missing") from exc
            except OSError as exc:
                raise BackendError("filesystem nofollow parent open failed") from exc
            try:
                return self._identity_at(parent_descriptor, parts[-1])
            finally:
                os.close(parent_descriptor)
        path = self._path(relative)
        if not path.exists() and not path.is_symlink():
            return None
        if path.is_symlink():
            raise BackendError("filesystem symlink component rejected")
        info = os.lstat(path)
        self._verify_owner(info)
        kind = "dir" if stat.S_ISDIR(info.st_mode) else "file" if stat.S_ISREG(info.st_mode) else "other"
        payload: dict[str, Any] = {
            "kind": kind,
            "mode": stat.S_IMODE(info.st_mode),
            "uid": info.st_uid if hasattr(info, "st_uid") else None,
            "gid": info.st_gid if hasattr(info, "st_gid") else None,
        }
        if kind == "file":
            descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
            try:
                digest = hashlib.sha256()
                while chunk := os.read(descriptor, 1024 * 1024):
                    digest.update(chunk)
                payload["content_sha256"] = digest.hexdigest()
            finally:
                os.close(descriptor)
        return _digest(_canonical(payload))

    def remove_exact(self, relative: str, expected_identity: str) -> None:
        parts = self._parts(relative)
        if os.name != "nt":
            try:
                parent_descriptor = self._open_directory_parts(tuple(parts[:-1]))
            except (FileNotFoundError, OSError) as exc:
                raise BackendError("filesystem remove parent unavailable") from exc
            try:
                actual = self._identity_at(parent_descriptor, parts[-1])
                if actual is None:
                    return
                if actual != expected_identity:
                    raise BackendError("filesystem CAS identity drift")
                info = os.stat(parts[-1], dir_fd=parent_descriptor, follow_symlinks=False)
                if stat.S_ISDIR(info.st_mode):
                    os.rmdir(parts[-1], dir_fd=parent_descriptor)
                elif stat.S_ISREG(info.st_mode):
                    os.unlink(parts[-1], dir_fd=parent_descriptor)
                else:
                    raise BackendError("filesystem object type drift")
                os.fsync(parent_descriptor)
                if self._identity_at(parent_descriptor, parts[-1]) is not None:
                    raise BackendError("filesystem removal not observable")
                return
            finally:
                os.close(parent_descriptor)
        actual = self.identity(relative)
        if actual is None:
            return
        if actual != expected_identity:
            raise BackendError("filesystem CAS identity drift")
        path = self._path(relative, allow_missing_leaf=False)
        if path.is_dir():
            os.rmdir(path)
        elif path.is_file():
            os.unlink(path)
        else:
            raise BackendError("filesystem object type drift")
        if self.identity(relative) is not None:
            raise BackendError("filesystem removal not observable")


class MutationLedger:
    SCHEMA = "amn2.spain-live-mutation-ledger.v1"
    GENESIS = "sha256:" + "0" * 64
    MAX_BYTES = 1024 * 1024

    def __init__(
        self,
        *,
        allowed_objects: set[str],
        persist: Callable[[bytes], None] | None = None,
    ) -> None:
        if not isinstance(allowed_objects, set) or not allowed_objects or any(
            not isinstance(value, str) or not value for value in allowed_objects
        ):
            raise BackendError("ledger allowlist invalid")
        if persist is not None and not callable(persist):
            raise BackendError("ledger persist callback invalid")
        self.allowed_objects = frozenset(allowed_objects)
        self._events: list[dict[str, Any]] = []
        self._persist = persist

    @staticmethod
    def _valid_identity(value: Any) -> bool:
        if not isinstance(value, str) or not value.startswith(IDENTITY_PATTERN):
            return False
        tail = value[len(IDENTITY_PATTERN) :]
        return len(tail) == 64 and all(char in "0123456789abcdef" for char in tail)

    def _states(self) -> dict[str, dict[str, Any]]:
        states: dict[str, dict[str, Any]] = {}
        for event in self._events:
            states[event["object"]] = event
        return states

    def _append(self, event: dict[str, Any]) -> None:
        previous = self._events[-1]["chain_sha256"] if self._events else self.GENESIS
        body = {"seq": len(self._events), "previous_sha256": previous, **event}
        body["chain_sha256"] = _digest(previous.encode("ascii") + _canonical(body))
        self._events.append(body)
        if self._persist is not None:
            try:
                self._persist(self.to_bytes())
            except Exception as exc:
                self._events.pop()
                raise BackendError("ledger transition could not be persisted") from exc

    def intent(self, stage: str, owned_object: str, desired_identity: str) -> None:
        if owned_object not in self.allowed_objects:
            raise BackendError("ledger object outside sealed allowlist")
        if not isinstance(stage, str) or not stage or not self._valid_identity(desired_identity):
            raise BackendError("ledger intent invalid")
        if owned_object in self._states():
            raise BackendError("duplicate ledger intent")
        self._append(
            {
                "event": "intent",
                "stage": stage,
                "object": owned_object,
                "desired_identity": desired_identity,
                "actual_identity": None,
            }
        )

    def commit(self, stage: str, owned_object: str, actual_identity: str) -> None:
        current = self._states().get(owned_object)
        if (
            current is None
            or current["event"] != "intent"
            or current["stage"] != stage
            or not self._valid_identity(actual_identity)
        ):
            raise BackendError("ledger commit requires matching intent")
        self._append(
            {
                "event": "committed",
                "stage": stage,
                "object": owned_object,
                "desired_identity": current["desired_identity"],
                "actual_identity": actual_identity,
            }
        )

    def removed(self, stage: str, owned_object: str, actual_identity: str) -> None:
        current = self._states().get(owned_object)
        if (
            current is None
            or current["event"] != "committed"
            or current["stage"] != stage
            or current["actual_identity"] != actual_identity
        ):
            raise BackendError("ledger removal requires matching committed identity")
        self._append(
            {
                "event": "removed",
                "stage": stage,
                "object": owned_object,
                "desired_identity": current["desired_identity"],
                "actual_identity": actual_identity,
            }
        )

    def abandon(self, stage: str, owned_object: str) -> None:
        current = self._states().get(owned_object)
        if (
            current is None
            or current["event"] != "intent"
            or current["stage"] != stage
        ):
            raise BackendError("ledger abandon requires matching intent")
        self._append(
            {
                "event": "abandoned",
                "stage": stage,
                "object": owned_object,
                "desired_identity": current["desired_identity"],
                "actual_identity": None,
            }
        )

    def state(self, owned_object: str) -> str | None:
        event = self._states().get(owned_object)
        return None if event is None else event["event"].replace("committed", "committed")

    def event_for(self, owned_object: str) -> dict[str, Any] | None:
        event = self._states().get(owned_object)
        return None if event is None else copy.deepcopy(event)

    def to_mapping(self) -> dict[str, Any]:
        return {
            "schema": self.SCHEMA,
            "allowed_objects_sha256": _digest(_canonical(sorted(self.allowed_objects))),
            "events": copy.deepcopy(self._events),
        }

    def to_bytes(self) -> bytes:
        payload = _canonical(self.to_mapping()) + b"\n"
        if len(payload) > self.MAX_BYTES:
            raise BackendError("ledger exceeds size bound")
        return payload

    @classmethod
    def from_bytes(
        cls,
        payload: bytes,
        *,
        allowed_objects: set[str],
        persist: Callable[[bytes], None] | None = None,
    ) -> "MutationLedger":
        if (
            not isinstance(payload, bytes)
            or not payload.endswith(b"\n")
            or len(payload) > cls.MAX_BYTES
        ):
            raise BackendError("ledger byte envelope invalid")
        try:
            value = json.loads(payload[:-1].decode("ascii"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise BackendError("ledger JSON invalid") from exc
        if _canonical(value) + b"\n" != payload:
            raise BackendError("ledger bytes are not canonical")
        return cls.from_mapping(value, allowed_objects=allowed_objects, persist=persist)

    @classmethod
    def from_mapping(
        cls,
        value: Any,
        *,
        allowed_objects: set[str],
        persist: Callable[[bytes], None] | None = None,
    ) -> "MutationLedger":
        if not isinstance(value, dict) or set(value) != {
            "schema",
            "allowed_objects_sha256",
            "events",
        }:
            raise BackendError("ledger schema mismatch")
        # Replay must not emit intermediate snapshots. Attach the durable sink
        # only after the complete chain is validated.
        ledger = cls(allowed_objects=allowed_objects)
        if (
            value["schema"] != cls.SCHEMA
            or value["allowed_objects_sha256"]
            != _digest(_canonical(sorted(ledger.allowed_objects)))
            or not isinstance(value["events"], list)
        ):
            raise BackendError("ledger schema/allowlist mismatch")
        expected_keys = {
            "seq",
            "previous_sha256",
            "event",
            "stage",
            "object",
            "desired_identity",
            "actual_identity",
            "chain_sha256",
        }
        for raw in value["events"]:
            if not isinstance(raw, dict) or set(raw) != expected_keys:
                raise BackendError("ledger event schema mismatch")
            supplied_chain = raw["chain_sha256"]
            body = {key: raw[key] for key in raw if key != "chain_sha256"}
            previous = ledger._events[-1]["chain_sha256"] if ledger._events else cls.GENESIS
            if (
                raw["seq"] != len(ledger._events)
                or raw["previous_sha256"] != previous
                or supplied_chain != _digest(previous.encode("ascii") + _canonical(body))
            ):
                raise BackendError("ledger hash chain mismatch")
            event = raw["event"]
            if event == "intent":
                if raw["actual_identity"] is not None:
                    raise BackendError("ledger intent event malformed")
                ledger.intent(raw["stage"], raw["object"], raw["desired_identity"])
            elif event == "committed":
                ledger.commit(raw["stage"], raw["object"], raw["actual_identity"])
            elif event == "removed":
                ledger.removed(raw["stage"], raw["object"], raw["actual_identity"])
            elif event == "abandoned":
                if raw["actual_identity"] is not None:
                    raise BackendError("ledger abandoned event malformed")
                ledger.abandon(raw["stage"], raw["object"])
            else:
                raise BackendError("ledger event type invalid")
            if ledger._events[-1] != raw:
                raise BackendError("ledger event canonical mismatch")
        if persist is not None and not callable(persist):
            raise BackendError("ledger persist callback invalid")
        ledger._persist = persist
        return ledger


class DurableMutationLedgerStore:
    """Atomic root-private storage for the outer hash-chained mutation ledger."""

    def __init__(self, path: Path, *, expected_uid: int | None = 0) -> None:
        self.path = Path(path)
        self.expected_uid = expected_uid
        if (
            not self.path.is_absolute()
            or self.path.parent.is_symlink()
            or not self.path.parent.is_dir()
            or self.path.is_symlink()
        ):
            raise BackendError("durable ledger path invalid")

    def _read(self) -> bytes | None:
        if not self.path.exists() and not self.path.is_symlink():
            return None
        if self.path.is_symlink():
            raise BackendError("durable ledger symlink rejected")
        try:
            descriptor = os.open(
                self.path,
                os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
                | getattr(os, "O_BINARY", 0),
            )
        except OSError as exc:
            raise BackendError("durable ledger cannot be opened") from exc
        try:
            info = os.fstat(descriptor)
            if (
                not stat.S_ISREG(info.st_mode)
                or info.st_size <= 0
                or info.st_size > MutationLedger.MAX_BYTES
                or (
                    os.name != "nt"
                    and (
                        stat.S_IMODE(info.st_mode) != 0o600
                        or (
                            self.expected_uid is not None
                            and info.st_uid != self.expected_uid
                        )
                    )
                )
            ):
                raise BackendError("durable ledger owner/mode/type mismatch")
            chunks: list[bytes] = []
            remaining = MutationLedger.MAX_BYTES + 1
            while remaining and (
                chunk := os.read(descriptor, min(64 * 1024, remaining))
            ):
                chunks.append(chunk)
                remaining -= len(chunk)
            payload = b"".join(chunks)
            after = os.fstat(descriptor)
            if (
                len(payload) > MutationLedger.MAX_BYTES
                or (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns)
                != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
            ):
                raise BackendError("durable ledger changed during read")
            return payload
        finally:
            os.close(descriptor)

    def persist(self, payload: bytes) -> None:
        if (
            not isinstance(payload, bytes)
            or not payload
            or len(payload) > MutationLedger.MAX_BYTES
            or self.path.parent.is_symlink()
            or self.path.is_symlink()
        ):
            raise BackendError("durable ledger write boundary invalid")
        descriptor = -1
        temporary: Path | None = None
        try:
            descriptor, raw_name = tempfile.mkstemp(
                prefix=".amn2-mutation-ledger-", dir=self.path.parent
            )
            temporary = Path(raw_name)
            if os.name != "nt":
                os.fchmod(descriptor, 0o600)
            offset = 0
            while offset < len(payload):
                written = os.write(descriptor, payload[offset:])
                if written <= 0:
                    raise BackendError("durable ledger short write")
                offset += written
            os.fsync(descriptor)
            os.close(descriptor)
            descriptor = -1
            os.replace(temporary, self.path)
            temporary = None
            if os.name != "nt":
                parent_descriptor = os.open(
                    self.path.parent,
                    os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                    | getattr(os, "O_NOFOLLOW", 0),
                )
                try:
                    os.fsync(parent_descriptor)
                finally:
                    os.close(parent_descriptor)
        except (OSError, BackendError) as exc:
            raise BackendError("durable ledger atomic write failed") from exc
        finally:
            if descriptor >= 0:
                os.close(descriptor)
            if temporary is not None:
                try:
                    os.unlink(temporary)
                except OSError:
                    pass

    def load_or_create(self, allowed_objects: set[str]) -> MutationLedger:
        payload = self._read()
        if payload is None:
            return MutationLedger(
                allowed_objects=allowed_objects, persist=self.persist
            )
        return MutationLedger.from_bytes(
            payload,
            allowed_objects=allowed_objects,
            persist=self.persist,
        )


@dataclass(frozen=True)
class OwnedOperation:
    stage: str
    owned_object: str
    desired_identity: str

    def __post_init__(self) -> None:
        if (
            not isinstance(self.stage, str)
            or not self.stage
            or not isinstance(self.owned_object, str)
            or not self.owned_object
            or not MutationLedger._valid_identity(self.desired_identity)
        ):
            raise BackendError("owned operation invalid")


class OwnedAdapter(Protocol):
    def observe(self, operation: OwnedOperation) -> str | None: ...

    def create(self, operation: OwnedOperation) -> None: ...

    def remove(self, operation: OwnedOperation, identity: str) -> None: ...


@dataclass(frozen=True)
class SystemAction:
    """One sealed, identity-bearing system mutation.

    The action object deliberately contains no dynamic argv construction.  A
    concrete action may close over a FixedCommandRunner or SafeFs instance, but
    the operation presented by LinuxBackend must compare exactly with the
    registered operation before any observer or mutator is invoked.
    """

    operation: OwnedOperation
    observe_identity: Callable[[], str | None] = field(repr=False)
    create_exact: Callable[[], None] = field(repr=False)
    remove_exact: Callable[[str], None] = field(repr=False)
    observe_pending_identity: Callable[[], str | None] | None = field(
        default=None, repr=False
    )
    observe_rollback_identity: Callable[[], str | None] | None = field(
        default=None, repr=False
    )
    reconcile_absent_removal: bool = False

    def __post_init__(self) -> None:
        if not all(
            callable(value)
            for value in (self.observe_identity, self.create_exact, self.remove_exact)
        ):
            raise BackendError("system action callback invalid")
        if self.observe_pending_identity is not None and not callable(
            self.observe_pending_identity
        ):
            raise BackendError("system pending observer invalid")
        if self.observe_rollback_identity is not None and not callable(
            self.observe_rollback_identity
        ):
            raise BackendError("system rollback observer invalid")
        if type(self.reconcile_absent_removal) is not bool:
            raise BackendError("system absent-removal policy invalid")


class SystemOwnedAdapter:
    """Dispatch only operations from an immutable, exact action registry."""

    def __init__(self, *, actions: Mapping[str, SystemAction]) -> None:
        if not isinstance(actions, Mapping) or not actions:
            raise BackendError("system action registry invalid")
        sealed: dict[str, SystemAction] = {}
        for owned_object, action in actions.items():
            if (
                not isinstance(owned_object, str)
                or not isinstance(action, SystemAction)
                or owned_object != action.operation.owned_object
                or owned_object in sealed
            ):
                raise BackendError("system action registry mismatch")
            sealed[owned_object] = action
        self._actions = MappingProxyType(sealed)

    def _action(self, operation: OwnedOperation) -> SystemAction:
        if not isinstance(operation, OwnedOperation):
            raise BackendError("system operation type invalid")
        action = self._actions.get(operation.owned_object)
        if action is None:
            raise BackendError("system operation outside sealed action registry")
        if action.operation != operation:
            raise BackendError("system operation disagrees with sealed action registry")
        return action

    def observe(self, operation: OwnedOperation) -> str | None:
        return self._action(operation).observe_identity()

    def create(self, operation: OwnedOperation) -> None:
        self._action(operation).create_exact()

    def observe_pending(self, operation: OwnedOperation) -> str | None:
        action = self._action(operation)
        observer = action.observe_pending_identity or action.observe_identity
        return observer()

    def observe_rollback(self, operation: OwnedOperation) -> str | None:
        action = self._action(operation)
        observer = action.observe_rollback_identity or action.observe_identity
        return observer()

    def remove(self, operation: OwnedOperation, identity: str) -> None:
        if not MutationLedger._valid_identity(identity):
            raise BackendError("system removal identity invalid")
        self._action(operation).remove_exact(identity)

    def reconcile_absent_remove(
        self, operation: OwnedOperation, identity: str
    ) -> None:
        action = self._action(operation)
        if action.reconcile_absent_removal:
            action.remove_exact(identity)


def _new_fs_identity(fs: SafeFs, relative: str, *, kind: str, mode: int,
                     payload: bytes | None = None) -> str:
    parts = fs._parts(relative)
    parent_relative = "/".join(parts[:-1])
    parent = fs.root
    if parent_relative:
        for part in parts[:-1]:
            candidate = parent / part
            if candidate.exists() or candidate.is_symlink():
                if candidate.is_symlink() or not candidate.is_dir():
                    raise BackendError("filesystem action parent invalid")
                parent = candidate
            else:
                break
    if parent.is_symlink() or not parent.is_dir():
        raise BackendError("filesystem action parent invalid")
    info = os.lstat(parent)
    identity: dict[str, Any] = {
        "kind": kind,
        "mode": mode if os.name != "nt" else (0o777 if kind == "dir" else 0o666),
        "uid": (
            fs.expected_uid
            if os.name != "nt" and fs.expected_uid is not None
            else info.st_uid if hasattr(info, "st_uid") else None
        ),
        "gid": (
            fs.expected_gid
            if os.name != "nt" and fs.expected_gid is not None
            else info.st_gid if hasattr(info, "st_gid") else None
        ),
    }
    if payload is not None:
        identity["content_sha256"] = hashlib.sha256(payload).hexdigest()
    return _digest(_canonical(identity))


def build_directory_action(
    fs: SafeFs, stage: str, relative: str, mode: int
) -> SystemAction:
    # Resolve the parent before constructing an intent.  This prevents mkdir()
    # from implicitly creating unledgered ancestor directories.
    desired = _new_fs_identity(fs, relative, kind="dir", mode=mode)
    operation = OwnedOperation(
        stage=stage, owned_object="dir:/" + relative, desired_identity=desired
    )

    def create() -> None:
        parts = fs._parts(relative)
        parent_relative = "/".join(parts[:-1])
        if parent_relative:
            fs._path(parent_relative, allow_missing_leaf=False)
        if fs.mkdir(relative, mode) != desired:
            raise BackendError("directory creation identity mismatch")

    return SystemAction(
        operation=operation,
        observe_identity=lambda: fs.identity(relative),
        create_exact=create,
        remove_exact=lambda identity: fs.remove_exact(relative, identity),
    )


def build_file_action(
    fs: SafeFs,
    stage: str,
    relative: str,
    payload: bytes,
    mode: int,
    *,
    owned_kind: str = "file",
) -> SystemAction:
    if not isinstance(payload, bytes) or owned_kind not in {"file", "secret"}:
        raise BackendError("file action payload invalid")
    desired = _new_fs_identity(fs, relative, kind="file", mode=mode, payload=payload)
    operation = OwnedOperation(
        stage=stage, owned_object=owned_kind + ":/" + relative, desired_identity=desired
    )

    def create() -> None:
        if fs.write_file(relative, payload, mode) != desired:
            raise BackendError("file creation identity mismatch")

    return SystemAction(
        operation=operation,
        observe_identity=lambda: fs.identity(relative),
        create_exact=create,
        remove_exact=lambda identity: fs.remove_exact(relative, identity),
    )


def _validated_tree_plan(value: Any) -> dict[str, Any]:
    from scripts import phase12_spain_package as package

    if (
        not isinstance(value, dict)
        or set(value) != {"schema", "rows", "tree_sha256"}
        or value.get("schema") != "amn2.spain-expanded-tree-plan.v1"
        or not isinstance(value.get("rows"), list)
        or not value["rows"]
        or not isinstance(value.get("tree_sha256"), str)
        or len(value["tree_sha256"]) != 64
    ):
        raise BackendError("canonical tree plan schema invalid")
    names: set[str] = set()
    for row in value["rows"]:
        if (
            not isinstance(row, dict)
            or set(row)
            != (
                {"path", "type", "mode", "sha256", "size"}
                if row.get("type") == "file"
                else {"path", "type", "mode", "sha256"}
            )
            or not isinstance(row["path"], str)
            or not row["path"]
            or PurePosixPath(row["path"]).is_absolute()
            or any(part in {"", ".", ".."} for part in PurePosixPath(row["path"]).parts)
            or row["path"] in names
            or row["type"] not in {"dir", "file"}
            or row["mode"] != ("0755" if row["type"] == "dir" else "0644")
            or (
                row["sha256"] is not None
                and (
                    not isinstance(row["sha256"], str)
                    or len(row["sha256"]) != 64
                    or any(char not in "0123456789abcdef" for char in row["sha256"])
                )
            )
            or (row["type"] == "dir" and row["sha256"] is not None)
            or (row["type"] == "file" and row["sha256"] is None)
            or (
                row["type"] == "file"
                and (
                    not isinstance(row["size"], int)
                    or isinstance(row["size"], bool)
                    or row["size"] < 0
                    or row["size"] > package.MAX_TOTAL_UNPACKED_BYTES
                )
            )
        ):
            raise BackendError("canonical tree plan row invalid")
        names.add(row["path"])
    if package.sha256_canonical(value["rows"]) != value["tree_sha256"]:
        raise BackendError("canonical tree plan hash mismatch")
    return copy.deepcopy(value)


def _tree_parent_fd(target: Path) -> int:
    if not target.is_absolute() or not target.anchor:
        raise BackendError("owned tree target must be absolute")
    anchor = Path(target.anchor)
    descriptor = os.open(
        anchor,
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        anchor_parts = anchor.parts
        parent_parts = target.parent.parts[len(anchor_parts) :]
        for part in parent_parts:
            child = os.open(
                part,
                os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=descriptor,
            )
            os.close(descriptor)
            descriptor = child
        return descriptor
    except Exception:
        os.close(descriptor)
        raise


def _open_tree_directory(root_fd: int, parts: tuple[str, ...]) -> int:
    descriptor = os.dup(root_fd)
    try:
        for part in parts:
            child = os.open(
                part,
                os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=descriptor,
            )
            os.close(descriptor)
            descriptor = child
        return descriptor
    except Exception:
        os.close(descriptor)
        raise


def _scan_tree(target: Path) -> dict[str, Any] | None:
    from scripts import phase12_spain_package as package

    rows: list[dict[str, Any]] = []
    if os.name == "nt":
        if not target.exists() and not target.is_symlink():
            return None
        if target.is_symlink() or not target.is_dir():
            raise BackendError("owned tree type/symlink collision")
        for current, directories, files in os.walk(target, followlinks=False):
            base = Path(current)
            for name in sorted(directories):
                path = base / name
                if path.is_symlink():
                    raise BackendError("owned tree symlink collision")
                relative = path.relative_to(target).as_posix()
                rows.append({"path": relative, "type": "dir", "mode": "0755", "sha256": None})
            for name in sorted(files):
                path = base / name
                if path.is_symlink() or not path.is_file():
                    raise BackendError("owned tree special file collision")
                info = os.lstat(path)
                relative = path.relative_to(target).as_posix()
                rows.append({
                    "path": relative, "type": "file", "mode": "0644",
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "size": info.st_size,
                })
    else:
        try:
            parent_fd = _tree_parent_fd(target)
        except OSError as exc:
            raise BackendError("owned tree ancestor nofollow open failed") from exc
        try:
            try:
                root_fd = os.open(
                    target.name,
                    os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                    | getattr(os, "O_NOFOLLOW", 0),
                    dir_fd=parent_fd,
                )
            except FileNotFoundError:
                return None
            except OSError as exc:
                raise BackendError("owned tree type/symlink collision") from exc
        finally:
            os.close(parent_fd)

        def visit(descriptor: int, prefix: PurePosixPath) -> None:
            for name in sorted(os.listdir(descriptor)):
                info = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
                relative = (prefix / name).as_posix()
                if stat.S_ISDIR(info.st_mode):
                    rows.append({
                        "path": relative, "type": "dir",
                        "mode": f"{stat.S_IMODE(info.st_mode):04o}", "sha256": None,
                    })
                    child = os.open(
                        name,
                        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                        | getattr(os, "O_NOFOLLOW", 0),
                        dir_fd=descriptor,
                    )
                    try:
                        visit(child, prefix / name)
                    finally:
                        os.close(child)
                elif stat.S_ISREG(info.st_mode):
                    file_fd = os.open(
                        name,
                        os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
                        dir_fd=descriptor,
                    )
                    try:
                        before = os.fstat(file_fd)
                        digest = hashlib.sha256()
                        while chunk := os.read(file_fd, 1024 * 1024):
                            digest.update(chunk)
                        after = os.fstat(file_fd)
                        if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
                            after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns
                        ):
                            raise BackendError("owned tree file changed during observation")
                    finally:
                        os.close(file_fd)
                    rows.append({
                        "path": relative, "type": "file",
                        "mode": f"{stat.S_IMODE(info.st_mode):04o}",
                        "sha256": digest.hexdigest(),
                        "size": after.st_size,
                    })
                else:
                    raise BackendError("owned tree special file collision")

        try:
            visit(root_fd, PurePosixPath())
        finally:
            os.close(root_fd)
    if not rows:
        raise BackendError("owned tree is unexpectedly empty")
    return package._canonical_tree_plan(rows)


def _tree_root_mode(target: Path) -> str | None:
    if os.name == "nt":
        if not target.exists() and not target.is_symlink():
            return None
        if target.is_symlink() or not target.is_dir():
            raise BackendError("owned tree root type collision")
        return "0755"
    try:
        parent_fd = _tree_parent_fd(target)
        try:
            descriptor = os.open(
                target.name,
                os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=parent_fd,
            )
        except FileNotFoundError:
            return None
        finally:
            os.close(parent_fd)
    except OSError as exc:
        raise BackendError("owned tree root nofollow observation failed") from exc
    try:
        return f"{stat.S_IMODE(os.fstat(descriptor).st_mode):04o}"
    finally:
        os.close(descriptor)


def inspect_terminal_owned_tree(target: Path) -> dict[str, object]:
    """Return a bounded no-follow inventory for one dedicated AMN2 tree."""
    from scripts import phase12_spain_package as package

    target = Path(target)
    if not target.is_absolute():
        raise BackendError("terminal owned tree path invalid")
    if os.name == "nt":
        tree = _scan_tree(target)
        if tree is None:
            raise BackendError("terminal owned tree unavailable")
        rows = tree["rows"]
        total_bytes = sum(
            row.get("size", 0) for row in rows if row.get("type") == "file"
        )
        return {
            "tree_sha256": tree["tree_sha256"],
            "entry_count": len(rows),
            "total_bytes": total_bytes,
            "root_mode": _tree_root_mode(target),
        }
    try:
        parent_fd = _tree_parent_fd(target)
        root_fd = os.open(
            target.name,
            os.O_RDONLY
            | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=parent_fd,
        )
    except OSError as exc:
        raise BackendError("terminal owned tree unavailable") from exc
    finally:
        if "parent_fd" in locals():
            os.close(parent_fd)
    root_info = os.fstat(root_fd)
    root_device = root_info.st_dev
    rows: list[dict[str, object]] = []
    total_bytes = 0

    def visit(descriptor: int, prefix: PurePosixPath) -> None:
        nonlocal total_bytes
        for name in sorted(os.listdir(descriptor)):
            info = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
            if info.st_dev != root_device:
                raise BackendError("terminal owned tree mount collision")
            relative = (prefix / name).as_posix()
            if stat.S_ISDIR(info.st_mode):
                rows.append(
                    {
                        "path": relative,
                        "type": "dir",
                        "mode": f"{stat.S_IMODE(info.st_mode):04o}",
                        "sha256": None,
                    }
                )
                child = os.open(
                    name,
                    os.O_RDONLY
                    | getattr(os, "O_DIRECTORY", 0)
                    | getattr(os, "O_NOFOLLOW", 0),
                    dir_fd=descriptor,
                )
                try:
                    visit(child, prefix / name)
                finally:
                    os.close(child)
            elif stat.S_ISREG(info.st_mode):
                child = os.open(
                    name,
                    os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
                    dir_fd=descriptor,
                )
                try:
                    before = os.fstat(child)
                    digest = hashlib.sha256()
                    while chunk := os.read(child, 1024 * 1024):
                        digest.update(chunk)
                    after = os.fstat(child)
                finally:
                    os.close(child)
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
                    raise BackendError("terminal owned tree changed during observation")
                rows.append(
                    {
                        "path": relative,
                        "type": "file",
                        "mode": f"{stat.S_IMODE(info.st_mode):04o}",
                        "sha256": digest.hexdigest(),
                        "size": after.st_size,
                    }
                )
                total_bytes += after.st_size
            else:
                raise BackendError("terminal owned tree special file collision")

    try:
        visit(root_fd, PurePosixPath())
    finally:
        os.close(root_fd)
    if not rows or len(rows) > 50_000 or total_bytes > 2 * 1024 * 1024 * 1024:
        raise BackendError("terminal owned tree inventory bound invalid")
    return {
        "tree_sha256": package.sha256_canonical(rows),
        "entry_count": len(rows),
        "total_bytes": total_bytes,
        "root_mode": f"{stat.S_IMODE(root_info.st_mode):04o}",
    }


def cleanup_terminal_owned_tree(
    target: Path,
    *,
    expected_tree_sha256: str,
    expected_entry_count: int,
    expected_total_bytes: int,
    expected_root_mode: str,
) -> dict[str, object]:
    """Remove one audit-bound regular-file/directory tree without following links."""
    target = Path(target)
    expected = {
        "tree_sha256": expected_tree_sha256,
        "entry_count": expected_entry_count,
        "total_bytes": expected_total_bytes,
        "root_mode": expected_root_mode,
    }
    if (
        not target.is_absolute()
        or re.fullmatch(r"[0-9a-f]{64}", expected_tree_sha256) is None
        or not isinstance(expected_entry_count, int)
        or isinstance(expected_entry_count, bool)
        or not 0 < expected_entry_count <= 50_000
        or not isinstance(expected_total_bytes, int)
        or isinstance(expected_total_bytes, bool)
        or not 0 <= expected_total_bytes <= 2 * 1024 * 1024 * 1024
        or expected_root_mode not in {"0750", "0755"}
    ):
        raise BackendError("terminal owned tree cleanup input invalid")
    first = inspect_terminal_owned_tree(target)
    second = inspect_terminal_owned_tree(target)
    if first != expected or second != expected:
        raise BackendError("terminal owned tree inventory drift")
    _remove_owned_tree(target)
    if target.exists() or target.is_symlink():
        raise BackendError("terminal owned tree removal not observable")
    return first


def _remove_owned_tree(target: Path) -> None:
    if os.name == "nt":
        for current, directories, files in os.walk(target, topdown=False, followlinks=False):
            base = Path(current)
            for name in files:
                path = base / name
                if path.is_symlink() or not path.is_file():
                    raise BackendError("owned tree special file collision")
                path.unlink()
            for name in directories:
                path = base / name
                if path.is_symlink() or not path.is_dir():
                    raise BackendError("owned tree symlink collision")
                path.rmdir()
        target.rmdir()
        return
    parent_fd = _tree_parent_fd(target)
    try:
        root_fd = os.open(
            target.name,
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=parent_fd,
        )
        root_device = os.fstat(root_fd).st_dev

        def remove_children(descriptor: int) -> None:
            for name in sorted(os.listdir(descriptor)):
                info = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
                if info.st_dev != root_device:
                    raise BackendError("owned tree mount collision")
                if stat.S_ISDIR(info.st_mode):
                    child = os.open(
                        name,
                        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                        | getattr(os, "O_NOFOLLOW", 0),
                        dir_fd=descriptor,
                    )
                    try:
                        remove_children(child)
                    finally:
                        os.close(child)
                    os.rmdir(name, dir_fd=descriptor)
                elif stat.S_ISREG(info.st_mode):
                    os.unlink(name, dir_fd=descriptor)
                else:
                    raise BackendError("owned tree special file collision")
            os.fsync(descriptor)

        try:
            remove_children(root_fd)
        finally:
            os.close(root_fd)
        os.rmdir(target.name, dir_fd=parent_fd)
        os.fsync(parent_fd)
    finally:
        os.close(parent_fd)


def _terminal_docker_data_root_entry_kind(mode: int, rdev: int) -> str:
    if stat.S_ISDIR(mode):
        return "dir"
    if stat.S_ISREG(mode):
        return "file"
    if stat.S_ISLNK(mode):
        return "symlink"
    if stat.S_ISBLK(mode):
        return "whiteout" if rdev == 0 else "block"
    raise BackendError("terminal Docker data-root special file collision")


def _validate_terminal_docker_data_root_entry(
    info: os.stat_result, *, root_device: int
) -> str:
    """Accept only one-filesystem Docker-tree entries safe for no-follow unlink."""
    if info.st_dev != root_device:
        raise BackendError("terminal Docker data-root mount collision")
    kind = _terminal_docker_data_root_entry_kind(info.st_mode, info.st_rdev)
    if kind == "block" and (
        info.st_rdev != root_device
        or stat.S_IMODE(info.st_mode) != 0o600
        or info.st_uid != 0
        or info.st_gid != 0
        or info.st_nlink != 1
    ):
        raise BackendError("terminal Docker data-root block device collision")
    return kind


def _terminal_docker_tree_digest(rows: list[dict[str, object]]) -> str:
    """Return the canonical Docker-tree digest in the intent's raw-hex form."""
    return hashlib.sha256(_canonical(rows)).hexdigest()


def _scan_terminal_docker_data_root(target: Path) -> dict[str, object]:
    """Hash the dedicated Docker root without following links or whiteouts."""
    target = Path(target)
    if not target.is_absolute():
        raise BackendError("terminal Docker data-root path invalid")
    if os.name == "nt":
        tree = _scan_tree(target)
        if tree is None:
            raise BackendError("terminal Docker data-root unavailable")
        rows = tree["rows"]
        return {
            "tree_sha256": tree["tree_sha256"],
            "entry_count": len(rows),
            "total_bytes": sum(
                row.get("size", 0)
                for row in rows
                if row.get("type") == "file"
            ),
        }
    try:
        parent_fd = _tree_parent_fd(target)
        root_fd = os.open(
            target.name,
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=parent_fd,
        )
    except OSError as exc:
        raise BackendError("terminal Docker data-root unavailable") from exc
    finally:
        if "parent_fd" in locals():
            os.close(parent_fd)
    root_device = os.fstat(root_fd).st_dev
    rows: list[dict[str, object]] = []
    total_bytes = 0

    def visit(descriptor: int, prefix: PurePosixPath) -> None:
        nonlocal total_bytes
        for name in sorted(os.listdir(descriptor)):
            info = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
            kind = _validate_terminal_docker_data_root_entry(
                info, root_device=root_device
            )
            row: dict[str, object] = {
                "path": (prefix / name).as_posix(),
                "type": kind,
                "mode": f"{stat.S_IMODE(info.st_mode):04o}",
                "uid": info.st_uid,
                "gid": info.st_gid,
            }
            if kind == "dir":
                child = os.open(name, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0), dir_fd=descriptor)
                try:
                    visit(child, prefix / name)
                finally:
                    os.close(child)
            elif kind == "file":
                child = os.open(name, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0), dir_fd=descriptor)
                try:
                    before = os.fstat(child); digest = hashlib.sha256(); size = 0
                    while chunk := os.read(child, 1024 * 1024):
                        digest.update(chunk); size += len(chunk)
                    after = os.fstat(child)
                finally:
                    os.close(child)
                if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns):
                    raise BackendError("terminal Docker data-root changed during scan")
                row.update({"sha256": digest.hexdigest(), "size": size}); total_bytes += size
            elif kind == "symlink":
                value = os.readlink(name, dir_fd=descriptor)
                row.update({"target_sha256": hashlib.sha256(value.encode("utf-8")).hexdigest(), "target_size": len(value.encode("utf-8"))})
            elif kind == "block":
                row.update({"rdev": info.st_rdev, "nlink": info.st_nlink})
            else:
                row["rdev"] = info.st_rdev
            rows.append(row)

    try:
        visit(root_fd, PurePosixPath())
    finally:
        os.close(root_fd)
    if not rows or len(rows) > 10_000 or total_bytes > 2 * 1024 * 1024 * 1024:
        raise BackendError("terminal Docker data-root inventory bound invalid")
    return {
        "tree_sha256": _terminal_docker_tree_digest(rows),
        "entry_count": len(rows),
        "total_bytes": total_bytes,
    }


def _remove_terminal_docker_data_root_tree(target: Path) -> None:
    if os.name == "nt":
        _remove_owned_tree(target)
        return
    parent_fd = _tree_parent_fd(target)
    try:
        root_fd = os.open(target.name, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0), dir_fd=parent_fd)
        root_device = os.fstat(root_fd).st_dev
        def remove_children(descriptor: int) -> None:
            for name in sorted(os.listdir(descriptor)):
                info = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
                kind = _validate_terminal_docker_data_root_entry(
                    info, root_device=root_device
                )
                if kind == "dir":
                    child = os.open(name, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0), dir_fd=descriptor)
                    try: remove_children(child)
                    finally: os.close(child)
                    os.rmdir(name, dir_fd=descriptor)
                else:
                    os.unlink(name, dir_fd=descriptor)
            os.fsync(descriptor)
        try: remove_children(root_fd)
        finally: os.close(root_fd)
        os.rmdir(target.name, dir_fd=parent_fd); os.fsync(parent_fd)
    finally:
        os.close(parent_fd)


def cleanup_terminal_docker_data_root(
    *,
    fs: SafeFs,
    relative: str,
    expected_identity: str,
    expected_tree_sha256: str,
    expected_tree_entry_count: int,
    expected_tree_total_bytes: int,
) -> dict[str, object]:
    """Remove a terminal Docker data-root after a daemon-only mode drift.

    The normal directory action intentionally uses ``rmdir`` and therefore
    stops if an abandoned ``docker load`` leaves layer data behind.  This
    recovery primitive is narrower: it accepts only the recorded AMN2
    data-root, root-owned modes 0700/0710, an exactly approved no-follow tree
    inventory, and regular files/directories plus one tightly validated block
    inode below that root.
    """
    if (
        not isinstance(fs, SafeFs)
        or relative != "var/lib/amn2-spain-docker"
        or not isinstance(expected_identity, str)
        or re.fullmatch(r"sha256:[0-9a-f]{64}", expected_identity) is None
        or not isinstance(expected_tree_sha256, str)
        or re.fullmatch(r"[0-9a-f]{64}", expected_tree_sha256) is None
        or not isinstance(expected_tree_entry_count, int)
        or isinstance(expected_tree_entry_count, bool)
        or not 0 < expected_tree_entry_count <= 10_000
        or not isinstance(expected_tree_total_bytes, int)
        or isinstance(expected_tree_total_bytes, bool)
        or not 0 < expected_tree_total_bytes <= 2 * 1024 * 1024 * 1024
    ):
        raise BackendError("terminal Docker data-root cleanup input invalid")
    expected_operation = build_directory_action(
        fs, "filesystem_staged", relative, 0o700
    ).operation
    if expected_operation.desired_identity != expected_identity:
        raise BackendError("terminal Docker data-root ledger binding mismatch")
    actual_identity = fs.identity(relative)
    if actual_identity is None:
        raise BackendError("terminal Docker data-root absent")
    target = fs.root.joinpath(*fs._parts(relative))

    def inspect() -> dict[str, object]:
        root_mode = _tree_root_mode(target)
        if root_mode not in {"0700", "0710"}:
            raise BackendError("terminal Docker data-root mode drift")
        tree = _scan_terminal_docker_data_root(target)
        receipt = {
            "tree_sha256": tree.get("tree_sha256"),
            "entry_count": tree.get("entry_count"),
            "total_bytes": tree.get("total_bytes"),
            "root_mode": root_mode,
        }
        if (
            receipt["tree_sha256"] != expected_tree_sha256
            or receipt["entry_count"] != expected_tree_entry_count
            or receipt["total_bytes"] != expected_tree_total_bytes
        ):
            raise BackendError("terminal Docker data-root tree drift")
        return receipt

    receipt = inspect()
    if inspect() != receipt:
        raise BackendError("terminal Docker data-root changed during verification")
    _remove_terminal_docker_data_root_tree(target)
    if fs.identity(relative) is not None:
        raise BackendError("terminal Docker data-root removal not observable")
    return receipt


def _materialize_tree(target: Path, plan: dict[str, Any], payloads: Mapping[str, bytes]) -> None:
    expected_files = {
        row["path"] for row in plan["rows"] if row["type"] == "file"
    }
    if set(payloads) != expected_files:
        raise BackendError("owned tree materialization boundary invalid")
    for name, payload in payloads.items():
        row = next(item for item in plan["rows"] if item["path"] == name)
        if not isinstance(payload, bytes) or hashlib.sha256(payload).hexdigest() != row["sha256"]:
            raise BackendError("owned tree payload hash mismatch")
    if os.name == "nt":
        if target.exists() or target.is_symlink():
            raise BackendError("owned tree materialization boundary invalid")
        target.mkdir(mode=0o755)
        for row in sorted(plan["rows"], key=lambda item: (item["path"].count("/"), item["path"])):
            destination = target.joinpath(*PurePosixPath(row["path"]).parts)
            if row["type"] == "dir":
                destination.mkdir(exist_ok=True, mode=0o755)
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(payloads[row["path"]])
        return
    parent_fd = _tree_parent_fd(target)
    try:
        try:
            os.stat(target.name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            raise BackendError("owned tree materialization boundary invalid")
        os.mkdir(target.name, 0o755, dir_fd=parent_fd)
        root_fd = os.open(
            target.name,
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=parent_fd,
        )
        try:
            os.fchmod(root_fd, 0o755)
            for row in sorted(plan["rows"], key=lambda item: (item["path"].count("/"), item["path"])):
                parts = PurePosixPath(row["path"]).parts
                parent = _open_tree_directory(root_fd, tuple(parts[:-1]))
                try:
                    if row["type"] == "dir":
                        try:
                            os.mkdir(parts[-1], 0o755, dir_fd=parent)
                        except FileExistsError:
                            pass
                        child = os.open(
                            parts[-1],
                            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                            | getattr(os, "O_NOFOLLOW", 0),
                            dir_fd=parent,
                        )
                        try:
                            os.fchmod(child, 0o755)
                            os.fsync(child)
                        finally:
                            os.close(child)
                    else:
                        descriptor = os.open(
                            parts[-1],
                            os.O_WRONLY | os.O_CREAT | os.O_EXCL
                            | getattr(os, "O_NOFOLLOW", 0),
                            0o644,
                            dir_fd=parent,
                        )
                        try:
                            payload = payloads[row["path"]]
                            offset = 0
                            while offset < len(payload):
                                written = os.write(descriptor, payload[offset:])
                                if written <= 0:
                                    raise BackendError("owned tree short write")
                                offset += written
                            os.fchmod(descriptor, 0o644)
                            os.fsync(descriptor)
                        finally:
                            os.close(descriptor)
                    os.fsync(parent)
                finally:
                    os.close(parent)
            os.fsync(root_fd)
        finally:
            os.close(root_fd)
        os.fsync(parent_fd)
    finally:
        os.close(parent_fd)


def _build_tree_action(
    *,
    target: Path,
    stage: str,
    plan: dict[str, Any],
    payloads: Mapping[str, bytes],
) -> SystemAction:
    target = Path(target)
    plan = _validated_tree_plan(plan)
    if not target.is_absolute():
        raise BackendError("owned tree target boundary invalid")
    if os.name != "nt":
        try:
            descriptor = _tree_parent_fd(target)
        except OSError as exc:
            raise BackendError("owned tree target ancestor invalid") from exc
        else:
            os.close(descriptor)
    elif target.parent.is_symlink() or not target.parent.is_dir():
        raise BackendError("owned tree target boundary invalid")
    desired = "sha256:" + plan["tree_sha256"]
    operation = OwnedOperation(stage, "tree:" + target.as_posix(), desired)

    def state(*, pending: bool) -> str | None:
        actual = _scan_tree(target)
        if actual is None:
            return None
        root_mode = _tree_root_mode(target)
        if actual == plan and root_mode == "0755":
            return desired
        if pending:
            return None
        return _digest(
            _canonical({
                "kind": "owned-tree-collision",
                "root_mode": root_mode,
                "tree_sha256": actual["tree_sha256"],
            })
        )

    def create() -> None:
        actual = _scan_tree(target)
        if actual is not None:
            if actual == plan and _tree_root_mode(target) == "0755":
                return
            _remove_owned_tree(target)
        _materialize_tree(target, plan, payloads)
        if _scan_tree(target) != plan or _tree_root_mode(target) != "0755":
            raise BackendError("owned tree post-materialization mismatch")

    def remove(identity: str) -> None:
        if (
            identity != desired
            or _scan_tree(target) != plan
            or _tree_root_mode(target) != "0755"
        ):
            raise BackendError("owned tree CAS identity drift")
        _remove_owned_tree(target)

    return SystemAction(
        operation=operation,
        observe_identity=lambda: state(pending=False),
        observe_pending_identity=lambda: state(pending=True),
        create_exact=create,
        remove_exact=remove,
    )


def _build_deferred_tree_action(
    *,
    target: Path,
    stage: str,
    plan: dict[str, Any],
    payloads: Mapping[str, bytes],
) -> SystemAction:
    target = Path(target)
    sealed_plan = _validated_tree_plan(plan)
    if not target.is_absolute():
        raise BackendError("owned tree target boundary invalid")
    operation = OwnedOperation(
        stage,
        "tree:" + target.as_posix(),
        "sha256:" + sealed_plan["tree_sha256"],
    )
    bound: SystemAction | None = None

    def action() -> SystemAction:
        nonlocal bound
        if bound is None:
            candidate = _build_tree_action(
                target=target,
                stage=stage,
                plan=sealed_plan,
                payloads=payloads,
            )
            if candidate.operation != operation:
                raise BackendError("deferred owned tree operation drift")
            bound = candidate
        return bound

    return SystemAction(
        operation=operation,
        observe_identity=lambda: action().observe_identity(),
        observe_pending_identity=lambda: (
            action().observe_pending_identity or action().observe_identity
        )(),
        observe_rollback_identity=lambda: (
            action().observe_rollback_identity or action().observe_identity
        )(),
        create_exact=lambda: action().create_exact(),
        remove_exact=lambda identity: action().remove_exact(identity),
    )


def _plan_verified_source_tree_action(
    *,
    archive_path: Path,
    expected_sha256: str,
    expected_size: int,
    expected_commit: str,
) -> tuple[dict[str, Any], dict[str, bytes]]:
    from scripts import phase12_spain_package as package

    try:
        plan = package.plan_verified_source_tree(
            archive_path,
            expected_sha256=expected_sha256,
            expected_size=expected_size,
            expected_commit=expected_commit,
        )
        raw = package._read_nofollow_bytes(Path(archive_path))
        if len(raw) != expected_size or hashlib.sha256(raw).hexdigest() != expected_sha256:
            raise BackendError("source archive changed after planning")
        payloads: dict[str, bytes] = {}
        with tarfile.open(fileobj=io.BytesIO(raw), mode="r:*") as archive:
            for row in plan["rows"]:
                if row["type"] != "file":
                    continue
                stream = archive.extractfile("source/" + row["path"])
                if stream is None:
                    raise BackendError("source tree member missing")
                payloads[row["path"]] = stream.read()
    except BackendError:
        raise
    except Exception as exc:
        raise BackendError("source tree planning failed") from exc
    return plan, payloads


def build_source_tree_action(
    *,
    archive_path: Path,
    target_dir: Path,
    expected_sha256: str,
    expected_size: int,
    expected_commit: str,
    stage: str,
) -> SystemAction:
    plan, payloads = _plan_verified_source_tree_action(
        archive_path=archive_path,
        expected_sha256=expected_sha256,
        expected_size=expected_size,
        expected_commit=expected_commit,
    )
    return _build_tree_action(
        target=Path(target_dir), stage=stage, plan=plan, payloads=payloads
    )


def build_deferred_source_tree_action(
    *,
    archive_path: Path,
    target_dir: Path,
    expected_sha256: str,
    expected_size: int,
    expected_commit: str,
    stage: str,
) -> SystemAction:
    plan, payloads = _plan_verified_source_tree_action(
        archive_path=archive_path,
        expected_sha256=expected_sha256,
        expected_size=expected_size,
        expected_commit=expected_commit,
    )
    return _build_deferred_tree_action(
        target=Path(target_dir), stage=stage, plan=plan, payloads=payloads
    )


def _plan_verified_wheel_tree(
    wheelhouse_dir: Path, inventory_path: Path
) -> tuple[dict[str, Any], dict[str, bytes]]:
    from scripts import phase12_spain_package as package

    wheelhouse = Path(wheelhouse_dir)
    inventory_raw = package._read_nofollow_bytes(Path(inventory_path))
    inventory = package._load_json_exact(inventory_raw, "wheelhouse inventory")
    if (
        not isinstance(inventory, dict)
        or inventory.get("schema") != package.WHEELHOUSE_SCHEMA
        or inventory.get("target")
        != {"architecture": "x86_64", "python_major_minor": "3.12"}
        or not isinstance(inventory.get("wheels"), list)
        or not inventory["wheels"]
    ):
        raise BackendError("wheel tree inventory invalid")
    entries = list(wheelhouse.iterdir())
    for entry in entries:
        try:
            info = os.lstat(entry)
        except OSError as exc:
            raise BackendError("wheelhouse entry observation failed") from exc
        if entry.is_symlink() or not stat.S_ISREG(info.st_mode):
            raise BackendError("wheelhouse top-level entry must be regular file")
    rows: dict[str, dict[str, Any]] = {}
    payloads: dict[str, bytes] = {}
    expected_wheels: set[str] = set()
    archive_total = 0
    uncompressed_total = 0

    def add_directory(path: PurePosixPath) -> None:
        for parent in reversed(path.parents):
            if parent == PurePosixPath("."):
                continue
            name = parent.as_posix()
            existing = rows.get(name)
            if existing is not None and existing["type"] != "dir":
                raise BackendError("wheel expanded path type collision")
            rows.setdefault(name, {"path": name, "type": "dir", "mode": "0755", "sha256": None})

    for inventory_row in inventory["wheels"]:
        if not isinstance(inventory_row, dict) or set(inventory_row) != {"filename", "sha256", "size"}:
            raise BackendError("wheel inventory row invalid")
        filename = package._safe_relative_path(inventory_row["filename"], "wheel filename").as_posix()
        if "/" in filename or not filename.endswith(".whl") or filename in expected_wheels:
            raise BackendError("wheel filename invalid/duplicate")
        expected_wheels.add(filename)
        body = package._read_nofollow_bytes(wheelhouse / filename)
        archive_total += len(body)
        if (
            archive_total > package.MAX_WHEEL_ARCHIVE_BYTES
            or len(body) != inventory_row["size"]
            or hashlib.sha256(body).hexdigest() != inventory_row["sha256"]
        ):
            raise BackendError("wheel archive hash/size/budget mismatch")
        try:
            with zipfile.ZipFile(io.BytesIO(body), "r") as wheel:
                local_names: set[str] = set()
                for info in wheel.infolist():
                    raw_name = info.filename[:-1] if info.is_dir() and info.filename.endswith("/") else info.filename
                    member = package._safe_relative_path(raw_name, "wheel member")
                    name = member.as_posix()
                    if name in local_names:
                        raise BackendError("wheel expanded path duplicate")
                    local_names.add(name)
                    mode = package._wheel_member_mode(info)
                    if info.is_dir():
                        if mode and not stat.S_ISDIR(mode):
                            raise BackendError("wheel directory type mismatch")
                        existing = rows.get(name)
                        if existing is not None and existing["type"] != "dir":
                            raise BackendError("wheel expanded path type collision")
                        add_directory(member)
                        rows.setdefault(
                            name,
                            {"path": name, "type": "dir", "mode": "0755", "sha256": None},
                        )
                        continue
                    if name in rows:
                        raise BackendError("wheel expanded path duplicate")
                    if (
                        package._wheel_mode_has_forbidden_type(mode)
                        or info.file_size > package.MAX_WHEEL_MEMBER_BYTES
                        or (info.file_size and (
                            info.compress_size <= 0
                            or info.file_size > info.compress_size * package.MAX_WHEEL_COMPRESSION_RATIO
                        ))
                        or any(part.endswith(".data") for part in member.parts)
                    ):
                        raise BackendError("wheel member type/size/layout rejected")
                    uncompressed_total += info.file_size
                    if uncompressed_total > package.MAX_WHEEL_UNCOMPRESSED_BYTES:
                        raise BackendError("wheel expanded aggregate budget exceeded")
                    add_directory(member)
                    payload = wheel.read(info)
                    rows[name] = {
                        "path": name, "type": "file", "mode": "0644",
                        "sha256": hashlib.sha256(payload).hexdigest(),
                        "size": len(payload),
                    }
                    payloads[name] = payload
        except zipfile.BadZipFile as exc:
            raise BackendError("wheel archive invalid") from exc
    actual_files = {entry.name for entry in entries}
    actual_wheels = {name for name in actual_files if name.endswith(".whl")}
    allowed_metadata = {"requirements-linux-x86_64-py312.lock", "wheelhouse-inventory.json"}
    if actual_wheels != expected_wheels or actual_files - actual_wheels - allowed_metadata:
        raise BackendError("wheelhouse file allowlist mismatch")
    return package._canonical_tree_plan(list(rows.values())), payloads


def build_wheel_tree_action(
    *,
    wheelhouse_dir: Path,
    inventory_path: Path,
    target_dir: Path,
    stage: str,
) -> SystemAction:
    try:
        plan, payloads = _plan_verified_wheel_tree(wheelhouse_dir, inventory_path)
    except BackendError:
        raise
    except Exception as exc:
        raise BackendError("wheel tree planning failed") from exc
    return _build_tree_action(
        target=Path(target_dir), stage=stage, plan=plan, payloads=payloads
    )


def build_deferred_wheel_tree_action(
    *,
    wheelhouse_dir: Path,
    inventory_path: Path,
    target_dir: Path,
    stage: str,
) -> SystemAction:
    try:
        plan, payloads = _plan_verified_wheel_tree(wheelhouse_dir, inventory_path)
    except BackendError:
        raise
    except Exception as exc:
        raise BackendError("wheel tree planning failed") from exc
    return _build_deferred_tree_action(
        target=Path(target_dir), stage=stage, plan=plan, payloads=payloads
    )


def read_canonical_root_json(
    path: Path,
    *,
    expected_keys: set[str],
    expected_uid: int | None = 0,
    max_bytes: int = 1024 * 1024,
) -> dict[str, Any]:
    """Read an approval/report envelope without following links or accepting
    alternate JSON encodings.

    Canonical bytes make the detached SHA binding unambiguous.  Production
    callers retain the root-owned default; tests may supply their effective UID.
    """

    candidate = Path(path)
    if (
        not candidate.is_absolute()
        or not isinstance(expected_keys, set)
        or not expected_keys
        or any(not isinstance(key, str) or not key for key in expected_keys)
        or not isinstance(max_bytes, int)
        or not 0 < max_bytes <= 1024 * 1024
    ):
        raise BackendError("canonical JSON boundary invalid")
    for parent in (candidate, *candidate.parents):
        if parent.is_symlink():
            raise BackendError("canonical JSON symlink path rejected")
    try:
        descriptor = os.open(
            candidate,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0),
        )
    except OSError as exc:
        raise BackendError("canonical JSON cannot be opened") from exc
    try:
        before = os.fstat(descriptor)
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_size <= 0
            or before.st_size > max_bytes
        ):
            raise BackendError("canonical JSON size/type invalid")
        if os.name != "nt" and (
            stat.S_IMODE(before.st_mode) != 0o600
            or (expected_uid is not None and before.st_uid != expected_uid)
        ):
            raise BackendError("canonical JSON owner/mode mismatch")
        chunks: list[bytes] = []
        remaining = max_bytes + 1
        while remaining and (chunk := os.read(descriptor, min(64 * 1024, remaining))):
            chunks.append(chunk)
            remaining -= len(chunk)
        payload = b"".join(chunks)
        after = os.fstat(descriptor)
        if (
            len(payload) > max_bytes
            or (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
            != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
        ):
            raise BackendError("canonical JSON changed during read or exceeded size")
    finally:
        os.close(descriptor)
    try:
        value = json.loads(payload.decode("ascii"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BackendError("canonical JSON syntax invalid") from exc
    if (
        not isinstance(value, dict)
        or set(value) != expected_keys
        or _canonical(value) + b"\n" != payload
    ):
        raise BackendError("canonical JSON schema/canonical bytes mismatch")
    return value


def _semantic_identity(value: Mapping[str, Any]) -> str:
    return _digest(_canonical(dict(value)))


def build_posix_identity_actions(
    *,
    runner: Callable[..., bytes],
    group_lookup: Callable[[], Mapping[str, Any] | None],
    user_lookup: Callable[[], Mapping[str, Any] | None],
) -> tuple[SystemAction, SystemAction]:
    """Build the exact uid/gid 61212 identity boundary.

    Production lookups are intentionally injected: a caller can use pwd/grp
    directly, while tests exercise crash/reconcile behavior without mutating the
    local machine.  Command execution is still expected to be a
    FixedCommandRunner whose exact vectors include these constants.
    """

    if not all(callable(value) for value in (runner, group_lookup, user_lookup)):
        raise BackendError("POSIX identity action dependency invalid")
    group_value = {"name": "amn2-spain", "gid": 61212}
    user_value = {
        "name": "amn2-spain",
        "uid": 61212,
        "gid": 61212,
        "home": "/var/lib/amn2-spain",
        "shell": "/usr/sbin/nologin",
    }
    group_operation = OwnedOperation(
        "identity", "group:amn2-spain", _semantic_identity(group_value)
    )
    user_operation = OwnedOperation(
        "identity", "user:amn2-spain", _semantic_identity(user_value)
    )
    groupadd = ("/usr/sbin/groupadd", "--gid", "61212", "--system", "amn2-spain")
    groupdel = ("/usr/sbin/groupdel", "amn2-spain")
    useradd = (
        "/usr/sbin/useradd", "--uid", "61212", "--gid", "61212", "--system",
        "--home-dir", "/var/lib/amn2-spain", "--no-create-home", "--shell",
        "/usr/sbin/nologin", "amn2-spain",
    )
    userdel = ("/usr/sbin/userdel", "amn2-spain")

    def observe(
        lookup: Callable[[], Mapping[str, Any] | None], keys: set[str]
    ) -> str | None:
        value = lookup()
        if value is None:
            return None
        if not isinstance(value, Mapping) or set(value) != keys:
            raise BackendError("POSIX identity observation schema mismatch")
        return _semantic_identity(value)

    return (
        SystemAction(
            operation=group_operation,
            observe_identity=lambda: observe(group_lookup, {"name", "gid"}),
            create_exact=lambda: runner(groupadd),
            remove_exact=lambda _identity: runner(groupdel),
        ),
        SystemAction(
            operation=user_operation,
            observe_identity=lambda: observe(
                user_lookup, {"name", "uid", "gid", "home", "shell"}
            ),
            create_exact=lambda: runner(useradd),
            remove_exact=lambda _identity: runner(userdel),
        ),
    )


GROUPADD_ARGV = (
    "/usr/sbin/groupadd", "--gid", "61212", "--system", "amn2-spain",
)
GROUPDEL_ARGV = ("/usr/sbin/groupdel", "amn2-spain")
USERADD_ARGV = (
    "/usr/sbin/useradd", "--uid", "61212", "--gid", "61212", "--system",
    "--home-dir", "/nonexistent", "--no-create-home", "--shell",
    "/usr/sbin/nologin", "amn2-spain",
)
USERDEL_ARGV = ("/usr/sbin/userdel", "amn2-spain")
IDENTITY_COMMAND_ALLOWLIST = frozenset(
    {GROUPADD_ARGV, GROUPDEL_ARGV, USERADD_ARGV, USERDEL_ARGV}
)


@dataclass(frozen=True)
class StructuredPosixIdentityObserver:
    group_by_name: Callable[[], Mapping[str, Any] | None] = field(repr=False)
    group_by_gid: Callable[[], Mapping[str, Any] | None] = field(repr=False)
    user_by_name: Callable[[], Mapping[str, Any] | None] = field(repr=False)
    user_by_uid: Callable[[], Mapping[str, Any] | None] = field(repr=False)

    def __post_init__(self) -> None:
        if not all(
            callable(value)
            for value in (
                self.group_by_name,
                self.group_by_gid,
                self.user_by_name,
                self.user_by_uid,
            )
        ):
            raise BackendError("POSIX structured observer invalid")

    @staticmethod
    def _record(
        value: Mapping[str, Any] | None, expected_keys: set[str], label: str
    ) -> dict[str, Any] | None:
        if value is None:
            return None
        if not isinstance(value, Mapping) or set(value) != expected_keys:
            raise BackendError(f"POSIX {label} observation schema mismatch")
        return dict(value)

    def observe_group(self) -> str | None:
        expected = {"name": "amn2-spain", "gid": 61212, "members": []}
        by_name = self._record(
            self.group_by_name(), {"name", "gid", "members"}, "group-by-name"
        )
        by_gid = self._record(
            self.group_by_gid(), {"name", "gid", "members"}, "group-by-gid"
        )
        if by_name is None and by_gid is None:
            return None
        if by_name != expected or by_gid != expected:
            raise BackendError("POSIX group name/id collision")
        return _semantic_identity({"kind": "posix-group", **expected})

    def observe_user(self) -> str | None:
        expected = {
            "name": "amn2-spain",
            "uid": 61212,
            "gid": 61212,
            "home": "/nonexistent",
            "shell": "/usr/sbin/nologin",
            "supplementary_groups": [],
        }
        keys = {"name", "uid", "gid", "home", "shell", "supplementary_groups"}
        by_name = self._record(self.user_by_name(), keys, "user-by-name")
        by_uid = self._record(self.user_by_uid(), keys, "user-by-uid")
        if by_name is None and by_uid is None:
            return None
        if by_name != expected or by_uid != expected:
            raise BackendError("POSIX user name/id collision")
        return _semantic_identity({"kind": "posix-user", **expected})


@dataclass(frozen=True)
class FixedIdentityBundle:
    actions: tuple[SystemAction, SystemAction]
    logical_receipt: Mapping[str, str]

    def __post_init__(self) -> None:
        if len(self.actions) != 2 or set(self.logical_receipt) != {
            "group:amn2-spain", "gid:61212", "user:amn2-spain", "uid:61212"
        }:
            raise BackendError("fixed identity bundle schema mismatch")
        if any(
            not MutationLedger._valid_identity(value)
            for value in self.logical_receipt.values()
        ):
            raise BackendError("fixed identity logical receipt invalid")


def build_fixed_identity_bundle(
    *,
    runner: Callable[..., bytes],
    observer: StructuredPosixIdentityObserver,
) -> FixedIdentityBundle:
    if not callable(runner) or not isinstance(observer, StructuredPosixIdentityObserver):
        raise BackendError("fixed identity dependency invalid")
    group_expected = _semantic_identity(
        {
            "kind": "posix-group", "name": "amn2-spain", "gid": 61212,
            "members": [],
        }
    )
    user_expected = _semantic_identity(
        {
            "kind": "posix-user", "name": "amn2-spain", "uid": 61212,
            "gid": 61212, "home": "/nonexistent", "shell": "/usr/sbin/nologin",
            "supplementary_groups": [],
        }
    )
    group_operation = OwnedOperation(
        "identity_created", "group:amn2-spain", group_expected
    )
    user_operation = OwnedOperation(
        "identity_created", "user:amn2-spain", user_expected
    )

    def create_group() -> None:
        runner(GROUPADD_ARGV)

    def remove_group(identity: str) -> None:
        if identity != group_expected or observer.observe_group() != group_expected:
            raise BackendError("POSIX group rollback CAS drift")
        runner(GROUPDEL_ARGV)

    def create_user() -> None:
        if observer.observe_group() != group_expected:
            raise BackendError("POSIX primary group missing before user creation")
        runner(USERADD_ARGV)

    def remove_user(identity: str) -> None:
        if identity != user_expected or observer.observe_user() != user_expected:
            raise BackendError("POSIX user rollback CAS drift")
        runner(USERDEL_ARGV)

    actions = (
        SystemAction(
            operation=group_operation,
            observe_identity=observer.observe_group,
            observe_pending_identity=observer.observe_group,
            create_exact=create_group,
            remove_exact=remove_group,
        ),
        SystemAction(
            operation=user_operation,
            observe_identity=observer.observe_user,
            observe_pending_identity=observer.observe_user,
            create_exact=create_user,
            remove_exact=remove_user,
        ),
    )
    receipt = MappingProxyType(
        {
            "group:amn2-spain": group_expected,
            "gid:61212": group_expected,
            "user:amn2-spain": user_expected,
            "uid:61212": user_expected,
        }
    )
    return FixedIdentityBundle(actions=actions, logical_receipt=receipt)


def build_production_identity_bundle() -> FixedIdentityBundle:
    if os.name == "nt":
        raise BackendError("production POSIX identity unavailable on this platform")
    import grp
    import pwd

    def optional(call: Callable[[], Any]) -> Any | None:
        try:
            return call()
        except KeyError:
            return None

    observer = StructuredPosixIdentityObserver(
        group_by_name=lambda: (
            None
            if (record := optional(lambda: grp.getgrnam("amn2-spain"))) is None
            else {
                "name": record.gr_name, "gid": record.gr_gid,
                "members": sorted(record.gr_mem),
            }
        ),
        group_by_gid=lambda: (
            None
            if (record := optional(lambda: grp.getgrgid(61212))) is None
            else {
                "name": record.gr_name, "gid": record.gr_gid,
                "members": sorted(record.gr_mem),
            }
        ),
        user_by_name=lambda: (
            None
            if (record := optional(lambda: pwd.getpwnam("amn2-spain"))) is None
            else {
                "name": record.pw_name, "uid": record.pw_uid, "gid": record.pw_gid,
                "home": record.pw_dir, "shell": record.pw_shell,
                "supplementary_groups": sorted(
                    group.gr_name
                    for group in grp.getgrall()
                    if record.pw_name in group.gr_mem
                ),
            }
        ),
        user_by_uid=lambda: (
            None
            if (record := optional(lambda: pwd.getpwuid(61212))) is None
            else {
                "name": record.pw_name, "uid": record.pw_uid, "gid": record.pw_gid,
                "home": record.pw_dir, "shell": record.pw_shell,
                "supplementary_groups": sorted(
                    group.gr_name
                    for group in grp.getgrall()
                    if record.pw_name in group.gr_mem
                ),
            }
        ),
    )
    runner = FixedCommandRunner(allowed_argv=IDENTITY_COMMAND_ALLOWLIST)
    return build_fixed_identity_bundle(runner=runner, observer=observer)


class NetworkContourController(Protocol):
    def read_ledger(self) -> dict[str, Any] | None: ...

    def assert_absent(self) -> None: ...

    def is_exact(self, ledger: dict[str, Any]) -> bool: ...

    def apply(self) -> dict[str, Any]: ...

    def rollback(self, ledger: dict[str, Any]) -> None: ...

    def remove_ledger(self, ledger: dict[str, Any]) -> None: ...


def network_contour_identity() -> str:
    from scripts.phase12_spain_network import (
        EXPECTED_NFT_SEMANTIC_SHA256,
        ROUTE_IDENTITY,
    )

    return _semantic_identity(
        {
            "kind": "amn2.spain-network-contour.v1",
            "nft_semantic_sha256": EXPECTED_NFT_SEMANTIC_SHA256,
            "route": ROUTE_IDENTITY,
            "sysctl": {"name": "net.ipv4.ip_forward", "applied": "1"},
        }
    )


def build_network_contour_action(controller: NetworkContourController) -> SystemAction:
    required = (
        "read_ledger", "assert_absent", "is_exact", "apply", "rollback",
        "remove_ledger",
    )
    if any(not callable(getattr(controller, name, None)) for name in required):
        raise BackendError("network contour controller invalid")
    desired = network_contour_identity()
    operation = OwnedOperation(
        "network", "network-contour:amn2-spain", desired
    )

    def observe() -> str | None:
        ledger = controller.read_ledger()
        if ledger is None:
            controller.assert_absent()
            return None
        if not controller.is_exact(ledger):
            raise BackendError("network contour collision")
        return desired

    def create() -> None:
        ledger = controller.apply()
        if not controller.is_exact(ledger):
            raise BackendError("network contour post-apply identity mismatch")

    def remove(identity: str) -> None:
        if identity != desired:
            raise BackendError("network contour CAS identity drift")
        ledger = controller.read_ledger()
        if ledger is None:
            raise BackendError("network contour rollback ledger missing")
        controller.rollback(ledger)
        controller.remove_ledger(ledger)

    return SystemAction(
        operation=operation,
        observe_identity=observe,
        create_exact=create,
        remove_exact=remove,
    )


def build_network_service_contour_action(
    *,
    systemd_active_action: SystemAction,
    controller: NetworkContourController,
) -> SystemAction:
    required = (
        "read_ledger", "assert_absent", "is_exact", "rollback",
        "remove_ledger",
    )
    expected_systemd_object = "systemd-active:amn2-spain-network.service"
    if (
        not isinstance(systemd_active_action, SystemAction)
        or systemd_active_action.operation.stage != "host_network_applied"
        or systemd_active_action.operation.owned_object != expected_systemd_object
        or any(not callable(getattr(controller, name, None)) for name in required)
    ):
        raise BackendError("network service contour dependency invalid")
    systemd_identity = systemd_active_action.operation.desired_identity
    desired = _semantic_identity(
        {
            "kind": "amn2.spain-network-service-contour.v1",
            "systemd_active_identity": systemd_identity,
            "network_contour_identity": network_contour_identity(),
        }
    )
    operation = OwnedOperation(
        "host_network_applied", "network-contour:amn2-spain", desired
    )

    def observe() -> str | None:
        service = systemd_active_action.observe_identity()
        ledger = controller.read_ledger()
        if service is None:
            if ledger is not None:
                raise BackendError("network service contour collision")
            controller.assert_absent()
            return None
        if service != systemd_identity or ledger is None or not controller.is_exact(ledger):
            raise BackendError("network service contour collision")
        return desired

    def observe_rollback() -> str | None:
        callback = (
            systemd_active_action.observe_rollback_identity
            or systemd_active_action.observe_identity
        )
        service = callback()
        ledger = controller.read_ledger()
        if service is None and ledger is None:
            controller.assert_absent()
            return None
        if service not in {None, systemd_identity}:
            raise BackendError("network service contour rollback drift")
        if service is not None and (
            ledger is None or not controller.is_exact(ledger)
        ):
            raise BackendError("network service contour rollback drift")
        return desired

    def create() -> None:
        if observe() is not None:
            return
        systemd_active_action.create_exact()
        if observe() != desired:
            raise BackendError("network service contour post-start drift")

    def remove(identity: str) -> None:
        if identity != desired:
            raise BackendError("network service contour CAS drift")
        callback = (
            systemd_active_action.observe_rollback_identity
            or systemd_active_action.observe_identity
        )
        service = callback()
        ledger = controller.read_ledger()
        if service == systemd_identity:
            if ledger is None or not controller.is_exact(ledger):
                raise BackendError("network service contour rollback drift")
            systemd_active_action.remove_exact(systemd_identity)
        elif service is None and ledger is not None:
            controller.rollback(ledger)
            controller.remove_ledger(ledger)
        elif service is not None:
            raise BackendError("network service contour rollback drift")
        if callback() is not None or controller.read_ledger() is not None:
            raise BackendError("network service contour rollback incomplete")
        controller.assert_absent()

    return SystemAction(
        operation=operation,
        observe_identity=observe,
        observe_pending_identity=observe,
        observe_rollback_identity=observe_rollback,
        create_exact=create,
        remove_exact=remove,
        reconcile_absent_removal=True,
    )


PRODUCTION_INSTALL_MUTATING_STAGES = (
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
)


@dataclass(frozen=True, repr=False)
class ProductionInstallActionPlan:
    actions: tuple[SystemAction, ...]
    operations: tuple[OwnedOperation, ...]
    operations_by_stage: Mapping[str, tuple[OwnedOperation, ...]]

    def __post_init__(self) -> None:
        if (
            not self.actions
            or self.operations != tuple(action.operation for action in self.actions)
            or tuple(self.operations_by_stage) != PRODUCTION_INSTALL_MUTATING_STAGES
            or tuple(
                operation
                for stage in PRODUCTION_INSTALL_MUTATING_STAGES
                for operation in self.operations_by_stage[stage]
            )
            != self.operations
            or any(not self.operations_by_stage[stage] for stage in PRODUCTION_INSTALL_MUTATING_STAGES)
            or len({operation.owned_object for operation in self.operations})
            != len(self.operations)
        ):
            raise BackendError("production install action plan invalid")


@dataclass(frozen=True, repr=False)
class ProductionInstallAssembly:
    action_plan: ProductionInstallActionPlan
    operation_logical_contract: Mapping[str, str]
    stage_object_contract: Mapping[str, tuple[str, ...]]

    def __post_init__(self) -> None:
        operations = self.action_plan.operations
        owned = {operation.owned_object for operation in operations}
        if (
            set(self.operation_logical_contract) != owned
            or any(
                self.operation_logical_contract[operation.owned_object]
                != operation.owned_object
                for operation in operations
            )
            or tuple(self.stage_object_contract) != PRODUCTION_INSTALL_MUTATING_STAGES
            or tuple(
                value
                for stage in PRODUCTION_INSTALL_MUTATING_STAGES
                for value in self.stage_object_contract[stage]
            )
            != tuple(operation.owned_object for operation in operations)
        ):
            raise BackendError("production install assembly contract invalid")


def compose_production_install_actions(
    *,
    identity_actions: Iterable[SystemAction],
    filesystem_actions: Iterable[SystemAction],
    database_action: SystemAction,
    systemd_actions: Iterable[SystemAction],
    docker_actions: Iterable[SystemAction],
    network_service_contour_action: SystemAction,
) -> ProductionInstallActionPlan:
    identity = tuple(identity_actions)
    filesystem = tuple(filesystem_actions)
    systemd = tuple(systemd_actions)
    docker = tuple(docker_actions)
    groups = (identity, filesystem, systemd, docker)
    if (
        any(not group or any(not isinstance(action, SystemAction) for action in group) for group in groups)
        or not isinstance(database_action, SystemAction)
        or not isinstance(network_service_contour_action, SystemAction)
    ):
        raise BackendError("production install action dependency invalid")
    if any(action.operation.stage != "identity_created" for action in identity):
        raise BackendError("production identity action stage mismatch")
    if any(
        action.operation.stage not in {"filesystem_staged", "secrets_configs_rendered"}
        for action in filesystem
    ):
        raise BackendError("production filesystem action stage mismatch")
    if database_action.operation.stage != "clean_db_initialized":
        raise BackendError("production database action stage mismatch")
    if any(
        action.operation.stage
        not in {"units_installed", "docker_started", "host_network_applied", "web_started"}
        for action in systemd
    ):
        raise BackendError("production systemd action stage mismatch")
    if any(
        action.operation.stage not in {"awg_image_loaded", "network_container_started"}
        for action in docker
    ):
        raise BackendError("production Docker action stage mismatch")
    network_active_object = "systemd-active:amn2-spain-network.service"
    network_active = tuple(
        action for action in systemd
        if action.operation.owned_object == network_active_object
    )
    if (
        len(network_active) != 1
        or network_service_contour_action.operation.stage != "host_network_applied"
        or network_service_contour_action.operation.owned_object
        != "network-contour:amn2-spain"
    ):
        raise BackendError("production network composite action mismatch")
    candidates = (
        *identity,
        *filesystem,
        database_action,
        *(action for action in systemd if action is not network_active[0]),
        *docker,
        network_service_contour_action,
    )
    stage_rank = {
        stage: index for index, stage in enumerate(PRODUCTION_INSTALL_MUTATING_STAGES)
    }
    if any(action.operation.stage not in stage_rank for action in candidates):
        raise BackendError("production action outside sealed stages")
    actions = tuple(
        sorted(candidates, key=lambda action: stage_rank[action.operation.stage])
    )
    operations = tuple(action.operation for action in actions)
    by_stage = MappingProxyType(
        {
            stage: tuple(
                operation for operation in operations if operation.stage == stage
            )
            for stage in PRODUCTION_INSTALL_MUTATING_STAGES
        }
    )
    return ProductionInstallActionPlan(
        actions=actions,
        operations=operations,
        operations_by_stage=by_stage,
    )


def assemble_production_install_actions(
    *,
    host_root: Path,
    package_content_root: Path,
    prepared_source_root: Path,
    endpoint_host: str,
    boot_id: str,
    runtime_binding: Mapping[str, Any],
    prepared_payloads: "PreparedProductionFilesystemPayloads",
    systemd_runner: Callable[..., bytes],
    docker_runner: Callable[..., bytes],
    network_manager: Any,
    socket_observer: Callable[[], Mapping[str, Any]] | None = None,
    identity_bundle: "FixedIdentityBundle | None" = None,
    expected_root_uid: int | None = 0,
    expected_root_gid: int | None = 0,
    expected_service_uid: int | None = 61212,
    expected_service_gid: int | None = 61212,
) -> ProductionInstallAssembly:
    """Build the exact callback registry from one re-verifiable package binding."""
    from scripts import phase12_spain_package as package

    root = Path(host_root)
    content = Path(package_content_root)
    prepared_source = Path(prepared_source_root)
    if (
        not root.is_absolute()
        or root.is_symlink()
        or not root.is_dir()
        or not content.is_absolute()
        or content.is_symlink()
        or not content.is_dir()
        or not prepared_source.is_absolute()
        or prepared_source.is_symlink()
        or not prepared_source.is_dir()
        or not isinstance(endpoint_host, str)
        or not endpoint_host
        or not isinstance(runtime_binding, Mapping)
        or not isinstance(prepared_payloads, PreparedProductionFilesystemPayloads)
        or not callable(systemd_runner)
        or not callable(docker_runner)
        or (socket_observer is not None and not callable(socket_observer))
    ):
        raise BackendError("production install assembly dependency invalid")
    actual_binding = package.plan_verified_runtime_artifacts(content)
    if dict(runtime_binding) != actual_binding:
        raise BackendError("production runtime artifact binding drift")

    def artifact(relative: str) -> Path:
        safe = package._safe_relative_path(relative, "production runtime artifact")
        return content.joinpath(*safe.parts)

    source = actual_binding["source"]
    wheelhouse = actual_binding["wheelhouse"]
    docker = actual_binding["docker"]
    awg = actual_binding["awg_image"]
    identity = identity_bundle or build_production_identity_bundle()
    filesystem = build_production_filesystem_bundle(
        root=root,
        source_root=prepared_source,
        endpoint_host=endpoint_host,
        root_uid=expected_root_uid,
        root_gid=expected_root_gid,
        service_uid=expected_service_uid,
        service_gid=expected_service_gid,
        prepared_payloads=prepared_payloads,
    )
    runtime_fs = SafeFs(
        root=root,
        expected_uid=expected_root_uid,
        expected_gid=expected_root_gid,
    )
    runtime_actions = (
        build_static_docker_action(
            fs=runtime_fs,
            archive_path=artifact(docker["path"]),
            expected_sha256=docker["sha256"],
            expected_size=docker["size"],
        ),
        build_deferred_source_tree_action(
            archive_path=artifact(source["path"]),
            target_dir=root / "opt/amn2-spain/runtime/source",
            expected_sha256=source["sha256"],
            expected_size=source["size"],
            expected_commit=source["commit"],
            stage="filesystem_staged",
        ),
        build_deferred_wheel_tree_action(
            wheelhouse_dir=artifact(wheelhouse["path"]),
            inventory_path=artifact(wheelhouse["inventory_path"]),
            target_dir=root / "opt/amn2-spain/runtime/site-packages",
            stage="filesystem_staged",
        ),
    )
    database = build_deferred_production_clean_database_action(
        source_root=prepared_source,
        expected_source_tree_identity=prepared_payloads.source_tree_identity,
        database_path=root / "var/lib/amn2-spain/amn2.sqlite3",
        expected_uid=expected_service_uid,
        expected_gid=expected_service_gid,
    )
    systemd = build_production_systemd_bundle(
        root=root,
        runner=systemd_runner,
        package_content_root=content,
        root_uid=expected_root_uid,
        root_gid=expected_root_gid,
    )
    effective_socket_observer = socket_observer or observe_dedicated_docker_socket
    docker_runtime = build_production_docker_runtime_bundle(
        runner=docker_runner,
        image_archive_path=artifact(awg["path"]),
        image_archive_sha256=awg["sha256"],
        image_archive_size=awg["size"],
        socket_observer=effective_socket_observer,
    )
    network_active = tuple(
        action
        for action in systemd.actions
        if action.operation.owned_object
        == "systemd-active:amn2-spain-network.service"
    )
    if len(network_active) != 1:
        raise BackendError("production network systemd action missing")
    controller = SystemNetworkContourController(
        manager=network_manager,
        ledger_path=root / "var/lib/amn2-spain/network-ledger.json",
        expected_boot_id=boot_id,
    )
    network = build_network_service_contour_action(
        systemd_active_action=network_active[0],
        controller=controller,
    )
    plan = compose_production_install_actions(
        identity_actions=identity.actions,
        filesystem_actions=(*filesystem.actions, *runtime_actions),
        database_action=database,
        systemd_actions=systemd.actions,
        docker_actions=docker_runtime.actions,
        network_service_contour_action=network,
    )
    logical = MappingProxyType(
        {
            operation.owned_object: operation.owned_object
            for operation in plan.operations
        }
    )
    stage_contract = MappingProxyType(
        {
            stage: tuple(
                operation.owned_object
                for operation in plan.operations_by_stage[stage]
            )
            for stage in PRODUCTION_INSTALL_MUTATING_STAGES
        }
    )
    return ProductionInstallAssembly(
        action_plan=plan,
        operation_logical_contract=logical,
        stage_object_contract=stage_contract,
    )


class SystemNetworkContourController:
    """Adapter around NetworkManager's prepared/final durable ledger."""

    def __init__(self, *, manager: Any, ledger_path: Path, expected_boot_id: str) -> None:
        from scripts.phase12_spain_network import BOOT_ID_PATTERN

        self.manager = manager
        self.ledger_path = Path(ledger_path)
        self.expected_boot_id = expected_boot_id
        if (
            BOOT_ID_PATTERN.fullmatch(expected_boot_id) is None
            or not self.ledger_path.is_absolute()
            or self.ledger_path.parent.is_symlink()
        ):
            raise BackendError("network contour binding invalid")

    def read_ledger(self) -> dict[str, Any] | None:
        from scripts.phase12_spain_network import NetworkError, _read_ledger

        try:
            return _read_ledger(self.ledger_path)
        except NetworkError as exc:
            raise BackendError("network contour ledger invalid") from exc

    def assert_absent(self) -> None:
        from scripts.phase12_spain_network import NetworkError

        try:
            declared = self.manager._assert_foreign_compatible()
            nft_state = self.manager._owned_state(declared)
            route_state = self.manager._route_state()
        except NetworkError as exc:
            raise BackendError("network contour absence observation failed") from exc
        if nft_state != "absent" or route_state != "absent":
            raise BackendError("network contour pre-existing collision")

    def is_exact(self, ledger: dict[str, Any]) -> bool:
        from scripts.phase12_spain_network import NetworkError

        try:
            self.manager.verify(ledger)
        except NetworkError:
            return False
        return True

    def apply(self) -> dict[str, Any]:
        from scripts.phase12_spain_network import NetworkError, _write_ledger

        existing = self.read_ledger()
        try:
            if existing is None:
                ledger = self.manager.apply(
                    expected_boot_id=self.expected_boot_id,
                    persist_intent=lambda value: _write_ledger(self.ledger_path, value),
                )
            else:
                ledger = self.manager.apply(
                    expected_boot_id=self.expected_boot_id,
                    existing_ledger=existing,
                )
            _write_ledger(self.ledger_path, ledger)
            return ledger
        except NetworkError as exc:
            raise BackendError("network contour apply failed") from exc

    def rollback(self, ledger: dict[str, Any]) -> None:
        from scripts.phase12_spain_network import NetworkError

        try:
            self.manager.rollback(ledger)
        except NetworkError as exc:
            raise BackendError("network contour rollback failed") from exc

    def remove_ledger(self, ledger: dict[str, Any]) -> None:
        current = self.read_ledger()
        if current != ledger:
            raise BackendError("network contour ledger CAS drift")
        if self.ledger_path.is_symlink() or not self.ledger_path.is_file():
            raise BackendError("network contour ledger type drift")
        try:
            os.unlink(self.ledger_path)
            if os.name != "nt":
                descriptor = os.open(
                    self.ledger_path.parent,
                    os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                    | getattr(os, "O_NOFOLLOW", 0),
                )
                try:
                    os.fsync(descriptor)
                finally:
                    os.close(descriptor)
        except OSError as exc:
            raise BackendError("network contour ledger removal failed") from exc


SYSTEMD_UNITS = frozenset(
    {
        "amn2-spain-web.service",
        "amn2-spain-bot.service",
        "amn2-spain-docker.service",
        "amn2-spain-network.service",
    }
)
SYSTEMD_UNIT_ORDER = (
    "amn2-spain-docker.service",
    "amn2-spain-network.service",
    "amn2-spain-web.service",
    "amn2-spain-bot.service",
)
MAX_SYSTEMCTL_SHOW_BYTES = 4096
SYSTEMCTL = "/usr/bin/systemctl"


def _systemctl_show_argv(unit: str) -> tuple[str, ...]:
    return (
        SYSTEMCTL,
        "show",
        unit,
        "--no-pager",
        "--property=LoadState,FragmentPath,UnitFileState,ActiveState",
    )


SYSTEMCTL_COMMAND_ALLOWLIST = frozenset(
    {(SYSTEMCTL, "daemon-reload")}
    | {_systemctl_show_argv(unit) for unit in SYSTEMD_UNIT_ORDER}
    | {
        (SYSTEMCTL, verb, unit)
        for unit in SYSTEMD_UNIT_ORDER[:-1]
        for verb in ("enable", "disable", "start", "stop")
    }
)


def parse_systemctl_show(payload: bytes, *, unit: str) -> dict[str, str]:
    if (
        unit not in SYSTEMD_UNITS
        or not isinstance(payload, bytes)
        or not payload
        or len(payload) > MAX_SYSTEMCTL_SHOW_BYTES
    ):
        raise BackendError("systemd show observation invalid")
    try:
        text = payload.decode("ascii")
    except UnicodeDecodeError as exc:
        raise BackendError("systemd show observation invalid") from exc
    values: dict[str, str] = {}
    for line in text.splitlines():
        if "=" not in line:
            raise BackendError("systemd show observation invalid")
        key, value = line.split("=", maxsplit=1)
        if key in values:
            raise BackendError("systemd show observation invalid")
        values[key] = value
    if set(values) != {"LoadState", "FragmentPath", "UnitFileState", "ActiveState"}:
        raise BackendError("systemd show observation invalid")
    expected_fragment = "/etc/systemd/system/" + unit
    if values["LoadState"] == "loaded":
        if (
            values["FragmentPath"] != expected_fragment
            or values["UnitFileState"] not in {"disabled", "enabled", "static"}
            or values["ActiveState"] not in {"inactive", "active"}
        ):
            raise BackendError("systemd show observation invalid")
    elif values["LoadState"] == "not-found":
        if (
            values["FragmentPath"]
            or values["UnitFileState"] not in {"", "not-found"}
            or values["ActiveState"] != "inactive"
        ):
            raise BackendError("systemd show observation invalid")
    else:
        raise BackendError("systemd show observation invalid")
    return values


@dataclass(frozen=True, repr=False)
class ProductionSystemdBundle:
    actions: tuple[SystemAction, ...]
    logical_receipt: Mapping[str, str]

    def __post_init__(self) -> None:
        operations = tuple(action.operation for action in self.actions)
        if (
            len(operations) != 10
            or len({operation.owned_object for operation in operations}) != 10
            or set(self.logical_receipt)
            != {operation.owned_object for operation in operations}
            or any(
                self.logical_receipt[operation.owned_object]
                != operation.desired_identity
                for operation in operations
            )
        ):
            raise BackendError("production systemd bundle schema mismatch")


def build_production_systemd_bundle(
    *,
    root: Path,
    runner: Callable[..., bytes],
    package_content_root: Path | None = None,
    root_uid: int | None = 0,
    root_gid: int | None = 0,
) -> ProductionSystemdBundle:
    if not callable(runner):
        raise BackendError("production systemd runner invalid")
    fs = SafeFs(root=Path(root), expected_uid=root_uid, expected_gid=root_gid)
    if (fs.root / "etc/amn2-spain/bot-enabled").exists() or (
        fs.root / "etc/amn2-spain/bot-enabled"
    ).is_symlink():
        raise BackendError("bot enable marker collision")

    def run(argv: tuple[str, ...]) -> bytes:
        if argv not in SYSTEMCTL_COMMAND_ALLOWLIST:
            raise BackendError("systemd command outside exact allowlist")
        try:
            output = runner(
                argv,
                timeout=DEFAULT_COMMAND_TIMEOUT,
                max_output=MAX_SYSTEMCTL_SHOW_BYTES,
            )
        except Exception:
            raise BackendError("systemd command failed") from None
        if not isinstance(output, bytes) or len(output) > MAX_SYSTEMCTL_SHOW_BYTES:
            raise BackendError("systemd command output invalid")
        return output

    def show(unit: str) -> dict[str, str]:
        return parse_systemctl_show(run(_systemctl_show_argv(unit)), unit=unit)

    def loaded_exact(state: Mapping[str, str], unit: str) -> bool:
        return (
            state["LoadState"] == "loaded"
            and state["FragmentPath"] == "/etc/systemd/system/" + unit
        )

    def require_bot_marker_absent() -> None:
        marker = fs.root / "etc/amn2-spain/bot-enabled"
        if marker.exists() or marker.is_symlink():
            raise BackendError("bot enable marker collision")

    unit_actions: list[SystemAction] = []
    unit_prefix = (
        "packaging/phase12-spain/units/"
        if package_content_root is None
        else "units/"
    )
    for unit in SYSTEMD_UNIT_ORDER:
        relative = "etc/systemd/system/" + unit
        payload = _read_package_bound_bytes(
            unit_prefix + unit,
            content_root=package_content_root,
            max_bytes=128 * 1024,
        )
        desired = _new_fs_identity(fs, relative, kind="file", mode=0o644, payload=payload)
        operation = OwnedOperation(
            "units_installed", "file:/" + relative, desired
        )
        is_bot = unit == "amn2-spain-bot.service"

        def observe(
            *, relative: str = relative, desired: str = desired,
            unit: str = unit, is_bot: bool = is_bot,
        ) -> str | None:
            if is_bot:
                require_bot_marker_absent()
            actual = fs.identity(relative)
            if actual is None:
                if show(unit)["LoadState"] != "not-found":
                    raise BackendError("systemd manager/file collision")
                return None
            if actual != desired:
                return actual
            if is_bot:
                state = show(unit)
                if not (
                    loaded_exact(state, unit)
                    and state["UnitFileState"] == "static"
                    and state["ActiveState"] == "inactive"
                ):
                    raise BackendError("bot systemd state drift")
            return desired

        def observe_pending(
            *, relative: str = relative, desired: str = desired,
            unit: str = unit, is_bot: bool = is_bot,
        ) -> str | None:
            if is_bot:
                require_bot_marker_absent()
            actual = fs.identity(relative)
            if actual is None:
                return None
            if actual != desired:
                return None
            state = show(unit)
            if not loaded_exact(state, unit):
                return None
            if is_bot and not (
                state["UnitFileState"] == "static"
                and state["ActiveState"] == "inactive"
            ):
                raise BackendError("bot systemd state drift")
            return desired

        def observe_rollback(
            *, relative: str = relative, desired: str = desired,
            unit: str = unit, is_bot: bool = is_bot,
        ) -> str | None:
            if is_bot:
                require_bot_marker_absent()
            actual = fs.identity(relative)
            if actual is None:
                return None
            return observe(
                relative=relative,
                desired=desired,
                unit=unit,
                is_bot=is_bot,
            )

        def create(
            *, relative: str = relative, payload: bytes = payload,
            desired: str = desired, unit: str = unit, is_bot: bool = is_bot,
        ) -> None:
            if is_bot:
                require_bot_marker_absent()
            actual = fs.identity(relative)
            if actual is None:
                actual = fs.write_file(relative, payload, 0o644)
            if actual != desired:
                raise BackendError("systemd unit file collision")
            run((SYSTEMCTL, "daemon-reload"))
            state = show(unit)
            if not loaded_exact(state, unit):
                raise BackendError("systemd unit reload identity mismatch")
            if is_bot:
                if not (
                    state["UnitFileState"] == "static"
                    and state["ActiveState"] == "inactive"
                ):
                    raise BackendError("bot systemd state drift")
            elif not (
                state["UnitFileState"] == "disabled"
                and state["ActiveState"] == "inactive"
            ):
                raise BackendError("systemd new unit state collision")

        def remove(
            identity: str,
            *, relative: str = relative, desired: str = desired,
            unit: str = unit, is_bot: bool = is_bot,
        ) -> None:
            if is_bot:
                require_bot_marker_absent()
            actual = fs.identity(relative)
            if identity != desired or actual not in {None, desired}:
                raise BackendError("systemd unit rollback CAS drift")
            if actual == desired:
                state = show(unit)
                expected_unit_file_state = "static" if is_bot else "disabled"
                if not (
                    loaded_exact(state, unit)
                    and state["UnitFileState"] == expected_unit_file_state
                    and state["ActiveState"] == "inactive"
                ):
                    raise BackendError("systemd unit rollback state drift")
                fs.remove_exact(relative, desired)
            run((SYSTEMCTL, "daemon-reload"))
            if show(unit)["LoadState"] != "not-found":
                raise BackendError("systemd unit removal reload mismatch")

        unit_actions.append(
            SystemAction(
                operation=operation,
                observe_identity=observe,
                observe_pending_identity=observe_pending,
                observe_rollback_identity=observe_rollback,
                create_exact=create,
                remove_exact=remove,
                reconcile_absent_removal=True,
            )
        )

    state_actions: list[SystemAction] = []
    for unit, stage in (
        ("amn2-spain-docker.service", "docker_started"),
        ("amn2-spain-network.service", "host_network_applied"),
        ("amn2-spain-web.service", "web_started"),
    ):
        enabled_identity = _semantic_identity(
            {
                "kind": "systemd-enabled-state.v2",
                "unit": unit,
                "fragment": "/etc/systemd/system/" + unit,
            }
        )
        active_identity = _semantic_identity(
            {
                "kind": "systemd-active-state.v2",
                "unit": unit,
                "fragment": "/etc/systemd/system/" + unit,
            }
        )

        def observe_enabled(
            *, unit: str = unit, desired: str = enabled_identity
        ) -> str | None:
            state = show(unit)
            if not loaded_exact(state, unit):
                raise BackendError("systemd unit fragment drift")
            if state["UnitFileState"] == "enabled":
                return desired
            if state["UnitFileState"] == "disabled":
                return None
            raise BackendError("systemd unit-file state drift")

        def create_enabled(
            *, unit: str = unit, desired: str = enabled_identity
        ) -> None:
            before = show(unit)
            if not (
                loaded_exact(before, unit)
                and before["UnitFileState"] == "disabled"
                and before["ActiveState"] == "inactive"
            ):
                raise BackendError("systemd enable precondition drift")
            run((SYSTEMCTL, "enable", unit))
            after = show(unit)
            if not (
                loaded_exact(after, unit)
                and after["UnitFileState"] == "enabled"
                and after["ActiveState"] == "inactive"
            ):
                raise BackendError("systemd enable verification failed")

        def remove_enabled(
            identity: str,
            *, unit: str = unit, desired: str = enabled_identity,
        ) -> None:
            before = show(unit)
            if identity != desired or not (
                loaded_exact(before, unit)
                and before["UnitFileState"] == "enabled"
                and before["ActiveState"] == "inactive"
            ):
                raise BackendError("systemd disable CAS drift")
            run((SYSTEMCTL, "disable", unit))
            after = show(unit)
            if not (
                loaded_exact(after, unit)
                and after["UnitFileState"] == "disabled"
                and after["ActiveState"] == "inactive"
            ):
                raise BackendError("systemd disable verification failed")

        enabled_action = SystemAction(
            operation=OwnedOperation(
                stage, "systemd-enabled:" + unit, enabled_identity
            ),
            observe_identity=observe_enabled,
            create_exact=create_enabled,
            remove_exact=remove_enabled,
        )

        def observe_active(
            *, unit: str = unit, desired: str = active_identity
        ) -> str | None:
            state = show(unit)
            if not (
                loaded_exact(state, unit)
                and state["UnitFileState"] == "enabled"
            ):
                raise BackendError("systemd active fragment/enable drift")
            return desired if state["ActiveState"] == "active" else None

        def create_active(
            *, unit: str = unit, desired: str = active_identity
        ) -> None:
            before = show(unit)
            if not (
                loaded_exact(before, unit)
                and before["UnitFileState"] == "enabled"
                and before["ActiveState"] == "inactive"
            ):
                raise BackendError("systemd start precondition drift")
            run((SYSTEMCTL, "start", unit))
            after = show(unit)
            if not (
                loaded_exact(after, unit)
                and after["UnitFileState"] == "enabled"
                and after["ActiveState"] == "active"
            ):
                raise BackendError("systemd start verification failed")

        def remove_active(
            identity: str,
            *, unit: str = unit, desired: str = active_identity,
        ) -> None:
            before = show(unit)
            if identity != desired or not (
                loaded_exact(before, unit)
                and before["UnitFileState"] == "enabled"
                and before["ActiveState"] == "active"
            ):
                raise BackendError("systemd stop CAS drift")
            run((SYSTEMCTL, "stop", unit))
            after = show(unit)
            if not (
                loaded_exact(after, unit)
                and after["UnitFileState"] == "enabled"
                and after["ActiveState"] == "inactive"
            ):
                raise BackendError("systemd stop verification failed")

        active_action = SystemAction(
            operation=OwnedOperation(
                stage, "systemd-active:" + unit, active_identity
            ),
            observe_identity=observe_active,
            create_exact=create_active,
            remove_exact=remove_active,
        )
        state_actions.extend((enabled_action, active_action))

    actions = tuple((*unit_actions, *state_actions))
    receipt = MappingProxyType(
        {
            action.operation.owned_object: action.operation.desired_identity
            for action in actions
        }
    )
    return ProductionSystemdBundle(actions=actions, logical_receipt=receipt)


def build_systemd_unit_actions(
    *,
    unit: str,
    stage: str,
    runner: Callable[..., bytes],
    lookup: Callable[[], Mapping[str, Any]],
    start_active: bool,
) -> tuple[SystemAction, ...]:
    if (
        unit not in SYSTEMD_UNITS
        or not isinstance(stage, str)
        or not stage
        or not callable(runner)
        or not callable(lookup)
        or type(start_active) is not bool
    ):
        raise BackendError("systemd action boundary invalid")
    systemctl = "/usr/bin/systemctl"
    reload_argv = (systemctl, "daemon-reload")
    enable_argv = (systemctl, "enable", unit)
    disable_argv = (systemctl, "disable", unit)
    start_argv = (systemctl, "start", unit)
    stop_argv = (systemctl, "stop", unit)

    def state() -> Mapping[str, Any]:
        value = lookup()
        if (
            not isinstance(value, Mapping)
            or set(value) != {"UnitFileState", "ActiveState"}
            or value["UnitFileState"] not in {"disabled", "enabled"}
            or value["ActiveState"] not in {"inactive", "active"}
        ):
            raise BackendError("systemd exact state observation invalid")
        return value

    enable_identity = _semantic_identity(
        {"kind": "systemd-unit-file-state", "unit": unit, "state": "enabled"}
    )
    enable_operation = OwnedOperation(
        stage, "systemd-enabled:" + unit, enable_identity
    )

    def observe_enabled() -> str | None:
        return enable_identity if state()["UnitFileState"] == "enabled" else None

    def create_enabled() -> None:
        runner(reload_argv)
        runner(enable_argv)

    enabled_action = SystemAction(
        operation=enable_operation,
        observe_identity=observe_enabled,
        create_exact=create_enabled,
        remove_exact=lambda _identity: runner(disable_argv),
    )
    if not start_active:
        return (enabled_action,)

    active_identity = _semantic_identity(
        {"kind": "systemd-active-state", "unit": unit, "state": "active"}
    )
    active_operation = OwnedOperation(
        stage, "systemd-active:" + unit, active_identity
    )
    active_action = SystemAction(
        operation=active_operation,
        observe_identity=lambda: (
            active_identity if state()["ActiveState"] == "active" else None
        ),
        create_exact=lambda: runner(start_argv),
        remove_exact=lambda _identity: runner(stop_argv),
    )
    return enabled_action, active_action


class LinuxBackend:
    """Crash-reconciling executor; approval locking remains installer-owned."""

    def __init__(self, *, adapter: OwnedAdapter, ledger: MutationLedger) -> None:
        self.adapter = adapter
        self.ledger = ledger

    @staticmethod
    def _validate_operations(operations: Iterable[OwnedOperation]) -> tuple[OwnedOperation, ...]:
        result = tuple(operations)
        objects = [operation.owned_object for operation in result]
        if not result or len(objects) != len(set(objects)):
            raise BackendError("owned operation sequence invalid")
        return result

    def apply(self, operations: Iterable[OwnedOperation]) -> None:
        for operation in self._validate_operations(operations):
            if operation.owned_object not in self.ledger.allowed_objects:
                raise BackendError("owned operation outside ledger allowlist")
            event = self.ledger.event_for(operation.owned_object)
            if event is None:
                if self.adapter.observe(operation) is not None:
                    raise BackendError("pre-existing owned-object collision")
                self.ledger.intent(
                    operation.stage, operation.owned_object, operation.desired_identity
                )
                event = self.ledger.event_for(operation.owned_object)
            if event is None:
                raise BackendError("ledger intent not observable")
            if event["stage"] != operation.stage or event["desired_identity"] != operation.desired_identity:
                raise BackendError("owned operation disagrees with retained ledger")
            if event["event"] == "intent":
                pending_observer = getattr(self.adapter, "observe_pending", None)
                actual = (
                    pending_observer(operation)
                    if callable(pending_observer)
                    else self.adapter.observe(operation)
                )
                if actual is None:
                    self.adapter.create(operation)
                    actual = self.adapter.observe(operation)
                if actual != operation.desired_identity:
                    raise BackendError("owned object post-mutation identity drift")
                self.ledger.commit(operation.stage, operation.owned_object, actual)
            elif event["event"] == "committed":
                if self.adapter.observe(operation) != event["actual_identity"]:
                    raise BackendError("committed owned-object identity drift")
            elif event["event"] in {"removed", "abandoned"}:
                raise BackendError("cannot reapply retained removed object")
            else:
                raise BackendError("unknown retained ledger state")

    def rollback(self, operations: Iterable[OwnedOperation]) -> None:
        validated = self._validate_operations(operations)
        ingress = tuple(
            operation for operation in validated
            if operation.stage == "network"
            or operation.owned_object == "network-contour:amn2-spain"
        )
        remainder = tuple(operation for operation in validated if operation not in ingress)
        rollback_order = (*reversed(ingress), *reversed(remainder))
        for operation in rollback_order:
            event = self.ledger.event_for(operation.owned_object)
            if event is None or event["event"] in {"removed", "abandoned"}:
                continue
            if event["stage"] != operation.stage or event["desired_identity"] != operation.desired_identity:
                raise BackendError("rollback operation disagrees with retained ledger")
            rollback_observer = getattr(self.adapter, "observe_rollback", None)
            actual = (
                rollback_observer(operation)
                if callable(rollback_observer)
                else self.adapter.observe(operation)
            )
            if event["event"] == "intent":
                if actual is None:
                    self.ledger.abandon(operation.stage, operation.owned_object)
                    continue
                if actual != operation.desired_identity:
                    raise BackendError("pending owned-object identity drift")
                # A crash after syscall but before commit is deterministically adopted,
                # then removed through the same CAS path.
                self.ledger.commit(operation.stage, operation.owned_object, actual)
                event = self.ledger.event_for(operation.owned_object)
            if event is None or event["event"] != "committed":
                raise BackendError("rollback retained ledger state invalid")
            expected = event["actual_identity"]
            if actual is None:
                # A crash after successful removal but before the ledger append.
                reconcile_absent = getattr(
                    self.adapter, "reconcile_absent_remove", None
                )
                if callable(reconcile_absent):
                    reconcile_absent(operation, expected)
                self.ledger.removed(operation.stage, operation.owned_object, expected)
                continue
            if actual != expected:
                raise BackendError("committed owned-object identity drift")
            self.adapter.remove(operation, expected)
            if self.adapter.observe(operation) is not None:
                raise BackendError("owned-object rollback not observable")
            self.ledger.removed(operation.stage, operation.owned_object, expected)


def build_docker_network_argv() -> tuple[str, ...]:
    return (
        DOCKER,
        "-H",
        DOCKER_SOCKET,
        "network",
        "create",
        "--driver",
        "bridge",
        "--subnet",
        "172.29.251.0/28",
        "--gateway",
        "172.29.251.1",
        "--opt",
        "com.docker.network.bridge.name=amn2spbr0",
        "amn2-spain-net",
    )


class _DigestingFdReader:
    """Small-chunk reader that binds streamed tar bytes to one open file."""

    def __init__(self, descriptor: int) -> None:
        self.descriptor = descriptor
        self.digest = hashlib.sha256()
        self.count = 0

    def read(self, size: int = -1) -> bytes:
        bound = 1024 * 1024 if size is None or size < 0 else min(size, 1024 * 1024)
        chunk = os.read(self.descriptor, bound)
        self.digest.update(chunk)
        self.count += len(chunk)
        return chunk


def _open_bound_regular_archive(
    path: Path, *, expected_sha256: str, expected_size: int, maximum_size: int
) -> tuple[int, os.stat_result]:
    path = Path(path)
    if (
        not isinstance(expected_sha256, str)
        or len(expected_sha256) != 64
        or any(character not in "0123456789abcdef" for character in expected_sha256)
        or not isinstance(expected_size, int)
        or not 0 < expected_size <= maximum_size
    ):
        raise BackendError("archive checksum/size boundary invalid")
    try:
        if path.is_symlink():
            raise BackendError("archive symlink rejected")
        descriptor = os.open(
            path,
            os.O_RDONLY
            | getattr(os, "O_NOFOLLOW", 0)
            | getattr(os, "O_BINARY", 0),
        )
    except BackendError:
        raise
    except OSError as exc:
        raise BackendError("archive nofollow open failed") from exc
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_size != expected_size:
            raise BackendError("archive regular-file/size boundary invalid")
        return descriptor, info
    except Exception:
        os.close(descriptor)
        raise


def _same_regular_file(before: os.stat_result, after: os.stat_result) -> bool:
    return (
        stat.S_ISREG(after.st_mode)
        and (
            before.st_dev,
            before.st_ino,
            before.st_size,
            before.st_mtime_ns,
        )
        == (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
        )
    )


def _plan_static_docker_archive(
    archive_path: Path, *, expected_sha256: str, expected_size: int
) -> dict[str, dict[str, Any]]:
    from scripts import phase12_spain_package as package

    descriptor, before = _open_bound_regular_archive(
        archive_path,
        expected_sha256=expected_sha256,
        expected_size=expected_size,
        maximum_size=MAX_STATIC_DOCKER_ARCHIVE_BYTES,
    )
    try:
        with os.fdopen(os.dup(descriptor), "rb", closefd=True) as stream:
            package._validate_docker_bundle(stream)
        os.lseek(descriptor, 0, os.SEEK_SET)
        inventory: dict[str, dict[str, Any]] = {}
        with os.fdopen(os.dup(descriptor), "rb", closefd=True) as stream:
            with tarfile.open(fileobj=stream, mode="r:*") as archive:
                for member in archive.getmembers():
                    name = PurePosixPath(member.name).as_posix()
                    if not name.startswith("docker/") or member.isdir():
                        continue
                    binary_name = PurePosixPath(name).name
                    if binary_name not in {
                        PurePosixPath(value).name for value in STATIC_DOCKER_RELATIVE_PATHS
                    }:
                        continue
                    if stat.S_IMODE(member.mode) != 0o755:
                        raise BackendError("static Docker archive binary mode mismatch")
                    source = archive.extractfile(member)
                    if source is None:
                        raise BackendError("static Docker binary unreadable")
                    digest = hashlib.sha256()
                    size = 0
                    while chunk := source.read(1024 * 1024):
                        digest.update(chunk)
                        size += len(chunk)
                    inventory[binary_name] = {
                        "sha256": digest.hexdigest(),
                        "size": size,
                    }
        expected_names = {
            PurePosixPath(value).name for value in STATIC_DOCKER_RELATIVE_PATHS
        }
        if set(inventory) != expected_names:
            raise BackendError("static Docker inventory mismatch")
        os.lseek(descriptor, 0, os.SEEK_SET)
        digest = hashlib.sha256()
        count = 0
        while chunk := os.read(descriptor, 1024 * 1024):
            digest.update(chunk)
            count += len(chunk)
        after = os.fstat(descriptor)
        if (
            count != expected_size
            or digest.hexdigest() != expected_sha256
            or not _same_regular_file(before, after)
        ):
            raise BackendError("static Docker archive checksum/stability mismatch")
        return inventory
    except BackendError:
        raise
    except Exception as exc:
        raise BackendError("static Docker archive planning failed") from exc
    finally:
        os.close(descriptor)


def _hash_open_regular(descriptor: int) -> tuple[int, str]:
    before = os.fstat(descriptor)
    if not stat.S_ISREG(before.st_mode):
        raise BackendError("static Docker binary type drift")
    digest = hashlib.sha256()
    size = 0
    while chunk := os.read(descriptor, 1024 * 1024):
        digest.update(chunk)
        size += len(chunk)
    after = os.fstat(descriptor)
    if not _same_regular_file(before, after):
        raise BackendError("static Docker binary changed during observation")
    return size, digest.hexdigest()


def _static_docker_tree_state(
    fs: SafeFs, inventory: Mapping[str, Mapping[str, Any]]
) -> str:
    """Return absent/partial/full; raise on any foreign or drifted object."""

    expected_names = set(inventory)
    if os.name == "nt":
        parent = fs._path("opt/amn2-spain", allow_missing_leaf=False)
        docker_dir = parent / "docker"
        if not docker_dir.exists() and not docker_dir.is_symlink():
            return "absent"
        if docker_dir.is_symlink() or not docker_dir.is_dir():
            raise BackendError("static Docker tree drift")
        docker_entries = {entry.name for entry in docker_dir.iterdir()}
        if not docker_entries:
            return "partial"
        if docker_entries != {"bin"}:
            raise BackendError("static Docker tree drift")
        bin_dir = docker_dir / "bin"
        if bin_dir.is_symlink() or not bin_dir.is_dir():
            raise BackendError("static Docker tree drift")
        names = {entry.name for entry in bin_dir.iterdir()}
        if not names <= expected_names:
            raise BackendError("static Docker tree drift")
        for name in names:
            path = bin_dir / name
            if path.is_symlink() or not path.is_file():
                raise BackendError("static Docker tree drift")
            digest = hashlib.sha256()
            size = 0
            with path.open("rb") as stream:
                while chunk := stream.read(1024 * 1024):
                    digest.update(chunk)
                    size += len(chunk)
            if (
                size != inventory[name]["size"]
                or digest.hexdigest() != inventory[name]["sha256"]
            ):
                raise BackendError("static Docker binary drift")
        return "full" if names == expected_names else "partial"

    parent_fd = fs._open_directory_parts(("opt", "amn2-spain"))
    try:
        try:
            docker_info = os.stat("docker", dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            return "absent"
        if not stat.S_ISDIR(docker_info.st_mode) or stat.S_IMODE(docker_info.st_mode) != 0o755:
            raise BackendError("static Docker tree drift")
        fs._verify_owner(docker_info)
        docker_fd = os.open(
            "docker",
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=parent_fd,
        )
        try:
            docker_names = set(os.listdir(docker_fd))
            if not docker_names:
                return "partial"
            if docker_names != {"bin"}:
                raise BackendError("static Docker tree drift")
            bin_info = os.stat("bin", dir_fd=docker_fd, follow_symlinks=False)
            if not stat.S_ISDIR(bin_info.st_mode) or stat.S_IMODE(bin_info.st_mode) != 0o755:
                raise BackendError("static Docker tree drift")
            fs._verify_owner(bin_info)
            bin_fd = os.open(
                "bin",
                os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=docker_fd,
            )
            try:
                names = set(os.listdir(bin_fd))
                if not names <= expected_names:
                    raise BackendError("static Docker tree drift")
                for name in names:
                    info = os.stat(name, dir_fd=bin_fd, follow_symlinks=False)
                    if not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) != 0o755:
                        raise BackendError("static Docker binary mode/type drift")
                    fs._verify_owner(info)
                    file_fd = os.open(
                        name,
                        os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
                        dir_fd=bin_fd,
                    )
                    try:
                        size, digest = _hash_open_regular(file_fd)
                    finally:
                        os.close(file_fd)
                    if (
                        size != inventory[name]["size"]
                        or digest != inventory[name]["sha256"]
                    ):
                        raise BackendError("static Docker binary drift")
                return "full" if names == expected_names else "partial"
            finally:
                os.close(bin_fd)
        finally:
            os.close(docker_fd)
    finally:
        os.close(parent_fd)


def _ensure_static_docker_directories(fs: SafeFs) -> None:
    if os.name == "nt":
        parent = fs._path("opt/amn2-spain", allow_missing_leaf=False)
        (parent / "docker").mkdir(mode=0o755, exist_ok=True)
        (parent / "docker" / "bin").mkdir(mode=0o755, exist_ok=True)
        return
    parent_fd = fs._open_directory_parts(("opt", "amn2-spain"))
    try:
        try:
            os.mkdir("docker", 0o755, dir_fd=parent_fd)
        except FileExistsError:
            pass
        docker_fd = os.open(
            "docker",
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=parent_fd,
        )
        try:
            os.fchmod(docker_fd, 0o755)
            if fs.expected_uid is not None or fs.expected_gid is not None:
                os.fchown(
                    docker_fd,
                    -1 if fs.expected_uid is None else fs.expected_uid,
                    -1 if fs.expected_gid is None else fs.expected_gid,
                )
            try:
                os.mkdir("bin", 0o755, dir_fd=docker_fd)
            except FileExistsError:
                pass
            bin_fd = os.open(
                "bin",
                os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=docker_fd,
            )
            try:
                os.fchmod(bin_fd, 0o755)
                if fs.expected_uid is not None or fs.expected_gid is not None:
                    os.fchown(
                        bin_fd,
                        -1 if fs.expected_uid is None else fs.expected_uid,
                        -1 if fs.expected_gid is None else fs.expected_gid,
                    )
                os.fsync(bin_fd)
            finally:
                os.close(bin_fd)
            os.fsync(docker_fd)
        finally:
            os.close(docker_fd)
        os.fsync(parent_fd)
    finally:
        os.close(parent_fd)


def _install_static_docker_stream(
    fs: SafeFs,
    archive_path: Path,
    *,
    expected_sha256: str,
    expected_size: int,
    inventory: Mapping[str, Mapping[str, Any]],
) -> None:
    descriptor, before = _open_bound_regular_archive(
        archive_path,
        expected_sha256=expected_sha256,
        expected_size=expected_size,
        maximum_size=MAX_STATIC_DOCKER_ARCHIVE_BYTES,
    )
    _ensure_static_docker_directories(fs)
    bin_path = fs._path("opt/amn2-spain/docker/bin", allow_missing_leaf=False)
    bin_fd = -1
    if os.name != "nt":
        bin_fd = fs._open_directory_parts(("opt", "amn2-spain", "docker", "bin"))
    reader = _DigestingFdReader(descriptor)
    seen: set[str] = set()
    all_names: set[str] = set()
    try:
        with tarfile.open(fileobj=reader, mode="r|*") as archive:
            for member in archive:
                name = PurePosixPath(member.name).as_posix()
                if name in all_names:
                    raise BackendError("static Docker archive duplicate member")
                all_names.add(name)
                if name == "docker":
                    if not member.isdir():
                        raise BackendError("static Docker archive member drift")
                    continue
                if name == "DOCKER-BUNDLE.json":
                    if not member.isfile():
                        raise BackendError("static Docker archive member drift")
                    source = archive.extractfile(member)
                    if source is None:
                        raise BackendError("static Docker metadata unreadable")
                    while source.read(64 * 1024):
                        pass
                    continue
                if not name.startswith("docker/") or not member.isfile():
                    raise BackendError("static Docker archive member drift")
                binary_name = PurePosixPath(name).name
                if (
                    binary_name not in inventory
                    or binary_name in seen
                    or stat.S_IMODE(member.mode) != 0o755
                ):
                    raise BackendError("static Docker archive inventory drift")
                seen.add(binary_name)
                source = archive.extractfile(member)
                if source is None:
                    raise BackendError("static Docker binary unreadable")
                output_fd = -1
                try:
                    if os.name == "nt":
                        target = bin_path / binary_name
                        if not target.exists():
                            output_fd = os.open(
                                target,
                                os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0),
                                0o755,
                            )
                    else:
                        try:
                            output_fd = os.open(
                                binary_name,
                                os.O_WRONLY | os.O_CREAT | os.O_EXCL
                                | getattr(os, "O_NOFOLLOW", 0),
                                0o755,
                                dir_fd=bin_fd,
                            )
                        except FileExistsError:
                            output_fd = -1
                    digest = hashlib.sha256()
                    size = 0
                    while chunk := source.read(1024 * 1024):
                        digest.update(chunk)
                        size += len(chunk)
                        if output_fd >= 0:
                            offset = 0
                            while offset < len(chunk):
                                written = os.write(output_fd, chunk[offset:])
                                if written <= 0:
                                    raise BackendError("static Docker binary short write")
                                offset += written
                    if (
                        size != inventory[binary_name]["size"]
                        or digest.hexdigest() != inventory[binary_name]["sha256"]
                    ):
                        raise BackendError("static Docker source binary drift")
                    if output_fd >= 0:
                        if os.name != "nt":
                            os.fchmod(output_fd, 0o755)
                            if fs.expected_uid is not None or fs.expected_gid is not None:
                                os.fchown(
                                    output_fd,
                                    -1 if fs.expected_uid is None else fs.expected_uid,
                                    -1 if fs.expected_gid is None else fs.expected_gid,
                                )
                        os.fsync(output_fd)
                finally:
                    if output_fd >= 0:
                        os.close(output_fd)
        while reader.read(1024 * 1024):
            pass
        after = os.fstat(descriptor)
        if (
            seen != set(inventory)
            or reader.count != expected_size
            or reader.digest.hexdigest() != expected_sha256
            or not _same_regular_file(before, after)
        ):
            raise BackendError("static Docker streamed archive identity mismatch")
        if bin_fd >= 0:
            os.fsync(bin_fd)
    except BackendError:
        raise
    except Exception as exc:
        raise BackendError("static Docker streamed install failed") from exc
    finally:
        if bin_fd >= 0:
            os.close(bin_fd)
        os.close(descriptor)


def _remove_static_docker_tree(
    fs: SafeFs, inventory: Mapping[str, Mapping[str, Any]]
) -> None:
    state = _static_docker_tree_state(fs, inventory)
    if state == "absent":
        return
    if os.name == "nt":
        docker_dir = fs._path("opt/amn2-spain/docker", allow_missing_leaf=False)
        bin_dir = docker_dir / "bin"
        if bin_dir.exists():
            for name in sorted(inventory):
                path = bin_dir / name
                if path.exists():
                    path.unlink()
            bin_dir.rmdir()
        docker_dir.rmdir()
        return
    parent_fd = fs._open_directory_parts(("opt", "amn2-spain"))
    try:
        docker_fd = os.open(
            "docker",
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=parent_fd,
        )
        try:
            if "bin" in os.listdir(docker_fd):
                bin_fd = os.open(
                    "bin",
                    os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                    | getattr(os, "O_NOFOLLOW", 0),
                    dir_fd=docker_fd,
                )
                try:
                    for name in sorted(inventory):
                        try:
                            os.unlink(name, dir_fd=bin_fd)
                        except FileNotFoundError:
                            pass
                    os.fsync(bin_fd)
                finally:
                    os.close(bin_fd)
                os.rmdir("bin", dir_fd=docker_fd)
            os.fsync(docker_fd)
        finally:
            os.close(docker_fd)
        os.rmdir("docker", dir_fd=parent_fd)
        os.fsync(parent_fd)
    finally:
        os.close(parent_fd)


def build_static_docker_action(
    *,
    fs: SafeFs,
    archive_path: Path,
    expected_sha256: str,
    expected_size: int,
    stage: str = "filesystem_staged",
) -> SystemAction:
    if not isinstance(fs, SafeFs) or not isinstance(stage, str) or not stage:
        raise BackendError("static Docker action boundary invalid")
    inventory = _plan_static_docker_archive(
        Path(archive_path),
        expected_sha256=expected_sha256,
        expected_size=expected_size,
    )
    desired = _semantic_identity(
        {
            "kind": "static-docker-runtime",
            "archive_sha256": expected_sha256,
            "archive_size": expected_size,
            "mode": "0755",
            "inventory": {
                name: dict(inventory[name]) for name in sorted(inventory)
            },
        }
    )
    operation = OwnedOperation(stage, "runtime:docker-static", desired)

    def observe() -> str | None:
        state = _static_docker_tree_state(fs, inventory)
        if state == "absent":
            return None
        if state == "full":
            return desired
        return _semantic_identity({"kind": "static-docker-partial-collision"})

    def observe_pending() -> str | None:
        state = _static_docker_tree_state(fs, inventory)
        return desired if state == "full" else None

    def observe_rollback() -> str | None:
        state = _static_docker_tree_state(fs, inventory)
        return None if state == "absent" else desired

    def create() -> None:
        state = _static_docker_tree_state(fs, inventory)
        if state == "full":
            return
        _install_static_docker_stream(
            fs,
            Path(archive_path),
            expected_sha256=expected_sha256,
            expected_size=expected_size,
            inventory=inventory,
        )
        if _static_docker_tree_state(fs, inventory) != "full":
            raise BackendError("static Docker post-install drift")

    def remove(identity: str) -> None:
        if identity != desired:
            raise BackendError("static Docker CAS identity drift")
        _remove_static_docker_tree(fs, inventory)

    return SystemAction(
        operation=operation,
        observe_identity=observe,
        observe_pending_identity=observe_pending,
        observe_rollback_identity=observe_rollback,
        create_exact=create,
        remove_exact=remove,
        reconcile_absent_removal=True,
    )


_DEFAULT_REPO_TAGS = object()


def verify_loaded_awg_image(
    value: Any, *, expected_repo_tags: Any = _DEFAULT_REPO_TAGS
) -> str:
    repo_tags = (
        [AWG_LOCAL_IMAGE_TAG]
        if expected_repo_tags is _DEFAULT_REPO_TAGS
        else expected_repo_tags
    )
    if (
        not isinstance(value, dict)
        or set(value) != {"Id", "Architecture", "Os", "RepoTags"}
        or value["Id"] != AWG_IMAGE_CONFIG_DIGEST
        or value["Architecture"] != "amd64"
        or value["Os"] != "linux"
        or value["RepoTags"] != repo_tags
    ):
        raise BackendError("loaded AWG image identity mismatch")
    return AWG_IMAGE_CONFIG_DIGEST


def build_container_create_argv() -> tuple[str, ...]:
    return (
        DOCKER,
        "-H",
        DOCKER_SOCKET,
        "create",
        "--name",
        "amn2-spain-awg",
        "--network",
        "amn2-spain-net",
        "--ip",
        "172.29.251.2",
        "--read-only",
        "--cap-drop",
        "ALL",
        "--cap-add",
        "NET_ADMIN",
        "--device",
        "/dev/net/tun",
        "--tmpfs",
        "/run:rw,noexec,nosuid,nodev,size=16m",
        "--mount",
        "type=bind,src=/etc/amn2-spain/awgsp0.conf,dst=/etc/amnezia/amneziawg/awgsp0.conf,readonly",
        "--mount",
        "type=bind,src=/opt/amn2-spain/runtime/awg-start.sh,dst=/usr/local/sbin/amn2-awg-start,readonly",
        "--restart",
        "unless-stopped",
        "--entrypoint",
        "/usr/local/sbin/amn2-awg-start",
        AWG_LOCAL_IMAGE_TAG,
    )


_DOCKER_BASE = (DOCKER, "-H", DOCKER_SOCKET)
_IMAGE_LIST_FORMAT = '{"ID":{{json .ID}},"Repository":{{json .Repository}},"Tag":{{json .Tag}}}'
_IMAGE_INSPECT_FORMAT = (
    '{"Architecture":{{json .Architecture}},"Id":{{json .Id}},'
    '"Os":{{json .Os}},"RepoTags":{{json .RepoTags}}}'
)
_NETWORK_LIST_FORMAT = '{"ID":{{json .ID}},"Name":{{json .Name}}}'
_NETWORK_INSPECT_FORMAT = (
    '{"Attachable":{{json .Attachable}},"Containers":{{json .Containers}},'
    '"Driver":{{json .Driver}},"Gateway":{{json (index .IPAM.Config 0).Gateway}},'
    '"ID":{{json .Id}},'
    '"Ingress":{{json .Ingress}},"Internal":{{json .Internal}},'
    '"Name":{{json .Name}},"Scope":{{json .Scope}},'
    '"Subnet":{{json (index .IPAM.Config 0).Subnet}},'
    '"Bridge":{{json (index .Options "com.docker.network.bridge.name")}}}'
)
_CONTAINER_LIST_FORMAT = '{"ID":{{json .ID}},"Names":{{json .Names}}}'
_CONTAINER_INSPECT_FORMAT = (
    '{"CapAdd":{{json .HostConfig.CapAdd}},"CapDrop":{{json .HostConfig.CapDrop}},'
    '"ConfigImage":{{json .Config.Image}},"Devices":{{json .HostConfig.Devices}},'
    '"Entrypoint":{{json .Config.Entrypoint}},"ID":{{json .Id}},"Image":{{json .Image}},'
    '"Mounts":{{json .Mounts}},"Name":{{json .Name}},'
    '"NetworkEndpointID":{{json (index .NetworkSettings.Networks "amn2-spain-net").EndpointID}},'
    '"NetworkIPAddress":{{json (index .NetworkSettings.Networks "amn2-spain-net").IPAddress}},'
    '"ReadonlyRootfs":{{json .HostConfig.ReadonlyRootfs}},'
    '"RestartCount":{{json .RestartCount}},'
    '"RestartName":{{json .HostConfig.RestartPolicy.Name}},'
    '"Running":{{json .State.Running}},'
    '"TmpfsRun":{{json (index .HostConfig.Tmpfs "/run")}}}'
)
DOCKER_IMAGE_LIST_ARGV = (*_DOCKER_BASE, "image", "ls", "--all", "--no-trunc", "--format", _IMAGE_LIST_FORMAT)
DOCKER_IMAGE_INSPECT_TAG_ARGV = (
    *_DOCKER_BASE, "image", "inspect", "--format", _IMAGE_INSPECT_FORMAT, AWG_LOCAL_IMAGE_TAG,
)
DOCKER_IMAGE_INSPECT_ID_ARGV = (
    *_DOCKER_BASE, "image", "inspect", "--format", _IMAGE_INSPECT_FORMAT,
    AWG_IMAGE_CONFIG_DIGEST,
)
DOCKER_IMAGE_LOAD_ARGV = (*_DOCKER_BASE, "image", "load")
DOCKER_IMAGE_TAG_ARGV = (
    *_DOCKER_BASE, "image", "tag", AWG_IMAGE_CONFIG_DIGEST, AWG_LOCAL_IMAGE_TAG,
)
DOCKER_IMAGE_RM_TAG_ARGV = (*_DOCKER_BASE, "image", "rm", AWG_LOCAL_IMAGE_TAG)
DOCKER_IMAGE_RM_ID_ARGV = (*_DOCKER_BASE, "image", "rm", AWG_IMAGE_CONFIG_DIGEST)
DOCKER_NETWORK_LIST_ARGV = (
    *_DOCKER_BASE, "network", "ls", "--no-trunc", "--format", _NETWORK_LIST_FORMAT,
)
DOCKER_NETWORK_INSPECT_ARGV = (
    *_DOCKER_BASE, "network", "inspect", "--format", _NETWORK_INSPECT_FORMAT,
    "amn2-spain-net",
)
DOCKER_NETWORK_RM_ARGV = (*_DOCKER_BASE, "network", "rm", "amn2-spain-net")
DOCKER_CONTAINER_LIST_ARGV = (
    *_DOCKER_BASE, "container", "ls", "--all", "--no-trunc", "--format",
    _CONTAINER_LIST_FORMAT,
)
DOCKER_CONTAINER_INSPECT_ARGV = (
    *_DOCKER_BASE, "container", "inspect", "--format", _CONTAINER_INSPECT_FORMAT,
    "amn2-spain-awg",
)
DOCKER_CONTAINER_START_ARGV = (*_DOCKER_BASE, "container", "start", "amn2-spain-awg")
DOCKER_CONTAINER_STOP_ARGV = (*_DOCKER_BASE, "container", "stop", "amn2-spain-awg")
DOCKER_CONTAINER_RM_ARGV = (*_DOCKER_BASE, "container", "rm", "amn2-spain-awg")
DOCKER_ZERO_PEER_ARGV = (
    *_DOCKER_BASE, "container", "exec", "amn2-spain-awg",
    "awg", "show", "awgsp0", "peers",
)
DOCKER_LISTEN_PORT_ARGV = (
    *_DOCKER_BASE, "container", "exec", "amn2-spain-awg",
    "awg", "show", "awgsp0", "listen-port",
)
DOCKER_COMMAND_ALLOWLIST = frozenset(
    {
        DOCKER_IMAGE_LIST_ARGV,
        DOCKER_IMAGE_INSPECT_TAG_ARGV,
        DOCKER_IMAGE_INSPECT_ID_ARGV,
        DOCKER_IMAGE_LOAD_ARGV,
        DOCKER_IMAGE_TAG_ARGV,
        DOCKER_IMAGE_RM_TAG_ARGV,
        DOCKER_IMAGE_RM_ID_ARGV,
        DOCKER_NETWORK_LIST_ARGV,
        DOCKER_NETWORK_INSPECT_ARGV,
        build_docker_network_argv(),
        DOCKER_NETWORK_RM_ARGV,
        DOCKER_CONTAINER_LIST_ARGV,
        DOCKER_CONTAINER_INSPECT_ARGV,
        build_container_create_argv(),
        DOCKER_CONTAINER_START_ARGV,
        DOCKER_CONTAINER_STOP_ARGV,
        DOCKER_CONTAINER_RM_ARGV,
        DOCKER_ZERO_PEER_ARGV,
        DOCKER_LISTEN_PORT_ARGV,
    }
)


def _docker_json_lines(
    payload: bytes, *, keys: set[str], label: str
) -> list[dict[str, Any]]:
    if not isinstance(payload, bytes) or len(payload) > MAX_COMMAND_OUTPUT:
        raise BackendError(f"Docker {label} observation invalid")
    rows: list[dict[str, Any]] = []
    try:
        text = payload.decode("utf-8")
        for line in text.splitlines():
            if not line:
                continue
            value = json.loads(line)
            if not isinstance(value, dict) or set(value) != keys:
                raise BackendError(f"Docker {label} observation invalid")
            rows.append(value)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BackendError(f"Docker {label} observation invalid") from exc
    if len(rows) > 4096:
        raise BackendError(f"Docker {label} observation invalid")
    return rows


def _closed_docker_runner(
    runner: Callable[..., bytes],
) -> Callable[..., bytes]:
    if not callable(runner):
        raise BackendError("Docker runner invalid")

    def run(argv: tuple[str, ...], **kwargs: Any) -> bytes:
        if argv not in DOCKER_COMMAND_ALLOWLIST:
            raise BackendError("Docker argv outside exact allowlist")
        allowed_kwargs = (
            {"input_fd", "input_size", "timeout"}
            if argv == DOCKER_IMAGE_LOAD_ARGV else set()
        )
        if set(kwargs) - allowed_kwargs:
            raise BackendError("Docker command boundary invalid")
        try:
            result = runner(argv, **kwargs)
        except BackendError as exc:
            if argv == DOCKER_IMAGE_LOAD_ARGV:
                raise BackendError(_bounded_docker_image_load_failure_label(exc)) from None
            raise BackendError("Docker command failed") from None
        except Exception:
            if argv == DOCKER_IMAGE_LOAD_ARGV:
                raise BackendError("docker_image_load_command_failed") from None
            raise BackendError("Docker command failed") from None
        if not isinstance(result, bytes) or len(result) > MAX_COMMAND_OUTPUT:
            raise BackendError("Docker command output invalid")
        return result

    return run


def _docker_one_json(payload: bytes, *, keys: set[str], label: str) -> dict[str, Any]:
    rows = _docker_json_lines(payload, keys=keys, label=label)
    if len(rows) != 1:
        raise BackendError(f"Docker {label} observation invalid")
    return rows[0]


def _docker_image_state(runner: Callable[..., bytes]) -> str:
    rows = _docker_json_lines(
        runner(DOCKER_IMAGE_LIST_ARGV),
        keys={"ID", "Repository", "Tag"},
        label="image list",
    )
    if len(rows) > 1 or any(
        not all(isinstance(row[key], str) for key in row) for row in rows
    ):
        raise BackendError("Docker image list ambiguity")
    if not rows:
        return "absent"
    row = rows[0]
    if row["ID"] != AWG_IMAGE_CONFIG_DIGEST:
        raise BackendError("Docker image closed-delta drift")
    if row["Repository"] == "amn2-spain-awg" and row["Tag"] == "phase12":
        observation = _docker_one_json(
            runner(DOCKER_IMAGE_INSPECT_TAG_ARGV),
            keys={"Architecture", "Id", "Os", "RepoTags"},
            label="image inspect",
        )
        verify_loaded_awg_image(observation)
        return "full"
    if row["Repository"] == "<none>" and row["Tag"] == "<none>":
        observation = _docker_one_json(
            runner(DOCKER_IMAGE_INSPECT_ID_ARGV),
            keys={"Architecture", "Id", "Os", "RepoTags"},
            label="image inspect",
        )
        repo_tags = observation["RepoTags"]
        if repo_tags not in (None, []):
            raise BackendError("Docker untagged image has foreign tags")
        verify_loaded_awg_image(observation, expected_repo_tags=repo_tags)
        return "partial"
    raise BackendError("Docker image tag closed-delta drift")


def _read_small_tar_member(
    archive: tarfile.TarFile, member: tarfile.TarInfo, label: str
) -> bytes:
    if member.size > 1024 * 1024:
        raise BackendError(f"AWG image {label} oversized")
    source = archive.extractfile(member)
    if source is None:
        raise BackendError(f"AWG image {label} unreadable")
    payload = source.read(1024 * 1024 + 1)
    if len(payload) != member.size:
        raise BackendError(f"AWG image {label} truncated")
    return payload


def _validate_live_awg_archive_contract(
    archive_path: Path, *, expected_sha256: str, expected_size: int
) -> None:
    descriptor, before = _open_bound_regular_archive(
        archive_path,
        expected_sha256=expected_sha256,
        expected_size=expected_size,
        maximum_size=MAX_COMMAND_STREAM_INPUT,
    )
    try:
        with os.fdopen(os.dup(descriptor), "rb", closefd=True) as stream:
            with tarfile.open(fileobj=stream, mode="r:*") as archive:
                members: dict[str, tarfile.TarInfo] = {}
                for member in archive.getmembers():
                    path = PurePosixPath(member.name)
                    name = path.as_posix()
                    if (
                        path.is_absolute()
                        or any(part in {"", ".", ".."} for part in path.parts)
                        or name in members
                        or not member.isfile()
                        or member.issym()
                        or member.islnk()
                    ):
                        raise BackendError("AWG image archive member drift")
                    members[name] = member
                for required in ("manifest.json", "repositories"):
                    if required not in members:
                        raise BackendError("AWG image archive manifest missing")
                try:
                    manifest = json.loads(
                        _read_small_tar_member(
                            archive, members["manifest.json"], "manifest"
                        ).decode("utf-8")
                    )
                    repositories = json.loads(
                        _read_small_tar_member(
                            archive, members["repositories"], "repositories"
                        ).decode("utf-8")
                    )
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise BackendError("AWG image archive JSON invalid") from exc
                config_name = AWG_IMAGE_CONFIG_DIGEST.removeprefix("sha256:") + ".json"
                layers = manifest[0]["Layers"] if isinstance(manifest, list) and manifest else None
                if (
                    not isinstance(manifest, list)
                    or len(manifest) != 1
                    or not isinstance(manifest[0], dict)
                    or set(manifest[0]) != {"Config", "RepoTags", "Layers"}
                    or manifest[0]["Config"] != config_name
                    or manifest[0]["RepoTags"] is not None
                    or not isinstance(layers, list)
                    or not layers
                    or any(not isinstance(layer, str) for layer in layers)
                    or len(layers) != len(set(layers))
                    or config_name in layers
                    or repositories != {}
                    or config_name not in members
                    or any(
                        layer not in members
                        for layer in layers
                    )
                ):
                    raise BackendError("AWG image untagged manifest contract mismatch")
                try:
                    config_raw = _read_small_tar_member(
                        archive, members[config_name], "config"
                    )
                    config = json.loads(config_raw.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise BackendError("AWG image config JSON invalid") from exc
                if (
                    not isinstance(config, dict)
                    or config.get("architecture") != "amd64"
                    or config.get("os") != "linux"
                    or "sha256:" + hashlib.sha256(config_raw).hexdigest()
                    != AWG_IMAGE_CONFIG_DIGEST
                ):
                    raise BackendError("AWG image config platform mismatch")
        os.lseek(descriptor, 0, os.SEEK_SET)
        digest = hashlib.sha256()
        count = 0
        while chunk := os.read(descriptor, 1024 * 1024):
            digest.update(chunk)
            count += len(chunk)
        after = os.fstat(descriptor)
        if (
            count != expected_size
            or digest.hexdigest() != expected_sha256
            or not _same_regular_file(before, after)
        ):
            raise BackendError("AWG image archive checksum/stability mismatch")
    except BackendError:
        raise
    except (OSError, tarfile.TarError) as exc:
        raise BackendError("AWG image archive invalid") from exc
    finally:
        os.close(descriptor)


def _load_bound_awg_image(
    runner: Callable[..., bytes],
    archive_path: Path,
    *,
    expected_sha256: str,
    expected_size: int,
) -> None:
    descriptor, before = _open_bound_regular_archive(
        archive_path,
        expected_sha256=expected_sha256,
        expected_size=expected_size,
        maximum_size=MAX_COMMAND_STREAM_INPUT,
    )
    try:
        digest = hashlib.sha256()
        count = 0
        while chunk := os.read(descriptor, 1024 * 1024):
            digest.update(chunk)
            count += len(chunk)
        if count != expected_size or digest.hexdigest() != expected_sha256:
            raise BackendError("AWG image archive checksum mismatch")
        os.lseek(descriptor, 0, os.SEEK_SET)
        runner(
            DOCKER_IMAGE_LOAD_ARGV,
            input_fd=descriptor,
            input_size=expected_size,
            timeout=120.0,
        )
        after = os.fstat(descriptor)
        if not _same_regular_file(before, after):
            raise BackendError("AWG image archive changed during load")
    finally:
        os.close(descriptor)


def build_awg_image_action(
    *,
    runner: Callable[..., bytes],
    archive_path: Path,
    expected_sha256: str,
    expected_size: int,
    stage: str = "awg_image_loaded",
) -> SystemAction:
    runner = _closed_docker_runner(runner)
    if (
        not isinstance(expected_sha256, str)
        or len(expected_sha256) != 64
        or any(character not in "0123456789abcdef" for character in expected_sha256)
        or not isinstance(expected_size, int)
        or not 0 < expected_size <= MAX_COMMAND_STREAM_INPUT
    ):
        raise BackendError("AWG image archive boundary invalid")
    _validate_live_awg_archive_contract(
        Path(archive_path),
        expected_sha256=expected_sha256,
        expected_size=expected_size,
    )
    desired = _semantic_identity(
        {
            "kind": "docker-image",
            "config_digest": AWG_IMAGE_CONFIG_DIGEST,
            "platform_digest": AWG_IMAGE_PLATFORM_DIGEST,
            "local_tag": AWG_LOCAL_IMAGE_TAG,
            "archive_sha256": expected_sha256,
            "archive_size": expected_size,
        }
    )
    operation = OwnedOperation(stage, "image:" + AWG_IMAGE_CONFIG_DIGEST, desired)

    def observe() -> str | None:
        state = _docker_image_state(runner)
        if state == "absent":
            return None
        if state == "full":
            return desired
        return _semantic_identity({"kind": "docker-image-partial-collision"})

    def observe_pending() -> str | None:
        return desired if _docker_image_state(runner) == "full" else None

    def observe_rollback() -> str | None:
        return None if _docker_image_state(runner) == "absent" else desired

    def create() -> None:
        try:
            state = _docker_image_state(runner)
            if state == "absent":
                _load_bound_awg_image(
                    runner,
                    Path(archive_path),
                    expected_sha256=expected_sha256,
                    expected_size=expected_size,
                )
                state = _docker_image_state(runner)
            if state == "partial":
                runner(DOCKER_IMAGE_TAG_ARGV)
            if _docker_image_state(runner) != "full":
                raise BackendError("Docker image post-create drift")
        except BackendError as exc:
            # The outer install/rollback path exposes only this allowlisted
            # Docker-load classification.  It must also cover post-load state
            # validation and tagging, not just the `docker image load` argv.
            raise BackendError(_bounded_docker_image_load_failure_label(exc)) from exc

    def remove(identity: str) -> None:
        if identity != desired:
            raise BackendError("Docker image rollback CAS drift")
        state = _docker_image_state(runner)
        if state == "full":
            runner(DOCKER_IMAGE_RM_TAG_ARGV)
            state = _docker_image_state(runner)
        if state == "partial":
            runner(DOCKER_IMAGE_RM_ID_ARGV)
        if _docker_image_state(runner) != "absent":
            raise BackendError("Docker image rollback drift")

    return SystemAction(
        operation=operation,
        observe_identity=observe,
        observe_pending_identity=observe_pending,
        observe_rollback_identity=observe_rollback,
        create_exact=create,
        remove_exact=remove,
        reconcile_absent_removal=True,
    )


def _valid_dynamic_endpoint(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _docker_network_state(
    runner: Callable[..., bytes],
) -> tuple[str, str | None, str | None, str | None]:
    rows = _docker_json_lines(
        runner(DOCKER_NETWORK_LIST_ARGV),
        keys={"ID", "Name"},
        label="network list",
    )
    matches = [row for row in rows if row["Name"] == "amn2-spain-net"]
    names = [row["Name"] for row in rows]
    # dockerd's sealed config uses bridge=none, so only the built-in host/none
    # networks exist before our explicit bridge network is created.
    if (
        any(
            not isinstance(row["ID"], str) or not isinstance(row["Name"], str)
            for row in rows
        )
        or len(matches) > 1
        or len(names) != len(set(names))
        or set(names) not in ({"host", "none"}, {"host", "none", "amn2-spain-net"})
        or any(name not in {"host", "none", "amn2-spain-net"} for name in names)
        or any(not _valid_dynamic_endpoint(row["ID"]) for row in rows)
    ):
        raise BackendError("Docker network list ambiguity")
    if not matches:
        return "absent", None, None, None
    network_id = matches[0]["ID"]
    value = _docker_one_json(
        runner(DOCKER_NETWORK_INSPECT_ARGV),
        keys={
            "Attachable", "Bridge", "Containers", "Driver", "Gateway", "ID",
            "Ingress", "Internal", "Name", "Scope", "Subnet",
        },
        label="network inspect",
    )
    expected = {
        "Attachable": False,
        "Bridge": "amn2spbr0",
        "Driver": "bridge",
        "Gateway": "172.29.251.1",
        "ID": network_id,
        "Ingress": False,
        "Internal": False,
        "Name": "amn2-spain-net",
        "Scope": "local",
        "Subnet": "172.29.251.0/28",
    }
    if any(value[key] != expected[key] for key in expected):
        raise BackendError("Docker network topology drift")
    containers = value["Containers"]
    if not isinstance(containers, dict) or len(containers) > 1:
        raise BackendError("Docker network membership drift")
    endpoint_id: str | None = None
    container_id: str | None = None
    if containers:
        container_id, endpoint = next(iter(containers.items()))
        if (
            not isinstance(container_id, str)
            or not isinstance(endpoint, dict)
            or set(endpoint)
            != {"Name", "EndpointID", "MacAddress", "IPv4Address", "IPv6Address"}
            or endpoint["Name"] != "amn2-spain-awg"
            or endpoint["IPv4Address"] != "172.29.251.2/28"
            or endpoint["IPv6Address"] != ""
            or not isinstance(endpoint["MacAddress"], str)
            or not endpoint["MacAddress"]
            or not _valid_dynamic_endpoint(endpoint["EndpointID"])
        ):
            raise BackendError("Docker network membership drift")
        endpoint_id = endpoint["EndpointID"]
    return "full", endpoint_id, container_id, network_id


def build_docker_network_action(
    *, runner: Callable[..., bytes], stage: str = "network_container_started"
) -> SystemAction:
    runner = _closed_docker_runner(runner)
    desired = _semantic_identity(
        {
            "kind": "docker-network",
            "name": "amn2-spain-net",
            "driver": "bridge",
            "bridge": "amn2spbr0",
            "subnet": "172.29.251.0/28",
            "gateway": "172.29.251.1",
            "dynamic_fields": ["container_id", "endpoint_id", "mac_address"],
        }
    )
    operation = OwnedOperation(stage, "network:amn2-spain-net", desired)

    def observe() -> str | None:
        state, _endpoint, _container_id, _network_id = _docker_network_state(runner)
        return desired if state == "full" else None

    def remove(identity: str) -> None:
        if identity != desired:
            raise BackendError("Docker network rollback CAS drift")
        state, endpoint, _container_id, _network_id = _docker_network_state(runner)
        if state == "absent":
            return
        if endpoint is not None:
            raise BackendError("Docker network still has container endpoint")
        runner(DOCKER_NETWORK_RM_ARGV)
        if _docker_network_state(runner)[0] != "absent":
            raise BackendError("Docker network rollback drift")

    def create() -> None:
        if _docker_network_state(runner)[0] == "full":
            return
        runner(build_docker_network_argv())
        if _docker_network_state(runner)[0] != "full":
            raise BackendError("Docker network post-create drift")

    return SystemAction(
        operation=operation,
        observe_identity=observe,
        create_exact=create,
        remove_exact=remove,
        reconcile_absent_removal=True,
    )


def _exact_mounts(value: Any) -> bool:
    if not isinstance(value, list) or len(value) != 2:
        return False
    expected = {
        (
            "/etc/amn2-spain/awgsp0.conf",
            "/etc/amnezia/amneziawg/awgsp0.conf",
        ),
        (
            "/opt/amn2-spain/runtime/awg-start.sh",
            "/usr/local/sbin/amn2-awg-start",
        ),
    }
    observed: set[tuple[str, str]] = set()
    for row in value:
        if (
            not isinstance(row, dict)
            or row.get("Type") != "bind"
            or row.get("RW") is not False
            or not isinstance(row.get("Source"), str)
            or not isinstance(row.get("Destination"), str)
        ):
            return False
        observed.add((row["Source"], row["Destination"]))
    return observed == expected


def _exact_tmpfs_run(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    parts = value.split(",")
    if len(parts) != len(set(parts)):
        return False
    flags = {part for part in parts if "=" not in part}
    values = dict(part.split("=", 1) for part in parts if "=" in part)
    return (
        flags == {"rw", "noexec", "nosuid", "nodev"}
        and set(values) == {"size"}
        and values["size"].lower() in {"16m", "16777216"}
    )


def _docker_container_state(
    runner: Callable[..., bytes],
) -> tuple[str, bool, str | None]:
    rows = _docker_json_lines(
        runner(DOCKER_CONTAINER_LIST_ARGV),
        keys={"ID", "Names"},
        label="container list",
    )
    matches = [row for row in rows if row["Names"] == "amn2-spain-awg"]
    if (
        len(rows) > 1
        or len(matches) != len(rows)
        or any(
            not _valid_dynamic_endpoint(row["ID"])
            or not isinstance(row["Names"], str)
            for row in rows
        )
    ):
        raise BackendError("Docker container list ambiguity")
    if not matches:
        return "absent", False, None
    value = _docker_one_json(
        runner(DOCKER_CONTAINER_INSPECT_ARGV),
        keys={
            "CapAdd", "CapDrop", "ConfigImage", "Devices", "Entrypoint", "ID",
            "Image", "Mounts", "Name", "NetworkEndpointID",
            "NetworkIPAddress", "ReadonlyRootfs", "RestartCount",
            "RestartName", "Running", "TmpfsRun",
        },
        label="container inspect",
    )
    devices = value["Devices"]
    listed_container_id = matches[0]["ID"]
    if (
        value["Name"] != "/amn2-spain-awg"
        or value["ID"] != listed_container_id
        or not _valid_dynamic_endpoint(value["ID"])
        or value["Image"] != AWG_IMAGE_CONFIG_DIGEST
        or value["ConfigImage"] != AWG_LOCAL_IMAGE_TAG
        or value["Entrypoint"] != ["/usr/local/sbin/amn2-awg-start"]
        or value["ReadonlyRootfs"] is not True
        or value["CapDrop"] != ["ALL"]
        or value["CapAdd"] != ["NET_ADMIN"]
        or not isinstance(devices, list)
        or len(devices) != 1
        or not isinstance(devices[0], dict)
        or devices[0].get("PathOnHost") != "/dev/net/tun"
        or devices[0].get("PathInContainer") != "/dev/net/tun"
        or devices[0].get("CgroupPermissions") != "rwm"
        or not _exact_tmpfs_run(value["TmpfsRun"])
        or value["RestartName"] != "unless-stopped"
        or value["NetworkIPAddress"] != "172.29.251.2"
        or not _valid_dynamic_endpoint(value["NetworkEndpointID"])
        or not isinstance(value["Running"], bool)
        or type(value["RestartCount"]) is not int
        or value["RestartCount"] != 0
        or not _exact_mounts(value["Mounts"])
    ):
        raise BackendError("Docker container contract drift")
    (
        network_state,
        network_endpoint,
        network_container_id,
        _network_id,
    ) = _docker_network_state(runner)
    if (
        network_state != "full"
        or network_endpoint is None
        or network_endpoint != value["NetworkEndpointID"]
        or network_container_id != value["ID"]
    ):
        raise BackendError("Docker dynamic endpoint membership drift")
    return "full", value["Running"], value["NetworkEndpointID"]


def _docker_container_rollback_state(
    runner: Callable[..., bytes],
) -> tuple[str, bool]:
    """Recognize an AMN2-owned partial container only for rollback.

    A crash during ``docker create`` may leave the dedicated AMN2 daemon with
    incomplete capability and network fields.  Forward installation keeps its
    complete contract strict; rollback may remove this partial object only
    after every immutable AMN2 ownership anchor still matches.
    """
    rows = _docker_json_lines(
        runner(DOCKER_CONTAINER_LIST_ARGV),
        keys={"ID", "Names"},
        label="container list",
    )
    matches = [row for row in rows if row["Names"] == "amn2-spain-awg"]
    if (
        len(rows) > 1
        or len(matches) != len(rows)
        or any(
            not _valid_dynamic_endpoint(row["ID"])
            or not isinstance(row["Names"], str)
            for row in rows
        )
    ):
        raise BackendError("Docker container rollback ownership drift")
    if not matches:
        return "absent", False
    value = _docker_one_json(
        runner(DOCKER_CONTAINER_INSPECT_ARGV),
        keys={
            "CapAdd", "CapDrop", "ConfigImage", "Devices", "Entrypoint", "ID",
            "Image", "Mounts", "Name", "NetworkEndpointID",
            "NetworkIPAddress", "ReadonlyRootfs", "RestartCount",
            "RestartName", "Running", "TmpfsRun",
        },
        label="container inspect",
    )
    devices = value["Devices"]
    listed_container_id = matches[0]["ID"]
    if (
        value["Name"] != "/amn2-spain-awg"
        or value["ID"] != listed_container_id
        or not _valid_dynamic_endpoint(value["ID"])
        or value["Image"] != AWG_IMAGE_CONFIG_DIGEST
        or value["ConfigImage"] != AWG_LOCAL_IMAGE_TAG
        or value["Entrypoint"] != ["/usr/local/sbin/amn2-awg-start"]
        or value["ReadonlyRootfs"] is not True
        or not isinstance(devices, list)
        or len(devices) != 1
        or not isinstance(devices[0], dict)
        or devices[0].get("PathOnHost") != "/dev/net/tun"
        or devices[0].get("PathInContainer") != "/dev/net/tun"
        or devices[0].get("CgroupPermissions") != "rwm"
        or not _exact_tmpfs_run(value["TmpfsRun"])
        or value["RestartName"] != "unless-stopped"
        or not isinstance(value["Running"], bool)
        or type(value["RestartCount"]) is not int
        or value["RestartCount"] != 0
        or not _exact_mounts(value["Mounts"])
    ):
        raise BackendError("Docker container rollback ownership drift")
    return "owned", value["Running"]


def build_awg_container_actions(
    *, runner: Callable[..., bytes], stage: str = "network_container_started"
) -> tuple[SystemAction, SystemAction]:
    runner = _closed_docker_runner(runner)
    container_desired = _semantic_identity(
        {
            "kind": "docker-container",
            "name": "amn2-spain-awg",
            "image_config": AWG_IMAGE_CONFIG_DIGEST,
            "image_tag": AWG_LOCAL_IMAGE_TAG,
            "network": "amn2-spain-net",
            "ip": "172.29.251.2",
            "read_only": True,
            "cap_add": ["NET_ADMIN"],
            "device": "/dev/net/tun",
            "dynamic_fields": ["container_id", "endpoint_id", "mac_address"],
        }
    )
    container_operation = OwnedOperation(
        stage, "container:amn2-spain-awg", container_desired
    )

    def observe_container() -> str | None:
        state, _running, _endpoint = _docker_container_state(runner)
        return container_desired if state == "full" else None

    def create_container() -> None:
        if _docker_container_state(runner)[0] == "full":
            return
        runner(build_container_create_argv())
        state, running, _endpoint = _docker_container_state(runner)
        if state != "full" or running:
            raise BackendError("Docker container create/start separation drift")

    def remove_container(identity: str) -> None:
        if identity != container_desired:
            raise BackendError("Docker container rollback CAS drift")
        state, running = _docker_container_rollback_state(runner)
        if state == "absent":
            return
        if running:
            runner(DOCKER_CONTAINER_STOP_ARGV)
        state, running = _docker_container_rollback_state(runner)
        if state != "owned" or running:
            raise BackendError("Docker container stop verification failed")
        runner(DOCKER_CONTAINER_RM_ARGV)
        if _docker_container_rollback_state(runner)[0] != "absent":
            raise BackendError("Docker container rollback drift")

    container_action = SystemAction(
        operation=container_operation,
        observe_identity=observe_container,
        observe_rollback_identity=lambda: (
            None
            if _docker_container_rollback_state(runner)[0] == "absent"
            else container_desired
        ),
        create_exact=create_container,
        remove_exact=remove_container,
        reconcile_absent_removal=True,
    )

    active_desired = _semantic_identity(
        {
            "kind": "awg-zero-peer-health",
            "container": "amn2-spain-awg",
            "interface": "awgsp0",
            "peer_count": 0,
            "restart_count": 0,
        }
    )
    active_operation = OwnedOperation(stage, "interface:awgsp0", active_desired)

    def observe_active() -> str | None:
        state, running, _endpoint = _docker_container_state(runner)
        if state == "absent" or not running:
            return None
        peers = runner(DOCKER_ZERO_PEER_ARGV)
        if not isinstance(peers, bytes) or peers.strip():
            raise BackendError("AWG zero-peer health drift")
        listen_port = runner(DOCKER_LISTEN_PORT_ARGV)
        if listen_port.strip() != b"30001":
            raise BackendError("AWG listen-port health drift")
        return active_desired

    def create_active() -> None:
        state, running, _endpoint = _docker_container_state(runner)
        if state != "full":
            raise BackendError("AWG container missing before start")
        if not running:
            runner(DOCKER_CONTAINER_START_ARGV)
        if observe_active() != active_desired:
            raise BackendError("AWG zero-peer start health failed")

    def remove_active(identity: str) -> None:
        if identity != active_desired:
            raise BackendError("AWG active rollback CAS drift")
        state, running, _endpoint = _docker_container_state(runner)
        if state == "absent":
            return
        if running:
            runner(DOCKER_CONTAINER_STOP_ARGV)
        state, running, _endpoint = _docker_container_state(runner)
        if state != "full" or running:
            raise BackendError("AWG container stop verification failed")

    active_action = SystemAction(
        operation=active_operation,
        observe_identity=observe_active,
        observe_rollback_identity=lambda: (
            None if _docker_container_state(runner)[0] == "absent" else active_desired
        ),
        create_exact=create_active,
        remove_exact=remove_active,
        reconcile_absent_removal=True,
    )
    return container_action, active_action


@dataclass(frozen=True, repr=False)
class ProductionDockerRuntimeBundle:
    actions: tuple[SystemAction, ...]
    logical_receipt: Mapping[str, str]
    command_allowlist: frozenset[tuple[str, ...]]
    dynamic_observation_fields: frozenset[str]

    def __post_init__(self) -> None:
        operations = tuple(action.operation for action in self.actions)
        if (
            len(operations) != 4
            or len({operation.owned_object for operation in operations}) != 4
            or set(self.logical_receipt)
            != {
                *(operation.owned_object for operation in operations),
                "socket:/run/amn2-spain-docker/docker.sock",
                "bridge:amn2spbr0",
                "listener:udp:30001",
                "endpoint:amn2-spain-awg@amn2-spain-net",
            }
            or self.command_allowlist != DOCKER_COMMAND_ALLOWLIST
            or self.dynamic_observation_fields
            != frozenset(
                {"container_id", "endpoint_id", "mac_address", "network_id"}
            )
        ):
            raise BackendError("production Docker runtime bundle schema mismatch")


def observe_dedicated_docker_socket(
    path: Path = Path("/run/amn2-spain-docker/docker.sock"),
) -> Mapping[str, Any]:
    path = Path(path)
    try:
        info = os.lstat(path)
    except OSError as exc:
        raise BackendError("dedicated Docker socket missing") from exc
    if (
        path.is_symlink()
        or not stat.S_ISSOCK(info.st_mode)
        or stat.S_IMODE(info.st_mode) != 0o660
        or not hasattr(info, "st_uid")
        or not hasattr(info, "st_gid")
        or info.st_uid != 0
        or info.st_gid != 0
    ):
        raise BackendError("dedicated Docker socket ownership/mode drift")
    return MappingProxyType(
        {
            "kind": "unix-socket",
            "path": "/run/amn2-spain-docker/docker.sock",
            "mode": "0660",
            "uid": 0,
            "gid": 0,
        }
    )


def _validated_socket_observation(value: Any) -> Mapping[str, Any]:
    expected = {
        "kind": "unix-socket",
        "path": "/run/amn2-spain-docker/docker.sock",
        "mode": "0660",
        "uid": 0,
        "gid": 0,
    }
    if not isinstance(value, Mapping) or dict(value) != expected:
        raise BackendError("dedicated Docker socket observation drift")
    return MappingProxyType(expected)


def build_production_docker_runtime_bundle(
    *,
    runner: Callable[..., bytes],
    image_archive_path: Path,
    image_archive_sha256: str,
    image_archive_size: int,
    socket_observer: Callable[[], Mapping[str, Any]] = observe_dedicated_docker_socket,
) -> ProductionDockerRuntimeBundle:
    if not callable(runner) or not callable(socket_observer):
        raise BackendError("production Docker runtime dependency invalid")

    def socket_guarded_runner(argv: tuple[str, ...], **kwargs: Any) -> bytes:
        _validated_socket_observation(socket_observer())
        return runner(argv, **kwargs)

    image_action = build_awg_image_action(
        runner=socket_guarded_runner,
        archive_path=Path(image_archive_path),
        expected_sha256=image_archive_sha256,
        expected_size=image_archive_size,
    )
    network_action = build_docker_network_action(runner=socket_guarded_runner)
    container_actions = build_awg_container_actions(runner=socket_guarded_runner)
    actions = (image_action, network_action, *container_actions)
    receipt = {
        action.operation.owned_object: action.operation.desired_identity
        for action in actions
    }
    receipt.update(
        {
            "socket:/run/amn2-spain-docker/docker.sock": _semantic_identity(
                dict(_validated_socket_observation(
                    {
                        "kind": "unix-socket",
                        "path": "/run/amn2-spain-docker/docker.sock",
                        "mode": "0660",
                        "uid": 0,
                        "gid": 0,
                    }
                ))
            ),
            "bridge:amn2spbr0": _semantic_identity(
                {
                    "kind": "docker-bridge",
                    "name": "amn2spbr0",
                    "network": "amn2-spain-net",
                }
            ),
            "listener:udp:30001": _semantic_identity(
                {
                    "kind": "awg-listener",
                    "interface": "awgsp0",
                    "protocol": "udp",
                    "port": 30001,
                }
            ),
            "endpoint:amn2-spain-awg@amn2-spain-net": _semantic_identity(
                {
                    "kind": "docker-endpoint-membership",
                    "container": "amn2-spain-awg",
                    "network": "amn2-spain-net",
                    "ip": "172.29.251.2",
                    "dynamic_fields": [
                        "container_id", "endpoint_id", "mac_address", "network_id",
                    ],
                }
            ),
        }
    )
    return ProductionDockerRuntimeBundle(
        actions=actions,
        logical_receipt=MappingProxyType(receipt),
        command_allowlist=DOCKER_COMMAND_ALLOWLIST,
        dynamic_observation_fields=frozenset(
            {"container_id", "endpoint_id", "mac_address", "network_id"}
        ),
    )


@dataclass(frozen=True, repr=False)
class ServerKeyMaterial:
    private_key: str = field(repr=False)
    public_key: str

    def __iter__(self) -> Iterator[str]:
        yield self.private_key
        yield self.public_key


def _load_authoritative_module(source_root: Path, relative: str, label: str) -> Any:
    root = Path(source_root)
    path = root / relative
    if root.is_symlink() or path.is_symlink() or not path.is_file():
        raise BackendError(f"authoritative {label} module missing")
    spec = importlib.util.spec_from_file_location(
        "_amn2_phase12_" + label + "_" + hashlib.sha256(str(path).encode()).hexdigest(), path
    )
    if spec is None or spec.loader is None:
        raise BackendError(f"authoritative {label} module cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    previous_bytecode_policy = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    except Exception as exc:
        raise BackendError(f"authoritative {label} import smoke failed") from exc
    finally:
        sys.dont_write_bytecode = previous_bytecode_policy
    return module


def generate_server_keypair(source_root: Path) -> ServerKeyMaterial:
    module = _load_authoritative_module(
        source_root, "app/vpn/amneziawg_v2/keys.py", "keys"
    )
    try:
        pair = module.generate_keypair()
        private_key = str(pair.private_key)
        public_key = str(pair.public_key)
    except Exception as exc:
        raise BackendError("authoritative X25519 key generation failed") from exc
    if len(private_key) != 44 or len(public_key) != 44 or private_key == public_key:
        raise BackendError("authoritative X25519 key material invalid")
    return ServerKeyMaterial(private_key=private_key, public_key=public_key)


@dataclass(frozen=True, repr=False)
class RuntimeSecretSeeds:
    telegram_bot_token: str = field(repr=False)
    app_secret_key: str = field(repr=False)
    web_admin_session_secret: str = field(repr=False)


def generate_runtime_secrets(
    token_factory: Callable[[int], str] = secrets.token_urlsafe,
) -> RuntimeSecretSeeds:
    if not callable(token_factory):
        raise BackendError("runtime secret factory invalid")
    return RuntimeSecretSeeds(
        telegram_bot_token=_safe_generated_secret(token_factory(48)),
        app_secret_key=_safe_generated_secret(token_factory(48)),
        web_admin_session_secret=_safe_generated_secret(token_factory(48)),
    )


def initialize_clean_database(source_root: Path, database_path: Path) -> dict[str, Any]:
    path = Path(database_path)
    if path.exists() or path.is_symlink():
        raise BackendError("clean database path collision")
    connection_module = _load_authoritative_module(
        source_root, "app/db/connection.py", "connection"
    )
    schema_module = _load_authoritative_module(source_root, "app/db/schema.py", "schema")
    connection = None
    try:
        connection = connection_module.connect(path)
        schema_module.initialize_schema(connection)
        connection.commit()
        foreign_keys = int(connection.execute("PRAGMA foreign_keys").fetchone()[0])
        integrity = str(connection.execute("PRAGMA integrity_check").fetchone()[0])
        violations = [tuple(row) for row in connection.execute("PRAGMA foreign_key_check")]
        tables = [
            str(row[0])
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
        ]
        nonempty: dict[str, int] = {}
        for table in tables:
            if not table.replace("_", "").isalnum():
                raise BackendError("authoritative database table name invalid")
            count = int(connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0])
            if count:
                nonempty[table] = count
    except BackendError:
        raise
    except Exception as exc:
        raise BackendError("authoritative clean database initialization failed") from exc
    finally:
        if connection is not None:
            connection.close()
    if os.name != "nt":
        os.chmod(path, 0o600, follow_symlinks=False)
        if stat.S_IMODE(os.lstat(path).st_mode) != 0o600:
            raise BackendError("clean database mode mismatch")
    if foreign_keys != 1 or integrity != "ok" or violations or nonempty or not tables:
        raise BackendError("clean database invariant mismatch")
    return {
        "integrity_check": integrity,
        "foreign_key_check": violations,
        "foreign_keys": foreign_keys,
        "application_table_count": len(tables),
        "nonempty_tables": nonempty,
    }


def source_tree_identity(source_root: Path) -> str:
    root = Path(source_root)
    plan = _scan_tree(root)
    if plan is None or _tree_root_mode(root) != "0755":
        raise BackendError("authoritative source tree identity unavailable")
    return "sha256:" + plan["tree_sha256"]


def _sqlite_schema_projection(connection: Any) -> dict[str, Any]:
    objects: list[dict[str, str]] = []
    for row in connection.execute(
        "SELECT type, name, tbl_name, sql FROM sqlite_master "
        "WHERE name NOT LIKE 'sqlite_%' "
        "ORDER BY type, name, tbl_name, sql"
    ):
        if len(row) != 4 or not all(isinstance(value, str) for value in row):
            raise BackendError("authoritative database schema projection invalid")
        objects.append(
            {"type": row[0], "name": row[1], "tbl_name": row[2], "sql": row[3]}
        )
    if not any(item["type"] == "table" for item in objects):
        raise BackendError("authoritative database schema has no application tables")
    return {
        "objects": objects,
        "pragmas": {
            "application_id": int(
                connection.execute("PRAGMA application_id").fetchone()[0]
            ),
            "user_version": int(
                connection.execute("PRAGMA user_version").fetchone()[0]
            ),
        },
    }


def _authoritative_clean_database_schema_identity(source_root: Path) -> str:
    connection_module = _load_authoritative_module(
        source_root, "app/db/connection.py", "connection_schema_projection"
    )
    schema_module = _load_authoritative_module(
        source_root, "app/db/schema.py", "schema_projection"
    )
    connection = None
    try:
        connection = connection_module.connect(":memory:")
        schema_module.initialize_schema(connection)
        connection.commit()
        projection = _sqlite_schema_projection(connection)
    except BackendError:
        raise
    except Exception as exc:
        raise BackendError("authoritative database schema projection failed") from exc
    finally:
        if connection is not None:
            connection.close()
    return _digest(_canonical(projection))


def _database_file_identity(info: os.stat_result) -> dict[str, int]:
    return {
        "dev": int(info.st_dev),
        "ino": int(info.st_ino),
        "size": int(info.st_size),
        "mtime_ns": int(info.st_mtime_ns),
        "mode": int(stat.S_IMODE(info.st_mode)),
        "uid": int(getattr(info, "st_uid", 0)),
        "gid": int(getattr(info, "st_gid", 0)),
    }


def _inspect_clean_database_content(
    source_root: Path,
    database_path: Path,
    *,
    expected_schema_identity: str | None = None,
) -> dict[str, Any]:
    path = Path(database_path)
    if path.is_symlink() or not path.is_file():
        raise BackendError("clean database path/type mismatch")
    before = os.lstat(path)
    if not stat.S_ISREG(before.st_mode):
        raise BackendError("clean database path/type mismatch")
    connection_module = _load_authoritative_module(
        source_root, "app/db/connection.py", "connection_observer"
    )
    if not callable(getattr(connection_module, "connect_read_only", None)):
        raise BackendError("authoritative read-only database connector missing")
    connection = None
    try:
        connection = connection_module.connect_read_only(path)
        foreign_keys = int(connection.execute("PRAGMA foreign_keys").fetchone()[0])
        query_only = int(connection.execute("PRAGMA query_only").fetchone()[0])
        integrity = str(connection.execute("PRAGMA integrity_check").fetchone()[0])
        violations = [tuple(row) for row in connection.execute("PRAGMA foreign_key_check")]
        schema_projection = _sqlite_schema_projection(connection)
        schema_identity = _digest(_canonical(schema_projection))
        tables = [
            str(row[0])
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
        ]
        nonempty: dict[str, int] = {}
        for table in tables:
            if not table.replace("_", "").isalnum():
                raise BackendError("authoritative database table name invalid")
            count = int(connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0])
            if count:
                nonempty[table] = count
    except BackendError:
        raise
    except Exception as exc:
        raise BackendError("clean database observation failed") from exc
    finally:
        if connection is not None:
            connection.close()
    after = os.lstat(path)
    if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
        after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns
    ):
        raise BackendError("clean database changed during read-only observation")
    if (
        foreign_keys != 1
        or query_only != 1
        or integrity != "ok"
        or violations
        or nonempty
        or not tables
    ):
        raise BackendError("clean database content collision/drift")
    if expected_schema_identity is not None and schema_identity != expected_schema_identity:
        raise BackendError("clean database schema collision/drift")
    return {
        "integrity_check": integrity,
        "foreign_key_check": violations,
        "foreign_keys": foreign_keys,
        "query_only": query_only,
        "application_table_count": len(tables),
        "nonempty_tables": nonempty,
        "schema_identity": schema_identity,
        "file_identity": _database_file_identity(after),
    }


def _observe_clean_database(
    source_root: Path,
    database_path: Path,
    *,
    expected_uid: int | None,
    expected_gid: int | None,
) -> dict[str, Any]:
    path = Path(database_path)
    if path.is_symlink() or not path.is_file():
        raise BackendError("clean database path/type mismatch")
    info = os.lstat(path)
    if (
        not stat.S_ISREG(info.st_mode)
        or (
            os.name != "nt"
            and (
                stat.S_IMODE(info.st_mode) != 0o600
                or (expected_uid is not None and info.st_uid != expected_uid)
                or (expected_gid is not None and info.st_gid != expected_gid)
            )
        )
    ):
        raise BackendError("clean database owner/mode mismatch")
    return _inspect_clean_database_content(source_root, path)


def build_clean_database_action(
    source_root: Path,
    database_path: Path,
    *,
    expected_uid: int | None = 61212,
    expected_gid: int | None = 61212,
) -> SystemAction:
    path = Path(database_path)
    if not path.is_absolute() or path.parent.is_symlink() or not path.parent.is_dir():
        raise BackendError("clean database action path invalid")
    desired = _semantic_identity(
        {
            "kind": "amn2.spain-clean-database.v1",
            "foreign_keys": 1,
            "integrity_check": "ok",
            "application_tables": "all-zero",
            "mode": "0600",
            "uid": expected_uid,
            "gid": expected_gid,
        }
    )
    operation = OwnedOperation(
        "database", "database:" + path.as_posix(), desired
    )

    def observe() -> str | None:
        if not path.exists() and not path.is_symlink():
            return None
        _observe_clean_database(
            source_root,
            path,
            expected_uid=expected_uid,
            expected_gid=expected_gid,
        )
        return desired

    def create() -> None:
        initialize_clean_database(source_root, path)
        if os.name != "nt" and (expected_uid is not None or expected_gid is not None):
            os.chown(
                path,
                -1 if expected_uid is None else expected_uid,
                -1 if expected_gid is None else expected_gid,
                follow_symlinks=False,
            )
        if observe() != desired:
            raise BackendError("clean database post-create identity mismatch")

    def remove(identity: str) -> None:
        if identity != desired or observe() != desired:
            raise BackendError("clean database CAS identity drift")
        try:
            os.unlink(path)
        except OSError as exc:
            raise BackendError("clean database rollback failed") from exc

    return SystemAction(
        operation=operation,
        observe_identity=observe,
        create_exact=create,
        remove_exact=remove,
    )


def build_production_clean_database_action(
    *,
    source_root: Path,
    expected_source_tree_identity: str,
    database_path: Path,
    expected_uid: int | None = 61212,
    expected_gid: int | None = 61212,
) -> SystemAction:
    source = Path(source_root)
    path = Path(database_path)
    if (
        not MutationLedger._valid_identity(expected_source_tree_identity)
        or source_tree_identity(source) != expected_source_tree_identity
        or not path.is_absolute()
        or path.parent.is_symlink()
        or not path.parent.is_dir()
    ):
        raise BackendError("production clean database source/path binding invalid")
    expected_schema_identity = _authoritative_clean_database_schema_identity(source)
    parent_info = os.lstat(path.parent)
    if not stat.S_ISDIR(parent_info.st_mode):
        raise BackendError("production clean database parent invalid")
    protected_parent_identity = {
        "dev": int(parent_info.st_dev),
        "ino": int(parent_info.st_ino),
        "mode": int(stat.S_IMODE(parent_info.st_mode)),
        "uid": int(getattr(parent_info, "st_uid", 0)),
        "gid": int(getattr(parent_info, "st_gid", 0)),
    }
    desired = _semantic_identity(
        {
            "kind": "amn2.spain-clean-database.v3",
            "source_tree_identity": expected_source_tree_identity,
            "schema_projection_identity": expected_schema_identity,
            "foreign_keys": 1,
            "integrity_check": "ok",
            "foreign_key_check": [],
            "application_tables": "all-zero",
            "mode": "0600",
            "uid": expected_uid,
            "gid": expected_gid,
        }
    )
    operation = OwnedOperation(
        "clean_db_initialized", "database:" + path.as_posix(), desired
    )

    def source_exact() -> None:
        if source_tree_identity(source) != expected_source_tree_identity:
            raise BackendError("authoritative source tree identity drift")

    def parent_exact() -> None:
        try:
            info = os.lstat(path.parent)
        except OSError as exc:
            raise BackendError("clean database protected parent drift") from exc
        actual = {
            "dev": int(info.st_dev),
            "ino": int(info.st_ino),
            "mode": int(stat.S_IMODE(info.st_mode)),
            "uid": int(getattr(info, "st_uid", 0)),
            "gid": int(getattr(info, "st_gid", 0)),
        }
        if not stat.S_ISDIR(info.st_mode) or actual != protected_parent_identity:
            raise BackendError("clean database protected parent drift")

    def metadata_exact(file_identity: Mapping[str, int]) -> bool:
        return (
            os.name == "nt"
            or (
                file_identity["mode"] == 0o600
                and (expected_uid is None or file_identity["uid"] == expected_uid)
                and (expected_gid is None or file_identity["gid"] == expected_gid)
            )
        )

    def state_with_observation(
        *, pending: bool
    ) -> tuple[str | None, dict[str, Any] | None]:
        source_exact()
        parent_exact()
        if not path.exists() and not path.is_symlink():
            return None, None
        try:
            observation = _inspect_clean_database_content(
                source, path, expected_schema_identity=expected_schema_identity
            )
        except BackendError as exc:
            raise BackendError("clean database content collision/drift") from exc
        if metadata_exact(observation["file_identity"]):
            return desired, observation
        if pending:
            return None, observation
        return (
            _digest(
                _canonical(
                    {
                        "kind": "clean-database-metadata-collision",
                        "path": path.as_posix(),
                    }
                )
            ),
            observation,
        )

    def state(*, pending: bool) -> str | None:
        return state_with_observation(pending=pending)[0]

    def create() -> None:
        source_exact()
        if not path.exists() and not path.is_symlink():
            initialize_clean_database(source, path)
        else:
            _inspect_clean_database_content(
                source, path, expected_schema_identity=expected_schema_identity
            )
        if os.name != "nt":
            if expected_uid is not None or expected_gid is not None:
                os.chown(
                    path,
                    -1 if expected_uid is None else expected_uid,
                    -1 if expected_gid is None else expected_gid,
                    follow_symlinks=False,
                )
            os.chmod(path, 0o600, follow_symlinks=False)
        if state(pending=True) != desired:
            raise BackendError("clean database post-create identity mismatch")

    def remove(identity: str) -> None:
        observed_state, observation = state_with_observation(pending=False)
        if identity != desired or observed_state != desired or observation is None:
            raise BackendError("clean database rollback CAS drift")
        try:
            if os.name != "nt":
                parent_descriptor = _tree_parent_fd(path)
                try:
                    current_parent = os.fstat(parent_descriptor)
                    current_parent_identity = {
                        "dev": int(current_parent.st_dev),
                        "ino": int(current_parent.st_ino),
                        "mode": int(stat.S_IMODE(current_parent.st_mode)),
                        "uid": int(getattr(current_parent, "st_uid", 0)),
                        "gid": int(getattr(current_parent, "st_gid", 0)),
                    }
                    if current_parent_identity != protected_parent_identity:
                        raise BackendError("clean database protected parent drift")
                    descriptor = os.open(
                        path.name,
                        os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
                        | getattr(os, "O_BINARY", 0),
                        dir_fd=parent_descriptor,
                    )
                    try:
                        opened_identity = _database_file_identity(os.fstat(descriptor))
                        if opened_identity != observation["file_identity"]:
                            raise BackendError("clean database rollback file swap/drift")
                        named_identity = _database_file_identity(
                            os.stat(path.name, dir_fd=parent_descriptor, follow_symlinks=False)
                        )
                        if named_identity != opened_identity:
                            raise BackendError("clean database rollback file swap/drift")
                        os.unlink(path.name, dir_fd=parent_descriptor)
                    finally:
                        os.close(descriptor)
                    os.fsync(parent_descriptor)
                finally:
                    os.close(parent_descriptor)
            else:
                parent_exact()
                if _database_file_identity(os.lstat(path)) != observation["file_identity"]:
                    raise BackendError("clean database rollback file swap/drift")
                os.unlink(path)
        except BackendError:
            raise
        except OSError as exc:
            raise BackendError("clean database rollback failed") from exc

    return SystemAction(
        operation=operation,
        observe_identity=lambda: state(pending=False),
        observe_pending_identity=lambda: state(pending=True),
        create_exact=create,
        remove_exact=remove,
    )


def plan_production_clean_database_operation(
    *,
    source_root: Path,
    expected_source_tree_identity: str,
    database_path: Path,
    expected_uid: int | None = 61212,
    expected_gid: int | None = 61212,
) -> OwnedOperation:
    source = Path(source_root)
    path = Path(database_path)
    if (
        not MutationLedger._valid_identity(expected_source_tree_identity)
        or source_tree_identity(source) != expected_source_tree_identity
        or not path.is_absolute()
        or path.is_symlink()
        or any(
            value is not None
            and (
                not isinstance(value, int)
                or isinstance(value, bool)
                or value < 0
            )
            for value in (expected_uid, expected_gid)
        )
    ):
        raise BackendError("production clean database operation plan invalid")
    expected_schema_identity = _authoritative_clean_database_schema_identity(source)
    desired = _semantic_identity(
        {
            "kind": "amn2.spain-clean-database.v3",
            "source_tree_identity": expected_source_tree_identity,
            "schema_projection_identity": expected_schema_identity,
            "foreign_keys": 1,
            "integrity_check": "ok",
            "foreign_key_check": [],
            "application_tables": "all-zero",
            "mode": "0600",
            "uid": expected_uid,
            "gid": expected_gid,
        }
    )
    return OwnedOperation(
        "clean_db_initialized",
        "database:" + path.as_posix(),
        desired,
    )


def build_deferred_production_clean_database_action(
    *,
    source_root: Path,
    expected_source_tree_identity: str,
    database_path: Path,
    expected_uid: int | None = 61212,
    expected_gid: int | None = 61212,
) -> SystemAction:
    """Seal the operation now; bind parent inode callbacks after filesystem stage."""
    operation = plan_production_clean_database_operation(
        source_root=source_root,
        expected_source_tree_identity=expected_source_tree_identity,
        database_path=database_path,
        expected_uid=expected_uid,
        expected_gid=expected_gid,
    )
    bound: SystemAction | None = None

    def action() -> SystemAction:
        nonlocal bound
        if bound is None:
            candidate = build_production_clean_database_action(
                source_root=source_root,
                expected_source_tree_identity=expected_source_tree_identity,
                database_path=database_path,
                expected_uid=expected_uid,
                expected_gid=expected_gid,
            )
            if candidate.operation != operation:
                raise BackendError("deferred clean database operation drift")
            bound = candidate
        return bound

    return SystemAction(
        operation=operation,
        observe_identity=lambda: action().observe_identity(),
        observe_pending_identity=lambda: (
            action().observe_pending_identity or action().observe_identity
        )(),
        observe_rollback_identity=lambda: (
            action().observe_rollback_identity or action().observe_identity
        )(),
        create_exact=lambda: action().create_exact(),
        remove_exact=lambda identity: action().remove_exact(identity),
    )


def _read_template(name: str, *, template_root: Path | None = None) -> str:
    path = (TEMPLATE_ROOT if template_root is None else Path(template_root)) / name
    if path.is_symlink() or not path.is_file():
        raise BackendError("runtime template missing")
    return path.read_text(encoding="utf-8")


def render_awg_config(
    private_key: str, *, template_root: Path | None = None
) -> str:
    if not isinstance(private_key, str) or len(private_key) != 44 or "\n" in private_key:
        raise BackendError("server private key invalid")
    template = _read_template("awgsp0.conf", template_root=template_root)
    marker = "__AMN2_GENERATED_SERVER_PRIVATE_KEY__"
    if template.count(marker) != 1:
        raise BackendError("AWG private-key marker mismatch")
    rendered = template.replace(marker, private_key)
    if "[Peer]" in rendered:
        raise BackendError("fresh AWG config must contain zero peers")
    return rendered


def render_servers_yml(
    *,
    endpoint_host: str,
    public_key: str,
    template_root: Path | None = None,
) -> str:
    if (
        not isinstance(endpoint_host, str)
        or not endpoint_host
        or any(char in endpoint_host for char in "\r\n\t ")
        or not isinstance(public_key, str)
        or len(public_key) != 44
        or "\n" in public_key
    ):
        raise BackendError("servers.yml runtime value invalid")
    template = _read_template("servers.yml", template_root=template_root)
    markers = {
        "__AMN2_SPAIN_ENDPOINT_HOST__": (endpoint_host, 2),
        "__AMN2_GENERATED_SERVER_PUBLIC_KEY__": (public_key, 1),
    }
    for marker, (replacement, expected_count) in markers.items():
        if template.count(marker) != expected_count:
            raise BackendError("servers.yml marker mismatch")
        template = template.replace(marker, replacement)
    if "__AMN2_" in template:
        raise BackendError("servers.yml unresolved marker")
    return template


@dataclass(frozen=True, repr=False)
class RuntimeSecretMaterial:
    telegram_bot_token: str = field(repr=False)
    app_secret_key: str = field(repr=False)
    web_admin_session_secret: str = field(repr=False)
    web_admin_password_hash: str = field(repr=False)


@dataclass(frozen=True, repr=False)
class ProductionFilesystemBundle:
    actions: tuple[SystemAction, ...]
    logical_receipt: Mapping[str, str]

    def __post_init__(self) -> None:
        operations = tuple(action.operation for action in self.actions)
        if (
            not operations
            or len({operation.owned_object for operation in operations}) != len(operations)
            or set(self.logical_receipt)
            != {operation.owned_object for operation in operations}
            or any(
                self.logical_receipt[operation.owned_object]
                != operation.desired_identity
                for operation in operations
            )
        ):
            raise BackendError("production filesystem bundle schema mismatch")


@dataclass(frozen=True, repr=False)
class PreparedProductionFilesystemPayloads:
    source_tree_identity: str
    endpoint_host: str
    rendered_payloads: Mapping[str, bytes] = field(repr=False)
    package_bound_payloads: Mapping[str, bytes] = field(repr=False)

    def __post_init__(self) -> None:
        if (
            not MutationLedger._valid_identity(self.source_tree_identity)
            or not isinstance(self.endpoint_host, str)
            or not self.endpoint_host
            or set(self.rendered_payloads)
            != {
                "etc/amn2-spain/runtime.env",
                "etc/amn2-spain/awgsp0.conf",
                "etc/amn2-spain/servers.yml",
                "etc/amn2-spain/docker-daemon.json",
                "opt/amn2-spain/runtime/awg-start.sh",
            }
            or set(self.package_bound_payloads)
            != {
                "opt/amn2-spain/current/scripts/phase12_spain_network.py",
                "opt/amn2-spain/current/packaging/phase12-spain/templates/nftables.conf",
            }
            or any(
                not isinstance(payload, bytes) or not payload
                for payload in (
                    *self.rendered_payloads.values(),
                    *self.package_bound_payloads.values(),
                )
            )
        ):
            raise BackendError("prepared production filesystem payloads invalid")


def _safe_generated_secret(value: Any) -> str:
    if (
        not isinstance(value, str)
        or len(value) < 32
        or any(character in value for character in "\x00\r\n")
    ):
        raise BackendError("generated runtime secret invalid")
    return value


def _render_exact_markers(
    template_name: str,
    replacements: Mapping[str, str],
    *,
    template_root: Path | None = None,
) -> str:
    rendered = _read_template(template_name, template_root=template_root)
    if "\r" in rendered or not rendered.endswith("\n") or rendered.endswith("\n\n"):
        raise BackendError("runtime template line-ending contract invalid")
    for marker, replacement in replacements.items():
        if (
            not isinstance(marker, str)
            or not marker.startswith("__AMN2_")
            or rendered.count(marker) != 1
            or not isinstance(replacement, str)
            or not replacement
            or any(character in replacement for character in "\x00\r\n")
        ):
            raise BackendError("runtime template marker contract invalid")
        rendered = rendered.replace(marker, replacement)
    if "__AMN2_" in rendered or "\r" in rendered:
        raise BackendError("runtime template unresolved marker")
    return rendered


def _runtime_env_mapping(rendered: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in rendered.splitlines():
        if not line or "=" not in line:
            raise BackendError("runtime environment format invalid")
        key, value = line.split("=", maxsplit=1)
        if (
            not key
            or key in values
            or not key.replace("_", "").isalnum()
            or key != key.upper()
            or any(character in value for character in "\x00\r\n")
        ):
            raise BackendError("runtime environment format invalid")
        values[key] = value
    return values


def _validate_authoritative_runtime_settings(
    source_root: Path, runtime_values: Mapping[str, str]
) -> None:
    root = Path(source_root)
    if root.is_symlink() or not root.is_dir() or not isinstance(runtime_values, Mapping):
        raise BackendError("authoritative runtime Settings validation failed")
    saved_modules = {
        name: module
        for name, module in tuple(sys.modules.items())
        if name == "app" or name.startswith("app.")
    }
    original_path = list(sys.path)
    previous_bytecode_policy = sys.dont_write_bytecode
    try:
        for name in saved_modules:
            sys.modules.pop(name, None)
        sys.path.insert(0, str(root))
        sys.dont_write_bytecode = True
        module = importlib.import_module("app.config.settings")
        settings = module.Settings(_env_file=None, **dict(runtime_values))
        if (
            settings.vps_apply_enabled is not False
            or settings.web_admin_enabled is not True
            or settings.web_admin_host != "127.0.0.1"
            or settings.web_admin_port != 3031
            or settings.vpn_server_runtime != "docker"
            or settings.server_name != "spain"
        ):
            raise BackendError("authoritative runtime Settings invariant mismatch")
    except BackendError:
        raise
    except Exception as exc:
        raise BackendError("authoritative runtime Settings validation failed") from exc
    finally:
        for name in tuple(sys.modules):
            if name == "app" or name.startswith("app."):
                sys.modules.pop(name, None)
        sys.modules.update(saved_modules)
        sys.path[:] = original_path
        sys.dont_write_bytecode = previous_bytecode_policy


def _read_package_bound_bytes(
    relative: str,
    *,
    content_root: Path | None = None,
    max_bytes: int = 2 * 1024 * 1024,
) -> bytes:
    path = (ROOT if content_root is None else Path(content_root)) / relative
    try:
        info = os.lstat(path)
        if path.is_symlink() or not stat.S_ISREG(info.st_mode) or not 0 < info.st_size <= max_bytes:
            raise BackendError("package-bound runtime artifact invalid")
        descriptor = os.open(
            path,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0),
        )
        try:
            before = os.fstat(descriptor)
            chunks: list[bytes] = []
            remaining = max_bytes + 1
            while remaining > 0:
                chunk = os.read(descriptor, min(1024 * 1024, remaining))
                if not chunk:
                    break
                chunks.append(chunk)
                remaining -= len(chunk)
            payload = b"".join(chunks)
            after = os.fstat(descriptor)
        finally:
            os.close(descriptor)
    except BackendError:
        raise
    except OSError as exc:
        raise BackendError("package-bound runtime artifact unavailable") from exc
    if (
        not payload
        or len(payload) > max_bytes
        or (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
        != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
    ):
        raise BackendError("package-bound runtime artifact changed during read")
    return payload


def prepare_production_filesystem_payloads(
    *,
    source_root: Path,
    endpoint_host: str,
    secret_token_factory: Callable[[int], str] = secrets.token_urlsafe,
    package_content_root: Path | None = None,
) -> PreparedProductionFilesystemPayloads:
    """Generate and validate payloads without requiring future install parents."""
    source = Path(source_root)
    if not callable(secret_token_factory):
        raise BackendError("runtime secret factory invalid")
    try:
        seed_material = generate_runtime_secrets(secret_token_factory)
        temporary_password = _safe_generated_secret(secret_token_factory(48))
        key_material = generate_server_keypair(source)
        auth_module = _load_authoritative_module(source, "app/web/auth.py", "web_auth")
        password_hash = str(auth_module.create_password_hash(temporary_password))
        temporary_password = ""
        del temporary_password
        auth_module.require_web_admin_config(
            password_hash=password_hash,
            session_secret=seed_material.web_admin_session_secret,
        )
    except BackendError:
        raise
    except Exception as exc:
        raise BackendError("authoritative runtime credential preparation failed") from exc
    material = RuntimeSecretMaterial(
        telegram_bot_token=seed_material.telegram_bot_token,
        app_secret_key=seed_material.app_secret_key,
        web_admin_session_secret=seed_material.web_admin_session_secret,
        web_admin_password_hash=password_hash,
    )
    del seed_material
    content = None if package_content_root is None else Path(package_content_root)
    template_root = None if content is None else content / "templates"
    package_template_prefix = (
        "packaging/phase12-spain/templates" if content is None else "templates"
    )
    runtime_env = _render_exact_markers(
        "runtime.env",
        {
            "__AMN2_GENERATED_TELEGRAM_BOT_TOKEN__": material.telegram_bot_token,
            "__AMN2_GENERATED_APP_SECRET_KEY__": material.app_secret_key,
            "__AMN2_GENERATED_WEB_ADMIN_PASSWORD_HASH__": material.web_admin_password_hash,
            "__AMN2_GENERATED_WEB_ADMIN_SESSION_SECRET__": material.web_admin_session_secret,
        },
        template_root=template_root,
    )
    # A package-bound install creates its verified wheelhouse later in the
    # filesystem stage.  Do not import Settings from the system interpreter
    # before those pinned dependencies exist on a clean host.
    if content is None:
        _validate_authoritative_runtime_settings(
            source, _runtime_env_mapping(runtime_env)
        )
    rendered = MappingProxyType(
        {
            "etc/amn2-spain/runtime.env": runtime_env.encode("utf-8"),
            "etc/amn2-spain/awgsp0.conf": render_awg_config(
                key_material.private_key,
                template_root=template_root,
            ).encode("utf-8"),
            "etc/amn2-spain/servers.yml": render_servers_yml(
                endpoint_host=endpoint_host,
                public_key=key_material.public_key,
                template_root=template_root,
            ).encode("utf-8"),
            "etc/amn2-spain/docker-daemon.json": _read_package_bound_bytes(
                package_template_prefix + "/docker-daemon.json",
                content_root=content,
            ),
            "opt/amn2-spain/runtime/awg-start.sh": _read_package_bound_bytes(
                package_template_prefix + "/awg-start.sh",
                content_root=content,
            ),
        }
    )
    package_bound = MappingProxyType(
        {
            "opt/amn2-spain/current/scripts/phase12_spain_network.py": _read_package_bound_bytes(
                "scripts/phase12_spain_network.py",
                content_root=content,
            ),
            "opt/amn2-spain/current/packaging/phase12-spain/templates/nftables.conf": _read_package_bound_bytes(
                package_template_prefix + "/nftables.conf",
                content_root=content,
            ),
        }
    )
    for payload in (*rendered.values(), *package_bound.values()):
        try:
            text = payload.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise BackendError("package-bound runtime artifact encoding invalid") from exc
        if "\r" in text or not text.endswith("\n") or "__AMN2_" in text:
            raise BackendError("package-bound runtime artifact text invalid")
    identity = source_tree_identity(source)
    del material
    return PreparedProductionFilesystemPayloads(
        source_tree_identity=identity,
        endpoint_host=endpoint_host,
        rendered_payloads=rendered,
        package_bound_payloads=package_bound,
    )


def recover_production_filesystem_payloads(
    *,
    source_root: Path,
    endpoint_host: str,
    expected_source_tree_identity: str,
    rendered_payloads: Mapping[str, bytes],
    package_content_root: Path | None = None,
) -> PreparedProductionFilesystemPayloads:
    """Reconstruct prepared payloads from a sealed capsule without new secrets."""
    source = Path(source_root)
    expected_paths = {
        "etc/amn2-spain/runtime.env",
        "etc/amn2-spain/awgsp0.conf",
        "etc/amn2-spain/servers.yml",
        "etc/amn2-spain/docker-daemon.json",
        "opt/amn2-spain/runtime/awg-start.sh",
    }
    if (
        source.is_symlink()
        or not source.is_dir()
        or not isinstance(endpoint_host, str)
        or not endpoint_host
        or source_tree_identity(source) != expected_source_tree_identity
        or not isinstance(rendered_payloads, Mapping)
        or set(rendered_payloads) != expected_paths
        or any(
            not isinstance(payload, bytes) or not payload
            for payload in rendered_payloads.values()
        )
    ):
        raise BackendError("recovered production payload binding invalid")
    rendered = MappingProxyType(dict(rendered_payloads))
    try:
        runtime_env = rendered["etc/amn2-spain/runtime.env"].decode("utf-8")
        awg = rendered["etc/amn2-spain/awgsp0.conf"].decode("utf-8")
        servers = rendered["etc/amn2-spain/servers.yml"].decode("utf-8")
    except UnicodeDecodeError as exc:
        raise BackendError("recovered production payload encoding invalid") from exc
    if (
        "[Peer]" in awg
        or servers.count(endpoint_host) != 2
        or any("__AMN2_" in payload.decode("utf-8") for payload in rendered.values())
    ):
        raise BackendError("recovered production payload semantic drift")
    content = None if package_content_root is None else Path(package_content_root)
    if content is None:
        _validate_authoritative_runtime_settings(
            source,
            _runtime_env_mapping(runtime_env),
        )
    package_template_prefix = (
        "packaging/phase12-spain/templates" if content is None else "templates"
    )
    package_bound = MappingProxyType(
        {
            "opt/amn2-spain/current/scripts/phase12_spain_network.py": _read_package_bound_bytes(
                "scripts/phase12_spain_network.py",
                content_root=content,
            ),
            "opt/amn2-spain/current/packaging/phase12-spain/templates/nftables.conf": _read_package_bound_bytes(
                package_template_prefix + "/nftables.conf",
                content_root=content,
            ),
        }
    )
    return PreparedProductionFilesystemPayloads(
        source_tree_identity=expected_source_tree_identity,
        endpoint_host=endpoint_host,
        rendered_payloads=rendered,
        package_bound_payloads=package_bound,
    )


def recovery_capsule_payload_specs(
    prepared: PreparedProductionFilesystemPayloads,
) -> Mapping[str, Mapping[str, object]]:
    if not isinstance(prepared, PreparedProductionFilesystemPayloads):
        raise BackendError("recovery capsule prepared payload dependency invalid")
    specs: dict[str, Mapping[str, object]] = {}
    for path, payload in prepared.rendered_payloads.items():
        try:
            uid_role, gid_role, mode = PRODUCTION_FILE_SECURITY[path]
        except KeyError as exc:
            raise BackendError("recovery capsule file security missing") from exc
        specs[path] = MappingProxyType(
            {
                "payload": payload,
                "mode": f"{mode:04o}",
                "uid_role": uid_role,
                "gid_role": gid_role,
            }
        )
    return MappingProxyType(specs)


def build_production_filesystem_bundle(
    *,
    root: Path,
    source_root: Path,
    endpoint_host: str,
    root_uid: int | None = 0,
    root_gid: int | None = 0,
    service_uid: int | None = 61212,
    service_gid: int | None = 61212,
    secret_token_factory: Callable[[int], str] = secrets.token_urlsafe,
    prepared_payloads: PreparedProductionFilesystemPayloads | None = None,
) -> ProductionFilesystemBundle:
    target_root = Path(root)
    source = Path(source_root)
    if not callable(secret_token_factory):
        raise BackendError("runtime secret factory invalid")
    root_fs = SafeFs(root=target_root, expected_uid=root_uid, expected_gid=root_gid)
    config_fs = SafeFs(root=target_root, expected_uid=root_uid, expected_gid=service_gid)
    service_fs = SafeFs(
        root=target_root, expected_uid=service_uid, expected_gid=service_gid
    )
    if (target_root / "etc/amn2-spain/bot-enabled").exists() or (
        target_root / "etc/amn2-spain/bot-enabled"
    ).is_symlink():
        raise BackendError("bot enable marker collision")

    prepared = prepared_payloads or prepare_production_filesystem_payloads(
        source_root=source,
        endpoint_host=endpoint_host,
        secret_token_factory=secret_token_factory,
    )
    if (
        not isinstance(prepared, PreparedProductionFilesystemPayloads)
        or prepared.endpoint_host != endpoint_host
        or prepared.source_tree_identity != source_tree_identity(source)
    ):
        raise BackendError("prepared production filesystem payload binding invalid")
    runtime_env = prepared.rendered_payloads["etc/amn2-spain/runtime.env"].decode("utf-8")
    awg_config = prepared.rendered_payloads["etc/amn2-spain/awgsp0.conf"].decode("utf-8")
    servers_yml = prepared.rendered_payloads["etc/amn2-spain/servers.yml"].decode("utf-8")
    docker_daemon = prepared.rendered_payloads["etc/amn2-spain/docker-daemon.json"]
    awg_start = prepared.rendered_payloads["opt/amn2-spain/runtime/awg-start.sh"]
    network_script = prepared.package_bound_payloads[
        "opt/amn2-spain/current/scripts/phase12_spain_network.py"
    ]
    nftables_template = prepared.package_bound_payloads[
        "opt/amn2-spain/current/packaging/phase12-spain/templates/nftables.conf"
    ]

    directory_specs = (
        (root_fs, "opt/amn2-spain", 0o755),
        (root_fs, "opt/amn2-spain/runtime", 0o755),
        (config_fs, "etc/amn2-spain", 0o750),
        (service_fs, "var/lib/amn2-spain", 0o750),
        (service_fs, "var/lib/amn2-spain/logs", 0o750),
        (service_fs, "var/lib/amn2-spain/config-templates", 0o750),
        (root_fs, "var/lib/amn2-spain-docker", 0o700),
        (root_fs, "run/amn2-spain-docker", 0o755),
        (root_fs, "opt/amn2-spain/current", 0o755),
        (root_fs, "opt/amn2-spain/current/scripts", 0o755),
        (root_fs, "opt/amn2-spain/current/packaging", 0o755),
        (root_fs, "opt/amn2-spain/current/packaging/phase12-spain", 0o755),
        (
            root_fs,
            "opt/amn2-spain/current/packaging/phase12-spain/templates",
            0o755,
        ),
    )
    actions: list[SystemAction] = [
        build_directory_action(fs, "filesystem_staged", relative, mode)
        for fs, relative, mode in directory_specs
    ]

    def production_file_action(
        stage: str,
        relative: str,
        payload: bytes,
        *,
        owned_kind: str = "file",
    ) -> SystemAction:
        try:
            uid_role, gid_role, mode = PRODUCTION_FILE_SECURITY[relative]
        except KeyError as exc:
            raise BackendError("production file security contract missing") from exc
        if uid_role != "root" or gid_role not in {"root", "service"}:
            raise BackendError("production file security role invalid")
        fs = root_fs if gid_role == "root" else config_fs
        return build_file_action(
            fs,
            stage,
            relative,
            payload,
            mode,
            owned_kind=owned_kind,
        )

    actions.extend(
        (
            production_file_action(
                "filesystem_staged",
                "opt/amn2-spain/current/scripts/phase12_spain_network.py",
                network_script,
            ),
            production_file_action(
                "filesystem_staged",
                "opt/amn2-spain/current/packaging/phase12-spain/templates/nftables.conf",
                nftables_template,
            ),
            production_file_action(
                "secrets_configs_rendered",
                "etc/amn2-spain/runtime.env",
                runtime_env.encode("utf-8"),
            ),
            production_file_action(
                "secrets_configs_rendered",
                "etc/amn2-spain/awgsp0.conf",
                awg_config.encode("utf-8"),
                owned_kind="secret",
            ),
            production_file_action(
                "secrets_configs_rendered",
                "etc/amn2-spain/servers.yml",
                servers_yml.encode("utf-8"),
            ),
            production_file_action(
                "secrets_configs_rendered",
                "etc/amn2-spain/docker-daemon.json",
                docker_daemon,
            ),
            production_file_action(
                "secrets_configs_rendered",
                "opt/amn2-spain/runtime/awg-start.sh",
                awg_start,
            ),
        )
    )
    sealed_actions = tuple(actions)
    receipt = MappingProxyType(
        {
            action.operation.owned_object: action.operation.desired_identity
            for action in sealed_actions
        }
    )
    return ProductionFilesystemBundle(
        actions=sealed_actions, logical_receipt=receipt
    )


def strict_postinstall_observation(
    value: Any,
    *,
    expected_owned_objects: set[str],
    expected_bindings: dict[str, str],
) -> dict[str, Any]:
    fields = {
        "schema",
        "result",
        "bindings",
        "owned_delta",
        "database",
        "network",
        "runtime",
    }
    if (
        not isinstance(value, dict)
        or set(value) != fields
        or value.get("schema") != "amn2.spain-live-postinstall-observation.v1"
        or value.get("result") != "passed"
    ):
        raise BackendError("postinstall observation schema mismatch")
    if (
        not isinstance(expected_bindings, dict)
        or set(expected_bindings) != POSTINSTALL_BINDING_FIELDS
        or any(not MutationLedger._valid_identity(item) for item in expected_bindings.values())
        or value["bindings"] != expected_bindings
    ):
        raise BackendError("postinstall immutable binding mismatch")
    owned_delta = value["owned_delta"]
    if (
        not isinstance(expected_owned_objects, set)
        or not REQUIRED_CLOSED_DELTA_OBJECTS.issubset(expected_owned_objects)
        or not isinstance(owned_delta, dict)
        or set(owned_delta) != expected_owned_objects
        or any(not MutationLedger._valid_identity(identity) for identity in owned_delta.values())
    ):
        raise BackendError("postinstall closed delta mismatch")
    database = value["database"]
    network = value["network"]
    runtime = value["runtime"]
    try:
        from scripts.phase12_spain_network import (
            EXPECTED_NFT_SEMANTIC_SHA256,
            NFT_RULE_COMMENTS,
            ROUTE_IDENTITY,
        )
    except Exception as exc:
        raise BackendError("postinstall network contract unavailable") from exc
    if (
        not isinstance(database, dict)
        or set(database)
        != {
            "integrity_check",
            "foreign_key_check",
            "foreign_keys",
            "application_table_count",
            "nonempty_tables",
        }
        or database.get("integrity_check") != "ok"
        or database.get("foreign_key_check") != []
        or database.get("foreign_keys") != 1
        or not isinstance(database.get("application_table_count"), int)
        or database["application_table_count"] <= 0
        or database.get("nonempty_tables") != {}
        or not isinstance(network, dict)
        or set(network)
        != {
            "ledger_sha256",
            "nft_semantic_sha256",
            "nft_rule_comments",
            "route",
            "sysctl",
        }
        or not MutationLedger._valid_identity(network.get("ledger_sha256"))
        or network.get("nft_semantic_sha256")
        != "sha256:" + EXPECTED_NFT_SEMANTIC_SHA256
        or network.get("nft_rule_comments") != NFT_RULE_COMMENTS
        or network.get("route") != ROUTE_IDENTITY
        or network.get("sysctl")
        != {"name": "net.ipv4.ip_forward", "applied": "1"}
        or not isinstance(runtime, dict)
        or set(runtime)
        != {
            "peer_count",
            "container_restart_count",
            "web_listener",
            "udp_listener",
            "docker_socket",
            "awg_interface",
            "vps_apply_enabled",
            "bot_enabled",
            "bot_active",
        }
        or runtime["peer_count"] != 0
        or runtime["container_restart_count"] != 0
        or runtime["web_listener"] != "127.0.0.1:3031"
        or runtime["udp_listener"] != "0.0.0.0:30001"
        or runtime["docker_socket"] != "/run/amn2-spain-docker/docker.sock"
        or runtime["awg_interface"] != "awgsp0"
        or runtime["vps_apply_enabled"] is not False
        or runtime["bot_enabled"] is not False
        or runtime["bot_active"] is not False
    ):
        raise BackendError("postinstall runtime invariant mismatch")
    return copy.deepcopy(value)
