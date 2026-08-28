#!/usr/bin/env python3
"""Upstream-only one-peer pilot. Default invocation is declarative, never SSH.

Live check/render/apply require separate operator authorization. This file is
not part of, and never modifies, immutable Phase 16 packages.
"""
from __future__ import annotations

import argparse
import base64
import configparser
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import platform
import re
import signal
import stat
import subprocess
import sys

TARGET = "138.124.181.246"
IMAGE = "docker.io/amneziavpn/amneziawg-go@sha256:4e1fd2840f8d26eb6ec8bc1598e66f2f17f5d0201cd2baadbde560c104d4fc9d"
DOCKER_PATH = "/opt/amn2-spain/docker/bin/docker"
DOCKER_SOCKET = "unix:///run/amn2-spain-docker/docker.sock"
CONTAINER = "amn2-spain-awg31-pilot"
NETWORK = "amn2sp31pilot"
BRIDGE = "amn2sp31p0"
INPUT_DIR = Path("/var/lib/amn2-spain/awg31-pilot-input")
CLAIM_ROOT = Path("/var/lib/amn2-phase16/pilot-attempts")
PEER_COUNT = 1
KEY_FIELDS = ("server_private", "server_public", "client_private", "client_public", "psk", "hpk")
PROFILES = ("server.conf", "windows.conf")


class PilotError(ValueError):
    """Only fixed, secret-free error tokens reach the caller."""


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def script_sha256():
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def render_pair(keys, *, dns, mtu=1280):
    try:
        if set(keys) != set(KEY_FIELDS):
            raise ValueError
        for key in keys.values():
            if not isinstance(key, str) or len(key) != 44:
                raise ValueError
            raw = base64.b64decode(key, validate=True)
            if len(raw) != 32 or not any(raw) or base64.b64encode(raw).decode() != key:
                raise ValueError
        if type(mtu) is not int or not 1280 <= mtu <= 1420:
            raise ValueError
        address = ipaddress.IPv4Address(dns)
        if address.is_unspecified or address.is_multicast or address.is_loopback:
            raise ValueError
    except (ValueError, TypeError):
        raise PilotError("invalid_profile_input") from None
    shared = (
        "S1 = 12\nS2 = 12\nS3 = 12\nS4 = 12\n"
        "H1 = 1\nH2 = 2\nH3 = 3\nH4 = 4\n"
        f"HeaderProtectionKey = {keys['hpk']}\n"
        "ContentPaddingAddition = 0\nRekeyAfterTime = 120\nRekeyTimeout = 5\n"
        "RejectAfterTime = 180\nKeepaliveTimeout = 10\nMaxHandshakeAttempts = 18\n"
        "RandomTrailers = on\nDisableCookies = on\n"
    )
    server = (
        f"[Interface]\nPrivateKey = {keys['server_private']}\nListenPort = 30002\n"
        + shared + f"\n[Peer]\nPublicKey = {keys['client_public']}\n"
        f"PresharedKey = {keys['psk']}\nAllowedIPs = 10.212.13.2/32\nAdvancedSecurity = on\n"
    )
    client = (
        f"[Interface]\nPrivateKey = {keys['client_private']}\nAddress = 10.212.13.2/32\n"
        f"DNS = {address}\nMTU = {mtu}\n" + shared
        + f"\n[Peer]\nPublicKey = {keys['server_public']}\nPresharedKey = {keys['psk']}\n"
        f"Endpoint = {TARGET}:30002\nAllowedIPs = 0.0.0.0/0, ::/0\nPersistentKeepalive = 25\nAdvancedSecurity = on\n"
    )
    return {"server.conf": server, "windows.conf": client}


def validate_pair(profiles):
    """Validate our narrow generated profile, not a substitute for upstream awg."""
    try:
        parsed = {}
        if set(profiles) != set(PROFILES):
            raise ValueError
        for name, body in profiles.items():
            parser = configparser.ConfigParser(interpolation=None)
            parser.optionxform = str
            parser.read_string(body)
            if set(parser.sections()) != {"Interface", "Peer"} or parser.defaults():
                raise ValueError
            parsed[name] = parser
        server, client = parsed["server.conf"], parsed["windows.conf"]
        keys = dict(server_private=server["Interface"]["PrivateKey"], server_public=client["Peer"]["PublicKey"],
                    client_private=client["Interface"]["PrivateKey"], client_public=server["Peer"]["PublicKey"],
                    psk=server["Peer"]["PresharedKey"], hpk=server["Interface"]["HeaderProtectionKey"])
        expected = render_pair(keys, dns=client["Interface"]["DNS"], mtu=int(client["Interface"]["MTU"]))
        if profiles != expected:
            raise ValueError
    except (configparser.Error, ValueError, KeyError, TypeError):
        raise PilotError("profile_pair_invalid") from None


def require_linux_root():
    if sys.platform != "linux" or os.geteuid() != 0 or platform.machine() != "x86_64":
        raise PilotError("linux_amd64_root_required")


def secure_read(path, maximum=16384):
    for parent in (path.parent, *path.parent.parents):
        info = parent.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o022:
            raise PilotError("unsafe_input_parent")
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o077:
            raise PilotError("unsafe_input_file")
        body = os.read(descriptor, maximum + 1)
        if not body or len(body) > maximum:
            raise PilotError("input_size_invalid")
        return body.decode("ascii")
    finally:
        os.close(descriptor)


def load_profiles():
    profiles = {name: secure_read(INPUT_DIR / name) for name in PROFILES}
    validate_pair(profiles)
    return profiles


def secure_parent_chain(path):
    # The executable actions are Linux-root-only; but the pure test seam is portable.
    if os.name == "posix":
        for parent in (path, *path.parents):
            if parent.exists() or parent.is_symlink():
                info = parent.lstat()
                if not stat.S_ISDIR(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o022:
                    raise PilotError("unsafe_parent_directory")


def prepare_profiles(key_directory, *, dns, mtu):
    require_linux_root()
    keys = {name: secure_read(key_directory / (name + ".key"), maximum=128).strip() for name in KEY_FIELDS}
    profiles = render_pair(keys, dns=dns, mtu=mtu)
    secure_parent_chain(INPUT_DIR.parent)
    INPUT_DIR.mkdir(mode=0o700, exist_ok=False)
    created = []
    try:
        for name, body in profiles.items():
            path = INPUT_DIR / name
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            created.append(path)
            with os.fdopen(descriptor, "wb") as output:
                output.write(body.encode("ascii"))
                output.flush()
                os.fsync(output.fileno())
    except Exception:
        for path in created:
            path.unlink()
        INPUT_DIR.rmdir()
        raise PilotError("profile_write_failed") from None
    return {"result": "profiles_prepared_not_installed", "peer_count": PEER_COUNT,
            "sha256": {name: hashlib.sha256(body.encode()).hexdigest() for name, body in profiles.items()}}


def command(arguments, *, timeout=30):
    try:
        result = subprocess.run(arguments, capture_output=True, timeout=timeout,
                                env={"PATH": "/usr/sbin:/usr/bin:/sbin:/bin", "LC_ALL": "C"})
        if result.returncode or len(result.stdout) > 1048576:
            raise PilotError("command_failed")
        return result.stdout.decode("utf-8").strip()
    except (OSError, subprocess.SubprocessError, UnicodeError):
        raise PilotError("command_unavailable") from None


class Docker:
    def __call__(self, *arguments, timeout=30):
        return command([DOCKER_PATH, "--host", DOCKER_SOCKET, *arguments], timeout=timeout)


def awg2_snapshot(docker):
    owner = command(["/usr/bin/systemctl", "show", "amn2-spain-docker.service",
                     "--property=ActiveState,SubState,UnitFileState", "--value"])
    identities = docker("ps", "-a", "--filter", "name=^/amn2-spain-awg$", "--format", "{{.ID}}")
    if not identities:
        return fingerprint({"owner": owner, "container": "absent"})
    if not re.fullmatch(r"[0-9a-f]{12,64}", identities):
        raise PilotError("awg2_identity_ambiguous")
    data = json.loads(docker("inspect", identities))
    peers = docker("exec", "amn2-spain-awg", "/usr/bin/awg", "show", "awgsp0", "peers") if data[0]["State"]["Running"] else "not_running"
    return fingerprint({"owner": owner, "peers_sha256": hashlib.sha256(peers.encode()).hexdigest(),
                        "containers": [{key: item[key] for key in ("Id", "Image", "HostConfig", "Mounts", "RestartCount")}
                                       | {"running": item["State"]["Running"], "started": item["State"]["StartedAt"]}
                                       for item in data]})


def require_host_prerequisites():
    require_linux_root()
    if not Path(DOCKER_PATH).is_file() or not stat.S_ISSOCK(Path(DOCKER_SOCKET[7:]).stat().st_mode):
        raise PilotError("dedicated_docker_unavailable")
    if not stat.S_ISCHR(Path("/dev/net/tun").stat().st_mode):
        raise PilotError("tun_unavailable")
    if Path("/proc/sys/net/ipv4/ip_forward").read_text().strip() != "1":
        raise PilotError("host_forwarding_disabled")
    if Path("/sys/class/net", BRIDGE).exists():
        raise PilotError("bridge_already_exists")
    if platform.freedesktop_os_release().get("ID") != "ubuntu" or platform.freedesktop_os_release().get("VERSION_ID") != "24.04":
        raise PilotError("host_os_mismatch")


def preflight(docker):
    require_host_prerequisites()
    addresses = json.loads(command(["/usr/sbin/ip", "-j", "-4", "address", "show"]))
    if TARGET not in {entry["local"] for interface in addresses for entry in interface.get("addr_info", [])}:
        raise PilotError("host_identity_mismatch")
    if docker("version", "--format", "{{.Server.Os}}/{{.Server.Arch}}") != "linux/amd64":
        raise PilotError("docker_platform_mismatch")
    for name in (CONTAINER, CONTAINER + "-check"):
        if docker("ps", "-a", "--filter", f"name=^/{name}$", "--format", "{{.ID}}"):
            raise PilotError("container_already_exists")
    if NETWORK in docker("network", "ls", "--format", "{{.Name}}").splitlines():
        raise PilotError("network_already_exists")
    if command(["/usr/bin/ss", "-H", "-lun", "sport = :30002"]):
        raise PilotError("udp_port_in_use")
    routes = json.loads(command(["/usr/sbin/ip", "-j", "-4", "route", "show", "table", "all"]))
    wanted = [ipaddress.ip_network(value) for value in ("10.212.13.0/24", "172.29.252.0/28")]
    for route in routes:
        prefix = route.get("dst", "default")
        if prefix != "default" and any(ipaddress.ip_network(prefix, strict=False).overlaps(net) for net in wanted):
            raise PilotError("route_overlap")
    network_ids = docker("network", "ls", "-q").splitlines()
    if len(network_ids) > 128:
        raise PilotError("network_inventory_limit")
    networks = json.loads(docker("network", "inspect", *network_ids)) if network_ids else []
    for network in networks:
        for entry in network.get("IPAM", {}).get("Config") or []:
            prefix = entry.get("Subnet")
            if prefix:
                subnet = ipaddress.ip_network(prefix)
                if subnet.version == 4 and any(subnet.overlaps(net) for net in wanted):
                    raise PilotError("docker_subnet_overlap")
    return {"target": TARGET, "image": IMAGE, "ready": True, "awg2_snapshot": awg2_snapshot(docker)}


NATIVE_CHECK = r"""set -eu
umask 077
field() { awk -v section="$2" -v key="$3" '/^\[/{s=$0} s==section && $1==key {print $3}' "$1"; }
test "$(field /input/server.conf '[Interface]' PrivateKey | /usr/bin/awg pubkey)" = "$(field /input/windows.conf '[Peer]' PublicKey)"
test "$(field /input/windows.conf '[Interface]' PrivateKey | /usr/bin/awg pubkey)" = "$(field /input/server.conf '[Peer]' PublicKey)"
/usr/bin/amneziawg-go -f awgcheck >/dev/null 2>&1 &
worker=$!
trap 'kill "$worker" 2>/dev/null || :; wait "$worker" 2>/dev/null || :' EXIT
trap 'exit 143' TERM
trap 'exit 130' INT
count=0
until test -S /var/run/amneziawg/awgcheck.sock; do
    kill -0 "$worker"
    count=$((count+1)); test "$count" -le 50; sleep 0.1
done
/usr/bin/awg setconf awgcheck /input/server.conf >/dev/null 2>&1
/usr/bin/awg-quick strip /input/windows.conf > /tmp/client.native 2>/dev/null
/usr/bin/awg setconf awgcheck /tmp/client.native >/dev/null 2>&1
"""

RUNTIME_START = r"""set -eu
/usr/bin/amneziawg-go -f awg3 >/dev/null 2>&1 &
worker=$!
trap 'kill "$worker" 2>/dev/null || :; wait "$worker" 2>/dev/null || :' EXIT
trap 'exit 143' TERM
trap 'exit 130' INT
count=0
until test -S /var/run/amneziawg/awg3.sock; do
    kill -0 "$worker"
    count=$((count+1)); test "$count" -le 50; sleep 0.1
done
/usr/bin/awg setconf awg3 /input/server.conf >/dev/null 2>&1
/sbin/ip address add 10.212.13.1/24 dev awg3
/sbin/ip link set dev awg3 mtu "$PILOT_MTU" up
/sbin/iptables -t nat -A POSTROUTING -s 10.212.13.0/24 -o eth0 -j MASQUERADE
: > /run/pilot.ready
wait "$worker"
"""

RUNTIME_HEALTH = r"""set -eu
count=0
until test -f /run/pilot.ready; do
    count=$((count+1)); test "$count" -le 80; sleep 0.1
done
test "$(/usr/bin/awg show awg3 listen-port)" = 30002
test "$(/usr/bin/awg show awg3 peers | wc -l)" -eq 1
test "$(cat /proc/sys/net/ipv4/ip_forward)" = 1
"""


def _resource_id(value):
    if re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise PilotError("resource_identity_unknown")
    return value


def _owned_id(docker, kind, name, claim):
    prefix = ("ps", "-aq", "--no-trunc") if kind == "container" else ("network", "ls", "-q", "--no-trunc")
    selector = f"^/{name}$" if kind == "container" else f"^{name}$"
    value = docker(*prefix, "--filter", f"name={selector}", "--filter", f"label=amn2.phase16.pilot={claim}")
    return _resource_id(value) if value else ""


def append_record(descriptor, record):
    raw = (json.dumps(record, sort_keys=True) + "\n").encode()
    while raw:
        count = os.write(descriptor, raw)
        if count <= 0:
            raise PilotError("journal_write_failed")
        raw = raw[count:]
    os.fsync(descriptor)


def snapshot_profiles(profiles, claim):
    directory = CLAIM_ROOT / (claim + "-files")
    directory.mkdir(mode=0o700, exist_ok=False)
    for name, body in profiles.items():
        descriptor = os.open(directory / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "wb") as output:
            output.write(body.encode("ascii"))
            output.flush()
            os.fsync(output.fileno())
        if os.name == "posix":
            os.chmod(directory / name, 0o400)
    return directory


def apply_pilot(docker, *, script_sha256, state_sha256, server_sha256, client_sha256, claim):
    require_linux_root()
    hashes = (script_sha256, state_sha256, server_sha256, client_sha256)
    if any(not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value) for value in hashes):
        raise PilotError("approval_binding_invalid")
    if not re.fullmatch(r"pilot-[a-z0-9][a-z0-9-]{0,70}", claim) or script_sha256 != hashlib.sha256(Path(__file__).read_bytes()).hexdigest():
        raise PilotError("approval_binding_invalid")
    profiles = load_profiles()
    for name, digest in zip(PROFILES, (server_sha256, client_sha256)):
        if hashlib.sha256(profiles[name].encode()).hexdigest() != digest:
            raise PilotError("profile_hash_mismatch")
    state = preflight(docker)
    if not state.get("ready") or fingerprint(state) != state_sha256:
        raise PilotError("preflight_state_changed")
    secure_parent_chain(CLAIM_ROOT)
    CLAIM_ROOT.mkdir(mode=0o700, parents=True, exist_ok=True)
    if CLAIM_ROOT.is_symlink():
        raise PilotError("unsafe_claim_root")
    try:
        descriptor = os.open(CLAIM_ROOT / claim, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        raise PilotError("claim_already_consumed") from None
    container_id = network_id = ""
    verifier_name = CONTAINER + "-check"
    label = f"amn2.phase16.pilot={claim}"
    common = ("--pull=never", "--read-only", "--cap-drop=ALL", "--cap-add=NET_ADMIN",
              "--device=/dev/net/tun", "--tmpfs=/run", "--tmpfs=/tmp", "--log-driver=none", "--label", label)
    phase = "claim"
    outcome = {"result": "stop", "general_issuance_enabled": False}
    try:
        append_record(descriptor, {"claim": claim, "script_sha256": script_sha256,
                                  "state_sha256": state_sha256, "status": "consumed"})
        phase = "input_snapshot"
        inputs = snapshot_profiles(profiles, claim)
        phase = "image_pull"
        docker("pull", IMAGE, timeout=120)
        phase = "native_validation"
        docker("run", "--rm", "--name", verifier_name, "--network", "none", *common,
               "--mount", f"type=bind,src={inputs},dst=/input,readonly", IMAGE,
               "/bin/sh", "-ec", NATIVE_CHECK, timeout=30)
        phase = "network_create"
        network_id = _resource_id(docker("network", "create", "--label", label, "--driver", "bridge",
                                          "--subnet", "172.29.252.0/28", "--opt", f"com.docker.network.bridge.name={BRIDGE}", NETWORK))
        phase = "container_create"
        mtu = re.search(r"^MTU = ([0-9]+)$", profiles["windows.conf"], re.MULTILINE).group(1)
        container_id = _resource_id(docker("create", "--name", CONTAINER, *common, "--network", NETWORK,
                                            "--ip", "172.29.252.2", "--sysctl", "net.ipv4.ip_forward=1",
                                            "--sysctl", "net.ipv6.conf.all.disable_ipv6=1", "--env", f"PILOT_MTU={mtu}",
                                            "--restart=no", "--publish", "30002:30002/udp", "--mount",
                                            f"type=bind,src={inputs / 'server.conf'},dst=/input/server.conf,readonly",
                                            IMAGE, "/bin/sh", "-ec", RUNTIME_START))
        phase = "container_start"
        docker("start", container_id)
        phase = "runtime_health"
        docker("exec", container_id, "/bin/sh", "-ec", RUNTIME_HEALTH, timeout=15)
        phase = "awg2_equality"
        if awg2_snapshot(docker) != state["awg2_snapshot"]:
            raise PilotError("awg2_state_changed")
        outcome = {"result": "pilot_started_client_test_pending", "peer_count": PEER_COUNT,
                   "general_issuance_enabled": False, "awg2_state_equal": True, "claim": claim}
        phase = "outcome_publish"
        append_record(descriptor, outcome)
        return outcome
    except Exception:
        rollback_failed = False
        for kind, name, identity in (("container", verifier_name, ""), ("container", CONTAINER, container_id),
                                     ("network", NETWORK, network_id)):
            try:
                identity = identity or _owned_id(docker, kind, name, claim)
                if identity:
                    docker(*(("rm", "-f", identity) if kind == "container" else ("network", "rm", identity)))
                    if _owned_id(docker, kind, name, claim):
                        rollback_failed = True
            except Exception:
                rollback_failed = True
        try:
            awg2_equal = awg2_snapshot(docker) == state["awg2_snapshot"]
        except Exception:
            awg2_equal = "unknown"
        outcome = {"result": "stop", "failure_locus": phase,
                   "rollback": "failed_or_unknown" if rollback_failed else "owned_resources_removed",
                   "image_cache_and_inputs_retained": True, "general_issuance_enabled": False,
                   "awg2_state_equal": awg2_equal}
        raise PilotError(phase + "_failed_" + outcome["rollback"]) from None
    finally:
        try:
            if outcome["result"] == "stop":
                append_record(descriptor, outcome)
        finally:
            os.close(descriptor)


def _cancel(signum, frame):
    raise PilotError("operator_interrupted")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action")
    commands.add_parser("plan", help="print non-secret plan; execute nothing")
    render = commands.add_parser("render", help="authorized Linux-only preparation from existing protected keys")
    render.add_argument("--key-directory", type=Path, required=True)
    render.add_argument("--dns", required=True)
    render.add_argument("--mtu", type=int, default=1280)
    check = commands.add_parser("check", help="authorized read-only server preflight; no keys required")
    check.add_argument("--with-profiles", action="store_true", help="also validate separately prepared protected inputs")
    apply = commands.add_parser("apply", help="requires a separate exact operator approval")
    for field in ("script-sha256", "state-sha256", "server-sha256", "client-sha256", "claim"):
        apply.add_argument("--" + field, required=True)
    args = parser.parse_args(argv)
    try:
        if args.action in (None, "plan"):
            result = {"target": TARGET, "image": IMAGE, "container": CONTAINER, "network": NETWORK,
                      "peer_count": PEER_COUNT, "executes_commands": False, "general_issuance_enabled": False,
                      "script_sha256": script_sha256(), "input_directory": str(INPUT_DIR),
                      "live_approval_required": True, "ipv6_forwarding": False}
        elif args.action == "render":
            result = prepare_profiles(args.key_directory, dns=args.dns, mtu=args.mtu)
        elif args.action == "check":
            require_linux_root()
            state = preflight(Docker())
            result = {"state": state, "state_sha256": fingerprint(state), "script_sha256": script_sha256()}
            if args.with_profiles:
                profiles = load_profiles()
                result["sha256"] = {name: hashlib.sha256(body.encode()).hexdigest() for name, body in profiles.items()}
        else:
            require_linux_root()
            previous = {sig: signal.signal(sig, _cancel) for sig in (signal.SIGINT, signal.SIGTERM)}
            try:
                result = apply_pilot(Docker(), script_sha256=args.script_sha256, state_sha256=args.state_sha256,
                                     server_sha256=args.server_sha256, client_sha256=args.client_sha256, claim=args.claim)
            finally:
                for sig, handler in previous.items():
                    signal.signal(sig, handler)
        print(json.dumps(result, sort_keys=True))
        return 0
    except Exception as error:
        reason = str(error) if isinstance(error, PilotError) else "operation_failed"
        print(json.dumps({"result": "stop", "reason": reason, "general_issuance_enabled": False}, sort_keys=True))
        return 64


if __name__ == "__main__":
    raise SystemExit(main())
