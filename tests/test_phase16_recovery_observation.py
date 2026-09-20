"""Synthetic, local observations only; no collector or live resources."""
import copy
from dataclasses import FrozenInstanceError
import importlib
import itertools
import json

import pytest


def parse(raw, **expected):
    # Import at the call site so a missing implementation is an ordinary RED.
    module = importlib.import_module("scripts.vps.phase16_recovery_observation")
    return module.parse_observation(raw, **expected)


def canonical(doc):
    return (json.dumps(doc, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("ascii")


@pytest.fixture
def expected():
    return {
        "expected_bindings": {
            "package_id": "synthetic-package",
            "transaction_id": "synthetic-transaction",
            "package_identity_sha256": "a" * 64,
            "manifest_sha256": "b" * 64,
            "state_sha256": "c" * 64,
            "rollback_scope_sha256": "d" * 64,
        },
        "expected_host_id": "e" * 64,
        "expected_query_id": "f" * 64,
        "expected_sequence": 0,
        "expected_scope": {"worker": "process"},
    }


@pytest.fixture
def document(expected):
    return {
        "schema": "amn2.phase16.recovery-observation.v1",
        "bindings": copy.deepcopy(expected["expected_bindings"]),
        "host_id": expected["expected_host_id"],
        "boot_id": "12345678-1234-1234-abcd-123456789abc",
        "query_id": expected["expected_query_id"],
        "sequence": 0,
        "resources": [{
            "logical_id": "worker", "kind": "process", "status": "present",
            "identity": {"pid": 42, "start_ticks": 0, "pid_ns": 100},
        }],
    }


IDENTITIES = [
    ("process", {"pid": 42, "start_ticks": 0, "pid_ns": 100},
     (("pid", 42), ("pid_ns", 100), ("start_ticks", 0))),
    ("container", {"object_id": "1" * 64}, (("object_id", "1" * 64),)),
    ("network", {"object_id": "2" * 64}, (("object_id", "2" * 64),)),
    ("directory", {"mount_id": 3, "dev": 0, "inode": 12},
     (("dev", 0), ("inode", 12), ("mount_id", 3))),
    ("service", {"invocation_id": "3" * 32}, (("invocation_id", "3" * 32),)),
]


@pytest.mark.parametrize("kind,identity,want", IDENTITIES)
def test_present_identity_is_preserved_and_normalized(expected, document, kind, identity, want):
    expected["expected_scope"] = {"worker": kind}
    document["resources"][0].update(kind=kind, identity=identity)
    result = parse(canonical(document), **expected)
    assert result.resources[0].identity == want
    assert result.resources[0].logical_id == "worker"
    assert result.resources[0].kind == kind
    assert result.resources[0].status == "present"
    assert dict(result.bindings) == expected["expected_bindings"]
    assert (result.host_id, result.boot_id, result.query_id, result.sequence) == (
        "e" * 64, "12345678-1234-1234-abcd-123456789abc", "f" * 64, 0)


@pytest.mark.parametrize("kind,status", itertools.product(
    ["process", "container", "network", "directory", "service"], ["absent", "query_failed"]))
def test_missing_and_failed_queries_keep_distinct_status(expected, document, kind, status):
    expected["expected_scope"] = {"worker": kind}
    document["resources"][0].update(kind=kind, status=status, identity={})
    resource = parse(canonical(document), **expected).resources[0]
    assert (resource.status, resource.identity) == (status, ())


def test_snapshot_is_detached_sorted_and_immutable(expected, document):
    expected["expected_scope"] = {"z": "process", "a": "process"}
    document["resources"] = [
        dict(copy.deepcopy(document["resources"][0]), logical_id=name) for name in ("z", "a")
    ]
    old_document, old_expected = copy.deepcopy(document), copy.deepcopy(expected)
    snapshot = parse(canonical(document), **expected)
    assert [r.logical_id for r in snapshot.resources] == ["a", "z"]
    assert snapshot.bindings[0][0] == "manifest_sha256"
    assert document == old_document and expected == old_expected
    expected["expected_bindings"]["manifest_sha256"] = "9" * 64
    document["resources"][0]["identity"]["pid"] = 999
    assert dict(snapshot.bindings)["manifest_sha256"] == "b" * 64
    assert dict(snapshot.resources[1].identity)["pid"] == 42
    with pytest.raises(FrozenInstanceError):
        snapshot.sequence = 1
    with pytest.raises(FrozenInstanceError):
        snapshot.resources[0].status = "absent"


def assert_invalid(raw, expected):
    with pytest.raises(ValueError) as error:
        parse(raw, **expected)
    assert str(error.value) == "invalid_observation"
    assert "CANARY_PRIVATE_CONFIG" not in repr(error.value)
    assert error.value.__suppress_context__


@pytest.mark.parametrize("raw", [
    b'{"secret":"CANARY_PRIVATE_CONFIG"}\n', b'{"schema":NaN}\n',
    b'{"schema":"x","schema":"y"}\n', b"x" * 65537,
    b"[]\n", b"{}\n", b"", b"\xff\n", None, "CANARY_PRIVATE_CONFIG",
    b'{"x":' + b"[" * 1100 + b"0" + b"]" * 1100 + b"}\n",
], ids=["canary", "nan", "duplicate-json", "oversize", "array", "empty-object",
        "empty-bytes", "invalid-encoding", "none", "text", "too-deep"])
def test_invalid_bytes_never_echo_input(expected, raw):
    assert_invalid(raw, expected)


@pytest.mark.parametrize("encoding", ["spacing", "no-newline", "utf16", "bom"])
def test_noncanonical_encodings_rejected(expected, document, encoding):
    raw = canonical(document)
    if encoding == "spacing":
        raw = json.dumps(document).encode() + b"\n"
    elif encoding == "no-newline":
        raw = raw[:-1]
    elif encoding == "utf16":
        raw = raw.decode().encode("utf-16")
    else:
        raw = b"\xef\xbb\xbf" + raw
    assert_invalid(raw, expected)


@pytest.mark.parametrize("mutation", [
    "extra", "missing", "schema", "bindings-extra", "binding-mismatch", "binding-type",
    "host-mismatch", "host-uppercase", "query-mismatch", "boot-short", "boot-uppercase",
    "sequence-bool", "sequence-float", "sequence-wrong", "resources-dict", "empty-scope",
    "duplicate-id", "scope-extra", "scope-missing", "kind-mismatch", "resource-extra",
    "resource-missing", "resource-nonobject", "status-unknown", "status-list",
    "identity-extra", "identity-missing", "identity-list", "absent-with-identity",
])
def test_ambiguous_incomplete_or_mismatched_documents_rejected(expected, document, mutation):
    resource = document["resources"][0]
    if mutation == "extra": document["log"] = "CANARY_PRIVATE_CONFIG"
    elif mutation == "missing": del document["boot_id"]
    elif mutation == "schema": document["schema"] = "future-schema"
    elif mutation == "bindings-extra": document["bindings"]["raw"] = "CANARY_PRIVATE_CONFIG"
    elif mutation == "binding-mismatch": document["bindings"]["manifest_sha256"] = "9" * 64
    elif mutation == "binding-type": document["bindings"]["package_id"] = ["synthetic-package"]
    elif mutation == "host-mismatch": document["host_id"] = "9" * 64
    elif mutation == "host-uppercase": document["host_id"] = "E" * 64
    elif mutation == "query-mismatch": document["query_id"] = "9" * 64
    elif mutation == "boot-short": document["boot_id"] = "1234"
    elif mutation == "boot-uppercase": document["boot_id"] = document["boot_id"].upper()
    elif mutation == "sequence-bool": document["sequence"] = False
    elif mutation == "sequence-float": document["sequence"] = 0.0
    elif mutation == "sequence-wrong": document["sequence"] = 1
    elif mutation == "resources-dict": document["resources"] = {}
    elif mutation == "empty-scope": document["resources"] = []; expected["expected_scope"] = {}
    elif mutation == "duplicate-id": document["resources"].append(copy.deepcopy(resource))
    elif mutation == "scope-extra": document["resources"].append(dict(resource, logical_id="extra"))
    elif mutation == "scope-missing": expected["expected_scope"]["extra"] = "process"
    elif mutation == "kind-mismatch": resource["kind"] = "container"
    elif mutation == "resource-extra": resource["cmdline"] = "CANARY_PRIVATE_CONFIG"
    elif mutation == "resource-missing": del resource["status"]
    elif mutation == "resource-nonobject": document["resources"][0] = []
    elif mutation == "status-unknown": resource["status"] = "quiescent"
    elif mutation == "status-list": resource["status"] = ["present"]
    elif mutation == "identity-extra": resource["identity"]["argv"] = "CANARY_PRIVATE_CONFIG"
    elif mutation == "identity-missing": del resource["identity"]["pid_ns"]
    elif mutation == "identity-list": resource["identity"] = []
    elif mutation == "absent-with-identity": resource["status"] = "absent"
    assert_invalid(canonical(document), expected)


@pytest.mark.parametrize("key,value", [
    ("expected_bindings", {}), ("expected_bindings", None),
    ("expected_host_id", "E" * 64), ("expected_host_id", "e" * 63),
    ("expected_query_id", None), ("expected_query_id", "f" * 65),
    ("expected_sequence", False), ("expected_sequence", 0.0), ("expected_sequence", 2),
    ("expected_scope", {}), ("expected_scope", []),
    ("expected_scope", {"worker": "unknown"}), ("expected_scope", {"worker": []}),
    ("expected_scope", {"../worker": "process"}), ("expected_scope", {"x" * 101: "process"}),
])
def test_invalid_expectations_are_rejected_before_use(expected, document, key, value):
    expected[key] = value
    assert_invalid(canonical(document), expected)


@pytest.mark.parametrize("field,value", [
    ("package_id", "A"), ("transaction_id", "../x"), ("manifest_sha256", "b" * 63),
    ("state_sha256", "C" * 64), ("rollback_scope_sha256", None),
])
def test_matching_but_invalid_binding_values_are_not_trusted(expected, document, field, value):
    expected["expected_bindings"][field] = value
    document["bindings"][field] = value
    assert_invalid(canonical(document), expected)


@pytest.mark.parametrize("kind,field,value", [
    ("process", "pid", 0), ("process", "pid", True), ("process", "pid", "42"),
    ("process", "start_ticks", -1), ("process", "start_ticks", False),
    ("process", "pid_ns", 0), ("process", "pid_ns", 1.5),
    ("container", "object_id", "A" * 64), ("container", "object_id", "1" * 63),
    ("network", "object_id", "2" * 65), ("network", "object_id", None),
    ("directory", "mount_id", 0), ("directory", "dev", -1),
    ("directory", "inode", True), ("service", "invocation_id", "3" * 31),
    ("service", "invocation_id", "X" * 32),
])
def test_identity_types_and_ranges_are_strict(expected, document, kind, field, value):
    identity = copy.deepcopy(next(row[1] for row in IDENTITIES if row[0] == kind))
    identity[field] = value
    expected["expected_scope"] = {"worker": kind}
    document["resources"][0].update(kind=kind, identity=identity)
    assert_invalid(canonical(document), expected)


@pytest.mark.parametrize("count", [64, 65])
def test_resource_bound_includes_64_but_rejects_65(expected, document, count):
    expected["expected_scope"] = {f"worker-{i}": "process" for i in range(count)}
    document["resources"] = [
        dict(copy.deepcopy(document["resources"][0]), logical_id=name)
        for name in expected["expected_scope"]
    ]
    if count == 64:
        assert len(parse(canonical(document), **expected).resources) == 64
    else:
        assert_invalid(canonical(document), expected)


def compare(before, after):
    module = importlib.import_module("scripts.vps.phase16_recovery_observation")
    return module.compare_observations(before, after)


def snapshot_pair(expected, document, *, before_status="present", after_status="present"):
    before_doc, after_doc = copy.deepcopy(document), copy.deepcopy(document)
    before_doc["resources"][0]["status"] = before_status
    after_doc["resources"][0]["status"] = after_status
    if before_status != "present":
        before_doc["resources"][0]["identity"] = {}
    if after_status != "present":
        after_doc["resources"][0]["identity"] = {}
    after_doc["sequence"] = 1
    return (
        parse(canonical(before_doc), **expected),
        parse(canonical(after_doc), **dict(expected, expected_sequence=1)),
    )


@pytest.mark.parametrize("before_status,after_status,want", [
    ("present", "present", "IDENTITY_UNCHANGED"),
    ("present", "absent", "ABSENT_IN_SCOPE"),
    ("present", "query_failed", "UNKNOWN"),
    ("absent", "present", "APPEARED"),
    ("absent", "absent", "ABSENT_IN_SCOPE"),
    ("absent", "query_failed", "UNKNOWN"),
    ("query_failed", "present", "UNKNOWN"),
    ("query_failed", "absent", "UNKNOWN"),
    ("query_failed", "query_failed", "UNKNOWN"),
])
def test_comparison_status_table(expected, document, before_status, after_status, want):
    before, after = snapshot_pair(
        expected, document, before_status=before_status, after_status=after_status)
    assert compare(before, after) == {"worker": want}


@pytest.mark.parametrize("kind,field,new_value", [
    ("process", "pid", 43), ("process", "start_ticks", 1), ("process", "pid_ns", 101),
    ("container", "object_id", "4" * 64), ("network", "object_id", "5" * 64),
    ("directory", "mount_id", 4), ("directory", "dev", 1), ("directory", "inode", 13),
    ("service", "invocation_id", "4" * 32),
])
def test_comparison_detects_reused_alias_with_new_identity(expected, document, kind, field, new_value):
    identity = copy.deepcopy(next(row[1] for row in IDENTITIES if row[0] == kind))
    document["resources"][0].update(kind=kind, identity=identity)
    expected["expected_scope"] = {"worker": kind}
    before = parse(canonical(document), **expected)
    document["sequence"] = 1
    document["resources"][0]["identity"][field] = new_value
    after = parse(canonical(document), **dict(expected, expected_sequence=1))
    assert compare(before, after) == {"worker": "IDENTITY_CHANGED"}


@pytest.mark.parametrize("kind,identity,want", IDENTITIES)
def test_comparison_unchanged_identity_only_reports_field_equality(expected, document, kind, identity, want):
    document["resources"][0].update(kind=kind, identity=identity)
    expected["expected_scope"] = {"worker": kind}
    assert compare(*snapshot_pair(expected, document)) == {"worker": "IDENTITY_UNCHANGED"}


@pytest.mark.parametrize("mismatch", ["bindings", "host", "boot", "query", "scope", "kind"])
def test_comparison_rejects_different_contexts(expected, document, mismatch):
    before = parse(canonical(document), **expected)
    other_expected = copy.deepcopy(expected)
    other_expected["expected_sequence"] = 1
    document["sequence"] = 1
    if mismatch == "bindings":
        document["bindings"]["state_sha256"] = "9" * 64
        other_expected["expected_bindings"]["state_sha256"] = "9" * 64
    elif mismatch == "host":
        document["host_id"] = other_expected["expected_host_id"] = "9" * 64
    elif mismatch == "boot":
        document["boot_id"] = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    elif mismatch == "query":
        document["query_id"] = other_expected["expected_query_id"] = "9" * 64
    elif mismatch == "scope":
        document["resources"].append(dict(copy.deepcopy(document["resources"][0]), logical_id="child"))
        other_expected["expected_scope"]["child"] = "process"
    else:
        document["resources"][0].update(kind="container", identity={"object_id": "1" * 64})
        other_expected["expected_scope"]["worker"] = "container"
    after = parse(canonical(document), **other_expected)
    with pytest.raises(ValueError) as error:
        compare(before, after)
    assert str(error.value) == "incompatible_observations"
    assert error.value.__suppress_context__


@pytest.mark.parametrize("sequences", [(1, 0), (0, 0), (1, 1)])
def test_comparison_rejects_reversed_or_repeated_sequence(expected, document, sequences):
    snapshots = []
    for sequence in sequences:
        document["sequence"] = sequence
        snapshots.append(parse(canonical(document), **dict(expected, expected_sequence=sequence)))
    with pytest.raises(ValueError, match="^incompatible_observations$"):
        compare(*snapshots)


def test_comparison_two_absent_snapshots_give_no_cleanup_authority(expected, document):
    document["resources"][0].update(status="absent", identity={})
    document["resources"].append(dict(copy.deepcopy(document["resources"][0]), logical_id="child"))
    expected["expected_scope"]["child"] = "process"
    before = parse(canonical(document), **expected)
    document["sequence"] = 1
    after = parse(canonical(document), **dict(expected, expected_sequence=1))
    assert compare(before, after) == {"child": "ABSENT_IN_SCOPE", "worker": "ABSENT_IN_SCOPE"}
    assert before.sequence == 0 and after.sequence == 1


@pytest.mark.parametrize("bad", [None, {}, "CANARY_PRIVATE_CONFIG"])
@pytest.mark.parametrize("side", ["before", "after"])
def test_comparison_wrong_input_type_has_fixed_error(expected, document, bad, side):
    before, after = snapshot_pair(expected, document)
    with pytest.raises(ValueError) as error:
        compare(bad if side == "before" else before, bad if side == "after" else after)
    assert str(error.value) == "incompatible_observations"
    assert "CANARY_PRIVATE_CONFIG" not in repr(error.value)
