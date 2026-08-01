from __future__ import annotations

import argparse
import json
import os
import re
import stat
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Callable


NFT = "/usr/sbin/nft"
CAT = "/usr/bin/cat"
LIST_CHAIN_ARGV = (NFT, "-j", "-a", "list", "chain", "ip", "filter", "FORWARD")
NFT_BATCH_ARGV = (NFT, "-f", "-")
BOOT_ID_ARGV = (CAT, "/proc/sys/kernel/random/boot_id")
DOCKER = "/opt/amn2-spain/docker/bin/docker"
DOCKER_SOCKET = "unix:///run/amn2-spain-docker/docker.sock"
DOCKER_INSPECT_ARGV = (
    DOCKER, "-H", DOCKER_SOCKET, "inspect", "--format",
    "{{.State.Running}} {{.State.Pid}}", "amn2-spain-awg",
)
NSENTER = "/usr/bin/nsenter"
SYSCTL = "/usr/sbin/sysctl"
COMMENTS = (
    "amn2_spain:compat-forward-dnat",
    "amn2_spain:compat-forward-outbound",
    "amn2_spain:compat-forward-return",
)
BOOT_ID_RE = re.compile(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}")
MAX_OUTPUT = 1024 * 1024
MAX_LEDGER = 16 * 1024


class ForwardCompatError(RuntimeError):
    pass


def build_nsenter_argv(
    pid: int, *, query: bool, value: str | None = None
) -> tuple[str, ...]:
    if type(pid) is not int or pid < 2 or pid > 2**31 - 1:
        raise ForwardCompatError("container pid invalid")
    prefix = (NSENTER, f"--net=/proc/{pid}/ns/net", SYSCTL)
    if query and value is None:
        return (*prefix, "-n", "net.ipv4.ip_forward")
    if not query and value in {"0", "1"}:
        return (*prefix, "-q", "-w", f"net.ipv4.ip_forward={value}")
    raise ForwardCompatError("container sysctl command invalid")


def _meta(key: str, value: str) -> dict[str, Any]:
    return {"match": {"op": "==", "left": {"meta": {"key": key}}, "right": value}}


def _payload(protocol: str, field: str, value: Any) -> dict[str, Any]:
    return {
        "match": {
            "op": "==",
            "left": {"payload": {"protocol": protocol, "field": field}},
            "right": value,
        }
    }


def expected_rules() -> list[dict[str, Any]]:
    common = {"family": "ip", "table": "filter", "chain": "FORWARD"}
    return [
        {
            **common,
            "expr": [
                _meta("iifname", "ens3"),
                _meta("oifname", "amn2spbr0"),
                _payload("ip", "daddr", "172.29.251.2"),
                _payload("udp", "dport", 30001),
                {"match": {"op": "in", "left": {"ct": {"key": "status"}}, "right": "dnat"}},
                {"accept": None},
            ],
            "comment": COMMENTS[0],
        },
        {
            **common,
            "expr": [
                _meta("iifname", "amn2spbr0"),
                _meta("oifname", "ens3"),
                _payload("ip", "saddr", {"prefix": {"addr": "10.212.12.0", "len": 24}}),
                {"accept": None},
            ],
            "comment": COMMENTS[1],
        },
        {
            **common,
            "expr": [
                _meta("iifname", "ens3"),
                _meta("oifname", "amn2spbr0"),
                _payload("ip", "daddr", {"prefix": {"addr": "10.212.12.0", "len": 24}}),
                {"match": {"op": "in", "left": {"ct": {"key": "state"}}, "right": ["established", "related"]}},
                {"accept": None},
            ],
            "comment": COMMENTS[2],
        },
    ]


def _normal_rule(rule: dict[str, Any]) -> dict[str, Any]:
    normalized = {
        key: value
        for key, value in rule.items()
        if key not in {"handle", "index", "position", "packets", "bytes"}
    }
    expressions = normalized.get("expr")
    if isinstance(expressions, list):
        normalized["expr"] = [
            expression
            for expression in expressions
            if not (isinstance(expression, dict) and set(expression) == {"counter"})
        ]
    return normalized


class BoundedRunner:
    def __call__(self, argv: tuple[str, ...], *, input_bytes: bytes | None = None) -> bytes:
        allowed = argv in {LIST_CHAIN_ARGV, NFT_BATCH_ARGV, BOOT_ID_ARGV, DOCKER_INSPECT_ARGV}
        if not allowed:
            allowed = (
                len(argv) in {5, 6}
                and argv[0] == NSENTER
                and re.fullmatch(r"--net=/proc/[1-9][0-9]{0,9}/ns/net", argv[1]) is not None
                and argv[2] == SYSCTL
                and (
                    argv[3:] == ("-n", "net.ipv4.ip_forward")
                    or argv[3:] in {
                        ("-q", "-w", "net.ipv4.ip_forward=0"),
                        ("-q", "-w", "net.ipv4.ip_forward=1"),
                    }
                )
            )
        if not allowed:
            raise ForwardCompatError("command outside allowlist")
        result = subprocess.run(
            argv,
            input=input_bytes,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
            check=False,
        )
        if len(result.stdout) > MAX_OUTPUT or len(result.stderr) > MAX_OUTPUT:
            raise ForwardCompatError("command output exceeded bound")
        if result.returncode != 0:
            raise ForwardCompatError("command failed:" + os.path.basename(argv[0]))
        return result.stdout


Runner = Callable[..., bytes]


class ForwardCompat:
    def __init__(self, *, runner: Runner | None = None) -> None:
        self._runner = runner or BoundedRunner()

    def _boot_id(self) -> str:
        try:
            value = self._runner(BOOT_ID_ARGV).decode("ascii").strip()
        except UnicodeDecodeError as exc:
            raise ForwardCompatError("boot id malformed") from exc
        if BOOT_ID_RE.fullmatch(value) is None:
            raise ForwardCompatError("boot id malformed")
        return value

    def _owned(self) -> list[dict[str, Any]]:
        try:
            value = json.loads(self._runner(LIST_CHAIN_ARGV).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ForwardCompatError("nft observation malformed") from exc
        if not isinstance(value, dict) or set(value) != {"nftables"} or not isinstance(value["nftables"], list):
            raise ForwardCompatError("nft observation malformed")
        owned: list[dict[str, Any]] = []
        for entry in value["nftables"]:
            rule = entry.get("rule") if isinstance(entry, dict) else None
            if isinstance(rule, dict) and rule.get("comment") in COMMENTS:
                owned.append(rule)
        return owned

    def _container_forward(self) -> tuple[int, str]:
        try:
            state, raw_pid = self._runner(DOCKER_INSPECT_ARGV).decode("ascii").strip().split()
            pid = int(raw_pid)
        except (UnicodeDecodeError, ValueError) as exc:
            raise ForwardCompatError("container state malformed") from exc
        if state != "true" or pid < 2 or pid > 2**31 - 1:
            raise ForwardCompatError("container not running")
        try:
            value = self._runner(build_nsenter_argv(pid, query=True)).decode("ascii").strip()
        except UnicodeDecodeError as exc:
            raise ForwardCompatError("container ip_forward malformed") from exc
        if value not in {"0", "1"}:
            raise ForwardCompatError("container ip_forward malformed")
        return pid, value

    def _set_container_forward(self, pid: int, value: str) -> None:
        self._runner(build_nsenter_argv(pid, query=False, value=value))
        observed_pid, observed = self._container_forward()
        if observed_pid != pid or observed != value:
            raise ForwardCompatError("container ip_forward verification failed")

    def _exact(self) -> list[dict[str, Any]]:
        owned = self._owned()
        if not owned:
            return []
        if len(owned) != len(COMMENTS):
            raise ForwardCompatError("owned forward rules partial or duplicate")
        by_comment = {rule.get("comment"): rule for rule in owned}
        if set(by_comment) != set(COMMENTS):
            raise ForwardCompatError("owned forward rules partial or duplicate")
        expected = {rule["comment"]: rule for rule in expected_rules()}
        for comment in COMMENTS:
            if _normal_rule(by_comment[comment]) != expected[comment]:
                raise ForwardCompatError("owned forward rule semantic drift")
            handle = by_comment[comment].get("handle")
            if type(handle) is not int or handle < 1:
                raise ForwardCompatError("owned forward rule handle malformed")
        return [by_comment[comment] for comment in COMMENTS]

    @staticmethod
    def _write_ledger(path: Path, value: dict[str, Any]) -> None:
        if path.is_symlink() or path.parent.is_symlink() or not path.parent.is_dir():
            raise ForwardCompatError("ledger path unsafe")
        payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode() + b"\n"
        if len(payload) > MAX_LEDGER:
            raise ForwardCompatError("ledger exceeds bound")
        descriptor, name = tempfile.mkstemp(prefix=".forward-compat-", dir=path.parent)
        try:
            os.fchmod(descriptor, 0o600)
            os.write(descriptor, payload)
            os.fsync(descriptor)
            os.close(descriptor)
            descriptor = -1
            os.replace(name, path)
        finally:
            if descriptor >= 0:
                os.close(descriptor)
            try:
                os.unlink(name)
            except FileNotFoundError:
                pass

    @staticmethod
    def _read_ledger(path: Path) -> dict[str, Any]:
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        try:
            descriptor = os.open(path, flags)
        except OSError as exc:
            raise ForwardCompatError("ledger unavailable") from exc
        try:
            info = os.fstat(descriptor)
            if not stat.S_ISREG(info.st_mode) or (os.name != "nt" and (info.st_uid != 0 or stat.S_IMODE(info.st_mode) != 0o600)):
                raise ForwardCompatError("ledger ownership mismatch")
            raw = os.read(descriptor, MAX_LEDGER + 1)
        finally:
            os.close(descriptor)
        if len(raw) > MAX_LEDGER:
            raise ForwardCompatError("ledger exceeds bound")
        try:
            value = json.loads(raw.decode())
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ForwardCompatError("ledger malformed") from exc
        if (
            not isinstance(value, dict)
            or set(value) != {"schema", "boot_id", "comments", "handles", "strategy", "container_ip_forward"}
            or value["schema"] != "amn2.spain-forward-compat.v1"
            or BOOT_ID_RE.fullmatch(value["boot_id"]) is None
            or value["comments"] != list(COMMENTS)
            or not isinstance(value["handles"], list)
            or len(value["handles"]) != 3
            or any(type(handle) is not int or handle < 1 for handle in value["handles"])
            or value["strategy"] not in {"adopted", "created"}
            or not isinstance(value["container_ip_forward"], dict)
            or set(value["container_ip_forward"]) != {"previous", "applied", "changed"}
            or value["container_ip_forward"]["previous"] not in {"0", "1"}
            or value["container_ip_forward"]["applied"] != "1"
            or type(value["container_ip_forward"]["changed"]) is not bool
            or value["container_ip_forward"]["changed"]
            != (value["container_ip_forward"]["previous"] == "0")
        ):
            raise ForwardCompatError("ledger malformed")
        return value

    def apply(self, ledger_path: Path) -> dict[str, Any]:
        current = self._exact()
        strategy = "adopted"
        pid, previous_forward = self._container_forward()
        changed_forward = previous_forward == "0"
        created_rules = not current
        create_batch = (
                'insert rule ip filter FORWARD iifname "ens3" oifname "amn2spbr0" ip daddr 172.29.251.2 udp dport 30001 ct status dnat accept comment "amn2_spain:compat-forward-dnat"\n'
                'insert rule ip filter FORWARD iifname "amn2spbr0" oifname "ens3" ip saddr 10.212.12.0/24 accept comment "amn2_spain:compat-forward-outbound"\n'
                'insert rule ip filter FORWARD iifname "ens3" oifname "amn2spbr0" ip daddr 10.212.12.0/24 ct state established,related accept comment "amn2_spain:compat-forward-return"\n'
        ).encode()
        try:
            if changed_forward:
                self._set_container_forward(pid, "1")
            if created_rules:
                self._runner(NFT_BATCH_ARGV, input_bytes=create_batch)
                current = self._exact()
                strategy = "created"
            ledger = {
                "schema": "amn2.spain-forward-compat.v1",
                "boot_id": self._boot_id(),
                "comments": list(COMMENTS),
                "handles": [rule["handle"] for rule in current],
                "strategy": strategy,
                "container_ip_forward": {
                    "previous": previous_forward,
                    "applied": "1",
                    "changed": changed_forward,
                },
            }
            self._write_ledger(ledger_path, ledger)
            return ledger
        except Exception:
            if created_rules:
                owned = self._owned()
                handles = [rule.get("handle") for rule in owned]
                if len(handles) == 3 and all(type(handle) is int for handle in handles):
                    batch = "".join(
                        f"delete rule ip filter FORWARD handle {handle}\n"
                        for handle in handles
                    ).encode()
                    self._runner(NFT_BATCH_ARGV, input_bytes=batch)
            if changed_forward:
                self._set_container_forward(pid, previous_forward)
            raise

    def verify(self, ledger_path: Path) -> dict[str, Any]:
        ledger = self._read_ledger(ledger_path)
        if ledger["boot_id"] != self._boot_id():
            raise ForwardCompatError("ledger boot mismatch")
        current = self._exact()
        if [rule["handle"] for rule in current] != ledger["handles"]:
            raise ForwardCompatError("owned forward handles drift")
        _pid, forward = self._container_forward()
        if forward != "1":
            raise ForwardCompatError("container ip_forward drift")
        return ledger

    def rollback(self, ledger_path: Path) -> dict[str, Any]:
        ledger = self.verify(ledger_path)
        batch = "".join(
            f"delete rule ip filter FORWARD handle {handle}\n"
            for handle in ledger["handles"]
        ).encode()
        self._runner(NFT_BATCH_ARGV, input_bytes=batch)
        if self._owned():
            raise ForwardCompatError("owned forward rollback drift")
        if ledger["container_ip_forward"]["changed"]:
            pid, current = self._container_forward()
            if current != "1":
                raise ForwardCompatError("container ip_forward rollback CAS drift")
            self._set_container_forward(pid, ledger["container_ip_forward"]["previous"])
        return {"removed_handles": ledger["handles"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("apply", "verify", "rollback"))
    parser.add_argument("--ledger", required=True, type=Path)
    args = parser.parse_args()
    receipt = getattr(ForwardCompat(), args.mode)(args.ledger)
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
