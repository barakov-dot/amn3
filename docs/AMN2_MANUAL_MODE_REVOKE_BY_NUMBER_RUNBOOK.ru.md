# AMN2 Manual Mode Revoke-By-Number Runbook

Дата: 2026-06-09.

Назначение: безопасно отозвать ровно один из четырех manual-runtime test peers `Neobyatnaya-AMNZ-1..4` по дружелюбному номеру, не печатая peer public key, private key, PSK, `.conf`, QR, endpoint, `servers.yml` или full logs.

Статус: `prepared-not-executed`.

## Boundary

Этот runbook разрешает только controlled revoke одного уже существующего test peer после отдельного явного решения оператора.

Не разрешено:

- отзывать больше одного номера за один gate;
- запускать live revoke без dry-run и precheck;
- публиковать `.env`, `servers.yml`, raw token, Authorization header, hashes, keys, PSK, peer public key, `.conf`, QR, endpoint, backup contents или full logs;
- включать service-mode, reverse proxy, public API `3040`, direct public web/admin `3030`, config delivery, Local Agent mutation, backup/import/reboot;
- расширять test group или создавать новые peers в этом runbook.

Важно: текущий Docker `revoke-peer --apply` переписывает persistent config и перезапускает container. Поэтому live revoke выполнять только после явного подтверждения номера.

## Expected Inputs

Оператор выбирает один номер:

```text
REVOKE_NUMBER=1|2|3|4
```

Маппинг:

```text
1 -> latest /root/amn2-phone-test-peer-*/client_public.key
2 -> latest /root/amn2-test-peers-batch-*/Neobyatnaya-AMNZ-2/client_public.key
3 -> latest /root/amn2-test-peers-batch-*/Neobyatnaya-AMNZ-3/client_public.key
4 -> latest /root/amn2-test-peers-batch-*/Neobyatnaya-AMNZ-4/client_public.key
```

Путь и содержимое ключа не публиковать. В evidence допускаются только safe summary строки из этого runbook.

## Phase 0: Read-Only Precheck And Dry-Run

На VPS:

```bash
cd /opt/amn2
source venv/bin/activate
export VPS_APPLY_ENABLED=false
export REVOKE_NUMBER="4"
export FIRST_DIR="$(ls -td /root/amn2-phone-test-peer-* 2>/dev/null | head -n 1 || true)"
export BATCH_DIR="$(ls -td /root/amn2-test-peers-batch-* 2>/dev/null | head -n 1 || true)"

python - <<'PY'
import os
import re
import subprocess
import sys
from pathlib import Path

from app.server.peer_apply import build_peer_revoke_dry_run
from app.server_config.loader import load_server_config, select_server
from app.server.ssh import SystemSshClient

def die(message):
    print(f"dry_run_status: blocked")
    print(f"block_reason: {message}")
    sys.exit(1)

def run(args):
    return subprocess.run(args, text=True, capture_output=True)

def port_state(port):
    out = run(["ss", "-ltnH"]).stdout.splitlines()
    hits = [line for line in out if re.search(rf"(^|[:.]){port}\b", line)]
    return "absent" if not hits else "present"

def target_key_path(number):
    first_dir = Path(os.environ.get("FIRST_DIR") or "")
    batch_dir = Path(os.environ.get("BATCH_DIR") or "")
    if number == 1:
        return first_dir / "client_public.key"
    return batch_dir / f"Neobyatnaya-AMNZ-{number}" / "client_public.key"

def persistent_public_keys(config_text):
    keys = set()
    in_peer = False
    for raw in config_text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            in_peer = line.strip("[]").strip().lower() == "peer"
            continue
        if in_peer and "=" in line:
            key, value = line.split("=", 1)
            if key.strip().lower() == "publickey":
                keys.add(value.strip())
    return keys

number_text = os.environ.get("REVOKE_NUMBER", "").strip()
if number_text not in {"1", "2", "3", "4"}:
    die("invalid_revoke_number")
number = int(number_text)
target_name = f"Neobyatnaya-AMNZ-{number}"
key_path = target_key_path(number)
if not key_path.exists():
    die("target_key_file_missing")

target_pub = key_path.read_text(encoding="utf-8").strip()
server = select_server(load_server_config("servers.yml"), "local")
ssh = SystemSshClient(server)

config_text = ssh.run(
    f"docker exec {server.runtime.container_name} cat {server.runtime.config_path}"
).stdout
persistent_keys = persistent_public_keys(config_text)

dump = ssh.run(
    f"docker exec {server.runtime.container_name} awg show {server.vpn.interface} dump"
).stdout
live_keys = set()
last = rx = tx = 0
for line in dump.splitlines()[1:]:
    parts = line.split("\t")
    if not parts or not parts[0]:
        continue
    live_keys.add(parts[0])
    if parts[0] == target_pub:
        try:
            last = int(parts[4] or 0) if len(parts) > 4 else 0
            rx = int(parts[5] or 0) if len(parts) > 5 else 0
            tx = int(parts[6] or 0) if len(parts) > 6 else 0
        except ValueError:
            last = rx = tx = 0

target_in_persistent = target_pub in persistent_keys
target_in_live = target_pub in live_keys
if last and rx > 0 and tx > 0:
    target_status = "connected-with-traffic"
elif last and (rx > 0 or tx > 0):
    target_status = "connected-partial-traffic"
elif last:
    target_status = "handshake-only"
elif target_in_live:
    target_status = "not-yet"
else:
    target_status = "not-found-on-server"

print("revoke_by_number_dry_run=started")
print(f"target_name: {target_name}")
print(f"target_key_file_present: yes")
print(f"target_in_persistent_config: {'yes' if target_in_persistent else 'no'}")
print(f"target_in_live_interface: {'yes' if target_in_live else 'no'}")
print(f"target_status_before: {target_status}")
print(f"live_peer_count_before: {len(live_keys)}")
print(f"tcp_3030_before: {port_state(3030)}")
print(f"tcp_3040_before: {port_state(3040)}")
print(f"VPS_APPLY_ENABLED_process: {os.environ.get('VPS_APPLY_ENABLED', 'unset')}")

if not target_in_persistent or not target_in_live:
    die("target_not_present_in_both_persistent_and_live_state")

dry_run_text = build_peer_revoke_dry_run(server, target_pub)
print(f"dry_run_operation_id_present: {'yes' if 'Operation ID: server.peer.revoke' in dry_run_text else 'no'}")
print(f"dry_run_risk_class_remote_state_write: {'yes' if 'Risk class: remote-state-write' in dry_run_text else 'no'}")
print(f"dry_run_no_changes_marker: {'yes' if 'No changes will be made.' in dry_run_text else 'no'}")
print(f"dry_run_remote_side_effects_marker: {'yes' if 'docker-config-peer-remove' in dry_run_text and 'container-restart' in dry_run_text else 'no'}")
print("dry_run_status: ok")
print("revoke_by_number_dry_run=done")
PY
```

Safe evidence из dry-run:

```text
revoke_by_number_dry_run: done
target_name:
target_in_persistent_config:
target_in_live_interface:
target_status_before:
live_peer_count_before:
tcp_3030_before:
tcp_3040_before:
VPS_APPLY_ENABLED_process:
dry_run_operation_id_present:
dry_run_risk_class_remote_state_write:
dry_run_no_changes_marker:
dry_run_remote_side_effects_marker:
dry_run_status:
```

Если `dry_run_status` не `ok`, live revoke не запускать.

## Phase 1: Live Revoke, Only After Explicit Confirmation

Live revoke запускать только после отдельной фразы оператора:

```text
отзываем Neobyatnaya-AMNZ-N live
```

На VPS:

```bash
cd /opt/amn2
source venv/bin/activate
export REVOKE_NUMBER="4"
export CONFIRM_REVOKE="REVOKE-Neobyatnaya-AMNZ-4"
export FIRST_DIR="$(ls -td /root/amn2-phone-test-peer-* 2>/dev/null | head -n 1 || true)"
export BATCH_DIR="$(ls -td /root/amn2-test-peers-batch-* 2>/dev/null | head -n 1 || true)"

export VPS_APPLY_ENABLED=true
python - <<'PY'
import os
import re
import subprocess
import sys
from pathlib import Path

from app.server.peer_apply import revoke_peer
from app.server_config.loader import load_server_config, select_server
from app.server.ssh import SystemSshClient

def die(message):
    print("live_revoke_status: blocked")
    print(f"block_reason: {message}")
    sys.exit(1)

def run(args):
    return subprocess.run(args, text=True, capture_output=True)

def port_state(port):
    out = run(["ss", "-ltnH"]).stdout.splitlines()
    hits = [line for line in out if re.search(rf"(^|[:.]){port}\b", line)]
    return "absent" if not hits else "present"

def target_key_path(number):
    first_dir = Path(os.environ.get("FIRST_DIR") or "")
    batch_dir = Path(os.environ.get("BATCH_DIR") or "")
    if number == 1:
        return first_dir / "client_public.key"
    return batch_dir / f"Neobyatnaya-AMNZ-{number}" / "client_public.key"

def persistent_public_keys(server, ssh):
    text = ssh.run(
        f"docker exec {server.runtime.container_name} cat {server.runtime.config_path}"
    ).stdout
    keys = set()
    in_peer = False
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            in_peer = line.strip("[]").strip().lower() == "peer"
            continue
        if in_peer and "=" in line:
            key, value = line.split("=", 1)
            if key.strip().lower() == "publickey":
                keys.add(value.strip())
    return keys

def live_public_keys(server, ssh):
    dump = ssh.run(
        f"docker exec {server.runtime.container_name} awg show {server.vpn.interface} dump"
    ).stdout
    keys = set()
    for line in dump.splitlines()[1:]:
        parts = line.split("\t")
        if parts and parts[0]:
            keys.add(parts[0])
    return keys

number_text = os.environ.get("REVOKE_NUMBER", "").strip()
if number_text not in {"1", "2", "3", "4"}:
    die("invalid_revoke_number")
number = int(number_text)
target_name = f"Neobyatnaya-AMNZ-{number}"
expected_confirm = f"REVOKE-{target_name}"
if os.environ.get("CONFIRM_REVOKE", "") != expected_confirm:
    die("confirmation_mismatch")
if os.environ.get("VPS_APPLY_ENABLED", "").lower() != "true":
    die("vps_apply_enabled_not_true")

key_path = target_key_path(number)
if not key_path.exists():
    die("target_key_file_missing")
target_pub = key_path.read_text(encoding="utf-8").strip()

server = select_server(load_server_config("servers.yml"), "local")
ssh = SystemSshClient(server)
before_persistent = persistent_public_keys(server, ssh)
before_live = live_public_keys(server, ssh)

if target_pub not in before_persistent or target_pub not in before_live:
    die("target_not_present_before_live_revoke")

print("revoke_by_number_live=started")
print(f"target_name: {target_name}")
print(f"live_peer_count_before: {len(before_live)}")
print(f"tcp_3030_before: {port_state(3030)}")
print(f"tcp_3040_before: {port_state(3040)}")

revoke_peer(server, target_pub, ssh_client=ssh)

after_persistent = persistent_public_keys(server, ssh)
after_live = live_public_keys(server, ssh)
print(f"target_in_persistent_after: {'yes' if target_pub in after_persistent else 'no'}")
print(f"target_in_live_after: {'yes' if target_pub in after_live else 'no'}")
print(f"live_peer_count_after: {len(after_live)}")
print(f"tcp_3030_after: {port_state(3030)}")
print(f"tcp_3040_after: {port_state(3040)}")
print(f"live_revoke_status: {'ok' if target_pub not in after_persistent and target_pub not in after_live else 'needs-investigation'}")
print("revoke_by_number_live=done")
PY
rc=$?
export VPS_APPLY_ENABLED=false
echo "VPS_APPLY_ENABLED_reset=false"
exit "$rc"
```

Expected safe live result for one target:

```text
live_revoke_status: ok
target_in_persistent_after: no
target_in_live_after: no
live_peer_count_after: <previous count minus 1>
tcp_3030_after: absent
tcp_3040_after: absent
VPS_APPLY_ENABLED_reset: false
```

## Failure Handling

If live revoke fails or postcheck returns `needs-investigation`:

1. Do not run another revoke.
2. Keep `VPS_APPLY_ENABLED=false`.
3. Confirm `tcp_3030_after` and `tcp_3040_after`.
4. Run read-only numbered monitor.
5. Preserve private operator notes for the target number.
6. Open a separate recovery gate. Accidental re-apply requires the retained operator-only peer metadata and must not be attempted from chat evidence.

## Evidence Template

```text
revoke_by_number_gate_status:
target_name:
dry_run_status:
live_revoke_executed:
live_revoke_status:
live_peer_count_before:
live_peer_count_after:
target_in_persistent_after:
target_in_live_after:
tcp_3030_after:
tcp_3040_after:
VPS_APPLY_ENABLED_final:
service_mode:
reverse_proxy:
safe_evidence_dir:
```

## Current Recommendation

With three of four test peers already `connected-with-traffic`, keep this runbook prepared and do not revoke anyone by default. Use it only if:

- a tester asks to leave the test;
- a config is believed compromised;
- the test group must be reduced before moving to service-mode;
- a specific profile starts causing operational issues.
