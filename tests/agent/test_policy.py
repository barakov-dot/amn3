import pytest

from app.agent.policy import (
    AGENT_ROUTE_POLICIES,
    AgentPolicyError,
    first_slice_policies,
    get_policy,
)


EXPECTED_FIRST_SLICE = (
    ("GET", "/agent/health", "agent:health", "read-only"),
    ("GET", "/agent/version", "agent:health", "read-only"),
    ("GET", "/agent/runtime", "agent:read", "read-only-runtime"),
    ("GET", "/agent/protocols", "agent:protocols:read", "read-only-runtime"),
)

KNOWN_RISK_CLASSES = {
    "read-only",
    "read-only-runtime",
    "secret-read",
    "state-write",
    "destructive-local",
}


def test_first_slice_policies_contain_exact_route_matrix():
    assert tuple(
        (policy.method, policy.path, policy.scope, policy.risk_class)
        for policy in first_slice_policies()
    ) == EXPECTED_FIRST_SLICE


def test_every_first_slice_policy_requires_audit():
    assert all(policy.audit_required is True for policy in first_slice_policies())


@pytest.mark.parametrize(
    "path",
    (
        "/agent/clients",
        "/agent/clients/{id}",
        "/agent/configs/{id}",
        "/agent/backup/redacted",
        "/agent/backup/full",
        "/agent/restore",
        "/agent/reboot",
    ),
)
def test_risky_paths_are_not_first_slice(path):
    assert path not in {policy.path for policy in first_slice_policies()}


def test_get_policy_returns_first_slice_protocols_policy():
    policy = get_policy("GET", "/agent/protocols")

    assert policy.scope == "agent:protocols:read"
    assert policy.risk_class == "read-only-runtime"
    assert policy.first_slice is True


def test_get_policy_rejects_future_blocked_policy():
    with pytest.raises(AgentPolicyError, match="No agent route policy"):
        get_policy("POST", "/agent/clients")


def test_every_policy_has_required_fields_and_known_classifications():
    for policy in AGENT_ROUTE_POLICIES:
        assert policy.method
        assert policy.path.startswith("/agent/")
        assert policy.scope.startswith("agent:")
        assert policy.risk_class in KNOWN_RISK_CLASSES
        assert isinstance(policy.audit_required, bool)
