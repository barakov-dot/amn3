from __future__ import annotations

import base64
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
import io
from pathlib import Path
import sys
import tarfile

import pytest


ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / "scripts/phase13_spain_bot_runtime_stage.py"
REMOTE = ROOT / "scripts/vps/phase13_spain_bot_runtime_stage_remote.py"
FOUNDATION = ROOT / "scripts/vps/phase13_bot_web_migration_production_stage_remote.py"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def canonical(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode()


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def future() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0) + timedelta(hours=2)


def package_inputs(module):
    proof = canonical(
        {
            "accepted_source_head": module.ACCEPTED_SPAIN_SOURCE_HEAD,
            "bot_web_runtime_equal": True,
            "changed_paths": sorted(module.EXPECTED_MIGRATION_ONLY_DIFF),
            "migration_head": module.AMN2_MIGRATION_HEAD,
            "schema": module.SOURCE_PROOF_SCHEMA,
        }
    )
    source_manifest = canonical(
        {
            "files": {
                "app/bot/example.py": {"sha256": "1" * 64, "size": 1},
                "app/web/example.py": {"sha256": "2" * 64, "size": 1},
            },
            "head": module.ACCEPTED_SPAIN_SOURCE_HEAD,
            "schema": module.SOURCE_MANIFEST_SCHEMA,
        }
    )
    return module.RuntimeStagePackageInputs(
        outcome_id="spain-bot-runtime-stage-test-001",
        expires_at=future(),
        tooling_head="a" * 40,
        runner_bytes=b"runner-bytes",
        remote_bytes=b"remote-bytes",
        foundation_bytes=b"foundation-bytes",
        recovery_crypto_bytes=b"crypto-bytes",
        runtime_delta_encrypted=b"encrypted-runtime-delta",
        source_proof=proof,
        source_manifest=source_manifest,
        bot_unit_bytes=b"[Unit]\nConditionPathExists=/etc/amn2-spain/bot-enabled\n",
    )


def test_red_modules_exist() -> None:
    assert LOCAL.is_file()
    assert REMOTE.is_file()


def test_package_is_strict_checksum_bound_and_deterministic(tmp_path: Path) -> None:
    module = load("phase13_runtime_stage_package", LOCAL)
    inputs = package_inputs(module)
    first = module.materialize_runtime_stage_package(inputs, tmp_path / "first")
    second = module.materialize_runtime_stage_package(inputs, tmp_path / "second")

    first_binding = module.verify_local_runtime_stage_package(
        first.package_root, now=datetime.now(timezone.utc)
    )
    second_binding = module.verify_local_runtime_stage_package(
        second.package_root, now=datetime.now(timezone.utc)
    )
    assert first_binding.manifest_sha256 == second_binding.manifest_sha256
    assert first_binding.artifact_sha256 == second_binding.artifact_sha256
    assert first_binding.max_attempts == 1
    assert first_binding.safety == module.SAFETY

    unknown = first.package_root / "unknown"
    unknown.write_bytes(b"x")
    with pytest.raises(module.RuntimeStageError, match="artifact set"):
        module.verify_local_runtime_stage_package(
            first.package_root, now=datetime.now(timezone.utc)
        )


def test_package_rejects_source_proof_or_runtime_delta_tamper(tmp_path: Path) -> None:
    module = load("phase13_runtime_stage_tamper", LOCAL)
    receipt = module.materialize_runtime_stage_package(package_inputs(module), tmp_path)
    for filename in ("source-proof.json", "runtime.env.delta.enc"):
        path = receipt.package_root / filename
        original = path.read_bytes()
        path.write_bytes(original + b"x")
        with pytest.raises(module.RuntimeStageError, match="checksum"):
            module.verify_local_runtime_stage_package(
                receipt.package_root, now=datetime.now(timezone.utc)
            )
        path.write_bytes(original)


def test_exact_approval_is_canonical_and_expiry_bound(tmp_path: Path) -> None:
    module = load("phase13_runtime_stage_approval", LOCAL)
    receipt = module.materialize_runtime_stage_package(package_inputs(module), tmp_path)
    binding = module.verify_local_runtime_stage_package(
        receipt.package_root, now=datetime.now(timezone.utc)
    )
    phrase = module.exact_approval_phrase(binding)
    assert "ONE_SSH_RUNTIME_ONLY" in phrase
    assert "NO_DATABASE_APPLY" in phrase
    assert "NO_SERVICE_ACTION" in phrase
    assert binding.manifest_sha256 in phrase
    assert binding.runtime_delta_sha256 in phrase
    assert binding.expires_at.strftime("%Y-%m-%dT%H:%M:%SZ") in phrase


def test_exact_amn2_diff_is_migration_only_and_accepted_source_is_bound() -> None:
    module = load("phase13_runtime_stage_source_evidence", LOCAL)
    proof_bytes, manifest_bytes = module._source_evidence(
        ROOT.parent / "amn2-phase13-bot-web-migration"
    )
    proof = json.loads(proof_bytes)
    manifest = json.loads(manifest_bytes)
    assert proof["changed_paths"] == sorted(module.EXPECTED_MIGRATION_ONLY_DIFF)
    assert proof["bot_web_runtime_equal"] is True
    assert len(manifest["files"]) >= 100
    assert "app/bot/assets/NEOBYATNAYA-AMNZ-BOT.png" in manifest["files"]
    assert "app/bot/assets/NEOBYATNAYA-AMNZ-LANGUAGE-HEADER.png" in manifest["files"]
    assert "app/web/static/brand-full.png" in manifest["files"]


def test_accepted_role_archive_normalizes_only_safe_dot_slash_prefix() -> None:
    module = load("phase13_runtime_stage_role_archive", LOCAL)
    buffer = io.BytesIO()
    values = {
        "./database.sqlite3": b"SQLite format 3\x00fixture",
        "./runtime.env": b"TELEGRAM_BOT_TOKEN=fixture\nADMIN_TELEGRAM_IDS=1\n",
        "./server-config.yml": b"servers: []\n",
    }
    with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
        for name, value in values.items():
            info = tarfile.TarInfo(name)
            info.size = len(value)
            archive.addfile(info, io.BytesIO(value))
    parsed = module._role_archive_files(buffer.getvalue())
    assert set(parsed) == {"database.sqlite3", "runtime.env", "server-config.yml"}


def test_runtime_merge_changes_only_token_and_admin_ids() -> None:
    module = load("phase13_runtime_stage_remote_merge", REMOTE)
    before = (
        b"PYTHONPATH=/opt/amn2-spain/runtime/source\n"
        b"TELEGRAM_BOT_TOKEN=old\n"
        b"APP_SECRET_KEY=keep-exact\n"
        b"WEB_ADMIN_PORT=3031\n"
    )
    delta = b"ADMIN_TELEGRAM_IDS=1001,1002\nTELEGRAM_BOT_TOKEN=new\n"
    after = module.merge_runtime_environment(before, delta)
    assert after == (
        b"PYTHONPATH=/opt/amn2-spain/runtime/source\n"
        b"TELEGRAM_BOT_TOKEN=new\n"
        b"APP_SECRET_KEY=keep-exact\n"
        b"WEB_ADMIN_PORT=3031\n"
        b"ADMIN_TELEGRAM_IDS=1001,1002\n"
    )
    with pytest.raises(module.RemoteRuntimeStageError, match="runtime_delta_invalid"):
        module.merge_runtime_environment(before, delta + b"APP_SECRET_KEY=forbidden\n")


def test_bound_foundation_adapter_uses_real_spain_backend() -> None:
    module = load("phase13_runtime_stage_real_foundation", REMOTE)
    foundation = module._load_foundation(FOUNDATION.read_bytes())
    backend = module.LiveSpainRuntimeBackend(foundation, {"files": {}})
    assert backend.foundation_backend.__class__.__name__ == "RealSpainBackend"


def test_runtime_stage_accepts_authoritative_phase12_or_hardened_bot_unit() -> None:
    module = load("phase13_runtime_stage_bot_unit_admission", REMOTE)
    phase12_live = "389792d871cc980d8972bfe6a9b3f18ebebd4500c1bfadc92477b3382e0135f9"
    hardened = "9383450e3ad3b9f079828ab12996994fe58b4a8559874a4fbde4210d4c4d2fd8"
    assert module._bot_unit_hash_accepted(phase12_live, hardened) is True
    assert module._bot_unit_hash_accepted(hardened, hardened) is True
    assert module._bot_unit_hash_accepted("0" * 64, hardened) is False


class FakeBackend:
    def __init__(self, fail_at: str | None = None) -> None:
        self.fail_at = fail_at
        self.events: list[str] = []
        self.applied = False
        self.rolled_back = False

    def _event(self, name: str) -> None:
        self.events.append(name)
        if self.fail_at == name:
            raise RuntimeError("synthetic")

    def preflight(self, payload: dict[str, object]) -> None:
        self._event("preflight")

    def apply_runtime_delta(self, delta: bytes) -> None:
        assert delta.startswith(b"ADMIN_TELEGRAM_IDS=")
        self._event("runtime_apply")
        self.applied = True

    def post_verify(self, payload: dict[str, object]) -> None:
        self._event("post_verify")

    def rollback(self, payload: dict[str, object]) -> None:
        self.events.append("rollback")
        self.applied = False
        self.rolled_back = True

    def terminal_state(self, payload: dict[str, object]) -> dict[str, bool]:
        return {
            "awg2_equal": True,
            "bot_disabled": True,
            "database_equal": True,
            "foreign_equal": True,
            "marker_absent": True,
            "runtime_delta_equal": self.applied,
            "source_equal": True,
            "web_loopback_healthy": True,
        }


def remote_payload(module) -> dict[str, object]:
    delta = b"ADMIN_TELEGRAM_IDS=1001,1002\nTELEGRAM_BOT_TOKEN=token\n"
    source_manifest = canonical(
        {
            "files": {"app/bot/example.py": {"sha256": "4" * 64, "size": 1}},
            "head": "55dc243b8e6c6bdb57f8301b56326e4cd4072d19",
            "schema": module.SOURCE_MANIFEST_SCHEMA,
        }
    )
    return {
        "expires_at": future().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "expected": {
            "accepted_source_head": "55dc243b8e6c6bdb57f8301b56326e4cd4072d19",
            "awg2_foundation_sha256": module.EXPECTED_AWG2_FOUNDATION_SHA256,
            "bot_unit_sha256": "1" * 64,
            "foreign_stable_sha256": module.EXPECTED_FOREIGN_STABLE_SHA256,
            "source_manifest_sha256": sha256(source_manifest),
        },
        "manifest_sha256": "3" * 64,
        "max_attempts": 1,
        "outcome_id": "spain-bot-runtime-stage-test-001",
        "runtime_delta_b64": base64.b64encode(delta).decode(),
        "runtime_delta_sha256": sha256(delta),
        "schema": module.PAYLOAD_SCHEMA,
        "source_manifest_b64": base64.b64encode(source_manifest).decode(),
    }


def test_remote_success_is_runtime_only_and_bot_stays_disabled() -> None:
    module = load("phase13_runtime_stage_remote_success", REMOTE)
    backend = FakeBackend()
    receipt = module.execute_runtime_stage(remote_payload(module), backend)
    assert receipt["outcome"] == "success"
    assert receipt["bot_disabled"] is True
    assert receipt["service_action_performed"] is False
    assert receipt["database_equal"] is True
    assert backend.events == ["preflight", "runtime_apply", "post_verify"]


@pytest.mark.parametrize("failure", ["runtime_apply", "post_verify"])
def test_remote_rolls_back_after_any_post_preflight_failure(failure: str) -> None:
    module = load(f"phase13_runtime_stage_remote_failure_{failure}", REMOTE)
    backend = FakeBackend(fail_at=failure)
    receipt = module.execute_runtime_stage(remote_payload(module), backend)
    assert receipt["outcome"] == "failure"
    assert receipt["rolled_back"] is True
    assert backend.rolled_back is True
    assert "rollback" in backend.events


def test_runner_claims_before_exactly_one_fixed_spain_ssh(tmp_path: Path) -> None:
    module = load("phase13_runtime_stage_runner", LOCAL)
    inputs = package_inputs(module)
    inputs = replace(inputs, runner_bytes=LOCAL.read_bytes(), remote_bytes=REMOTE.read_bytes())
    receipt = module.materialize_runtime_stage_package(inputs, tmp_path / "packages")
    binding = module.verify_local_runtime_stage_package(
        receipt.package_root, now=datetime.now(timezone.utc)
    )
    calls: list[tuple[str, tuple[str, ...], bytes]] = []

    def fake_process(executable, arguments, input_bytes, **kwargs):
        assert kwargs["timeout_seconds"] == module.FOUNDATION_MAX_TRANSPORT_TIMEOUT_SECONDS
        assert kwargs["maximum_input_bytes"] <= module.FOUNDATION_MAX_TRANSPORT_INPUT_BYTES
        assert kwargs["maximum_output_bytes"] <= module.FOUNDATION_MAX_TRANSPORT_OUTPUT_BYTES
        assert len(input_bytes) <= kwargs["maximum_input_bytes"]
        calls.append((executable, tuple(arguments), input_bytes))
        return canonical(
            {
                "awg2_equal": True,
                "bot_disabled": True,
                "database_equal": True,
                "foreign_equal": True,
                "marker_absent": True,
                "outcome": "success",
                "outcome_id": binding.outcome_id,
                "raw_output_persisted": False,
                "reason": "completed",
                "rolled_back": False,
                "runtime_delta_equal": True,
                "schema": module.RECEIPT_SCHEMA,
                "service_action_performed": False,
                "source_equal": True,
                "stage": "post_verify",
                "web_loopback_healthy": True,
            }
        )

    delta = b"ADMIN_TELEGRAM_IDS=1001\nTELEGRAM_BOT_TOKEN=token\n"
    result = module.run_runtime_stage_gate(
        receipt.package_root,
        module.exact_approval_phrase(binding),
        runtime_delta_plain=delta,
        process_runner=fake_process,
        binding_loader=lambda: module.FixedSpainBinding(
            target_host="fixed-host",
            target_user="fixed-user",
            key_path=tmp_path / "id",
            known_hosts_path=tmp_path / "known_hosts",
        ),
        private_root=tmp_path / "private",
        now=datetime.now(timezone.utc),
    )
    assert result.status == "success"
    assert result.ssh_process_count == 1
    assert len(calls) == 1
    assert (tmp_path / "private/outcomes/spain-bot-runtime-stage-test-001.claim.json").is_file()
