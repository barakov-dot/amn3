from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import stat
import subprocess
import tempfile
import threading
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
NFT_CONFIG_PATH = ROOT / "packaging" / "phase12-spain" / "templates" / "nftables.conf"
UNIT_PATH = ROOT / "packaging" / "phase12-spain" / "units" / "amn2-spain-network.service"
NFT_CONFIG = """table inet amn2_spain {
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

NFT = "/usr/sbin/nft"
IP = "/usr/sbin/ip"
SYSCTL = "/usr/sbin/sysctl"
CAT = "/usr/bin/cat"
COMMAND_TIMEOUT = 10.0
MAX_OUTPUT = 1024 * 1024
MAX_INPUT = 64 * 1024
MAX_LEDGER_BYTES = 64 * 1024
BOOT_ID_PATTERN = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")

ROUTE_IDENTITY = {
    "dst": "10.212.12.0/24",
    "gateway": "172.29.251.2",
    "dev": "amn2spbr0",
}
NFT_IDENTITY = {"family": "inet", "table": "amn2_spain"}
NFT_CHAINS = ["prerouting", "forward", "postrouting"]
NFT_RULE_COMMENTS = [
    "amn2_spain:udp30001",
    "amn2_spain:forward-dnat",
    "amn2_spain:forward-outbound",
    "amn2_spain:forward-return",
    "amn2_spain:masquerade",
]


class NetworkError(RuntimeError):
    pass


class CommandError(NetworkError):
    pass


class BoundedCommandRunner:
    def __call__(
        self,
        argv: tuple[str, ...],
        *,
        input_bytes: bytes | None = None,
        timeout: float = COMMAND_TIMEOUT,
        max_output: int = MAX_OUTPUT,
    ) -> bytes:
        if (
            not isinstance(argv, tuple)
            or not argv
            or any(not isinstance(part, str) or not part for part in argv)
            or not isinstance(timeout, (int, float))
            or timeout <= 0
            or not isinstance(max_output, int)
            or max_output <= 0
            or (input_bytes is not None and (not isinstance(input_bytes, bytes) or len(input_bytes) > MAX_INPUT))
        ):
            raise CommandError("invalid command boundary")
        try:
            process = subprocess.Popen(
                argv,
                stdin=subprocess.PIPE if input_bytes is not None else subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
            )
        except OSError as exc:
            raise CommandError("command could not be executed") from exc

        oversized = threading.Event()
        output = bytearray()
        error_output = bytearray()

        def drain(stream: Any, destination: bytearray) -> None:
            try:
                while chunk := stream.read(64 * 1024):
                    remaining = max_output + 1 - len(destination)
                    if remaining > 0:
                        destination.extend(chunk[:remaining])
                    if len(destination) > max_output:
                        oversized.set()
                        try:
                            process.kill()
                        except OSError:
                            pass
                        return
            finally:
                stream.close()

        if process.stdout is None or process.stderr is None:
            process.kill()
            raise CommandError("command pipes unavailable")
        readers = [
            threading.Thread(target=drain, args=(process.stdout, output), daemon=True),
            threading.Thread(target=drain, args=(process.stderr, error_output), daemon=True),
        ]
        for reader in readers:
            reader.start()
        try:
            if input_bytes is not None:
                if process.stdin is None:
                    raise CommandError("command input pipe unavailable")
                try:
                    process.stdin.write(input_bytes)
                    process.stdin.close()
                except BrokenPipeError:
                    pass
            try:
                return_code = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired as exc:
                process.kill()
                process.wait()
                raise CommandError("command timed out") from exc
        finally:
            for reader in readers:
                reader.join()
        if oversized.is_set():
            raise CommandError("command output exceeded bound")
        if return_code != 0:
            raise CommandError("command failed")
        return bytes(output)


Runner = Callable[..., bytes]


def _match(protocol: str, field: str, value: Any, *, operation: str = "==") -> dict[str, Any]:
    return {
        "match": {
            "op": operation,
            "left": {"payload": {"protocol": protocol, "field": field}},
            "right": value,
        }
    }


def _meta_match(key: str, value: Any, *, operation: str = "==") -> dict[str, Any]:
    return {
        "match": {
            "op": operation,
            "left": {"meta": {"key": key}},
            "right": value,
        }
    }


def expected_table_document() -> dict[str, Any]:
    common = {"family": "inet", "table": "amn2_spain"}
    return {
        "nftables": [
            {"table": {"family": "inet", "name": "amn2_spain"}},
            {"chain": {**common, "name": "prerouting", "type": "nat", "hook": "prerouting", "prio": -100, "policy": "accept"}},
            {"rule": {**common, "chain": "prerouting", "expr": [_match("udp", "dport", 30001), {"dnat": {"addr": "172.29.251.2", "port": 30001}}], "comment": "amn2_spain:udp30001"}},
            {"chain": {**common, "name": "forward", "type": "filter", "hook": "forward", "prio": 0, "policy": "accept"}},
            {"rule": {**common, "chain": "forward", "expr": [_meta_match("oifname", "amn2spbr0"), _match("ip", "daddr", "172.29.251.2"), _match("udp", "dport", 30001), {"accept": None}], "comment": "amn2_spain:forward-dnat"}},
            {"rule": {**common, "chain": "forward", "expr": [_meta_match("iifname", "amn2spbr0"), _match("ip", "saddr", {"prefix": {"addr": "10.212.12.0", "len": 24}}), {"accept": None}], "comment": "amn2_spain:forward-outbound"}},
            {"rule": {**common, "chain": "forward", "expr": [_meta_match("oifname", "amn2spbr0"), _match("ip", "daddr", {"prefix": {"addr": "10.212.12.0", "len": 24}}), {"match": {"op": "in", "left": {"ct": {"key": "state"}}, "right": ["established", "related"]}}, {"accept": None}], "comment": "amn2_spain:forward-return"}},
            {"chain": {**common, "name": "postrouting", "type": "nat", "hook": "postrouting", "prio": 100, "policy": "accept"}},
            {"rule": {**common, "chain": "postrouting", "expr": [_match("ip", "saddr", {"prefix": {"addr": "10.212.12.0", "len": 24}}), _meta_match("oifname", "amn2spbr0", operation="!="), {"masquerade": None}], "comment": "amn2_spain:masquerade"}},
        ]
    }


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _semantic_digest(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _decode_json(raw: bytes, label: str) -> Any:
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise NetworkError(f"{label} JSON malformed") from exc


def _remove_volatile(value: Any) -> Any:
    if isinstance(value, list):
        return [_remove_volatile(item) for item in value]
    if isinstance(value, dict):
        return {
            key: _remove_volatile(item)
            for key, item in value.items()
            if key not in {"handle", "index", "packets", "bytes"}
        }
    return value


def _owned_semantics(document: Any) -> dict[str, Any]:
    if not isinstance(document, dict) or set(document) != {"nftables"} or not isinstance(document["nftables"], list):
        raise NetworkError("owned nft JSON schema mismatch")
    entries: list[dict[str, Any]] = []
    for entry in document["nftables"]:
        if not isinstance(entry, dict) or len(entry) != 1:
            raise NetworkError("owned nft JSON schema mismatch")
        kind, body = next(iter(entry.items()))
        if kind == "metainfo":
            continue
        if kind not in {"table", "chain", "rule"} or not isinstance(body, dict):
            raise NetworkError("owned nft JSON schema mismatch")
        entries.append({kind: _remove_volatile(body)})
    return {"nftables": entries}


EXPECTED_NFT_SEMANTICS = _owned_semantics(expected_table_document())
EXPECTED_NFT_SEMANTIC_SHA256 = _semantic_digest(EXPECTED_NFT_SEMANTICS)


class NetworkManager:
    def __init__(
        self, runner: Runner | None = None, *, nft_config: str = NFT_CONFIG
    ) -> None:
        if nft_config != NFT_CONFIG:
            raise NetworkError("checksum-bound nft config mismatch")
        self._run: Runner = runner or BoundedCommandRunner()
        self._nft_config = nft_config

    def _command(self, argv: tuple[str, ...], input_bytes: bytes | None = None) -> bytes:
        return self._run(argv, input_bytes=input_bytes, timeout=COMMAND_TIMEOUT, max_output=MAX_OUTPUT)

    def _boot_id(self) -> str:
        try:
            value = self._command((CAT, "/proc/sys/kernel/random/boot_id")).decode("ascii").strip()
        except UnicodeDecodeError as exc:
            raise NetworkError("boot id malformed") from exc
        if BOOT_ID_PATTERN.fullmatch(value) is None:
            raise NetworkError("boot id malformed")
        return value

    def _assert_boot(self, expected: str) -> None:
        if BOOT_ID_PATTERN.fullmatch(expected) is None or self._boot_id() != expected:
            raise NetworkError("boot id mismatch")

    def _assert_foreign_compatible(self) -> bool:
        value = _decode_json(self._command((NFT, "-j", "list", "ruleset")), "nft ruleset")
        if not isinstance(value, dict) or set(value) != {"nftables"} or not isinstance(value["nftables"], list):
            raise NetworkError("nft ruleset JSON schema mismatch")
        foreign_forward_chains: set[tuple[str, str, str]] = set()
        owned_table_count = 0
        for entry in value["nftables"]:
            if not isinstance(entry, dict) or len(entry) != 1:
                raise NetworkError("nft ruleset JSON schema mismatch")
            kind, body = next(iter(entry.items()))
            if not isinstance(kind, str) or not isinstance(body, dict):
                raise NetworkError("nft ruleset JSON schema mismatch")
            if kind == "table" and not (
                isinstance(body.get("family"), str) and isinstance(body.get("name"), str)
            ):
                raise NetworkError("nft ruleset JSON schema mismatch")
            if kind == "table" and body.get("family") == "inet" and body.get("name") == "amn2_spain":
                owned_table_count += 1
            if kind == "chain" and not all(
                isinstance(body.get(field), str) and body.get(field)
                for field in ("family", "table", "name")
            ):
                raise NetworkError("nft ruleset JSON schema mismatch")
            if kind == "rule" and not (
                all(isinstance(body.get(field), str) and body.get(field) for field in ("family", "table", "chain"))
                and isinstance(body.get("expr"), list)
            ):
                raise NetworkError("nft ruleset JSON schema mismatch")
            chain = body if kind == "chain" else None
            if (
                chain is None
                or chain.get("hook") != "forward"
                or chain.get("table") == "amn2_spain"
                or (
                    chain.get("family") in {"ip", "ip6"}
                    and chain.get("table") == "docker-bridges"
                )
            ):
                continue
            identity = (chain.get("family"), chain.get("table"), chain.get("name"))
            if not all(isinstance(part, str) and part for part in identity):
                raise NetworkError("nft ruleset JSON schema mismatch")
            foreign_forward_chains.add(identity)
            if chain.get("type") != "filter" or chain.get("policy") != "accept":
                raise NetworkError("foreign forward base chain is incompatible")
        for entry in value["nftables"]:
            rule = entry.get("rule") if isinstance(entry, dict) else None
            if not isinstance(rule, dict):
                continue
            identity = (rule.get("family"), rule.get("table"), rule.get("chain"))
            if identity not in foreign_forward_chains:
                continue
            expressions = rule.get("expr")
            if not isinstance(expressions, list):
                raise NetworkError("nft ruleset JSON schema mismatch")
            if any(isinstance(expression, dict) and ("drop" in expression or "reject" in expression) for expression in expressions):
                raise NetworkError("foreign forward base chain is incompatible")
        if owned_table_count > 1:
            raise NetworkError("nft ruleset JSON schema mismatch")
        return owned_table_count == 1

    def _owned_declared(self) -> bool:
        value = _decode_json(self._command((NFT, "-j", "list", "ruleset")), "nft ruleset")
        if not isinstance(value, dict) or set(value) != {"nftables"} or not isinstance(value["nftables"], list):
            raise NetworkError("nft ruleset JSON schema mismatch")
        count = 0
        for entry in value["nftables"]:
            if not isinstance(entry, dict) or len(entry) != 1:
                raise NetworkError("nft ruleset JSON schema mismatch")
            kind, body = next(iter(entry.items()))
            if not isinstance(kind, str) or not isinstance(body, dict):
                raise NetworkError("nft ruleset JSON schema mismatch")
            if kind == "table" and body.get("family") == "inet" and body.get("name") == "amn2_spain":
                count += 1
        if count > 1:
            raise NetworkError("nft ruleset JSON schema mismatch")
        return count == 1

    def _owned_state(self, declared_present: bool | None = None) -> str:
        if declared_present is None:
            declared_present = self._owned_declared()
        if not declared_present:
            return "absent"
        try:
            raw = self._command((NFT, "-j", "list", "table", "inet", "amn2_spain"))
        except CommandError:
            raise
        current = _owned_semantics(_decode_json(raw, "owned nft"))
        if current != EXPECTED_NFT_SEMANTICS:
            raise NetworkError("owned nft semantics mismatch")
        return "exact"

    def _route_state(self) -> str:
        value = _decode_json(
            self._command((IP, "-j", "route", "show", "exact", "10.212.12.0/24")),
            "route",
        )
        if value == []:
            return "absent"
        if not isinstance(value, list) or len(value) != 1 or not isinstance(value[0], dict):
            raise NetworkError("route identity conflict")
        identity = {key: value[0].get(key) for key in ROUTE_IDENTITY}
        if identity != ROUTE_IDENTITY:
            raise NetworkError("route identity conflict")
        return "exact"

    def _sysctl_state(self) -> str:
        try:
            value = self._command((SYSCTL, "-n", "net.ipv4.ip_forward")).decode("ascii").strip()
        except UnicodeDecodeError as exc:
            raise NetworkError("ip_forward observation malformed") from exc
        if value not in {"0", "1"}:
            raise NetworkError("ip_forward observation malformed")
        return value

    def apply(
        self,
        *,
        expected_boot_id: str | None = None,
        existing_ledger: dict[str, Any] | None = None,
        persist_intent: Callable[[dict[str, Any]], None] | None = None,
    ) -> dict[str, Any]:
        boot_id = self._boot_id()
        if expected_boot_id is not None and expected_boot_id != boot_id:
            raise NetworkError("boot id mismatch")
        if existing_ledger is not None:
            ledger = self._validate_ledger(existing_ledger)
            if ledger["boot_id"] != boot_id:
                raise NetworkError("boot id mismatch")
        else:
            owned_declared = self._assert_foreign_compatible()
            nft_state = self._owned_state(owned_declared)
            route_state = self._route_state()
            sysctl_previous = self._sysctl_state()
            ledger = {
                "schema": "amn2.spain-network-ledger.v1",
                "boot_id": boot_id,
                "nft": {
                    "identity": copy.deepcopy(NFT_IDENTITY),
                    "chains": copy.deepcopy(NFT_CHAINS),
                    "rule_comments": copy.deepcopy(NFT_RULE_COMMENTS),
                    "semantic_sha256": EXPECTED_NFT_SEMANTIC_SHA256,
                    "created": nft_state == "absent",
                },
                "route": {
                    "identity": copy.deepcopy(ROUTE_IDENTITY),
                    "created": route_state == "absent",
                },
                "sysctl": {
                    "name": "net.ipv4.ip_forward",
                    "previous": sysctl_previous,
                    "applied": "1",
                    "changed": sysctl_previous == "0",
                },
            }
            mutation_planned = (
                ledger["nft"]["created"]
                or ledger["route"]["created"]
                or ledger["sysctl"]["changed"]
            )
            if mutation_planned and persist_intent is None:
                raise NetworkError("durable network intent callback required before mutation")
            if persist_intent is not None:
                try:
                    persist_intent(copy.deepcopy(ledger))
                except Exception as exc:
                    raise NetworkError("durable network intent could not be persisted") from exc
        try:
            self._converge_prepared(ledger)
            self.verify(ledger)
            return copy.deepcopy(ledger)
        except (CommandError, NetworkError) as exc:
            try:
                self._rollback_validated(ledger)
            except NetworkError as rollback_error:
                raise NetworkError("network apply failed; compensation failed") from rollback_error
            raise NetworkError("network apply failed; compensation completed") from exc

    def _converge_prepared(self, ledger: dict[str, Any]) -> None:
        owned_declared = self._assert_foreign_compatible()
        nft_state = self._owned_state(owned_declared)
        route_state = self._route_state()
        sysctl_state = self._sysctl_state()
        if ledger["nft"]["created"]:
            if nft_state == "absent":
                payload = self._nft_config.encode("utf-8")
                self._command((NFT, "--check", "-f", "-"), payload)
                self._command((NFT, "-f", "-"), payload)
            elif nft_state != "exact":
                raise NetworkError("owned nft prepared-intent CAS drift")
        elif nft_state != "exact":
            raise NetworkError("preexisting owned nft identity drift")
        if self._owned_state() != "exact":
            raise NetworkError("owned nft post-apply verification failed")

        if ledger["route"]["created"]:
            if route_state == "absent":
                self._command((IP, "route", "add", "10.212.12.0/24", "via", "172.29.251.2", "dev", "amn2spbr0"))
            elif route_state != "exact":
                raise NetworkError("route prepared-intent CAS drift")
        elif route_state != "exact":
            raise NetworkError("preexisting route identity drift")
        if self._route_state() != "exact":
            raise NetworkError("route post-apply verification failed")

        if ledger["sysctl"]["changed"]:
            if sysctl_state == ledger["sysctl"]["previous"]:
                self._command((SYSCTL, "-q", "-w", "net.ipv4.ip_forward=1"))
            elif sysctl_state != ledger["sysctl"]["applied"]:
                raise NetworkError("sysctl prepared-intent CAS drift")
        elif sysctl_state != ledger["sysctl"]["applied"]:
            raise NetworkError("preexisting sysctl identity drift")
        if self._sysctl_state() != "1":
            raise NetworkError("sysctl post-apply verification failed")

    def verify(self, ledger: dict[str, Any]) -> None:
        value = self._validate_ledger(ledger)
        self._assert_boot(value["boot_id"])
        owned_declared = self._assert_foreign_compatible()
        if self._owned_state(owned_declared) != "exact":
            raise NetworkError("owned nft verification failed")
        if self._route_state() != "exact":
            raise NetworkError("route verification failed")
        if self._sysctl_state() != "1":
            raise NetworkError("sysctl verification failed")

    def prepared_is_resumable(
        self, ledger: dict[str, Any], *, expected_boot_id: str
    ) -> bool:
        try:
            value = self._validate_ledger(ledger)
            if value["boot_id"] != expected_boot_id:
                return False
            self._assert_boot(expected_boot_id)
            owned_declared = self._assert_foreign_compatible()
            nft_state = self._owned_state(owned_declared)
            route_state = self._route_state()
            sysctl_state = self._sysctl_state()
        except (CommandError, NetworkError):
            return False
        return (
            nft_state
            in ({"absent", "exact"} if value["nft"]["created"] else {"exact"})
            and route_state
            in ({"absent", "exact"} if value["route"]["created"] else {"exact"})
            and sysctl_state
            in (
                {value["sysctl"]["previous"], value["sysctl"]["applied"]}
                if value["sysctl"]["changed"]
                else {value["sysctl"]["applied"]}
            )
        )

    def rollback(self, ledger: dict[str, Any]) -> None:
        value = self._validate_ledger(ledger)
        self._assert_boot(value["boot_id"])
        self._rollback_validated(value)

    def _rollback_validated(self, ledger: dict[str, Any]) -> None:
        nft_state = "unowned"
        route_state = "unowned"
        sysctl_state = "unowned"
        if ledger["nft"]["created"]:
            try:
                nft_state = self._owned_state()
            except NetworkError as exc:
                raise NetworkError("owned nft CAS drift") from exc
            if nft_state not in {"exact", "absent"}:
                raise NetworkError("owned nft CAS drift")
        if ledger["route"]["created"]:
            try:
                route_state = self._route_state()
            except NetworkError as exc:
                raise NetworkError("route CAS drift") from exc
            if route_state not in {"exact", "absent"}:
                raise NetworkError("route CAS drift")
        if ledger["sysctl"]["changed"]:
            try:
                sysctl_state = self._sysctl_state()
            except NetworkError as exc:
                raise NetworkError("sysctl CAS drift") from exc
            if sysctl_state not in {ledger["sysctl"]["applied"], ledger["sysctl"]["previous"]}:
                raise NetworkError("sysctl CAS drift")
        if ledger["sysctl"]["changed"] and sysctl_state == ledger["sysctl"]["applied"]:
            self._command((SYSCTL, "-q", "-w", f"net.ipv4.ip_forward={ledger['sysctl']['previous']}"))
            if self._sysctl_state() != ledger["sysctl"]["previous"]:
                raise NetworkError("sysctl rollback verification failed")
        if ledger["route"]["created"] and route_state == "exact":
            self._command((IP, "route", "del", "10.212.12.0/24", "via", "172.29.251.2", "dev", "amn2spbr0"))
            if self._route_state() != "absent":
                raise NetworkError("route rollback verification failed")
        if ledger["nft"]["created"] and nft_state == "exact":
            self._command((NFT, "delete", "table", "inet", "amn2_spain"))
            if self._owned_state() != "absent":
                raise NetworkError("owned nft rollback verification failed")

    @staticmethod
    def _validate_ledger(value: Any) -> dict[str, Any]:
        try:
            if not isinstance(value, dict) or set(value) != {"schema", "boot_id", "nft", "route", "sysctl"}:
                raise ValueError
            if value["schema"] != "amn2.spain-network-ledger.v1" or BOOT_ID_PATTERN.fullmatch(value["boot_id"]) is None:
                raise ValueError
            nft = value["nft"]
            route = value["route"]
            sysctl = value["sysctl"]
            if (
                not isinstance(nft, dict)
                or set(nft) != {"identity", "chains", "rule_comments", "semantic_sha256", "created"}
                or nft["identity"] != NFT_IDENTITY
                or nft["chains"] != NFT_CHAINS
                or nft["rule_comments"] != NFT_RULE_COMMENTS
                or nft["semantic_sha256"] != EXPECTED_NFT_SEMANTIC_SHA256
                or type(nft["created"]) is not bool
                or not isinstance(route, dict)
                or set(route) != {"identity", "created"}
                or route["identity"] != ROUTE_IDENTITY
                or type(route["created"]) is not bool
                or not isinstance(sysctl, dict)
                or set(sysctl) != {"name", "previous", "applied", "changed"}
                or sysctl["name"] != "net.ipv4.ip_forward"
                or sysctl["previous"] not in {"0", "1"}
                or sysctl["applied"] != "1"
                or type(sysctl["changed"]) is not bool
                or sysctl["changed"] != (sysctl["previous"] == "0")
            ):
                raise ValueError
        except (KeyError, TypeError, ValueError) as exc:
            raise NetworkError("network ledger schema mismatch") from exc
        return copy.deepcopy(value)


def _read_ledger(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise NetworkError("network ledger cannot be opened") from exc
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or (os.name != "nt" and (stat.S_IMODE(info.st_mode) != 0o600 or info.st_uid != 0)):
            raise NetworkError("network ledger ownership mismatch")
        raw = os.read(descriptor, MAX_LEDGER_BYTES + 1)
    finally:
        os.close(descriptor)
    if len(raw) > MAX_LEDGER_BYTES:
        raise NetworkError("network ledger exceeds size bound")
    return _decode_json(raw, "network ledger")


def _write_ledger(path: Path, ledger: dict[str, Any]) -> None:
    if path.parent.is_symlink() or path.is_symlink():
        raise NetworkError("network ledger path is unsafe")
    if not path.parent.is_dir():
        raise NetworkError("network ledger parent missing")
    payload = _canonical_bytes(ledger) + b"\n"
    if len(payload) > MAX_LEDGER_BYTES:
        raise NetworkError("network ledger exceeds size bound")
    descriptor, temporary_name = tempfile.mkstemp(prefix=".network-ledger-", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        os.fchmod(descriptor, 0o600)
        os.write(descriptor, payload)
        os.fsync(descriptor)
        os.close(descriptor)
        descriptor = -1
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if temporary.exists():
            temporary.unlink()


def _remove_ledger(path: Path) -> None:
    if path.is_symlink():
        raise NetworkError("network ledger path is unsafe")
    path.unlink()
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Manage the sealed AMN2 Spain network contour")
    parser.add_argument("action", choices=("apply", "verify", "rollback"))
    parser.add_argument("--ledger", required=True, type=Path)
    arguments = parser.parse_args(argv)
    manager = NetworkManager()
    try:
        existing = _read_ledger(arguments.ledger)
        if arguments.action == "apply":
            ledger = manager.apply(
                existing_ledger=existing,
                persist_intent=(
                    None
                    if existing is not None
                    else lambda prepared: _write_ledger(arguments.ledger, prepared)
                ),
            )
            _write_ledger(arguments.ledger, ledger)
        else:
            if existing is None:
                raise NetworkError("network ledger missing")
            if arguments.action == "verify":
                manager.verify(existing)
            else:
                manager.rollback(existing)
                _remove_ledger(arguments.ledger)
    except NetworkError:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
