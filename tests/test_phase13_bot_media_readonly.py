from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from scripts.vps import phase13_bot_media_readonly_remote as remote_module
from scripts.phase13_bot_media_readonly import (
    BotMediaGateError,
    BotMediaPackageInputs,
    FixedUsaBinding,
    exact_approval_phrase,
    materialize_bot_media_package,
    run_bot_media_gate,
    verify_local_bot_media_package,
)
from scripts.vps.phase13_bot_media_readonly_remote import (
    BotMediaRemoteError,
    collect_media_frame,
    parse_media_frame,
)


UTC = timezone.utc
NOW = datetime(2026, 8, 9, 9, 0, tzinfo=UTC)


def _source_bytes(relative: str) -> bytes:
    return (Path(__file__).parents[1] / relative).read_bytes()


def _git_head() -> str:
    return subprocess.run(
        ("git", "rev-parse", "HEAD"),
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    ).stdout.strip()


def _member_manifest_sha256(files: dict[str, bytes]) -> str:
    members = [
        {
            "name": name,
            "sha256": hashlib.sha256(files[name]).hexdigest(),
            "size": len(files[name]),
        }
        for name in sorted(files)
    ]
    value = (
        json.dumps(members, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def _package_inputs(outcome_id: str = "bot-media-check-20260809-001") -> BotMediaPackageInputs:
    return BotMediaPackageInputs(
        outcome_id=outcome_id,
        expires_at=NOW + timedelta(hours=2),
        root_head=_git_head(),
        runner_bytes=_source_bytes("scripts/phase13_bot_media_readonly.py"),
        collector_bytes=_source_bytes(
            "scripts/vps/phase13_bot_media_readonly_remote.py"
        ),
        recovery_crypto_bytes=_source_bytes("scripts/phase10_recovery_crypto.py"),
    )


def test_remote_collector_proves_absence_without_writing_plaintext(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    data_root.mkdir()

    before = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))
    parsed = parse_media_frame(collect_media_frame(data_root))
    after = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))

    assert parsed.files == {}
    assert parsed.evidence == {
        "content_sha256": hashlib.sha256(parsed.archive).hexdigest(),
        "file_count": 0,
        "media_root_present": False,
        "member_manifest_sha256": _member_manifest_sha256({}),
        "registry_present": False,
        "schema": "amn2.phase13.bot-media-readonly-evidence.v1",
        "total_bytes": 0,
    }
    assert before == after == ["data"]


def test_remote_collector_is_deterministic_and_preserves_only_exact_media_members(
    tmp_path: Path,
) -> None:
    data_root = tmp_path / "data"
    media = data_root / "bot-media" / "headers"
    media.mkdir(parents=True)
    (data_root / "bot-media-registry.json").write_bytes(b'{"selected":{}}\n')
    (media / "start.png").write_bytes(b"\x89PNG\r\n\x1a\nmedia")

    first = collect_media_frame(data_root)
    second = collect_media_frame(data_root)
    parsed = parse_media_frame(first)

    assert first == second
    assert parsed.files == {
        "bot-media-registry.json": b'{"selected":{}}\n',
        "bot-media/headers/start.png": b"\x89PNG\r\n\x1a\nmedia",
    }
    assert parsed.evidence["file_count"] == 2
    assert parsed.evidence["total_bytes"] == sum(map(len, parsed.files.values()))
    assert parsed.evidence["member_manifest_sha256"] == _member_manifest_sha256(
        dict(parsed.files)
    )
    assert parsed.evidence["registry_present"] is True
    assert parsed.evidence["media_root_present"] is True


def test_remote_collector_distinguishes_an_existing_empty_media_root(
    tmp_path: Path,
) -> None:
    data_root = tmp_path / "data"
    (data_root / "bot-media").mkdir(parents=True)

    parsed = parse_media_frame(collect_media_frame(data_root))

    assert parsed.files == {}
    assert parsed.evidence["media_root_present"] is True
    assert parsed.evidence["registry_present"] is False


def test_remote_collector_rejects_symlinks_and_oversized_files(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    media = data_root / "bot-media"
    media.mkdir(parents=True)
    outside = tmp_path / "outside.png"
    outside.write_bytes(b"outside")
    link = media / "linked.png"
    try:
        os.symlink(outside, link)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation unavailable")

    with pytest.raises(BotMediaRemoteError, match="media path unsafe"):
        collect_media_frame(data_root)

    link.unlink()
    (media / "large.png").write_bytes(b"x" * (10 * 1024 * 1024 + 1))
    with pytest.raises(BotMediaRemoteError, match="media file oversized"):
        collect_media_frame(data_root)


def test_remote_collector_handles_short_regular_file_reads(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data_root = tmp_path / "data"
    media = data_root / "bot-media"
    media.mkdir(parents=True)
    expected = b"bounded-media-content" * 1024
    (media / "header.png").write_bytes(expected)
    original_read = remote_module.os.read

    def short_read(descriptor: int, maximum: int) -> bytes:
        return original_read(descriptor, min(maximum, 17))

    monkeypatch.setattr(remote_module.os, "read", short_read)

    parsed = parse_media_frame(collect_media_frame(data_root))

    assert parsed.files["bot-media/header.png"] == expected


def test_package_materialization_is_deterministic_and_exactly_bound(tmp_path: Path) -> None:
    first = materialize_bot_media_package(_package_inputs(), tmp_path / "first")
    second = materialize_bot_media_package(_package_inputs(), tmp_path / "second")

    first_files = {
        path.name: path.read_bytes() for path in sorted(first.package_root.iterdir())
    }
    second_files = {
        path.name: path.read_bytes() for path in sorted(second.package_root.iterdir())
    }
    assert first_files == second_files
    assert set(first_files) == {
        "collector.py",
        "manifest.json",
        "recovery_crypto.py",
        "runner.py",
    }
    binding = verify_local_bot_media_package(first.package_root, now=NOW)
    assert binding.outcome_id == "bot-media-check-20260809-001"
    assert binding.max_attempts == 1
    assert exact_approval_phrase(binding).startswith(
        "УТВЕРЖДАЮ ОДИН CHECKSUM-BOUND USA BOT-MEDIA READ-ONLY COLLECTION "
    )
    manifest = json.loads(first_files["manifest.json"])
    assert manifest["safety"] == {
        "backup_created": False,
        "data_transfer_authorized": False,
        "live_mutation_authorized": False,
        "plaintext_persistence_authorized": False,
        "service_action_authorized": False,
        "spain_access_authorized": False,
    }


def test_gate_claims_before_one_fixed_usa_process_and_encrypts_before_write(
    tmp_path: Path,
) -> None:
    package = materialize_bot_media_package(_package_inputs(), tmp_path / "packages")
    binding = verify_local_bot_media_package(package.package_root, now=NOW)
    data_root = tmp_path / "remote-data"
    media = data_root / "bot-media"
    media.mkdir(parents=True)
    (data_root / "bot-media-registry.json").write_bytes(b"{}\n")
    (media / "header.png").write_bytes(b"png-bytes")
    calls: list[tuple[str, tuple[str, ...], bytes]] = []

    def fake_process(executable: str, arguments: tuple[str, ...], input_bytes: bytes, **_: object) -> bytes:
        claim = tmp_path / "private" / "outcomes" / (
            "bot-media-check-20260809-001.claim.json"
        )
        assert claim.is_file()
        calls.append((executable, arguments, input_bytes))
        return collect_media_frame(data_root)

    fake_binding = FixedUsaBinding(
        target_host="fixed.example",
        target_user="operator",
        key_path=tmp_path / "id_ed25519",
        known_hosts_path=tmp_path / "known_hosts",
    )
    result = run_bot_media_gate(
        package.package_root,
        exact_approval_phrase(binding),
        now=NOW,
        private_root=tmp_path / "private",
        process_runner=fake_process,
        binding_loader=lambda: fake_binding,
    )

    assert len(calls) == 1
    assert result.status == "success"
    assert result.ssh_process_count == 1
    assert result.remote_collection_completed is True
    assert result.plaintext_persisted is False
    assert result.file_count == 2
    assert result.encrypted_archive_path.is_file()
    assert result.encrypted_archive_path.suffix == ".enc"
    persisted_names = {
        path.name for path in (tmp_path / "private").rglob("*") if path.is_file()
    }
    assert "bot-media-registry.json" not in persisted_names
    assert "header.png" not in persisted_names


@pytest.mark.parametrize("case", ["approval", "expired", "tampered", "replay"])
def test_gate_blocks_before_second_process_and_never_persists_plaintext(
    tmp_path: Path, case: str
) -> None:
    package = materialize_bot_media_package(_package_inputs(), tmp_path / "packages")
    binding = verify_local_bot_media_package(package.package_root, now=NOW)
    approval = exact_approval_phrase(binding)
    run_now = NOW
    if case == "approval":
        approval += " invalid"
    elif case == "expired":
        run_now = NOW + timedelta(hours=3)
    elif case == "tampered":
        (package.package_root / "collector.py").write_bytes(b"tampered")
    elif case == "replay":
        outcome_root = tmp_path / "private" / "outcomes"
        outcome_root.mkdir(parents=True)
        (outcome_root / "bot-media-check-20260809-001.claim.json").write_text(
            "{}\n", encoding="utf-8"
        )
    calls = 0

    def fake_process(*_: object, **__: object) -> bytes:
        nonlocal calls
        calls += 1
        raise AssertionError("network must not start")

    with pytest.raises(BotMediaGateError):
        run_bot_media_gate(
            package.package_root,
            approval,
            now=run_now,
            private_root=tmp_path / "private",
            process_runner=fake_process,
            binding_loader=lambda: FixedUsaBinding(
                "fixed.example",
                "operator",
                tmp_path / "id_ed25519",
                tmp_path / "known_hosts",
            ),
        )
    assert calls == 0
    assert not list((tmp_path / "private").rglob("*.tar.gz"))


def test_gate_rejects_nonmatching_exact_head_before_network(tmp_path: Path) -> None:
    inputs = _package_inputs("bot-media-check-20260809-head")
    inputs = BotMediaPackageInputs(
        outcome_id=inputs.outcome_id,
        expires_at=inputs.expires_at,
        root_head="0" * 40,
        runner_bytes=inputs.runner_bytes,
        collector_bytes=inputs.collector_bytes,
        recovery_crypto_bytes=inputs.recovery_crypto_bytes,
    )
    package = materialize_bot_media_package(inputs, tmp_path / "packages")
    binding = verify_local_bot_media_package(package.package_root, now=NOW)
    calls = 0

    def fake_process(*_: object, **__: object) -> bytes:
        nonlocal calls
        calls += 1
        return b""

    with pytest.raises(BotMediaGateError, match="exact head mismatch"):
        run_bot_media_gate(
            package.package_root,
            exact_approval_phrase(binding),
            now=NOW,
            private_root=tmp_path / "private",
            process_runner=fake_process,
            binding_loader=lambda: FixedUsaBinding(
                "fixed.example",
                "operator",
                tmp_path / "id_ed25519",
                tmp_path / "known_hosts",
            ),
        )
    assert calls == 0


def test_gate_rejects_preexisting_private_root_with_unprotected_acl_before_network(
    tmp_path: Path,
) -> None:
    package = materialize_bot_media_package(
        _package_inputs("bot-media-check-20260809-acl"), tmp_path / "packages"
    )
    binding = verify_local_bot_media_package(package.package_root, now=NOW)
    private_root = tmp_path / "unsafe-private"
    private_root.mkdir()
    if os.name != "nt":
        private_root.chmod(0o755)
    calls = 0

    def fake_process(*_: object, **__: object) -> bytes:
        nonlocal calls
        calls += 1
        return b""

    with pytest.raises(BotMediaGateError, match="private ACL invalid"):
        run_bot_media_gate(
            package.package_root,
            exact_approval_phrase(binding),
            now=NOW,
            private_root=private_root,
            process_runner=fake_process,
            binding_loader=lambda: FixedUsaBinding(
                "fixed.example",
                "operator",
                tmp_path / "id_ed25519",
                tmp_path / "known_hosts",
            ),
        )
    assert calls == 0


def test_direct_script_materialize_entrypoint_loads_repository_modules(
    tmp_path: Path,
) -> None:
    repository = Path(__file__).parents[1]
    expires_at = datetime.now(UTC) + timedelta(hours=1)
    result = subprocess.run(
        (
            sys.executable,
            str(repository / "scripts/phase13_bot_media_readonly.py"),
            "materialize",
            "--outcome-id",
            "bot-media-check-cli-test",
            "--expires-at",
            expires_at.replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "--output-parent",
            str(tmp_path / "packages"),
        ),
        cwd=repository,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    document = json.loads(result.stdout)
    assert document["status"] == "materialized"
    assert document["outcome_id"] == "bot-media-check-cli-test"
