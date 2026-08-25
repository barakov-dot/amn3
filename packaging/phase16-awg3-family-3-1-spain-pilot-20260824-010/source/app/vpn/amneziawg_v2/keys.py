import base64
import secrets
from dataclasses import dataclass

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import x25519


@dataclass(frozen=True)
class KeyPair:
    private_key: str
    public_key: str


def generate_key() -> str:
    return base64.b64encode(secrets.token_bytes(32)).decode("ascii")


def generate_keypair() -> KeyPair:
    private_key = x25519.X25519PrivateKey.generate()
    public_key = private_key.public_key()
    return KeyPair(
        private_key=base64.b64encode(
            private_key.private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption(),
            )
        ).decode("ascii"),
        public_key=base64.b64encode(
            public_key.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw,
            )
        ).decode("ascii"),
    )
