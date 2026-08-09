from __future__ import annotations

import base64
from dataclasses import replace
import hashlib
import importlib
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys

import pytest

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from scripts.phase10_recovery_crypto import encrypt_hybrid
from scripts.vps.phase13_bot_web_migration_fresh_input_remote import (
    deterministic_archive_bytes,
)


ROOT = Path(__file__).resolve().parents[1]
REMOTE = ROOT / "scripts/vps/phase13_bot_web_migration_production_stage_remote.py"
RUNNER = ROOT / "scripts/vps/phase13_bot_web_migration_production_stage_runner.ps1"
PACKAGE = ROOT / "scripts/phase13_bot_web_migration_production_stage_package.py"
REFERENCE_STAGE = ROOT / "scripts/vps/phase13_bot_web_migration_stage_remote.sh"
REFERENCE_CUTOVER = ROOT / "scripts/vps/phase13_bot_web_migration_cutover_remote.sh"

REFERENCE_STAGE_SHA256 = "934bd8daa52f53ef7e0622f47c8c00a5691903de75d3993e9b90f5facd9fb425"
REFERENCE_CUTOVER_SHA256 = "b8a2db9401baacd2adf3698b6285aaebd0524efa0542429548dee92dec91f2b3"


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def load_module(name: str, path: Path):
    assert path.is_file(), f"missing production file: {path.name}"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sqlite_bytes(label: str) -> bytes:
    connection = sqlite3.connect(":memory:")
    try:
        connection.executescript(
            "CREATE TABLE marker(id INTEGER PRIMARY KEY, value TEXT NOT NULL);"
            "INSERT INTO marker(value) VALUES (?);".replace("?", f"'{label}'")
        )
        return connection.serialize()
    finally:
        connection.close()


def body_for_remote() -> dict[str, object]:
    target = sqlite_bytes("target-before")
    merged = sqlite_bytes("merged")
    runtime_delta = b"sealed-runtime-delta"
    bot_unit = (
        b"[Unit]\nConditionPathExists=/etc/amn2-spain/bot-enabled\n"
        b"[Install]\nWantedBy=multi-user.target\n"
    )
    return {
        "audit": {
            "spain": {
                "bot_active": False,
                "database_integrity_ok": True,
                "foreign_key_violations": 0,
                "web_active": True,
                "web_loopback_only": True,
            },
            "usa": {"bot_active": True},
        },
        "bot_unit_b64": base64.b64encode(bot_unit).decode("ascii"),
        "bot_unit_sha256": sha256(bot_unit),
        "expires_at": "2099-08-08T18:00:00Z",
        "expected": {
            "awg2_foundation_sha256": "0e5a5926821d88ae4a2515f9e95cd7c3f69db52100c1a1ec74e99fb794222281",
            "foreign_receipt_sha256": "bc9065b3fa7cab40f5eefebbfd8093f2d62477e972777fe665e8d9f6028aa704",
            "foreign_stable_sha256": "f5767f361a9441dd4b5361c07da164a3059e0d1347d5217594534797d367b7e8",
            "merged_database_sha256": sha256(merged),
            "spain_invariants_sha256": "a" * 64,
            "target_before_database_sha256": sha256(target),
            "target_runtime_env_sha256": "b" * 64,
        },
        "manifest_sha256": "c" * 64,
        "max_attempts": 1,
        "merged_database_b64": base64.b64encode(merged).decode("ascii"),
        "outcome_id": "bot-web-stage-test-001",
        "runtime_delta_encrypted_b64": base64.b64encode(runtime_delta).decode("ascii"),
        "runtime_delta_encrypted_sha256": sha256(runtime_delta),
        "schema": "amn2.phase13.bot-web-production-stage-input.v1",
    }


def envelope_for_remote(body: dict[str, object] | None = None) -> bytes:
    payload = body or body_for_remote()
    return canonical(
        {
            "payload": payload,
            "payload_sha256": sha256(canonical(payload)),
            "schema": "amn2.phase13.bot-web-production-stage-envelope.v1",
        }
    )


class FakeBackend:
    def __init__(self, *, fail_at: str | None = None) -> None:
        body = body_for_remote()
        expected = body["expected"]
        assert isinstance(expected, dict)
        self.target_before = sqlite_bytes("target-before")
        self.merged = sqlite_bytes("merged")
        assert sha256(self.target_before) == expected["target_before_database_sha256"]
        assert sha256(self.merged) == expected["merged_database_sha256"]
        self.live_database = self.target_before
        self.web_active = True
        self.bot_active = False
        self.marker_present = False
        self.stage_complete = False
        self.fail_at = fail_at
        self.events: list[str] = []
        self.primary_rollback_failed = False

    def _event(self, name: str) -> None:
        self.events.append(name)
        if self.fail_at == name or (
            self.fail_at == "rollback" and name == "post_apply_verify"
        ):
            raise RuntimeError("synthetic failure must be sanitized")

    def preflight(self, _payload: dict[str, object]) -> None:
        self._event("preflight")

    def stage(self, _payload: dict[str, object]) -> None:
        self._event("stage")
        self.stage_complete = True

    def stop_web(self) -> None:
        self._event("web_stop")
        self.web_active = False

    def apply_database(self, merged: bytes) -> None:
        self._event("atomic_db_apply")
        self.live_database = merged

    def start_web(self) -> None:
        self._event("web_start")
        self.web_active = True

    def post_apply_verify(self, _payload: dict[str, object]) -> None:
        self._event("post_apply_verify")

    def rollback(self, _payload: dict[str, object]) -> None:
        self.events.append("rollback")
        if self.fail_at == "rollback" and not self.primary_rollback_failed:
            self.primary_rollback_failed = True
            raise RuntimeError("synthetic primary rollback failure")
        self.live_database = self.target_before
        self.web_active = True
        self.bot_active = False
        self.marker_present = False

    def emergency_restore(self, _payload: dict[str, object]) -> None:
        self.events.append("emergency_restore")
        self.live_database = self.target_before
        self.web_active = True
        self.bot_active = False
        self.marker_present = False

    def cleanup_pre_web_failure(self) -> None:
        self.events.append("cleanup_pre_web_failure")
        self.stage_complete = False

    def terminal_state(
        self, _payload: dict[str, object], expected_database_sha256: str
    ) -> dict[str, bool]:
        return {
            "awg2_equal": True,
            "bot_active": self.bot_active,
            "database_equal": sha256(self.live_database) == expected_database_sha256,
            "foreign_equal": True,
            "marker_present": self.marker_present,
            "web_active": self.web_active,
        }


def test_new_production_files_are_separate_and_reference_files_are_unchanged() -> None:
    assert REMOTE.is_file()
    assert RUNNER.is_file()
    assert PACKAGE.is_file()
    assert sha256(REFERENCE_STAGE.read_bytes()) == REFERENCE_STAGE_SHA256
    assert sha256(REFERENCE_CUTOVER.read_bytes()) == REFERENCE_CUTOVER_SHA256


def test_remote_success_has_exact_order_and_keeps_bot_disabled() -> None:
    module = load_module("phase13_production_stage_remote_success", REMOTE)
    backend = FakeBackend()
    receipt = module.execute_stage_web_data_apply(envelope_for_remote(), backend)
    assert receipt["outcome"] == "passed"
    assert receipt["stage"] == "post_apply_verify"
    assert backend.events == [
        "preflight",
        "stage",
        "web_stop",
        "atomic_db_apply",
        "web_start",
        "post_apply_verify",
    ]
    assert backend.live_database == backend.merged
    assert backend.web_active is True
    assert backend.bot_active is False
    assert backend.marker_present is False
    assert receipt["awg2_equal"] is True
    assert receipt["database_equal"] is True
    assert receipt["foreign_equal"] is True


@pytest.mark.parametrize(
    "failure_stage",
    ["preflight", "stage", "web_stop", "atomic_db_apply", "web_start", "post_apply_verify", "rollback"],
)
def test_every_remote_failure_boundary_is_fail_closed(failure_stage: str) -> None:
    module = load_module(f"phase13_production_stage_remote_{failure_stage}", REMOTE)
    backend = FakeBackend(fail_at=failure_stage)
    receipt = module.execute_stage_web_data_apply(envelope_for_remote(), backend)
    assert receipt["outcome"] == "failed"
    assert backend.live_database == backend.target_before
    assert backend.web_active is True
    assert backend.bot_active is False
    assert backend.marker_present is False
    assert receipt["database_equal"] is True
    assert receipt["web_active"] is True
    assert receipt["bot_active"] is False
    assert receipt["marker_present"] is False
    assert receipt["awg2_equal"] is True
    assert receipt["foreign_equal"] is True
    if failure_stage in {"preflight", "stage"}:
        assert "cleanup_pre_web_failure" in backend.events
    else:
        assert "rollback" in backend.events
    if failure_stage == "rollback":
        assert "emergency_restore" in backend.events


def test_package_verify_rejects_noncanonical_or_tampered_input_before_backend() -> None:
    module = load_module("phase13_production_stage_remote_tamper", REMOTE)
    backend = FakeBackend()
    envelope = json.loads(envelope_for_remote())
    envelope["payload"]["manifest_sha256"] = "d" * 64
    receipt = module.execute_stage_web_data_apply(canonical(envelope), backend)
    assert receipt["outcome"] == "failed"
    assert receipt["stage"] == "package_verify"
    assert backend.events == []
    assert receipt["database_equal"] is False
    assert receipt["web_active"] is False


def test_bot_disabled_rejects_enabled_inactive_unit(monkeypatch: pytest.MonkeyPatch) -> None:
    module = load_module("phase13_production_stage_bot_disabled", REMOTE)
    module.RealSpainBackend._service_values = classmethod(
        lambda _cls, _unit: {
            "ActiveState": "inactive",
            "MainPID": "0",
            "NRestarts": "0",
            "UnitFileState": "enabled",
        }
    )
    monkeypatch.setattr(module.os.path, "lexists", lambda _path: False)
    with pytest.raises(module.RemoteStageError, match="bot_not_disabled"):
        module.RealSpainBackend()._assert_bot_disabled()


def test_foreign_projection_matches_phase12_container_and_unit_receipt() -> None:
    module = load_module("phase13_production_stage_foreign_projection", REMOTE)
    unit_contents = {
        f"foreign-{index:03d}.service": (
            f"[Service]\nExecStart=/bin/true #{index}\n".encode()
        )
        for index in range(152)
    }
    rows = [
        {
            "active_state": "running",
            "image_or_unit_sha256": sha256(b"foreign-image"),
            "kind": "container",
            "name_sha256": sha256(b"foreign-container"),
            "restart_count": 0,
        }
    ]
    rows.extend(
        {
            "active_state": "active:running",
            "bound_port_status": "cgroup_complete",
            "image_or_unit_sha256": sha256(content.rstrip(b"\n")),
            "kind": "unit",
            "name_sha256": sha256(unit.encode()),
            "restart_count": 0,
            "unit_content_status": "exact",
        }
        for unit, content in unit_contents.items()
    )
    expected = sha256(
        json.dumps(
            sorted(rows, key=lambda row: (row["kind"], row["name_sha256"])),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )
    module.EXPECTED_FOREIGN_STABLE_SHA256 = expected
    module.RealSpainBackend._system_docker_available = classmethod(lambda _cls: True)

    def fake_run(_cls, arguments: tuple[str, ...], timeout: int = 15) -> bytes:
        del timeout
        if arguments[:3] == ("/usr/bin/docker", "ps", "-a"):
            return b"foreign-container|foreign-image|running\n"
        if arguments[:3] == ("/usr/bin/docker", "inspect", "--format"):
            return b"0\n"
        if "list-units" in arguments:
            return "".join(
                f"{unit} loaded active running Foreign unit\n"
                for unit in unit_contents
            ).encode()
        if "cat" in arguments:
            return unit_contents[arguments[2]]
        if "--property=NRestarts" in arguments:
            return b"0\n"
        if "--property=ControlGroup" in arguments:
            return f"/system.slice/{arguments[2]}\n".encode()
        raise AssertionError(arguments)

    module.RealSpainBackend._run = classmethod(fake_run)
    assert module.RealSpainBackend._foreign_snapshot() == expected
    unit_contents["foreign-017.service"] = b"[Service]\nExecStart=/bin/false\n"
    with pytest.raises(module.RemoteStageError, match="foreign_equality_mismatch"):
        module.RealSpainBackend._foreign_snapshot()


def test_foreign_projection_skips_absent_system_docker_and_intersects_two_snapshots() -> None:
    module = load_module("phase13_production_stage_foreign_persistent", REMOTE)
    persistent_units = {
        f"foreign-{index:03d}.service": f"[Service]\nExecStart=/bin/true #{index}\n".encode()
        for index in range(153)
    }
    transient_unit = "transient-observer.service"
    all_contents = {
        **persistent_units,
        transient_unit: b"[Service]\nExecStart=/bin/true #transient\n",
    }
    rows = [
        {
            "active_state": "active:running",
            "bound_port_status": "cgroup_complete",
            "image_or_unit_sha256": sha256(content.rstrip(b"\n")),
            "kind": "unit",
            "name_sha256": sha256(unit.encode()),
            "restart_count": 0,
            "unit_content_status": "exact",
        }
        for unit, content in persistent_units.items()
    ]
    expected = sha256(
        json.dumps(
            sorted(rows, key=lambda row: (row["kind"], row["name_sha256"])),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )
    module.EXPECTED_FOREIGN_STABLE_SHA256 = expected
    module.RealSpainBackend._system_docker_available = classmethod(lambda _cls: False)
    list_calls = 0

    def fake_run(_cls, arguments: tuple[str, ...], timeout: int = 15) -> bytes:
        nonlocal list_calls
        del timeout
        if arguments and arguments[0] == "/usr/bin/docker":
            raise AssertionError("absent system Docker must not be invoked")
        if "list-units" in arguments:
            list_calls += 1
            units = list(persistent_units)
            if list_calls == 1:
                units.append(transient_unit)
            return "".join(
                f"{unit} loaded active running Foreign unit\n" for unit in units
            ).encode()
        if "cat" in arguments:
            return all_contents[arguments[2]]
        if "--property=NRestarts" in arguments:
            return b"0\n"
        if "--property=ControlGroup" in arguments:
            return f"/system.slice/{arguments[2]}\n".encode()
        raise AssertionError(arguments)

    module.RealSpainBackend._run = classmethod(fake_run)

    assert module.RealSpainBackend._foreign_snapshot() == expected
    assert list_calls == 2


@pytest.mark.parametrize(
    ("extra_chain", "should_fail"),
    (("forward", True), ("prerouting", False)),
)
def test_awg_projection_rejects_only_a_fourth_tagged_forward_rule(
    extra_chain: str, should_fail: bool
) -> None:
    module = load_module("phase13_production_stage_awg_rule_count", REMOTE)
    peers = tuple(f"{chr(65 + index) * 43}=" for index in range(7))

    def fake_run(_cls, arguments: tuple[str, ...], timeout: int = 15) -> bytes:
        del timeout
        if "inspect" in arguments:
            return json.dumps(
                [
                    {
                        "Image": "sha256:" + "1" * 64,
                        "HostConfig": {
                            "NetworkMode": "amn2-spain-net",
                            "Sysctls": {},
                        },
                        "RestartCount": 59,
                        "State": {"Running": True},
                    }
                ]
            ).encode()
        if "peers" in arguments:
            return ("\n".join(peers) + "\n").encode()
        if "listen-port" in arguments:
            return b"30001\n"
        if "sysctl" in arguments:
            return b"1\n"
        if arguments[:4] == ("/usr/sbin/ip", "-j", "route", "show"):
            return b'[{"dst":"10.212.12.0/24","dev":"amn2spbr0"}]'
        rules = [
            {"chain": "forward", "comment": "amn2_spain:forward-dnat"},
            {"chain": "forward", "comment": "amn2_spain:forward-outbound"},
            {"chain": "forward", "comment": "amn2_spain:forward-return"},
            {"chain": extra_chain, "comment": "amn2_spain:unexpected-fourth"},
        ]
        return json.dumps(
            {"nftables": [{"rule": value} for value in rules]}
        ).encode()

    module.RealSpainBackend._run = classmethod(fake_run)
    module.RealSpainBackend._persistent_peer_set = classmethod(lambda _cls: peers)
    module.RealSpainBackend._service_values = classmethod(
        lambda _cls, _unit: {
            "ActiveState": "active",
            "MainPID": "1",
            "NRestarts": "0",
            "UnitFileState": "enabled",
        }
    )
    if should_fail:
        with pytest.raises(module.RemoteStageError, match="awg2_equality_mismatch"):
            module.RealSpainBackend._awg_snapshot()
    else:
        assert len(module.RealSpainBackend._awg_snapshot()) == 64


def test_remote_main_installs_fail_closed_signal_guards() -> None:
    source = REMOTE.read_text(encoding="utf-8")
    assert "signal.SIGHUP" in source
    assert "signal.SIGTERM" in source
    assert "with _fail_closed_signal_guard():" in source


def powershell_executable() -> str:
    executable = shutil.which("powershell") or shutil.which("pwsh")
    if executable is None:
        pytest.skip("PowerShell is unavailable")
    return executable


def run_powershell(script: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            powershell_executable(),
            "-NoProfile",
            "-NonInteractive",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            script,
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8-sig",
        errors="strict",
        timeout=40,
    )


def run_pwsh(script: str) -> subprocess.CompletedProcess[str]:
    executable = shutil.which("pwsh")
    if executable is None:
        pytest.skip("PowerShell 7 is unavailable")
    return subprocess.run(
        [
            executable,
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            script,
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8-sig",
        errors="strict",
        timeout=40,
    )


def ps_literal(value: Path | str) -> str:
    return str(value).replace("'", "''")


def test_public_entrypoint_has_only_package_root_and_exact_approval() -> None:
    assert RUNNER.is_file()
    script = f"""
. '{ps_literal(RUNNER)}'
@((Get-Command Invoke-Phase13ProductionStageWebDataApply).Parameters.Keys | Sort-Object) -join ','
"""
    result = run_powershell(script)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "ExactApprovalPhrase,PackageRoot"


def test_runner_source_forbids_override_scp_retry_and_extra_process_paths() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    public = source[source.index("function Invoke-Phase13ProductionStageWebDataApply") :]
    for forbidden in (
        "TargetHost",
        "TargetUser",
        "KeyPath",
        "KnownHostsPath",
        "Port",
        "RemotePath",
        "Service",
        "Mode",
    ):
        assert f"${forbidden}" not in public
    assert "scp" not in source.lower()
    assert "ConnectionAttempts=1" in source
    assert "ExpectedSshProcessCount = 3" in source
    assert "New-Phase13ProductionStageOutcomeClaim" in source
    assert source.index("New-Phase13ProductionStageOutcomeClaim") < source.index(
        "Invoke-Phase13ProductionStageAuditTransport"
    )


def test_package_contract_uses_existing_manifest_and_failure_schemas_only() -> None:
    module = load_module("phase13_production_stage_package_contract", PACKAGE)
    assert module.MANIFEST_SCHEMA_ID == "amn2.phase13.bot-web-migration-manifest.v1"
    assert module.FAILURE_SCHEMA_ID == "amn2.phase13.bot-web-migration-failure.v1"
    assert not any(
        path.name.endswith("production-stage.schema.json")
        for path in (ROOT / "packaging/phase13-bot-web-migration").iterdir()
    )


def test_materializer_verifies_decrypted_merged_plaintext_binding() -> None:
    module = load_module("phase13_production_stage_merged_binding", PACKAGE)
    merged = sqlite_bytes("merged-binding")
    logical_result_sha256 = "0" * 64
    assert logical_result_sha256 != sha256(merged)
    assert module._verified_merged_database_sha256(merged) == sha256(merged)
    with pytest.raises(module.ProductionPackageError, match="merged database invalid"):
        module._verified_merged_database_sha256(b"not-a-sqlite-database")


def rsa_pair() -> tuple[bytes, bytes]:
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
    return private, public


def prepared_package_inputs(module):
    private, public = rsa_pair()
    source_database = sqlite_bytes("source")
    target_database = sqlite_bytes("target-before")
    merged_database = sqlite_bytes("merged")
    source_archive = deterministic_archive_bytes(
        {
            "database.sqlite3": source_database,
            "runtime.env": (
                b"TELEGRAM_BOT_TOKEN=synthetic-token\n"
                b"ADMIN_TELEGRAM_IDS=1001,1002\n"
            ),
            "server-config.yml": b"servers: []\n",
        }
    )
    target_runtime = (
        b"TELEGRAM_BOT_TOKEN=old-target-token\n"
        b"ADMIN_TELEGRAM_IDS=9\n"
        b"APP_SECRET_KEY=target-app-secret\n"
        b"WEB_ADMIN_PASSWORD_HASH=target-password-hash\n"
        b"WEB_ADMIN_SESSION_SECRET=target-session-secret\n"
    )
    target_archive = deterministic_archive_bytes(
        {
            "database.sqlite3": target_database,
            "runtime.env": target_runtime,
            "server-config.yml": b"servers: []\n",
        }
    )
    source_encrypted = encrypt_hybrid(source_archive, public)
    target_encrypted = encrypt_hybrid(target_archive, public)
    merged_encrypted = encrypt_hybrid(merged_database, public)
    runtime_delta = encrypt_hybrid(
        b"TELEGRAM_BOT_TOKEN=synthetic-token\nADMIN_TELEGRAM_IDS=1001,1002\n",
        public,
    )
    source_manifest = canonical(
        {
            "artifacts": {
                "source-full-backup.enc": {
                    "role": "usa",
                    "sha256": sha256(source_encrypted),
                    "size": len(source_encrypted),
                },
                "target-before-backup.enc": {
                    "role": "spain",
                    "sha256": sha256(target_encrypted),
                    "size": len(target_encrypted),
                },
            },
            "created_at": "2026-08-08T17:00:00Z",
            "expires_at": "2026-08-08T18:00:00Z",
            "outcome_id": "bot-web-fresh-test-001",
            "remote_collection_completed": True,
            "safety": {
                "live_mutation": False,
                "plaintext_persisted": False,
                "service_action": False,
                "usa_release": False,
            },
            "ssh_process_count": 2,
        }
    )
    preview = canonical(
        {
            "api_tokens_reissue_required": 1,
            "apply_allowed": True,
            "invariant_hashes": {
                "devices": "1" * 64,
                "passports": "2" * 64,
                "servers": "3" * 64,
            },
            "spain_devices_preserved": 7,
            "spain_passports_preserved": 7,
            "stop_reasons": [],
            "target_privileged_users_preserved": 1,
            "usable_secret_records_imported": 0,
        }
    )
    merge_claim = canonical(
        {
            "created_at": "2026-08-08T17:10:00Z",
            "expires_at": "2026-08-08T18:00:00Z",
            "heads": {"amn2": module.AMN2_HEAD, "tooling": module.ROOT_BASE_HEAD},
            "max_attempts": 1,
            "network_authorized": False,
            "outcome_id": "bot-web-merge-test-001",
            "source_outcome": "bot-web-fresh-test-001",
        }
    )
    merge_receipt = canonical(
        {
            "artifacts": {
                "merge-preview.json": {
                    "sha256": sha256(preview),
                    "size": len(preview),
                },
                "merged-target.sqlite3.enc": {
                    "sha256": sha256(merged_encrypted),
                    "size": len(merged_encrypted),
                },
            },
            "foreign_key_issues": 0,
            "integrity_ok": True,
            "live_mutation": False,
            "merge_result_sha256": sha256(merged_database),
            "network_started": False,
            "outcome_id": "bot-web-merge-test-001",
            "plaintext_persisted": False,
            "preview_sha256": sha256(preview),
            "remote_collection_completed": True,
            "schema": "amn2.phase13.bot-web-local-merge-receipt.v1",
            "source_outcome": "bot-web-fresh-test-001",
            "spain_d1_d7_preserved": True,
            "spain_target_privileges_preserved": True,
            "status": "success",
            "usable_secret_records_imported": 0,
        }
    )
    source_evidence = canonical(
        {
            "database_integrity_ok": True,
            "foreign_key_violations": 0,
            "role": "usa-source",
            "schema": "amn2.phase13.bot-web-package-evidence.v1",
        }
    )
    target_evidence = canonical(
        {
            "database_integrity_ok": True,
            "foreign_key_violations": 0,
            "role": "spain-target",
            "schema": "amn2.phase13.bot-web-package-evidence.v1",
        }
    )
    tooling = {
        "amn2-spain-bot.service": (
            b"[Unit]\nConditionPathExists=/etc/amn2-spain/bot-enabled\n"
            b"[Install]\nWantedBy=multi-user.target\n"
        ),
        "audit-ssh-runner.ps1": b"function Invoke-Audit { 'fixture' }\n",
        "failure-evidence.schema.json": (
            ROOT / "packaging/phase13-bot-web-migration/failure-evidence.schema.json"
        ).read_bytes(),
        "manifest.schema.json": (
            ROOT / "packaging/phase13-bot-web-migration/manifest.schema.json"
        ).read_bytes(),
        "production-stage-package.py": b"# package fixture\n",
        "production-stage-remote.py": b"# remote fixture\n",
        "production-stage-runner.ps1": b"# runner fixture\n",
        "readonly-collector.py": b"# collector fixture\n",
        "recovery_crypto.py": b"# crypto fixture\n",
    }
    inputs = module.PreparedStagePackageInputs(
        amn2_head=module.AMN2_HEAD,
        created_at="2026-08-08T17:30:00Z",
        expires_at="2099-08-08T18:30:00Z",
        merge_claim=merge_claim,
        merge_preview=preview,
        merge_receipt=merge_receipt,
        merged_database_sha256=sha256(merged_database),
        merged_target_db=merged_encrypted,
        outcome_id="bot-web-spain-stage-test-001",
        recovery_private_key_pem=private,
        root_base_head=module.ROOT_BASE_HEAD,
        runtime_delta_encrypted=runtime_delta,
        source_evidence=source_evidence,
        source_full_backup=source_encrypted,
        source_input_manifest=source_manifest,
        source_outcome_id="bot-web-fresh-test-001",
        spain_invariants_sha256=sha256(
            canonical(json.loads(preview)["invariant_hashes"])
        ),
        target_before_backup=target_encrypted,
        target_before_database_sha256=sha256(target_database),
        target_evidence=target_evidence,
        target_runtime_env_sha256=sha256(target_runtime),
        tooling_artifacts=tooling,
        tooling_head="f" * 40,
    )
    return inputs, private


def test_prepared_package_is_canonical_bound_and_deterministic(tmp_path: Path) -> None:
    module = load_module("phase13_production_stage_package_materialize", PACKAGE)
    inputs, _private = prepared_package_inputs(module)
    first = module.materialize_prepared_package(inputs, tmp_path / "first")
    second = module.materialize_prepared_package(inputs, tmp_path / "second")
    assert first.manifest_sha256 == second.manifest_sha256
    assert first.artifact_sha256 == second.artifact_sha256
    binding = module.verify_local_package(
        first.output_root, now="2026-08-08T17:31:00Z"
    )
    assert binding["max_attempts"] == 1
    assert binding["expected_ssh_processes"] == 3
    assert binding["live_mutation_authorized"] is False
    assert not any("PRIVATE KEY" in path.read_text(errors="ignore") for path in first.output_root.iterdir())


def test_payload_builder_decrypts_in_memory_and_emits_only_bound_remote_envelope(
    tmp_path: Path,
) -> None:
    module = load_module("phase13_production_stage_package_payload", PACKAGE)
    inputs, private = prepared_package_inputs(module)
    receipt = module.materialize_prepared_package(inputs, tmp_path / "package")
    audit_pair = canonical(
        {
            "audits": [
                {
                    "database": {"foreign_key_violations": 0, "integrity_ok": True},
                    "role": "usa-source",
                    "services": {"bot_active": True, "web_active": True, "web_loopback_only": True},
                },
                {
                    "database": {"foreign_key_violations": 0, "integrity_ok": True},
                    "role": "spain-target",
                    "services": {"bot_active": False, "web_active": True, "web_loopback_only": True},
                },
            ],
            "safety_receipt": {"raw_secret_emitted": False, "ssh_processes": 2},
            "schema": "amn2.phase13.bot-web-audit-pair.v1",
        }
    )
    envelope = module.build_remote_envelope(
        receipt.output_root,
        audit_pair,
        private,
        now="2026-08-08T17:31:00Z",
    )
    parsed = json.loads(envelope)
    assert parsed["payload"]["max_attempts"] == 1
    assert sha256(canonical(parsed["payload"])) == parsed["payload_sha256"]
    assert len(envelope) <= 1024 * 1024
    filenames = {path.name for path in receipt.output_root.iterdir()}
    assert not any(name.endswith(".sqlite3") or name.endswith(".env") for name in filenames)
    assert b"synthetic-token" not in b"".join(
        path.read_bytes() for path in receipt.output_root.iterdir()
    )


def production_tooling() -> dict[str, bytes]:
    return {
        "amn2-spain-bot.service": (
            ROOT / "packaging/phase12-spain/units/amn2-spain-bot.service"
        ).read_bytes(),
        "audit-ssh-runner.ps1": (
            ROOT / "scripts/vps/phase13_bot_web_migration_ssh_runner.ps1"
        ).read_bytes(),
        "failure-evidence.schema.json": (
            ROOT / "packaging/phase13-bot-web-migration/failure-evidence.schema.json"
        ).read_bytes(),
        "manifest.schema.json": (
            ROOT / "packaging/phase13-bot-web-migration/manifest.schema.json"
        ).read_bytes(),
        "production-stage-package.py": PACKAGE.read_bytes(),
        "production-stage-remote.py": REMOTE.read_bytes(),
        "production-stage-runner.ps1": RUNNER.read_bytes(),
        "readonly-collector.py": (
            ROOT / "scripts/vps/phase13_bot_web_migration_readonly_remote.py"
        ).read_bytes(),
        "recovery_crypto.py": (ROOT / "scripts/phase10_recovery_crypto.py").read_bytes(),
    }


def write_production_fake_ssh(path: Path) -> None:
    path.write_text(
        """from __future__ import annotations
import base64, hashlib, hmac, json, pathlib, sys
counter = pathlib.Path(sys.argv[1])
claim = pathlib.Path(sys.argv[2])
fail_at = sys.argv[3]
remote_command = sys.argv[-1]
if not claim.is_file():
    raise SystemExit(41)
if remote_command.endswith(' usa'):
    role = 'usa'
elif remote_command.endswith(' spain'):
    role = 'spain'
else:
    role = 'stage'
with counter.open('a', encoding='utf-8') as handle:
    handle.write(role + '\\n')
if role == fail_at:
    sys.stderr.write('raw-secret-sentinel')
    raise SystemExit(255)
if fail_at == role + '-127':
    raise SystemExit(127)
if fail_at == role + '-42':
    raise SystemExit(42)
envelope = json.loads(sys.stdin.buffer.read())
if role == 'stage':
    payload = envelope['payload']
    receipt = {
        'awg2_equal': True,
        'bot_active': False,
        'database_equal': True,
        'foreign_equal': True,
        'marker_present': False,
        'outcome': 'passed',
        'outcome_id': payload['payload']['outcome_id'],
        'raw_output_persisted': False,
        'reason': 'none',
        'rolled_back': False,
        'schema': 'amn2.phase13.bot-web-production-stage-receipt.v1',
        'stage': 'post_apply_verify',
        'web_active': True,
    }
    sys.stdout.write(json.dumps(receipt, sort_keys=True, separators=(',', ':')) + '\\n')
    raise SystemExit(0)
key = base64.b64decode(envelope['ephemeral_hmac_key_b64'], validate=True)
collector = base64.b64decode(envelope['collector_b64'], validate=True)
if hashlib.sha256(collector).hexdigest() != envelope['collector_sha256']:
    raise SystemExit(42)
references = {
    'telegram_bot_token': 'same-token',
    'app_secret_key': role + '-app-secret',
    'web_password_hash': role + '-password',
    'web_session_secret': role + '-session',
}
proof = {name: hmac.new(key, value.encode(), hashlib.sha256).hexdigest()
         for name, value in references.items()}
audit_role = 'usa-source' if role == 'usa' else 'spain-target'
document = {
    'schema': 'amn2.phase13.bot-web-collector.v1',
    'role': role,
    'audit': {
        'schema': 'amn2.phase13.bot-web-audit.v1',
        'role': audit_role,
        'checked_at': '2026-08-08T17:31:00Z',
        'services': {'web_active': True, 'bot_active': role == 'usa',
                     'web_loopback_only': True},
        'database': {'integrity_ok': True, 'foreign_key_violations': 0,
                     'table_count': 2, 'schema_sha256': 'a' * 64,
                     'counts_sha256': 'b' * 64},
        'environment': {'telegram_bot_token_present': True,
                        'app_secret_present': True,
                        'web_password_hash_present': True,
                        'session_secret_present': True},
        'required_artifacts': {'database_readable': True,
                               'environment_reference_proof_available': True},
        'safety_receipt': {'mutation_attempted': False,
                           'raw_output_persisted': False,
                           'secret_bearing_data_persisted': False},
    },
    'secret_reference_hmac': proof,
}
sys.stdout.write(json.dumps(document, sort_keys=True, separators=(',', ':')) + '\\n')
""",
        encoding="utf-8",
    )


def materialize_production_package(tmp_path: Path):
    module = load_module("phase13_production_stage_runner_fixture", PACKAGE)
    inputs, private = prepared_package_inputs(module)
    inputs = replace(inputs, tooling_artifacts=production_tooling())
    receipt = module.materialize_prepared_package(inputs, tmp_path / "package")
    approval = module.exact_approval_phrase(
        receipt.output_root, now="2026-08-08T17:31:00Z"
    )
    audit_pair = canonical(
        {
            "audits": [
                {
                    "database": {"foreign_key_violations": 0, "integrity_ok": True},
                    "role": "usa-source",
                    "services": {
                        "bot_active": True,
                        "web_active": True,
                        "web_loopback_only": True,
                    },
                },
                {
                    "database": {"foreign_key_violations": 0, "integrity_ok": True},
                    "role": "spain-target",
                    "services": {
                        "bot_active": False,
                        "web_active": True,
                        "web_loopback_only": True,
                    },
                },
            ],
            "safety_receipt": {"raw_secret_emitted": False, "ssh_processes": 2},
            "schema": "amn2.phase13.bot-web-audit-pair.v1",
        }
    )
    payload = module.build_remote_envelope(
        receipt.output_root,
        audit_pair,
        private,
        now="2026-08-08T17:31:00Z",
    )
    return receipt, approval, payload


@pytest.mark.parametrize("culture", ["ru-RU", "en-US"])
def test_exact_approval_expiry_is_canonical_utc_across_cultures(
    tmp_path: Path, culture: str
) -> None:
    receipt, approval, _payload = materialize_production_package(tmp_path)
    canonical_expiry = "2099-08-08T18:30:00Z"
    assert f"EXPIRES_AT_{canonical_expiry}" in approval
    localized_approval = approval.replace(
        f"EXPIRES_AT_{canonical_expiry}",
        "EXPIRES_AT_08/08/2099 18:30:00",
    )
    script = f"""
. '{ps_literal(RUNNER)}'
[Globalization.CultureInfo]::CurrentCulture = [Globalization.CultureInfo]::GetCultureInfo('{culture}')
[Globalization.CultureInfo]::CurrentUICulture = [Globalization.CultureInfo]::GetCultureInfo('{culture}')
$binding = Test-Phase13ProductionStagePackage -PackageRoot '{ps_literal(receipt.output_root)}' -ExactApprovalPhrase '{approval.replace("'", "''")}' -NowUtc ([DateTimeOffset]'2026-08-08T17:31:00Z')
$localized = 'accepted'
try {{
    $null = Test-Phase13ProductionStagePackage -PackageRoot '{ps_literal(receipt.output_root)}' -ExactApprovalPhrase '{localized_approval.replace("'", "''")}' -NowUtc ([DateTimeOffset]'2026-08-08T17:31:00Z')
}} catch {{
    $localized = 'rejected'
}}
[Console]::Out.Write((@{{ expires_at=$binding.ExpiresAt; localized=$localized }} | ConvertTo-Json -Compress))
"""
    result = run_pwsh(script)
    assert result.returncode == 0, result.stderr
    document = json.loads(result.stdout)
    assert document == {"expires_at": canonical_expiry, "localized": "rejected"}


@pytest.mark.parametrize(
    ("fail_at", "expected_processes", "expected_role", "expected_subreason"),
    [
        ("none", ["usa", "spain", "stage"], "not_applicable", "not_applicable"),
        ("usa", ["usa", "spain"], "usa", "ssh_client_failure"),
        ("spain", ["usa", "spain"], "spain", "ssh_client_failure"),
        ("usa-127", ["usa", "spain"], "usa", "remote_command_unavailable"),
        ("usa-42", ["usa", "spain"], "usa", "remote_exit_unclassified"),
    ],
)
def test_claim_precedes_exact_three_process_chain_and_failures_are_sanitized(
    tmp_path: Path,
    fail_at: str,
    expected_processes: list[str],
    expected_role: str,
    expected_subreason: str,
) -> None:
    receipt, approval, payload = materialize_production_package(tmp_path)
    outcome_root = tmp_path / "outcomes"
    outcome_root.mkdir()
    counter = tmp_path / "counter.txt"
    fake_ssh = tmp_path / "fake_ssh.py"
    write_production_fake_ssh(fake_ssh)
    claim = outcome_root / f"{receipt.outcome_id}.claim.json"
    invocation = f"""
. '{ps_literal(RUNNER)}'
$binding = Test-Phase13ProductionStagePackage -PackageRoot '{ps_literal(receipt.output_root)}' -ExactApprovalPhrase '{approval.replace("'", "''")}' -NowUtc ([DateTimeOffset]'2026-08-08T17:31:00Z')
$roles = @{{
    usa = [pscustomobject]@{{ TargetHost='usa.test'; TargetUser='operator'; KeyPath='fixed-key'; KnownHostsPath='fixed-known-hosts' }}
    spain = [pscustomobject]@{{ TargetHost='spain.test'; TargetUser='operator'; KeyPath='fixed-key'; KnownHostsPath='fixed-known-hosts' }}
}}
$result = Invoke-Phase13ProductionStageCore -Binding $binding -PackageRoot '{ps_literal(receipt.output_root)}' -OutcomeRoot '{ps_literal(outcome_root)}' -SshExecutable '{ps_literal(sys.executable)}' -SshPrefixArguments @('{ps_literal(fake_ssh)}','{ps_literal(counter)}','{ps_literal(claim)}','{fail_at}') -RoleBindings $roles -PreparedPayloadBytes ([Convert]::FromBase64String('{base64.b64encode(payload).decode("ascii")}')) -NowUtc ([DateTimeOffset]'2026-08-08T17:31:00Z')
$public = ConvertTo-Phase13ProductionStagePublicReceipt -CoreResult $result -OutcomeId $binding.OutcomeId
$text = [IO.File]::ReadAllText($result.OutcomePath)
[Console]::Out.Write((@{{ failure_role=$public.FailureRole; failure_subreason=$public.FailureSubreason; status=$result.Status; processes=@([IO.File]::ReadAllLines('{ps_literal(counter)}')); text=$text }} | ConvertTo-Json -Depth 8 -Compress))
"""
    result = run_powershell(invocation)
    assert result.returncode == 0, result.stderr
    document = json.loads(result.stdout)
    assert document["processes"] == expected_processes
    assert "raw-secret-sentinel" not in document["text"]
    if fail_at == "none":
        assert document["status"] == "success"
        assert document["failure_role"] == expected_role
        assert document["failure_subreason"] == expected_subreason
        assert json.loads(document["text"])["outcome"] == "passed"
    else:
        assert document["status"] == "failure"
        assert document["failure_role"] == expected_role
        assert document["failure_subreason"] == expected_subreason
        failure = json.loads(document["text"])
        assert failure["decision"] == "stop"
        assert failure["reason_code"] == "audit_incomplete"


def test_audit_transport_classifies_invalid_frame_without_raw_output() -> None:
    invocation = f"""
. '{ps_literal(RUNNER)}'
function Invoke-Phase13BoundedProcess {{
    return [pscustomobject]@{{
        Document = '{{invalid-frame'
        ExitCode = 0
        Reason = 'success'
    }}
}}
$binding = [pscustomobject]@{{
    CollectorBytes = [Text.Encoding]::UTF8.GetBytes('fixture')
    CollectorSha256 = '0' * 64
}}
$roles = @{{
    usa = [pscustomobject]@{{ TargetHost='usa.test'; TargetUser='operator'; KeyPath='fixed-key'; KnownHostsPath='fixed-known-hosts' }}
    spain = [pscustomobject]@{{ TargetHost='spain.test'; TargetUser='operator'; KeyPath='fixed-key'; KnownHostsPath='fixed-known-hosts' }}
}}
$result = Invoke-Phase13ProductionStageAuditTransport -Binding $binding -SshExecutable 'fake' -RoleBindings $roles
[Console]::Out.Write((@{{
    failure_role = $result.FailureRole
    failure_subreason = $result.FailureSubreason
    success = $result.Success
}} | ConvertTo-Json -Compress))
"""

    result = run_powershell(invocation)

    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    assert json.loads(result.stdout) == {
        "failure_role": "usa",
        "failure_subreason": "frame_invalid",
        "success": False,
    }


@pytest.mark.parametrize(
    ("exit_code", "expected_subreason"),
    [
        (74, "collector_failed"),
        (75, "collector_environment_failed"),
        (76, "collector_services_failed"),
        (77, "collector_database_failed"),
        (78, "collector_listener_failed"),
        (79, "collector_health_failed"),
        (80, "collector_output_failed"),
    ],
)
def test_audit_transport_maps_collector_stage_exit_codes_without_raw_output(
    exit_code: int, expected_subreason: str
) -> None:
    invocation = f"""
. '{ps_literal(RUNNER)}'
$subreason = Get-Phase13ProductionStageAuditTransportSubreason -Reason 'process_failure' -ExitCode {exit_code}
[Console]::Out.Write($subreason)
"""

    result = run_powershell(invocation)

    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    assert result.stdout == expected_subreason


@pytest.mark.parametrize(
    "subreason",
    [
        "collector_failed",
        "collector_environment_failed",
        "collector_services_failed",
        "collector_database_failed",
        "collector_listener_failed",
        "collector_health_failed",
        "collector_output_failed",
    ],
)
def test_public_receipt_accepts_only_closed_collector_stage_subreasons(
    tmp_path: Path, subreason: str
) -> None:
    outcome = tmp_path / "failure.json"
    outcome.write_text("{}\n", encoding="utf-8")
    invocation = f"""
. '{ps_literal(RUNNER)}'
$core = [pscustomobject]@{{
    FailureRole = 'usa'
    FailureSubreason = '{subreason}'
    OutcomePath = '{ps_literal(outcome)}'
    ProcessCount = 2
    Status = 'failure'
}}
$public = ConvertTo-Phase13ProductionStagePublicReceipt -CoreResult $core -OutcomeId 'outcome-test'
[Console]::Out.Write($public.FailureSubreason)
"""

    result = run_powershell(invocation)

    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    assert result.stdout == subreason


@pytest.mark.parametrize(
    ("failure_message", "expected_role", "expected_subreason"),
    [
        (
            "collector envelope invalid",
            "not_applicable",
            "audit_collector_envelope_invalid",
        ),
        (
            "ephemeral proof invalid",
            "not_applicable",
            "audit_ephemeral_proof_invalid",
        ),
        ("usa audit invalid", "usa", "audit_usa_projection_invalid"),
        ("spain audit invalid", "spain", "audit_spain_projection_invalid"),
        ("usa audit identity invalid", "usa", "audit_usa_identity_invalid"),
        ("usa audit schema invalid", "usa", "audit_usa_schema_invalid"),
        ("usa audit role invalid", "usa", "audit_usa_role_invalid"),
        ("usa audit checked_at invalid", "usa", "audit_usa_checked_at_invalid"),
        ("usa audit database invalid", "usa", "audit_usa_database_invalid"),
        ("usa audit safety invalid", "usa", "audit_usa_safety_invalid"),
        ("usa audit boolean invalid", "usa", "audit_usa_boolean_invalid"),
        ("spain audit identity invalid", "spain", "audit_spain_identity_invalid"),
        ("spain audit schema invalid", "spain", "audit_spain_schema_invalid"),
        ("spain audit role invalid", "spain", "audit_spain_role_invalid"),
        (
            "spain audit checked_at invalid",
            "spain",
            "audit_spain_checked_at_invalid",
        ),
        ("spain audit database invalid", "spain", "audit_spain_database_invalid"),
        ("spain audit safety invalid", "spain", "audit_spain_safety_invalid"),
        ("spain audit boolean invalid", "spain", "audit_spain_boolean_invalid"),
        (
            "raw-secret-sentinel",
            "not_applicable",
            "audit_pair_internal_failure",
        ),
    ],
)
def test_audit_pair_failure_mapping_is_closed_and_secret_safe(
    failure_message: str, expected_role: str, expected_subreason: str
) -> None:
    invocation = f"""
. '{ps_literal(RUNNER)}'
$result = Get-Phase13ProductionStageAuditPairFailure -FailureMessage '{failure_message}'
[Console]::Out.Write((@{{ role=$result.Role; subreason=$result.Subreason }} | ConvertTo-Json -Compress))
"""

    result = run_powershell(invocation)

    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    assert json.loads(result.stdout) == {
        "role": expected_role,
        "subreason": expected_subreason,
    }
    assert "raw-secret-sentinel" not in result.stdout
