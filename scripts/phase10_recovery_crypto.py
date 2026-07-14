#!/usr/bin/env python
"""Public-key envelope encryption for AMN2 recovery bundles."""

from __future__ import annotations

import struct


MAGIC = b"AMN2-HYBRID-RECOVERY-V1\n"
MIN_RSA_KEY_BITS = 3072
WRAPPED_KEY_LENGTH_BYTES = 4


class RecoveryCryptoError(RuntimeError):
    """A safe recovery-envelope failure with no key or payload content."""


def _load_public_key(public_key_pem: bytes):
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
    except ImportError as exc:
        raise RecoveryCryptoError("cryptography dependency is unavailable") from exc
    try:
        key = serialization.load_pem_public_key(public_key_pem)
    except (TypeError, ValueError) as exc:
        raise RecoveryCryptoError("recipient public key is invalid") from exc
    if not isinstance(key, rsa.RSAPublicKey):
        raise RecoveryCryptoError("recipient public key is not RSA")
    if key.key_size < MIN_RSA_KEY_BITS:
        raise RecoveryCryptoError("recipient RSA key is below the minimum size")
    return key


def _load_private_key(private_key_pem: bytes):
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
    except ImportError as exc:
        raise RecoveryCryptoError("cryptography dependency is unavailable") from exc
    try:
        key = serialization.load_pem_private_key(private_key_pem, password=None)
    except (TypeError, ValueError) as exc:
        raise RecoveryCryptoError("recovery private key is invalid") from exc
    if not isinstance(key, rsa.RSAPrivateKey):
        raise RecoveryCryptoError("recovery private key is not RSA")
    if key.key_size < MIN_RSA_KEY_BITS:
        raise RecoveryCryptoError("recovery RSA key is below the minimum size")
    return key


def _oaep_padding():
    try:
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import padding
    except ImportError as exc:
        raise RecoveryCryptoError("cryptography dependency is unavailable") from exc
    return padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=MAGIC,
    )


def encrypt_hybrid(plaintext: bytes, public_key_pem: bytes) -> bytes:
    """Encrypt bytes with a random Fernet key wrapped by RSA-OAEP/SHA-256."""
    try:
        from cryptography.fernet import Fernet
    except ImportError as exc:
        raise RecoveryCryptoError("cryptography dependency is unavailable") from exc
    if not isinstance(plaintext, bytes):
        raise RecoveryCryptoError("recovery plaintext is not bytes")
    public_key = _load_public_key(public_key_pem)
    data_key = Fernet.generate_key()
    try:
        wrapped_key = public_key.encrypt(data_key, _oaep_padding())
        ciphertext = Fernet(data_key).encrypt(plaintext)
    except ValueError as exc:
        raise RecoveryCryptoError("recovery envelope encryption failed") from exc
    return (
        MAGIC
        + struct.pack(">I", len(wrapped_key))
        + wrapped_key
        + ciphertext
    )


def decrypt_hybrid(envelope: bytes, private_key_pem: bytes) -> bytes:
    """Authenticate and decrypt a versioned AMN2 hybrid recovery envelope."""
    try:
        from cryptography.fernet import Fernet, InvalidToken
    except ImportError as exc:
        raise RecoveryCryptoError("cryptography dependency is unavailable") from exc
    if not isinstance(envelope, bytes) or not envelope.startswith(MAGIC):
        raise RecoveryCryptoError("recovery envelope format is unsupported")
    private_key = _load_private_key(private_key_pem)
    header_end = len(MAGIC) + WRAPPED_KEY_LENGTH_BYTES
    if len(envelope) <= header_end:
        raise RecoveryCryptoError("recovery envelope is truncated")
    wrapped_length = struct.unpack(">I", envelope[len(MAGIC) : header_end])[0]
    expected_length = private_key.key_size // 8
    if wrapped_length != expected_length:
        raise RecoveryCryptoError("recovery envelope wrapped-key length is invalid")
    wrapped_end = header_end + wrapped_length
    if len(envelope) <= wrapped_end:
        raise RecoveryCryptoError("recovery envelope is truncated")
    wrapped_key = envelope[header_end:wrapped_end]
    ciphertext = envelope[wrapped_end:]
    try:
        data_key = private_key.decrypt(wrapped_key, _oaep_padding())
        return Fernet(data_key).decrypt(ciphertext)
    except (InvalidToken, TypeError, ValueError) as exc:
        raise RecoveryCryptoError("recovery envelope authentication failed") from exc
