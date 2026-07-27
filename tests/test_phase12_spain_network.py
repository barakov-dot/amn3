from __future__ import annotations

import copy
import io
import json
import subprocess
from pathlib import Path

import pytest

from scripts.phase12_spain_network import (
    NFT_CONFIG,
    NFT_CONFIG_PATH,
    UNIT_PATH,
    BoundedCommandRunner,
    CommandError,
    NetworkError,
    NetworkManager,
    expected_table_document,
)


ROOT = Path(__file__).resolve().parents[1]
BOOT_ID = "12345678-1234-1234-1234-123456789abc"
ROUTE = {
    "dst": "10.212.12.0/24",
    "gateway": "172.29.251.2",
    "dev": "amn2spbr0",
}

EXPECTED_CONFIG = """table inet amn2_spain {
    chain prerouting {
        type nat hook prerouting priority dstnat; policy accept;
        udp dport 30001 dnat ip to 172.29.251.2:30001 comment \"amn2_spain:udp30001\"
    }
    chain forward {
        type filter hook forward priority filter; policy accept;
        oifname \"amn2spbr0\" ip daddr 172.29.251.2 udp dport 30001 accept comment \"amn2_spain:forward-dnat\"
        iifname \"amn2spbr0\" ip saddr 10.212.12.0/24 accept comment \"amn2_spain:forward-outbound\"
        oifname \"amn2spbr0\" ip daddr 10.212.12.0/24 ct state established,related accept comment \"amn2_spain:forward-return\"
    }
    chain postrouting {
        type nat hook postrouting priority srcnat; policy accept;
        ip saddr 10.212.12.0/24 oifname != \"amn2spbr0\" masquerade comment \"amn2_spain:masquerade\"
    }
}
"""


class FakeRunner:
    """Stateful command boundary; it emulates only the fixed approved argv."""

    def __init__(
        self,
        *,
        owned: dict | None = None,
        route: dict | None = None,
        sysctl: str = "0",
        boot_id: str = BOOT_ID,
        foreign_policy: str = "accept",
    ) -> None:
        self.owned = copy.deepcopy(owned)
        self.route = copy.deepcopy(route)
        self.sysctl = sysctl
        self.boot_id = boot_id
        self.foreign_policy = foreign_policy
        self.calls: list[tuple[tuple[str, ...], bytes | None, float, int]] = []
        self.fail_on: tuple[str, ...] | None = None

    def __call__(
        self,
        argv: tuple[str, ...],
        *,
        input_bytes: bytes | None = None,
        timeout: float,
        max_output: int,
    ) -> bytes:
        assert isinstance(argv, tuple)
        assert all(isinstance(part, str) and part for part in argv)
        self.calls.append((argv, input_bytes, timeout, max_output))
        if argv == self.fail_on:
            raise CommandError("command failed")
        if argv == ("/usr/bin/cat", "/proc/sys/kernel/random/boot_id"):
            return (self.boot_id + "\n").encode()
        if argv == ("/usr/sbin/nft", "-j", "list", "ruleset"):
            entries = [
                        {"metainfo": {"json_schema_version": 1}},
                        {
                            "table": {
                                "family": "inet",
                                "name": "foreign_filter",
                            }
                        },
                        {
                            "chain": {
                                "family": "inet",
                                "table": "foreign_filter",
                                "name": "forward",
                                "type": "filter",
                                "hook": "forward",
                                "prio": 0,
                                "policy": self.foreign_policy,
                            }
                        },
                    ]
            if self.owned is not None:
                entries.extend(copy.deepcopy(self.owned["nftables"]))
            return json.dumps({"nftables": entries}).encode()
        if argv == ("/usr/sbin/nft", "-j", "list", "table", "inet", "amn2_spain"):
            if self.owned is None:
                raise CommandError("command failed")
            return json.dumps(self.owned).encode()
        if argv == ("/usr/sbin/nft", "--check", "-f", "-"):
            assert input_bytes == EXPECTED_CONFIG.encode()
            return b""
        if argv == ("/usr/sbin/nft", "-f", "-"):
            assert input_bytes == EXPECTED_CONFIG.encode()
            self.owned = expected_table_document()
            return b""
        if argv == ("/usr/sbin/nft", "delete", "table", "inet", "amn2_spain"):
            if self.owned is None:
                raise CommandError("command failed")
            self.owned = None
            return b""
        if argv == ("/usr/sbin/ip", "-j", "route", "show", "exact", "10.212.12.0/24"):
            return json.dumps([] if self.route is None else [self.route]).encode()
        if argv == (
            "/usr/sbin/ip", "route", "add", "10.212.12.0/24", "via",
            "172.29.251.2", "dev", "amn2spbr0",
        ):
            self.route = copy.deepcopy(ROUTE)
            return b""
        if argv == (
            "/usr/sbin/ip", "route", "del", "10.212.12.0/24", "via",
            "172.29.251.2", "dev", "amn2spbr0",
        ):
            if self.route != ROUTE:
                raise CommandError("command failed")
            self.route = None
            return b""
        if argv == ("/usr/sbin/sysctl", "-n", "net.ipv4.ip_forward"):
            return (self.sysctl + "\n").encode()
        if argv[:3] == ("/usr/sbin/sysctl", "-q", "-w"):
            value = argv[3].split("=", 1)[1]
            self.sysctl = value
            return b""
        raise AssertionError(f"unexpected argv: {argv!r}")


def durable_apply(
    manager: NetworkManager, *, expected_boot_id: str = BOOT_ID
) -> dict:
    prepared: list[dict] = []
    return manager.apply(
        expected_boot_id=expected_boot_id,
        persist_intent=lambda value: prepared.append(copy.deepcopy(value)),
    )


def test_canonical_nft_config_and_unit_are_exact() -> None:
    assert NFT_CONFIG == EXPECTED_CONFIG
    assert "flush table" not in NFT_CONFIG
    assert NFT_CONFIG_PATH.read_text(encoding="utf-8") == EXPECTED_CONFIG
    unit = UNIT_PATH.read_text(encoding="utf-8")
    assert "After=amn2-spain-docker.service nftables.service" in unit
    assert "Requires=amn2-spain-docker.service" in unit
    assert "RemainAfterExit=yes" in unit
    assert "CapabilityBoundingSet=CAP_NET_ADMIN" in unit
    assert "AmbientCapabilities=CAP_NET_ADMIN" in unit
    assert "ExecStart=/usr/bin/python3 /opt/amn2-spain/current/scripts/phase12_spain_network.py apply --ledger /var/lib/amn2-spain/network-ledger.json" in unit
    assert "ExecStartPost=/usr/bin/python3 /opt/amn2-spain/current/scripts/phase12_spain_network.py verify --ledger /var/lib/amn2-spain/network-ledger.json" in unit
    assert "ExecStop=/usr/bin/python3 /opt/amn2-spain/current/scripts/phase12_spain_network.py rollback --ledger /var/lib/amn2-spain/network-ledger.json" in unit
    assert "docker restart" not in unit.lower()


def test_apply_is_atomic_bounded_and_records_semantic_ledger() -> None:
    runner = FakeRunner()
    ledger = durable_apply(NetworkManager(runner))

    assert runner.owned == expected_table_document()
    assert runner.route == ROUTE
    assert runner.sysctl == "1"
    assert ledger["schema"] == "amn2.spain-network-ledger.v1"
    assert ledger["boot_id"] == BOOT_ID
    assert ledger["nft"]["identity"] == {"family": "inet", "table": "amn2_spain"}
    assert ledger["nft"]["chains"] == ["prerouting", "forward", "postrouting"]
    assert ledger["nft"]["rule_comments"] == [
        "amn2_spain:udp30001",
        "amn2_spain:forward-dnat",
        "amn2_spain:forward-outbound",
        "amn2_spain:forward-return",
        "amn2_spain:masquerade",
    ]
    assert ledger["nft"]["created"] is True
    assert ledger["route"] == {"identity": ROUTE, "created": True}
    assert ledger["sysctl"] == {
        "name": "net.ipv4.ip_forward", "previous": "0", "applied": "1", "changed": True,
    }
    assert ("/usr/sbin/nft", "--check", "-f", "-") in [call[0] for call in runner.calls]
    assert ("/usr/sbin/nft", "-f", "-") in [call[0] for call in runner.calls]
    assert all(call[2] <= 10 and call[3] <= 1024 * 1024 for call in runner.calls)
    assert "private" not in json.dumps(ledger).lower()


def test_mutating_apply_requires_durable_prepared_intent_before_first_syscall() -> None:
    runner = FakeRunner()
    with pytest.raises(NetworkError, match="durable.*intent"):
        NetworkManager(runner).apply(expected_boot_id=BOOT_ID)
    assert runner.owned is None and runner.route is None and runner.sysctl == "0"


@pytest.mark.parametrize(
    "crash_argv",
    [
        ("/usr/sbin/nft", "-f", "-"),
        (
            "/usr/sbin/ip", "route", "add", "10.212.12.0/24", "via",
            "172.29.251.2", "dev", "amn2spbr0",
        ),
        ("/usr/sbin/sysctl", "-q", "-w", "net.ipv4.ip_forward=1"),
    ],
)
def test_prepared_intent_recovers_crash_after_each_network_syscall(
    crash_argv: tuple[str, ...],
) -> None:
    class CrashAfterMutation(FakeRunner):
        crashed = False

        def __call__(self, argv, **kwargs):
            result = super().__call__(argv, **kwargs)
            if argv == crash_argv and not self.crashed:
                self.crashed = True
                raise SystemExit("simulated process death")
            return result

    runner = CrashAfterMutation()
    prepared: list[dict] = []
    with pytest.raises(SystemExit, match="process death"):
        NetworkManager(runner).apply(
            expected_boot_id=BOOT_ID,
            persist_intent=lambda value: prepared.append(copy.deepcopy(value)),
        )
    assert len(prepared) == 1
    assert prepared[0]["boot_id"] == BOOT_ID
    assert prepared[0]["nft"]["created"] is True
    assert prepared[0]["route"]["created"] is True
    assert prepared[0]["sysctl"]["previous"] == "0"

    manager = NetworkManager(runner)
    applied = manager.apply(existing_ledger=prepared[0])
    manager.verify(applied)
    manager.rollback(applied)
    assert runner.owned is None and runner.route is None and runner.sysctl == "0"


def test_prepared_resumability_is_bound_to_current_boot_and_compatible_state() -> None:
    runner = FakeRunner()
    manager = NetworkManager(runner)
    ledger = durable_apply(manager)
    manager.rollback(ledger)

    assert manager.prepared_is_resumable(
        ledger, expected_boot_id=BOOT_ID
    ) is True

    other_boot = copy.deepcopy(ledger)
    other_boot["boot_id"] = "87654321-4321-4321-4321-cba987654321"
    assert manager.prepared_is_resumable(
        other_boot, expected_boot_id=BOOT_ID
    ) is False
    assert runner.owned is None and runner.route is None and runner.sysctl == "0"


def test_apply_and_verify_are_idempotent_for_exact_existing_state() -> None:
    runner = FakeRunner(owned=expected_table_document(), route=ROUTE, sysctl="1")
    manager = NetworkManager(runner)
    ledger = durable_apply(manager)
    manager.verify(ledger)

    mutating = [
        argv for argv, *_ in runner.calls
        if argv in {
            ("/usr/sbin/nft", "-f", "-"),
            ("/usr/sbin/ip", "route", "add", "10.212.12.0/24", "via", "172.29.251.2", "dev", "amn2spbr0"),
            ("/usr/sbin/sysctl", "-q", "-w", "net.ipv4.ip_forward=1"),
        }
    ]
    assert mutating == []
    assert ledger["nft"]["created"] is False
    assert ledger["route"]["created"] is False
    assert ledger["sysctl"]["changed"] is False


@pytest.mark.parametrize("mutation", ["extra_rule", "missing_rule", "extra_chain"])
def test_exact_owned_table_rejects_extra_or_missing_semantics(mutation: str) -> None:
    owned = expected_table_document()
    entries = owned["nftables"]
    if mutation == "extra_rule":
        entries.append({"rule": {"family": "inet", "table": "amn2_spain", "chain": "forward", "expr": [{"accept": None}], "comment": "amn2_spain:extra"}})
    elif mutation == "missing_rule":
        next(index for index, entry in enumerate(entries) if entry.get("rule", {}).get("comment") == "amn2_spain:forward-return")
        entries[:] = [entry for entry in entries if entry.get("rule", {}).get("comment") != "amn2_spain:forward-return"]
    else:
        entries.append({"chain": {"family": "inet", "table": "amn2_spain", "name": "extra"}})

    with pytest.raises(NetworkError, match="owned nft semantics mismatch"):
        durable_apply(NetworkManager(FakeRunner(owned=owned, route=ROUTE, sysctl="1")))


def test_owned_table_list_nonzero_is_not_treated_as_absence_when_ruleset_declares_it() -> None:
    class OwnedListFailure(FakeRunner):
        def __call__(self, argv, **kwargs):
            if argv == ("/usr/sbin/nft", "-j", "list", "table", "inet", "amn2_spain"):
                raise CommandError("command failed")
            return super().__call__(argv, **kwargs)

    runner = OwnedListFailure(owned=expected_table_document(), route=ROUTE, sysctl="1")
    with pytest.raises(CommandError, match="command failed"):
        durable_apply(NetworkManager(runner))
    assert ("/usr/sbin/nft", "-f", "-") not in [call[0] for call in runner.calls]


def test_foreign_forward_drop_policy_is_incompatible_before_mutation() -> None:
    runner = FakeRunner(foreign_policy="drop")
    with pytest.raises(NetworkError, match="foreign forward base chain is incompatible"):
        durable_apply(NetworkManager(runner))
    assert runner.owned is None and runner.route is None and runner.sysctl == "0"


def test_route_conflict_and_invalid_sysctl_are_rejected_before_mutation() -> None:
    conflict = {"dst": "10.212.12.0/24", "gateway": "192.0.2.1", "dev": "eth0"}
    runner = FakeRunner(route=conflict)
    with pytest.raises(NetworkError, match="route identity conflict"):
        durable_apply(NetworkManager(runner))
    assert runner.owned is None

    runner = FakeRunner(sysctl="2")
    with pytest.raises(NetworkError, match="ip_forward observation malformed"):
        durable_apply(NetworkManager(runner))
    assert runner.owned is None


def test_rollback_removes_only_created_exact_objects_and_restores_sysctl_cas() -> None:
    runner = FakeRunner()
    manager = NetworkManager(runner)
    ledger = durable_apply(manager)
    manager.rollback(ledger)
    assert runner.owned is None
    assert runner.route is None
    assert runner.sysctl == "0"
    first_call_count = len(runner.calls)
    manager.rollback(ledger)
    assert runner.owned is None and runner.route is None and runner.sysctl == "0"
    assert len(runner.calls) > first_call_count

    existing = FakeRunner(owned=expected_table_document(), route=ROUTE, sysctl="1")
    existing_manager = NetworkManager(existing)
    existing_ledger = durable_apply(existing_manager)
    existing_manager.rollback(existing_ledger)
    assert existing.owned == expected_table_document()
    assert existing.route == ROUTE
    assert existing.sysctl == "1"


def test_rollback_refuses_owned_route_or_sysctl_drift_without_deleting_foreign_state() -> None:
    runner = FakeRunner()
    manager = NetworkManager(runner)
    ledger = durable_apply(manager)
    runner.route = {"dst": "10.212.12.0/24", "gateway": "192.0.2.8", "dev": "eth0"}
    with pytest.raises(NetworkError, match="route CAS drift"):
        manager.rollback(ledger)
    assert runner.route["gateway"] == "192.0.2.8"

    runner = FakeRunner()
    manager = NetworkManager(runner)
    ledger = durable_apply(manager)
    runner.sysctl = "2"
    with pytest.raises(NetworkError, match="sysctl CAS drift"):
        manager.rollback(ledger)
    assert ("/usr/sbin/sysctl", "-q", "-w", "net.ipv4.ip_forward=0") not in [call[0] for call in runner.calls]


def test_boot_id_mismatch_rejects_apply_verify_and_rollback() -> None:
    runner = FakeRunner()
    manager = NetworkManager(runner)
    with pytest.raises(NetworkError, match="boot id mismatch"):
        durable_apply(manager, expected_boot_id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    assert runner.owned is None

    ledger = durable_apply(manager)
    runner.boot_id = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
    with pytest.raises(NetworkError, match="boot id mismatch"):
        manager.verify(ledger)
    with pytest.raises(NetworkError, match="boot id mismatch"):
        manager.rollback(ledger)


def test_malformed_json_nonzero_and_apply_failure_are_fail_closed_and_redacted() -> None:
    class Malformed(FakeRunner):
        def __call__(self, argv, **kwargs):
            if argv == ("/usr/sbin/nft", "-j", "list", "ruleset"):
                return b"{secret-private-key"
            return super().__call__(argv, **kwargs)

    with pytest.raises(NetworkError, match="nft ruleset JSON malformed") as error:
        durable_apply(NetworkManager(Malformed()))
    assert "secret-private-key" not in str(error.value)

    runner = FakeRunner()
    runner.fail_on = ("/usr/sbin/ip", "route", "add", "10.212.12.0/24", "via", "172.29.251.2", "dev", "amn2spbr0")
    with pytest.raises(NetworkError, match="network apply failed") as error:
        durable_apply(NetworkManager(runner))
    assert "private" not in str(error.value).lower()
    assert runner.owned is None

    class MalformedSchema(FakeRunner):
        def __call__(self, argv, **kwargs):
            if argv == ("/usr/sbin/nft", "-j", "list", "ruleset"):
                return b'{"nftables":[{"chain":"PrivateKey=do-not-log"}]}'
            return super().__call__(argv, **kwargs)

    with pytest.raises(NetworkError, match="nft ruleset JSON schema mismatch") as error:
        durable_apply(NetworkManager(MalformedSchema()))
    assert "PrivateKey" not in str(error.value)


def test_command_that_mutates_then_returns_failure_is_compensated_from_planned_ledger() -> None:
    class MutateThenFail(FakeRunner):
        def __call__(self, argv, **kwargs):
            if argv == (
                "/usr/sbin/ip", "route", "add", "10.212.12.0/24", "via",
                "172.29.251.2", "dev", "amn2spbr0",
            ):
                self.route = copy.deepcopy(ROUTE)
                raise CommandError("command failed")
            return super().__call__(argv, **kwargs)

    runner = MutateThenFail()
    with pytest.raises(NetworkError, match="compensation completed"):
        durable_apply(NetworkManager(runner))
    assert runner.owned is None and runner.route is None and runner.sysctl == "0"


def test_bounded_runner_rejects_timeout_nonzero_and_oversize_without_leaking_output(monkeypatch) -> None:
    secret = b"PrivateKey=do-not-log"

    class FakeProcess:
        def __init__(self, *, stdout: bytes, stderr: bytes, returncode: int, times_out: bool = False) -> None:
            self.stdout = io.BytesIO(stdout)
            self.stderr = io.BytesIO(stderr)
            self.stdin = None
            self.returncode = returncode
            self.times_out = times_out
            self.killed = False

        def wait(self, timeout=None):
            if self.times_out and not self.killed:
                raise subprocess.TimeoutExpired(("bounded",), timeout)
            return self.returncode

        def kill(self):
            self.killed = True

    def install_process(process: FakeProcess) -> None:
        def popen(*args, **kwargs):
            assert kwargs["shell"] is False
            return process

        monkeypatch.setattr(subprocess, "Popen", popen)
        monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("unbounded subprocess.run used")))

    install_process(FakeProcess(stdout=secret, stderr=secret, returncode=-9, times_out=True))
    with pytest.raises(CommandError, match="command timed out") as error:
        BoundedCommandRunner()(("/usr/bin/false",), timeout=1, max_output=64)
    assert "PrivateKey" not in str(error.value)

    install_process(FakeProcess(stdout=secret, stderr=secret, returncode=1))
    with pytest.raises(CommandError, match="command failed") as error:
        BoundedCommandRunner()(("/usr/bin/false",), timeout=1, max_output=64)
    assert "PrivateKey" not in str(error.value)

    install_process(FakeProcess(stdout=b"x" * 65, stderr=b"", returncode=0))
    with pytest.raises(CommandError, match="command output exceeded bound"):
        BoundedCommandRunner()(("/usr/bin/true",), timeout=1, max_output=64)


def test_ledger_validation_rejects_malformed_or_secret_bearing_input() -> None:
    runner = FakeRunner(owned=expected_table_document(), route=ROUTE, sysctl="1")
    manager = NetworkManager(runner)
    with pytest.raises(NetworkError, match="network ledger schema mismatch") as error:
        manager.verify({"schema": "amn2.spain-network-ledger.v1", "PrivateKey": "secret"})
    assert "PrivateKey" not in str(error.value)
