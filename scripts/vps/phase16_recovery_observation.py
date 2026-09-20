"""Pure bounded observations, never ownership, quiescence or recovery authority.

Only caller-supplied bytes are parsed. No collector, command, file or network I/O.
Expected context must come from an independently checked source; matching it
does not establish freshness or truth of observations.
"""
from dataclasses import dataclass
import re

from scripts.vps.phase16_recovery_metadata import BINDING_KEYS, parse_canonical


_SCHEMA = "amn2.phase16.recovery-observation.v1"
_TOP_KEYS = frozenset({
    "schema", "bindings", "host_id", "boot_id", "query_id", "sequence", "resources",
})
_RESOURCE_KEYS = frozenset({"logical_id", "kind", "status", "identity"})
_ALIAS = r"[a-z0-9][a-z0-9._-]{0,99}"
_HEX64 = r"[0-9a-f]{64}"
_UUID = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
_IDENTITY_RULES = {
    "process": {"pid": "positive", "pid_ns": "positive", "start_ticks": "nonnegative"},
    "container": {"object_id": "hex64"},
    "network": {"object_id": "hex64"},
    "directory": {"mount_id": "positive", "dev": "nonnegative", "inode": "nonnegative"},
    "service": {"invocation_id": "hex32"},
}


@dataclass(frozen=True)
class ResourceObservation:
    logical_id: str
    kind: str
    status: str
    identity: tuple[tuple[str, str | int], ...]


@dataclass(frozen=True)
class Snapshot:
    bindings: tuple[tuple[str, str], ...]
    host_id: str
    boot_id: str
    query_id: str
    sequence: int
    resources: tuple[ResourceObservation, ...]


def _matches(value, pattern):
    return isinstance(value, str) and re.fullmatch(pattern, value) is not None


def _bindings_valid(bindings):
    return (
        type(bindings) is dict
        and set(bindings) == BINDING_KEYS
        and all(_matches(bindings[key], _HEX64 if key.endswith("sha256") else _ALIAS)
                for key in BINDING_KEYS)
    )


def _scope_valid(scope):
    return (
        type(scope) is dict and 1 <= len(scope) <= 64
        and all(_matches(name, _ALIAS) and isinstance(kind, str) and kind in _IDENTITY_RULES
                for name, kind in scope.items())
    )


def _sequence_valid(sequence):
    return type(sequence) is int and sequence in (0, 1)


def _identity_valid(kind, identity):
    rules = _IDENTITY_RULES[kind]
    if type(identity) is not dict or set(identity) != set(rules):
        return False
    for key, rule in rules.items():
        value = identity[key]
        if rule in ("positive", "nonnegative"):
            if type(value) is not int or value < (1 if rule == "positive" else 0):
                return False
        elif not _matches(value, _HEX64 if rule == "hex64" else r"[0-9a-f]{32}"):
            return False
    return True


def parse_observation(
    raw: bytes, *, expected_bindings: dict[str, str], expected_host_id: str,
    expected_query_id: str, expected_sequence: int,
    expected_scope: dict[str, str],
) -> Snapshot:
    """Validate canonical bytes and context, returning a detached immutable value.

    A valid shape is no proof of ownership or of a complete resource inventory.
    Every invalid input raises ValueError("invalid_observation"), without raw data.
    """
    try:
        if not (
            _bindings_valid(expected_bindings)
            and _matches(expected_host_id, _HEX64)
            and _matches(expected_query_id, _HEX64)
            and _sequence_valid(expected_sequence)
            and _scope_valid(expected_scope)
        ):
            raise ValueError

        doc = parse_canonical(raw)
        if not (
            set(doc) == _TOP_KEYS and doc["schema"] == _SCHEMA
            and _bindings_valid(doc["bindings"])
            and doc["bindings"] == expected_bindings
            and doc["host_id"] == expected_host_id
            and _matches(doc["boot_id"], _UUID)
            and doc["query_id"] == expected_query_id
            and _sequence_valid(doc["sequence"])
            and doc["sequence"] == expected_sequence
            and type(doc["resources"]) is list
            and 1 <= len(doc["resources"]) <= 64
        ):
            raise ValueError

        resources = {}
        for item in doc["resources"]:
            if type(item) is not dict or set(item) != _RESOURCE_KEYS:
                raise ValueError
            name, kind, status, identity = (
                item["logical_id"], item["kind"], item["status"], item["identity"],
            )
            if not (
                _matches(name, _ALIAS) and name in expected_scope and name not in resources
                and isinstance(kind, str) and kind == expected_scope[name]
                and isinstance(status, str) and status in ("present", "absent", "query_failed")
                and type(identity) is dict
            ):
                raise ValueError
            if status == "present":
                if not _identity_valid(kind, identity):
                    raise ValueError
            elif identity:
                raise ValueError
            resources[name] = ResourceObservation(name, kind, status, tuple(sorted(identity.items())))

        if set(resources) != set(expected_scope):
            raise ValueError
        return Snapshot(
            tuple(sorted(doc["bindings"].items())), doc["host_id"], doc["boot_id"],
            doc["query_id"], doc["sequence"], tuple(resources[name] for name in sorted(resources)),
        )
    except (ValueError, TypeError, KeyError, RecursionError):
        raise ValueError("invalid_observation") from None


def compare_observations(before: Snapshot, after: Snapshot) -> dict[str, str]:
    """Compare two immutable snapshots returned by parse_observation.

    Equality means only equal observed fields, not proof of the same lifetime.
    Absence is limited to the supplied scope; UNKNOWN never implies absence.
    No result authorizes a signal, deletion, retry or lifting a stage block.
    """
    if not (
        type(before) is Snapshot and type(after) is Snapshot
        and type(before.sequence) is int and type(after.sequence) is int
        and (before.sequence, after.sequence) == (0, 1)
        and before.bindings == after.bindings
        and before.host_id == after.host_id
        and before.boot_id == after.boot_id
        and before.query_id == after.query_id
        and tuple((r.logical_id, r.kind) for r in before.resources)
        == tuple((r.logical_id, r.kind) for r in after.resources)
    ):
        raise ValueError("incompatible_observations") from None

    result = {}
    for old, new in zip(before.resources, after.resources):
        if "query_failed" in (old.status, new.status):
            outcome = "UNKNOWN"
        elif new.status == "absent":
            outcome = "ABSENT_IN_SCOPE"
        elif old.status == "absent":
            outcome = "APPEARED"
        elif old.identity == new.identity:
            outcome = "IDENTITY_UNCHANGED"
        else:
            outcome = "IDENTITY_CHANGED"
        result[old.logical_id] = outcome
    return result
