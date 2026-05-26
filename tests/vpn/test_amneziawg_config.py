import base64

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import x25519

from app.vpn.amneziawg_v2.config import ClientConfigInput, render_client_config
from app.vpn.amneziawg_v2.keys import generate_key, generate_keypair


def test_render_client_config_contains_expected_fields():
    config = render_client_config(
        ClientConfigInput(
            private_key="client-private",
            address="10.8.0.2/32",
            dns="1.1.1.1",
            server_public_key="server-public",
            preshared_key="psk",
            endpoint="vpn.example.com:30001",
            allowed_ips="0.0.0.0/0",
            persistent_keepalive=25,
            jc=4,
            jmin=40,
            jmax=70,
            s1=0,
            s2=0,
            h1=1,
            h2=2,
            h3=3,
            h4=4,
        )
    )

    assert "[Interface]" in config
    assert "PrivateKey = client-private" in config
    assert "Address = 10.8.0.2/32" in config
    assert "DNS = 1.1.1.1" in config
    assert "[Peer]" in config
    assert "PublicKey = server-public" in config
    assert "PresharedKey = psk" in config
    assert "Endpoint = vpn.example.com:30001" in config
    assert "AllowedIPs = 0.0.0.0/0" in config
    assert "PersistentKeepalive = 25" in config
    assert "Jc = 4" in config
    assert "H4 = 4" in config


def test_generate_key_returns_base64_encoded_32_byte_secret():
    key = generate_key()

    assert len(base64.b64decode(key)) == 32


def test_generate_keypair_returns_matching_base64_x25519_keys():
    keypair = generate_keypair()

    private_bytes = base64.b64decode(keypair.private_key)
    public_bytes = base64.b64decode(keypair.public_key)
    derived_public_bytes = (
        x25519.X25519PrivateKey.from_private_bytes(private_bytes)
        .public_key()
        .public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
    )

    assert len(private_bytes) == 32
    assert len(public_bytes) == 32
    assert public_bytes == derived_public_bytes
