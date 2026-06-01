from app.security.ssh_host_key import parse_ssh_host_key_line
from app.security.ssh_host_key import verify_ssh_host_key_pin


KEY_BLOB = "dGVzdC1ob3N0LWtleS12MQ=="
KEY_LINE = f"203.0.113.10 ssh-ed25519 {KEY_BLOB} operator-test-key"
EXPECTED_FINGERPRINT = "SHA256:23i3Y3BfBU5FfQ2kqEvZyXHvBGhxLcy1yJeBuujKtUs"


def test_parse_ssh_host_key_line_extracts_safe_identity():
    identity = parse_ssh_host_key_line(KEY_LINE)

    assert identity.hosts == ("203.0.113.10",)
    assert identity.key_type == "ssh-ed25519"
    assert identity.fingerprint_sha256 == EXPECTED_FINGERPRINT
    assert identity.comment == "operator-test-key"


def test_parse_ssh_host_key_line_accepts_bare_public_key_line():
    identity = parse_ssh_host_key_line(f"ssh-ed25519 {KEY_BLOB}")

    assert identity.hosts == ()
    assert identity.key_type == "ssh-ed25519"
    assert identity.fingerprint_sha256 == EXPECTED_FINGERPRINT


def test_verify_ssh_host_key_pin_allows_matching_pin_and_host():
    result = verify_ssh_host_key_pin(
        KEY_LINE,
        expected_sha256_fingerprint=EXPECTED_FINGERPRINT,
        expected_host="203.0.113.10",
    )

    assert result.trusted is True
    assert result.status == "verified"
    assert result.fingerprint_sha256 == EXPECTED_FINGERPRINT
    assert result.safe_metadata() == {
        "status": "verified",
        "trusted": True,
        "key_type": "ssh-ed25519",
        "fingerprint_sha256": EXPECTED_FINGERPRINT,
        "expected_fingerprint_sha256": EXPECTED_FINGERPRINT,
        "host": "203.0.113.10",
        "host_matched": True,
    }


def test_verify_ssh_host_key_pin_blocks_mismatched_pin_without_raw_key_metadata():
    result = verify_ssh_host_key_pin(
        KEY_LINE,
        expected_sha256_fingerprint="SHA256:wrong-pin",
        expected_host="203.0.113.10",
    )

    assert result.trusted is False
    assert result.status == "fingerprint-mismatch"
    assert result.fingerprint_sha256 == EXPECTED_FINGERPRINT
    assert KEY_BLOB not in str(result.safe_metadata())
    assert "operator-test-key" not in str(result.safe_metadata())


def test_verify_ssh_host_key_pin_blocks_missing_pin_before_trusting_key():
    result = verify_ssh_host_key_pin(KEY_LINE, expected_sha256_fingerprint="")

    assert result.trusted is False
    assert result.status == "missing-pin"
    assert result.expected_fingerprint_sha256 is None


def test_verify_ssh_host_key_pin_blocks_unexpected_host():
    result = verify_ssh_host_key_pin(
        KEY_LINE,
        expected_sha256_fingerprint=EXPECTED_FINGERPRINT,
        expected_host="198.51.100.7",
    )

    assert result.trusted is False
    assert result.status == "host-mismatch"
    assert result.host_matched is False


def test_verify_ssh_host_key_pin_blocks_invalid_key_line():
    result = verify_ssh_host_key_pin(
        "not a host key",
        expected_sha256_fingerprint=EXPECTED_FINGERPRINT,
    )

    assert result.trusted is False
    assert result.status == "invalid-host-key"
    assert result.fingerprint_sha256 is None


def test_verify_ssh_host_key_pin_blocks_invalid_key_blob():
    result = verify_ssh_host_key_pin(
        "203.0.113.10 ssh-ed25519 !!!not-base64!!!",
        expected_sha256_fingerprint=EXPECTED_FINGERPRINT,
    )

    assert result.trusted is False
    assert result.status == "invalid-host-key"
    assert result.fingerprint_sha256 is None
