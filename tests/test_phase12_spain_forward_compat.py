from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "phase12_spain_forward_compat.py"
UNIT = ROOT / "packaging" / "phase12-spain" / "units" / "amn2-spain-forward-compat.service"


def load_module():
    spec = importlib.util.spec_from_file_location("phase12_spain_forward_compat", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeRunner:
    def __init__(self, module, present: bool = False, inner_forward: str = "1") -> None:
        self.module = module
        self.rules = module.expected_rules() if present else []
        self.inner_forward = inner_forward
        self.calls: list[tuple[tuple[str, ...], bytes | None]] = []

    def __call__(self, argv, *, input_bytes=None, **_kwargs):
        argv = tuple(argv)
        self.calls.append((argv, input_bytes))
        if argv == self.module.LIST_CHAIN_ARGV:
            rows = [
                {"rule": {**rule, "handle": 157 + index}}
                for index, rule in enumerate(self.rules)
            ]
            return json.dumps({"nftables": rows}).encode()
        if argv == self.module.NFT_BATCH_ARGV:
            assert input_bytes is not None
            if b"insert rule" in input_bytes:
                self.rules = self.module.expected_rules()
            elif b"delete rule" in input_bytes:
                self.rules = []
            return b""
        if argv == self.module.BOOT_ID_ARGV:
            return b"11111111-2222-3333-4444-555555555555\n"
        if argv == self.module.DOCKER_INSPECT_ARGV:
            return b"true 4242\n"
        if argv == self.module.build_nsenter_argv(4242, query=True):
            return (self.inner_forward + "\n").encode()
        if argv == self.module.build_nsenter_argv(4242, query=False, value="1"):
            self.inner_forward = "1"
            return b""
        if argv == self.module.build_nsenter_argv(4242, query=False, value="0"):
            self.inner_forward = "0"
            return b""
        raise AssertionError(argv)


def test_apply_adopts_exact_current_rules_without_mutation(tmp_path: Path) -> None:
    module = load_module()
    runner = FakeRunner(module, present=True)
    ledger = tmp_path / "forward-ledger.json"

    receipt = module.ForwardCompat(runner=runner).apply(ledger)

    assert receipt["strategy"] == "adopted"
    assert [call for call in runner.calls if call[0] == module.NFT_BATCH_ARGV] == []
    assert module.ForwardCompat(runner=runner).verify(ledger)["handles"] == [157, 158, 159]


def test_apply_recreates_all_rules_atomically_when_absent(tmp_path: Path) -> None:
    module = load_module()
    runner = FakeRunner(module)
    ledger = tmp_path / "forward-ledger.json"

    receipt = module.ForwardCompat(runner=runner).apply(ledger)

    assert receipt["strategy"] == "created"
    batches = [body for argv, body in runner.calls if argv == module.NFT_BATCH_ARGV]
    assert len(batches) == 1
    assert batches[0].count(b"insert rule ip filter FORWARD") == 3
    assert module.ForwardCompat(runner=runner).verify(ledger)["handles"] == [157, 158, 159]


def test_apply_and_rollback_manage_container_forward_without_restart(tmp_path: Path) -> None:
    module = load_module()
    runner = FakeRunner(module, present=True, inner_forward="0")
    ledger = tmp_path / "forward-ledger.json"
    manager = module.ForwardCompat(runner=runner)

    receipt = manager.apply(ledger)

    assert receipt["container_ip_forward"] == {"previous": "0", "applied": "1", "changed": True}
    assert runner.inner_forward == "1"
    assert all("restart" not in " ".join(argv) for argv, _body in runner.calls)
    manager.rollback(ledger)
    assert runner.inner_forward == "0"


def test_rollback_deletes_only_recorded_exact_rules(tmp_path: Path) -> None:
    module = load_module()
    runner = FakeRunner(module, present=True)
    ledger = tmp_path / "forward-ledger.json"
    manager = module.ForwardCompat(runner=runner)
    manager.apply(ledger)

    receipt = manager.rollback(ledger)

    assert receipt["removed_handles"] == [157, 158, 159]
    batches = [body for argv, body in runner.calls if argv == module.NFT_BATCH_ARGV]
    assert len(batches) == 1
    assert batches[0].count(b"delete rule ip filter FORWARD handle") == 3


def test_partial_or_duplicate_owned_rules_fail_closed(tmp_path: Path) -> None:
    module = load_module()
    runner = FakeRunner(module, present=True)
    runner.rules = runner.rules[:2]
    with pytest.raises(module.ForwardCompatError, match="partial"):
        module.ForwardCompat(runner=runner).apply(tmp_path / "forward-ledger.json")


def test_unit_is_persistent_hardened_and_does_not_restart_awg() -> None:
    source = UNIT.read_text(encoding="utf-8")
    assert "After=amn2-spain-network.service" in source
    assert "ExecStart=" in source and " apply " in source
    assert "ExecStartPost=" in source and " verify " in source
    assert "ExecStop=" in source and " rollback " in source
    assert "WantedBy=multi-user.target" in source
    assert "CapabilityBoundingSet=CAP_NET_ADMIN" in source
    assert "CAP_SYS_ADMIN" in source
    assert "docker restart" not in source
    assert "systemctl restart" not in source
