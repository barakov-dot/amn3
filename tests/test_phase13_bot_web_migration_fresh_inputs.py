from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from scripts.phase10_recovery_crypto import MAGIC, decrypt_hybrid
from scripts.phase13_bot_web_migration_package import materialize_local_package
from scripts.phase13_bot_web_migration_fresh_inputs import (
    FixedRoleBinding,
    FixedSshFreshInputTransport,
    FreshInputError,
    bind_package_inputs,
    collect_encrypt_and_merge,
    create_external_keypair,
    run_bounded_process,
    run_amn2_merge_in_memory,
)
from scripts.vps import phase13_bot_web_migration_fresh_input_remote as remote


def canonical(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def audit(role: str) -> dict[str, object]:
    return {
        "checked_at": "2026-08-08T12:00:00Z",
        "database": {
            "counts_sha256": "1" * 64,
            "foreign_key_violations": 0,
            "integrity_ok": True,
            "schema_sha256": "2" * 64,
            "table_count": 1,
        },
        "environment": {
            "app_secret_present": True,
            "session_secret_present": True,
            "telegram_bot_token_present": True,
            "web_password_hash_present": True,
        },
        "required_artifacts": {
            "database_readable": True,
            "environment_reference_proof_available": True,
        },
        "role": "usa-source" if role == "usa" else "spain-target",
        "safety_receipt": {
            "mutation_attempted": False,
            "raw_output_persisted": False,
            "secret_bearing_data_persisted": False,
        },
        "schema": "amn2.phase13.bot-web-audit.v1",
        "services": {
            "bot_active": role == "usa",
            "web_active": True,
            "web_loopback_only": True,
        },
    }


def create_database(path: Path, marker: str) -> bytes:
    connection = sqlite3.connect(path)
    try:
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("CREATE TABLE items(id INTEGER PRIMARY KEY, marker TEXT)")
        connection.execute("INSERT INTO items(marker) VALUES (?)", (marker,))
        connection.commit()
    finally:
        connection.close()
    return path.read_bytes()


def role_files(database: bytes) -> dict[str, bytes]:
    return {
        "database.sqlite3": database,
        "runtime.env": b"SYNTHETIC_RUNTIME_REFERENCE=present\n",
        "server-config.yml": b"synthetic: fixed-role\n",
    }


@pytest.fixture(scope="module")
def recovery_keys() -> tuple[bytes, bytes]:
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
    return public, private


def test_remote_collector_uses_consistent_memory_snapshot_and_fixed_allowlist(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database = tmp_path / "role.sqlite3"
    create_database(database, "raw-db-marker")
    environment = tmp_path / "runtime.env"
    environment.write_text("TOKEN=raw-env-marker\n", encoding="utf-8")
    config = tmp_path / "server.yml"
    config.write_text("name: raw-config-marker\n", encoding="utf-8")
    monkeypatch.setitem(
        remote.ROLE_CONTRACTS,
        "usa",
        {
            "database": database,
            "application_files": (
                ("runtime.env", environment),
                ("server-config.yml", config),
            ),
        },
    )

    frame = remote.collect_role_frame("usa", audit("usa"))
    parsed = remote.parse_role_frame(frame)

    assert parsed.audit == canonical(audit("usa"))
    assert parsed.files["database.sqlite3"].startswith(b"SQLite format 3\x00")
    assert b"raw-db-marker" in parsed.files["database.sqlite3"]
    assert parsed.files["runtime.env"] == environment.read_bytes()
    assert parsed.files["server-config.yml"] == config.read_bytes()
    assert set(parsed.files) == {
        "database.sqlite3",
        "runtime.env",
        "server-config.yml",
    }


@dataclass(frozen=True)
class FakePreview:
    migration_id: str

    def canonical_bytes(self) -> bytes:
        return canonical(
            {
                "apply_allowed": True,
                "migration_id": self.migration_id,
                "usable_secret_records_imported": 0,
            }
        )


@dataclass(frozen=True)
class FakeResult:
    result_sha256: str = "3" * 64


class FakeAmn2Module:
    def __init__(self) -> None:
        self._source = Path("source.memory.sqlite3")
        self._target = Path("target.copy.sqlite3")
        self.sqlite3 = sqlite3

    @staticmethod
    def _resolve_database_path(value: Path) -> Path:
        return Path(value)

    @staticmethod
    def _remove_incomplete_copy(_value: Path) -> None:
        return None

    @contextmanager
    def _readonly_connection(self, path: Path):
        connection = sqlite3.connect(path)
        try:
            yield connection
        finally:
            connection.close()

    def build_bot_web_migration_preview(
        self, source_db: Path, target_db: Path, *, migration_id: str
    ) -> FakePreview:
        with self._readonly_connection(source_db) as source:
            assert source.execute("SELECT count(*) FROM items").fetchone()[0] == 1
        with self._readonly_connection(target_db) as target:
            assert target.execute("SELECT count(*) FROM items").fetchone()[0] == 1
        return FakePreview(migration_id)

    def apply_bot_web_migration_to_copy(
        self, preview: FakePreview, *, source_db: Path, target_copy_db: Path
    ) -> FakeResult:
        with self._readonly_connection(source_db) as source:
            marker = source.execute("SELECT marker FROM items").fetchone()[0]
        target = self.sqlite3.connect(target_copy_db)
        try:
            target.execute("INSERT INTO items(marker) VALUES (?)", (marker,))
            target.commit()
        finally:
            target.close()
        return FakeResult()


def test_in_memory_amn2_adapter_is_deterministic_and_writes_no_plaintext_file(
    tmp_path: Path,
) -> None:
    source = create_database(tmp_path / "source.sqlite3", "source-marker")
    target = create_database(tmp_path / "target.sqlite3", "target-marker")
    module = FakeAmn2Module()

    first = run_amn2_merge_in_memory(
        module, source, target, migration_id="phase13-fresh-test"
    )
    second = run_amn2_merge_in_memory(
        FakeAmn2Module(), source, target, migration_id="phase13-fresh-test"
    )

    assert first.preview_bytes == second.preview_bytes
    assert first.merged_database == second.merged_database
    assert first.result_sha256 == second.result_sha256 == "3" * 64
    assert sorted(path.name for path in tmp_path.iterdir()) == [
        "source.sqlite3",
        "target.sqlite3",
    ]


def test_collection_encrypts_before_persistent_binding_and_uses_exactly_two_roles(
    tmp_path: Path, recovery_keys: tuple[bytes, bytes]
) -> None:
    public_key, private_key = recovery_keys
    source_db = create_database(tmp_path / "usa.sqlite3", "usa-plaintext-marker")
    target_db = create_database(tmp_path / "spain.sqlite3", "spain-plaintext-marker")
    frames = {
        "usa": remote.build_role_frame(audit("usa"), role_files(source_db)),
        "spain": remote.build_role_frame(
            audit("spain"), role_files(target_db)
        ),
    }
    calls: list[str] = []

    def transport(role: str) -> bytes:
        calls.append(role)
        return frames[role]

    result = collect_encrypt_and_merge(
        transport=transport,
        recipient_public_key_pem=public_key,
        amn2_module=FakeAmn2Module(),
        migration_id="phase13-fresh-test",
    )

    assert calls == ["usa", "spain"]
    assert result.ssh_processes == 2
    assert result.source_full_backup.startswith(MAGIC)
    assert result.target_before_backup.startswith(MAGIC)
    assert result.merged_target_db.startswith(MAGIC)
    assert b"usa-plaintext-marker" not in result.source_full_backup
    assert b"spain-plaintext-marker" not in result.target_before_backup
    assert decrypt_hybrid(result.source_full_backup, private_key).startswith(
        remote.FRAME_ARCHIVE_MAGIC
    )


@pytest.mark.parametrize("failure", ["timeout", "oversized", "partial"])
def test_transport_failure_is_fail_closed_without_partial_result(
    failure: str, recovery_keys: tuple[bytes, bytes]
) -> None:
    public_key, _ = recovery_keys
    calls: list[str] = []

    def transport(role: str) -> bytes:
        calls.append(role)
        if failure == "timeout":
            raise TimeoutError("synthetic raw timeout detail")
        if failure == "oversized":
            return b"x" * (remote.MAX_FRAME_BYTES + 1)
        return remote.build_role_frame(audit(role), {})

    with pytest.raises(FreshInputError, match="fresh input collection failed"):
        collect_encrypt_and_merge(
            transport=transport,
            recipient_public_key_pem=public_key,
            amn2_module=FakeAmn2Module(),
            migration_id="phase13-fresh-failure",
        )
    assert len(calls) <= 2


def test_external_private_key_is_create_new_and_outside_artifact_root(
    tmp_path: Path,
) -> None:
    artifact_root = tmp_path / "artifacts"
    key_root = tmp_path / "external-key"
    artifact_root.mkdir()

    first = create_external_keypair(key_root, artifact_root=artifact_root)
    assert first.private_key_path.parent == key_root
    assert first.private_key_path.read_bytes().startswith(b"-----BEGIN PRIVATE KEY-----")
    assert first.public_key_pem.startswith(b"-----BEGIN PUBLIC KEY-----")
    assert not any(artifact_root.iterdir())

    with pytest.raises(FreshInputError, match="external key root already exists"):
        create_external_keypair(key_root, artifact_root=artifact_root)


def test_package_binding_uses_existing_package_contract(
    tmp_path: Path, recovery_keys: tuple[bytes, bytes]
) -> None:
    public_key, _ = recovery_keys
    source_db = create_database(tmp_path / "source.sqlite3", "source")
    target_db = create_database(tmp_path / "target.sqlite3", "target")
    frames = {
        "usa": remote.build_role_frame(audit("usa"), role_files(source_db)),
        "spain": remote.build_role_frame(
            audit("spain"), role_files(target_db)
        ),
    }
    result = collect_encrypt_and_merge(
        transport=frames.__getitem__,
        recipient_public_key_pem=public_key,
        amn2_module=FakeAmn2Module(),
        migration_id="phase13-fresh-test",
    )

    reviewed_runner = b"# reviewed fresh-input runner\n"
    migration_plan = canonical(
        {
            "api_tokens_reissue_required": 0,
            "live_mutation_authorized": False,
            "migration_id": "phase13-fresh-test",
            "preserve_target_app_secrets": True,
            "schema": "amn2.phase13.bot-web-migration-plan.v1",
            "source_audit_sha256": hashlib.sha256(result.source_audit).hexdigest(),
            "source_role": "usa-source",
            "target_audit_sha256": hashlib.sha256(result.target_audit).hexdigest(),
            "target_role": "spain-target",
            "usable_secret_records_imported": 0,
        }
    )
    additional = {
        "migration-plan.json": migration_plan,
        "source-audit.json": result.source_audit,
        "ssh-runner.ps1": reviewed_runner,
        "target-audit.json": result.target_audit,
    }
    rollback_plan = canonical(
        {
            "artifact_bindings": {
                name: {
                    "sha256": hashlib.sha256(value).hexdigest(),
                    "size": len(value),
                }
                for name, value in sorted(additional.items())
            },
            "live_mutation_authorized": False,
            "restore_apply_authorized": False,
            "schema": "amn2.phase13.bot-web-migration-rollback-plan.v1",
        }
    )
    inputs = bind_package_inputs(
        result,
        created_at="2026-08-08T12:00:00Z",
        expires_at="2099-08-08T13:00:00Z",
        migration_plan=migration_plan,
        rollback_plan=rollback_plan,
        reviewed_runner=reviewed_runner,
    )
    receipt = materialize_local_package(inputs, tmp_path / "package")

    assert inputs.outcome_id == "phase13-fresh-test"
    assert inputs.source_backup_encrypted is True
    assert inputs.target_backup_encrypted is True
    assert inputs.merged_target_encrypted is True
    assert inputs.external_key_stored_separately is True
    assert inputs.source_full_backup == result.source_full_backup
    assert inputs.target_before_backup == result.target_before_backup
    assert inputs.merged_target_db == result.merged_target_db
    assert receipt.live_mutation_authorized is False
    assert receipt.plaintext_database_written is False


def test_bounded_process_enforces_timeout_output_and_input_limits() -> None:
    success = run_bounded_process(
        sys.executable,
        ("-c", "import sys;sys.stdout.buffer.write(sys.stdin.buffer.read())"),
        b"bounded-input",
        timeout_seconds=2,
        maximum_input_bytes=64,
        maximum_output_bytes=64,
    )
    assert success == b"bounded-input"

    with pytest.raises(FreshInputError, match="bounded process timeout"):
        run_bounded_process(
            sys.executable,
            ("-c", "import time;time.sleep(2)"),
            b"",
            timeout_seconds=0.05,
            maximum_input_bytes=64,
            maximum_output_bytes=64,
        )
    with pytest.raises(FreshInputError, match="bounded process output oversized"):
        run_bounded_process(
            sys.executable,
            ("-c", "import sys;sys.stdout.buffer.write(b'x'*65)"),
            b"",
            timeout_seconds=2,
            maximum_input_bytes=64,
            maximum_output_bytes=64,
        )
    with pytest.raises(FreshInputError, match="bounded process input oversized"):
        run_bounded_process(
            sys.executable,
            ("-c", "pass"),
            b"x" * 65,
            timeout_seconds=2,
            maximum_input_bytes=64,
            maximum_output_bytes=64,
        )


def test_fixed_transport_accepts_only_roles_and_has_no_target_override(
    tmp_path: Path,
) -> None:
    database = create_database(tmp_path / "fixed.sqlite3", "fixed")
    frames = {
        role: remote.build_role_frame(audit(role), role_files(database))
        for role in ("usa", "spain")
    }
    calls: list[tuple[str, tuple[str, ...], bytes]] = []

    def binding_loader(role: str) -> FixedRoleBinding:
        return FixedRoleBinding(
            role=role,
            target_host="fixed.example",
            target_user="operator",
            key_path=Path("C:/fixed/id_ed25519"),
            known_hosts_path=Path("C:/fixed/known_hosts"),
        )

    def process_runner(executable: str, arguments: tuple[str, ...], value: bytes, **_):
        calls.append((executable, arguments, value))
        role = "usa" if arguments[-1].endswith(" usa") else "spain"
        return frames[role]

    transport = FixedSshFreshInputTransport(
        fresh_collector_bytes=b"fresh-collector",
        audit_collector_bytes=b"audit-collector",
        binding_loader=binding_loader,
        process_runner=process_runner,
        ssh_executable="C:/fixed/ssh.exe",
    )

    assert transport("usa") == frames["usa"]
    assert transport("spain") == frames["spain"]
    assert len(calls) == 2
    assert all(call[0] == "C:/fixed/ssh.exe" for call in calls)
    assert all("BatchMode=yes" in call[1] for call in calls)
    assert all("StrictHostKeyChecking=yes" in call[1] for call in calls)
    assert all("fresh-collector" not in " ".join(call[1]) for call in calls)
    assert all(b"fixed.example" not in call[2] for call in calls)

    with pytest.raises(FreshInputError, match="fixed role invalid"):
        transport("operator-supplied-role")
    assert len(calls) == 2


def test_role_frame_requires_exact_application_data_allowlist(tmp_path: Path) -> None:
    database = create_database(tmp_path / "exact.sqlite3", "exact")
    with pytest.raises(remote.FreshRemoteError, match="archive member set"):
        remote.build_role_frame(audit("usa"), {"database.sqlite3": database})
    with pytest.raises(remote.FreshRemoteError, match="archive member set"):
        remote.build_role_frame(
            audit("usa"),
            {**role_files(database), "unexpected.txt": b"not-allowlisted"},
        )
