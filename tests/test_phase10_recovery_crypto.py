from __future__ import annotations

import struct

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from scripts.phase10_recovery_crypto import (
    MAGIC,
    RecoveryCryptoError,
    decrypt_hybrid,
    encrypt_hybrid,
)


def rsa_pair(key_size: int = 3072) -> tuple[bytes, bytes]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)
    private_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    public_pem = private_key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return private_pem, public_pem


def test_hybrid_recovery_envelope_round_trip() -> None:
    private_pem, public_pem = rsa_pair()

    envelope = encrypt_hybrid(b"synthetic recovery payload", public_pem)

    assert envelope.startswith(MAGIC)
    assert decrypt_hybrid(envelope, private_pem) == b"synthetic recovery payload"


def test_hybrid_recovery_envelope_rejects_tampered_ciphertext() -> None:
    private_pem, public_pem = rsa_pair()
    envelope = bytearray(encrypt_hybrid(b"synthetic recovery payload", public_pem))
    envelope[-1] ^= 1

    with pytest.raises(RecoveryCryptoError, match="authentication failed"):
        decrypt_hybrid(bytes(envelope), private_pem)


def test_hybrid_recovery_envelope_rejects_malformed_wrapped_key_length() -> None:
    private_pem, public_pem = rsa_pair()
    envelope = bytearray(encrypt_hybrid(b"synthetic recovery payload", public_pem))
    envelope[len(MAGIC) : len(MAGIC) + 4] = struct.pack(">I", 1)

    with pytest.raises(RecoveryCryptoError, match="wrapped-key length is invalid"):
        decrypt_hybrid(bytes(envelope), private_pem)


def test_hybrid_recovery_envelope_rejects_weak_recipient_key() -> None:
    _private_pem, public_pem = rsa_pair(key_size=2048)

    with pytest.raises(RecoveryCryptoError, match="below the minimum size"):
        encrypt_hybrid(b"synthetic recovery payload", public_pem)
