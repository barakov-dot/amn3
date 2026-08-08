#!/usr/bin/env python
"""Encrypt-before-persistence bridge for Phase 13 bot/web fresh inputs."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import stat
import subprocess
from threading import Event, Lock, RLock, Thread
from typing import Callable, Iterator

from scripts.phase10_recovery_crypto import RecoveryCryptoError, encrypt_hybrid
from scripts.phase13_bot_web_migration_package import PackageInputs
from scripts.vps.phase13_bot_web_migration_fresh_input_remote import (
    MAX_FRAME_BYTES,
    ParsedRoleFrame,
    parse_role_frame,
)


ROLE_ORDER = ("usa", "spain")
MAX_TRANSPORT_INPUT_BYTES = 1024 * 1024
MAX_TRANSPORT_OUTPUT_BYTES = 64 * 1024 * 1024
MAX_TRANSPORT_TIMEOUT_SECONDS = 60.0
FIXED_TRUST_ROOTS = {
    "usa": Path(r"C:\ProgramData\AMN2\trust\usa"),
    "spain": Path(r"C:\ProgramData\AMN2\trust\spain"),
}
_MERGE_LOCK = RLock()


class FreshInputError(RuntimeError):
    """A secret-safe fresh-input orchestration failure."""


@dataclass(frozen=True)
class InMemoryMergeResult:
    preview_bytes: bytes
    merged_database: bytes
    result_sha256: str


@dataclass(frozen=True)
class EncryptedFreshInputs:
    outcome_id: str
    source_audit: bytes
    target_audit: bytes
    source_full_backup: bytes
    target_before_backup: bytes
    merged_target_db: bytes
    merge_preview: bytes
    merge_result_sha256: str
    ssh_processes: int
    plaintext_database_written: bool = False
    external_key_stored_separately: bool = True


@dataclass(frozen=True)
class ExternalKeyPair:
    private_key_path: Path
    public_key_pem: bytes


@dataclass(frozen=True)
class FixedRoleBinding:
    role: str
    target_host: str
    target_user: str
    key_path: Path
    known_hosts_path: Path


def run_bounded_process(
    executable: str,
    arguments: tuple[str, ...],
    input_bytes: bytes,
    *,
    timeout_seconds: float = MAX_TRANSPORT_TIMEOUT_SECONDS,
    maximum_input_bytes: int = MAX_TRANSPORT_INPUT_BYTES,
    maximum_output_bytes: int = MAX_TRANSPORT_OUTPUT_BYTES,
) -> bytes:
    """Run one local process with bounded stdin, stdout+stderr, and time."""

    if (
        not isinstance(input_bytes, bytes)
        or maximum_input_bytes < 1
        or maximum_input_bytes > MAX_TRANSPORT_INPUT_BYTES
        or maximum_output_bytes < 1
        or maximum_output_bytes > MAX_TRANSPORT_OUTPUT_BYTES
        or timeout_seconds <= 0
        or timeout_seconds > MAX_TRANSPORT_TIMEOUT_SECONDS
    ):
        raise FreshInputError("bounded process contract invalid")
    if len(input_bytes) > maximum_input_bytes:
        raise FreshInputError("bounded process input oversized")
    try:
        process = subprocess.Popen(
            (str(executable), *tuple(str(item) for item in arguments)),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )
    except OSError as error:
        raise FreshInputError("bounded process start failed") from error
    output = bytearray()
    total = [0]
    oversized = Event()
    io_failure = Event()
    lock = Lock()

    def read_stream(stream, *, capture: bool) -> None:
        try:
            while True:
                chunk = stream.read(4096)
                if not chunk:
                    return
                with lock:
                    total[0] += len(chunk)
                    if total[0] > maximum_output_bytes:
                        oversized.set()
                    elif capture:
                        output.extend(chunk)
                if oversized.is_set():
                    try:
                        process.kill()
                    except OSError:
                        pass
                    return
        except OSError:
            io_failure.set()

    def write_input() -> None:
        try:
            if process.stdin is None:
                io_failure.set()
                return
            if input_bytes:
                process.stdin.write(input_bytes)
                process.stdin.flush()
        except (BrokenPipeError, OSError):
            io_failure.set()
        finally:
            if process.stdin is not None:
                try:
                    process.stdin.close()
                except OSError:
                    pass

    stdout_thread = Thread(
        target=read_stream, args=(process.stdout,), kwargs={"capture": True}, daemon=True
    )
    stderr_thread = Thread(
        target=read_stream, args=(process.stderr,), kwargs={"capture": False}, daemon=True
    )
    input_thread = Thread(target=write_input, daemon=True)
    stdout_thread.start()
    stderr_thread.start()
    input_thread.start()
    try:
        process.wait(timeout=timeout_seconds)
    except subprocess.TimeoutExpired as error:
        process.kill()
        process.wait()
        raise FreshInputError("bounded process timeout") from error
    finally:
        input_thread.join(timeout=1)
        stdout_thread.join(timeout=1)
        stderr_thread.join(timeout=1)
        for stream in (process.stdout, process.stderr):
            if stream is not None:
                stream.close()
    if oversized.is_set():
        raise FreshInputError("bounded process output oversized")
    if io_failure.is_set() or process.returncode != 0:
        raise FreshInputError("bounded process failed")
    return bytes(output)


def load_fixed_role_binding(role: str) -> FixedRoleBinding:
    """Read one immutable role binding without returning raw trust material."""

    if role not in ROLE_ORDER:
        raise FreshInputError("fixed role invalid")
    root = FIXED_TRUST_ROOTS[role]
    binding_path = root / "target.env"
    key_path = root / "id_ed25519"
    known_hosts_path = root / "known_hosts"
    for path in (root, binding_path, key_path, known_hosts_path):
        _require_nofollow_path(path, directory=path == root)
        _assert_current_user_only_acl(path)
    try:
        lines = binding_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as error:
        raise FreshInputError("fixed role binding unavailable") from error
    names = (
        "TARGET_HOST",
        "TARGET_USER",
        "SSH_KEY_PATH",
        "EXPECTED_HOST_KEY_SHA256",
    )
    if len(lines) != len(names):
        raise FreshInputError("fixed role binding invalid")
    values: dict[str, str] = {}
    for name, line in zip(names, lines, strict=True):
        prefix = f"{name}="
        if not line.startswith(prefix):
            raise FreshInputError("fixed role binding invalid")
        values[name] = line[len(prefix) :]
    if (
        re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9.:-]{0,252}[A-Za-z0-9])?", values["TARGET_HOST"])
        is None
        or re.fullmatch(r"[a-z_][a-z0-9_-]{0,31}", values["TARGET_USER"])
        is None
        or Path(values["SSH_KEY_PATH"]) != key_path
        or re.fullmatch(r"SHA256:[A-Za-z0-9+/]{43}", values["EXPECTED_HOST_KEY_SHA256"])
        is None
    ):
        raise FreshInputError("fixed role binding invalid")
    try:
        host_lines = known_hosts_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as error:
        raise FreshInputError("fixed host pin unavailable") from error
    if len(host_lines) != 1:
        raise FreshInputError("fixed host pin invalid")
    parts = host_lines[0].split(" ")
    if len(parts) != 3 or parts[0] != values["TARGET_HOST"]:
        raise FreshInputError("fixed host pin invalid")
    try:
        key_blob = base64.b64decode(parts[2], validate=True)
    except ValueError as error:
        raise FreshInputError("fixed host pin invalid") from error
    fingerprint = "SHA256:" + base64.b64encode(hashlib.sha256(key_blob).digest()).decode(
        "ascii"
    ).rstrip("=")
    if fingerprint != values["EXPECTED_HOST_KEY_SHA256"]:
        raise FreshInputError("fixed host pin invalid")
    return FixedRoleBinding(
        role=role,
        target_host=values["TARGET_HOST"],
        target_user=values["TARGET_USER"],
        key_path=key_path,
        known_hosts_path=known_hosts_path,
    )


class FixedSshFreshInputTransport:
    """One-SSH-per-role binary transport with no public target/path inputs."""

    def __init__(
        self,
        *,
        fresh_collector_bytes: bytes,
        audit_collector_bytes: bytes,
        binding_loader: Callable[[str], FixedRoleBinding] = load_fixed_role_binding,
        process_runner: Callable[..., bytes] = run_bounded_process,
        ssh_executable: str = r"C:\Windows\System32\OpenSSH\ssh.exe",
    ) -> None:
        if (
            not isinstance(fresh_collector_bytes, bytes)
            or not fresh_collector_bytes
            or not isinstance(audit_collector_bytes, bytes)
            or not audit_collector_bytes
        ):
            raise FreshInputError("collector bytes invalid")
        self._fresh = fresh_collector_bytes
        self._audit = audit_collector_bytes
        self._binding_loader = binding_loader
        self._process_runner = process_runner
        self._ssh_executable = ssh_executable

    def __call__(self, role: str) -> bytes:
        if role not in ROLE_ORDER:
            raise FreshInputError("fixed role invalid")
        binding = self._binding_loader(role)
        if not isinstance(binding, FixedRoleBinding) or binding.role != role:
            raise FreshInputError("fixed role binding invalid")
        hmac_key = bytearray(os.urandom(32))
        try:
            envelope = {
                "audit_collector_b64": base64.b64encode(self._audit).decode("ascii"),
                "audit_collector_sha256": hashlib.sha256(self._audit).hexdigest(),
                "ephemeral_hmac_key_b64": base64.b64encode(hmac_key).decode("ascii"),
                "fresh_collector_b64": base64.b64encode(self._fresh).decode("ascii"),
                "fresh_collector_sha256": hashlib.sha256(self._fresh).hexdigest(),
            }
            input_bytes = (
                json.dumps(envelope, sort_keys=True, separators=(",", ":")) + "\n"
            ).encode("utf-8")
            bootstrap = (
                'import base64,hashlib,json,sys,types;'
                'e=json.load(sys.stdin);'
                'a=base64.b64decode(e["audit_collector_b64"],validate=True);'
                'hashlib.sha256(a).hexdigest()==e["audit_collector_sha256"] or sys.exit(70);'
                'am=types.ModuleType("phase13_bot_web_migration_readonly_remote");'
                'sys.modules[am.__name__]=am;'
                'exec(compile(a,"<bound-input-a>","exec"),am.__dict__);'
                'f=base64.b64decode(e["fresh_collector_b64"],validate=True);'
                'hashlib.sha256(f).hexdigest()==e["fresh_collector_sha256"] or sys.exit(70);'
                'fm=types.ModuleType("phase13_bot_web_migration_fresh_input_remote");'
                'sys.modules[fm.__name__]=fm;'
                'exec(compile(f,"<bound-input-b>","exec"),fm.__dict__);'
                'k=base64.b64decode(e["ephemeral_hmac_key_b64"],validate=True);'
                'd=am.collect(sys.argv[1],k);'
                'sys.stdout.buffer.write(fm.collect_role_frame(sys.argv[1],d["audit"]))'
            )
            remote_command = f"python3 -c '{bootstrap}' {role}"
            arguments = (
                "-T",
                "-F",
                "none",
                "-o",
                "BatchMode=yes",
                "-o",
                "IdentitiesOnly=yes",
                "-o",
                "StrictHostKeyChecking=yes",
                "-o",
                f"UserKnownHostsFile={binding.known_hosts_path}",
                "-o",
                "ConnectTimeout=10",
                "-o",
                "ConnectionAttempts=1",
                "-o",
                "ServerAliveInterval=5",
                "-o",
                "ServerAliveCountMax=1",
                "-i",
                str(binding.key_path),
                "-p",
                "22",
                f"{binding.target_user}@{binding.target_host}",
                remote_command,
            )
            frame = self._process_runner(
                self._ssh_executable,
                arguments,
                input_bytes,
                timeout_seconds=MAX_TRANSPORT_TIMEOUT_SECONDS,
                maximum_input_bytes=MAX_TRANSPORT_INPUT_BYTES,
                maximum_output_bytes=MAX_TRANSPORT_OUTPUT_BYTES,
            )
            parse_role_frame(frame)
            return frame
        except FreshInputError:
            raise
        except Exception as error:
            raise FreshInputError("fixed role transport failed") from error
        finally:
            for index in range(len(hmac_key)):
                hmac_key[index] = 0


def _require_nofollow_path(path: Path, *, directory: bool) -> None:
    try:
        metadata = os.lstat(path)
    except OSError as error:
        raise FreshInputError("fixed trust path unavailable") from error
    expected = stat.S_ISDIR(metadata.st_mode) if directory else stat.S_ISREG(metadata.st_mode)
    if stat.S_ISLNK(metadata.st_mode) or _is_reparse_point(metadata) or not expected:
        raise FreshInputError("fixed trust path unsafe")


class _ConnectionProxy:
    def __init__(self, connection: sqlite3.Connection) -> None:
        object.__setattr__(self, "_connection", connection)

    def __getattr__(self, name: str):
        return getattr(object.__getattribute__(self, "_connection"), name)

    def __setattr__(self, name: str, value: object) -> None:
        setattr(object.__getattribute__(self, "_connection"), name, value)

    def close(self) -> None:
        return None


class _SqliteProxy:
    def __init__(self, target_path: Path, target: sqlite3.Connection) -> None:
        self._target_path = target_path
        self._target = target

    def connect(self, database, *args, **kwargs):
        if Path(database) == self._target_path:
            return _ConnectionProxy(self._target)
        return sqlite3.connect(database, *args, **kwargs)

    def __getattr__(self, name: str):
        return getattr(sqlite3, name)


def run_amn2_merge_in_memory(
    amn2_module,
    source_database: bytes,
    target_database: bytes,
    *,
    migration_id: str,
) -> InMemoryMergeResult:
    """Run the exact AMN2 public merge API against SQLite memory images only."""

    if not isinstance(source_database, bytes) or not isinstance(target_database, bytes):
        raise FreshInputError("database bytes invalid")
    source_path = Path("source.memory.sqlite3")
    target_path = Path("target.copy.sqlite3")
    source = sqlite3.connect(":memory:")
    target = sqlite3.connect(":memory:")
    try:
        source.deserialize(source_database)
        target.deserialize(target_database)
    except sqlite3.DatabaseError as error:
        source.close()
        target.close()
        raise FreshInputError("database deserialize failed") from error

    @contextmanager
    def readonly_connection(path: Path) -> Iterator[sqlite3.Connection]:
        connection = source if Path(path) == source_path else target
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA query_only=ON")
        try:
            yield connection
        finally:
            connection.execute("PRAGMA query_only=OFF")

    def resolve_database_path(value: Path) -> Path:
        path = Path(value)
        if path == source_path:
            return source_path
        if path == target_path:
            return target_path
        raise ValueError("database path is not an in-memory role")

    required = (
        "build_bot_web_migration_preview",
        "apply_bot_web_migration_to_copy",
        "_readonly_connection",
        "_resolve_database_path",
        "_remove_incomplete_copy",
        "sqlite3",
    )
    if any(not hasattr(amn2_module, name) for name in required):
        source.close()
        target.close()
        raise FreshInputError("AMN2 merge contract unavailable")
    originals = {name: getattr(amn2_module, name) for name in required[2:]}
    with _MERGE_LOCK:
        try:
            amn2_module._readonly_connection = readonly_connection
            amn2_module._resolve_database_path = resolve_database_path
            amn2_module._remove_incomplete_copy = lambda _path: None
            amn2_module.sqlite3 = _SqliteProxy(target_path, target)
            preview = amn2_module.build_bot_web_migration_preview(
                source_path,
                target_path,
                migration_id=migration_id,
            )
            if not getattr(preview, "apply_allowed", True):
                raise FreshInputError("merge preview blocked")
            result = amn2_module.apply_bot_web_migration_to_copy(
                preview,
                source_db=source_path,
                target_copy_db=target_path,
            )
            merged = target.serialize()
            preview_bytes = preview.canonical_bytes()
            result_sha256 = str(result.result_sha256)
        except FreshInputError:
            raise
        except Exception as error:
            raise FreshInputError("AMN2 in-memory merge failed") from error
        finally:
            for name, value in originals.items():
                setattr(amn2_module, name, value)
            source.close()
            target.close()
    if not merged.startswith(b"SQLite format 3\x00"):
        raise FreshInputError("merged database invalid")
    return InMemoryMergeResult(
        preview_bytes=preview_bytes,
        merged_database=merged,
        result_sha256=result_sha256,
    )


def collect_encrypt_and_merge(
    *,
    transport: Callable[[str], bytes],
    recipient_public_key_pem: bytes,
    amn2_module,
    migration_id: str,
) -> EncryptedFreshInputs:
    """Collect exactly two fixed roles and encrypt before returning artifacts."""

    parsed: dict[str, ParsedRoleFrame] = {}
    raw_archives: list[bytearray] = []
    database_buffers: list[bytearray] = []
    process_count = 0
    try:
        encrypted: dict[str, bytes] = {}
        for role in ROLE_ORDER:
            frame = transport(role)
            process_count += 1
            if not isinstance(frame, bytes) or len(frame) > MAX_FRAME_BYTES:
                raise FreshInputError("bounded transport failed")
            document = parse_role_frame(frame)
            parsed[role] = document
            archive_buffer = bytearray(document.archive)
            raw_archives.append(archive_buffer)
            encrypted[role] = encrypt_hybrid(bytes(archive_buffer), recipient_public_key_pem)
        source_database = bytearray(parsed["usa"].files["database.sqlite3"])
        target_database = bytearray(parsed["spain"].files["database.sqlite3"])
        database_buffers.extend((source_database, target_database))
        merge = run_amn2_merge_in_memory(
            amn2_module,
            bytes(source_database),
            bytes(target_database),
            migration_id=migration_id,
        )
        merged_buffer = bytearray(merge.merged_database)
        database_buffers.append(merged_buffer)
        encrypted_merged = encrypt_hybrid(bytes(merged_buffer), recipient_public_key_pem)
        return EncryptedFreshInputs(
            outcome_id=migration_id,
            source_audit=parsed["usa"].audit,
            target_audit=parsed["spain"].audit,
            source_full_backup=encrypted["usa"],
            target_before_backup=encrypted["spain"],
            merged_target_db=encrypted_merged,
            merge_preview=merge.preview_bytes,
            merge_result_sha256=merge.result_sha256,
            ssh_processes=process_count,
        )
    except (FreshInputError, RecoveryCryptoError, KeyError, TimeoutError) as error:
        raise FreshInputError("fresh input collection failed") from error
    except Exception as error:
        raise FreshInputError("fresh input collection failed") from error
    finally:
        for buffer in raw_archives + database_buffers:
            for index in range(len(buffer)):
                buffer[index] = 0


def bind_package_inputs(
    fresh: EncryptedFreshInputs,
    *,
    created_at: str,
    expires_at: str,
    migration_plan: bytes,
    rollback_plan: bytes,
    reviewed_runner: bytes,
) -> PackageInputs:
    if not isinstance(fresh, EncryptedFreshInputs) or fresh.ssh_processes != 2:
        raise FreshInputError("fresh input binding invalid")
    try:
        preview = json.loads(fresh.merge_preview)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise FreshInputError("fresh merge preview invalid") from error
    if (
        not isinstance(preview, dict)
        or preview.get("apply_allowed") is not True
        or preview.get("usable_secret_records_imported") != 0
    ):
        raise FreshInputError("fresh merge preview invalid")
    preview["live_mutation_authorized"] = False
    package_preview = (
        json.dumps(preview, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")
    return PackageInputs(
        outcome_id=fresh.outcome_id,
        created_at=created_at,
        expires_at=expires_at,
        source_audit=fresh.source_audit,
        target_audit=fresh.target_audit,
        migration_plan=migration_plan,
        source_full_backup=fresh.source_full_backup,
        source_backup_encrypted=True,
        target_before_backup=fresh.target_before_backup,
        target_backup_encrypted=True,
        merged_target_db=fresh.merged_target_db,
        merged_target_encrypted=True,
        merge_preview=package_preview,
        rollback_plan=rollback_plan,
        reviewed_runner=reviewed_runner,
        external_key_stored_separately=True,
    )


def create_external_keypair(
    key_root: Path,
    *,
    artifact_root: Path,
) -> ExternalKeyPair:
    """Create a no-follow external RSA recovery key root exactly once."""

    root = Path(key_root)
    artifact = Path(artifact_root).resolve(strict=True)
    root_candidate = root.resolve(strict=False)
    if root_candidate == artifact or artifact in root_candidate.parents:
        raise FreshInputError("external key root must be outside artifact root")
    if os.path.lexists(root):
        raise FreshInputError("external key root already exists")
    parent = root.parent
    try:
        parent_metadata = os.lstat(parent)
    except OSError as error:
        raise FreshInputError("external key parent unavailable") from error
    if (
        stat.S_ISLNK(parent_metadata.st_mode)
        or _is_reparse_point(parent_metadata)
        or not stat.S_ISDIR(parent_metadata.st_mode)
    ):
        raise FreshInputError("external key parent unsafe")
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import rsa

        key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
        private = key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
        public = key.public_key().public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        os.mkdir(root, 0o700)
        _protect_current_user_only_acl(root, directory=True)
        private_path = root / "recovery-private.pem"
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(private_path, flags, 0o600)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                descriptor = -1
                handle.write(private)
                handle.flush()
                os.fsync(handle.fileno())
            os.chmod(root, 0o700)
            os.chmod(private_path, 0o600)
            _protect_current_user_only_acl(private_path, directory=False)
            _assert_current_user_only_acl(root)
            _assert_current_user_only_acl(private_path)
        finally:
            if descriptor >= 0:
                os.close(descriptor)
        return ExternalKeyPair(private_key_path=private_path, public_key_pem=public)
    except Exception as error:
        _remove_key_root(root)
        if isinstance(error, FreshInputError):
            raise
        raise FreshInputError("external key creation failed") from error


def _is_reparse_point(metadata: os.stat_result) -> bool:
    return bool(getattr(metadata, "st_file_attributes", 0) & 0x400)


def _protect_current_user_only_acl(path: Path, *, directory: bool) -> None:
    if os.name != "nt":
        os.chmod(path, 0o700 if directory else 0o600)
        return
    inheritance = (
        "[Security.AccessControl.InheritanceFlags]::ContainerInherit -bor "
        "[Security.AccessControl.InheritanceFlags]::ObjectInherit"
        if directory
        else "[Security.AccessControl.InheritanceFlags]::None"
    )
    script = (
        "$ErrorActionPreference='Stop';"
        "$p=$env:AMN2_PHASE13_ACL_PATH;"
        "$sid=[Security.Principal.WindowsIdentity]::GetCurrent().User;"
        "$info=if([IO.Directory]::Exists($p)){New-Object IO.DirectoryInfo($p)}"
        "else{New-Object IO.FileInfo($p)};"
        "$acl=$info.GetAccessControl();$acl.SetOwner($sid);"
        "$acl.SetAccessRuleProtection($true,$false);"
        "foreach($r in @($acl.Access)){[void]$acl.RemoveAccessRuleAll($r)};"
        f"$inheritance={inheritance};"
        "$rule=New-Object Security.AccessControl.FileSystemAccessRule("
        "$sid,[Security.AccessControl.FileSystemRights]::FullControl,"
        "$inheritance,"
        "[Security.AccessControl.PropagationFlags]::None,"
        "[Security.AccessControl.AccessControlType]::Allow);"
        "[void]$acl.AddAccessRule($rule);$info.SetAccessControl($acl)"
    )
    acl_environment = os.environ.copy()
    acl_environment["AMN2_PHASE13_ACL_PATH"] = str(path)
    result = subprocess.run(
        (
            r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            script,
        ),
        check=False,
        env=acl_environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=10,
    )
    if result.returncode != 0:
        raise FreshInputError("private ACL protection failed")


def _assert_current_user_only_acl(path: Path) -> None:
    if os.name != "nt":
        mode = stat.S_IMODE(os.lstat(path).st_mode)
        if mode & 0o077:
            raise FreshInputError("private ACL invalid")
        return
    script = (
        "$ErrorActionPreference='Stop';$p=$env:AMN2_PHASE13_ACL_PATH;"
        "$sid=[Security.Principal.WindowsIdentity]::GetCurrent().User.Value;"
        "$attrs=[IO.File]::GetAttributes($p);"
        "if(($attrs-band[IO.FileAttributes]::ReparsePoint)-ne 0){exit 3};"
        "$info=if([IO.Directory]::Exists($p)){New-Object IO.DirectoryInfo($p)}"
        "else{New-Object IO.FileInfo($p)};"
        "$a=$info.GetAccessControl();$owner=$a.Owner;"
        "try{$owner=([Security.Principal.NTAccount]$a.Owner).Translate("
        "[Security.Principal.SecurityIdentifier]).Value}catch{};"
        "if($owner-cne$sid-or-not$a.AreAccessRulesProtected){exit 4};"
        "foreach($r in $a.Access){$rs=$r.IdentityReference.Value;"
        "try{$rs=$r.IdentityReference.Translate("
        "[Security.Principal.SecurityIdentifier]).Value}catch{};"
        "if($r.IsInherited-or($r.AccessControlType-eq'Allow'-and$rs-cne$sid)){exit 5}}"
    )
    acl_environment = os.environ.copy()
    acl_environment["AMN2_PHASE13_ACL_PATH"] = str(path)
    result = subprocess.run(
        (
            r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            script,
        ),
        check=False,
        env=acl_environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=10,
    )
    if result.returncode != 0:
        raise FreshInputError("private ACL invalid")


def _remove_key_root(root: Path) -> None:
    if not os.path.lexists(root):
        return
    metadata = os.lstat(root)
    if stat.S_ISLNK(metadata.st_mode) or _is_reparse_point(metadata):
        return
    private = root / "recovery-private.pem"
    if os.path.lexists(private):
        item = os.lstat(private)
        if stat.S_ISREG(item.st_mode) and not _is_reparse_point(item):
            private.unlink()
    try:
        root.rmdir()
    except OSError:
        pass
