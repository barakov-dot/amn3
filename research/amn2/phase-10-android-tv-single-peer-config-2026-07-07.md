# Phase 10 Android TV single peer/config gate

Date: 2026-07-07.

Status: `server-side-prepared-awaiting-device-acceptance`.

Gate:
`CREATE_ONE_ANDROID_TV_PEER_AND_GENERATE_LOCAL_CONFIG_FOR_EXISTING_AMN2_VPS`.

This evidence records only safe metadata. The generated `.conf`, private key,
preshared key, QR payload, `vpn://` payload, raw Docker config, `.env`,
`servers.yml`, tokens and raw logs are not included.

## Result

```text
run_id=20260707T200605Z
source_overlay=4326cae
server_name=local
runtime=docker
docker_container=amnezia-awg2
device_id=8
device_name=Neobyatnaya-AMNZ-N-android-tv-01
device_status=active
vpn_ip=10.8.0.13
config_version=amneziawg_v2
config_material_status=available
peer_apply_status=passed
docker_restart_status=passed
db_record_status=passed
config_generation_status=passed
peer_present_after=true
active_device_count_after=8
working_config_proven=false
handshake_seen=false
rx_bytes=0
tx_bytes=0
```

## Private Artifacts

```text
local_private_artifact_root=private-artifacts/phase10/android-tv-single/20260707T200605Z/
local_config_filename=Neobyatnaya-AMNZ-N-android-tv-01.conf
local_config_path=private-artifacts/phase10/android-tv-single/20260707T200605Z/Neobyatnaya-AMNZ-N-android-tv-01.conf
local_safe_summary_path=private-artifacts/phase10/android-tv-single/20260707T200605Z/safe-summary.json
local_private_artifact_root_gitignored=true
remote_private_artifact_root=/root/amn2-private-artifacts/phase10/android-tv-single/20260707T200605Z/
remote_backup_created=true
local_config_acl=owner_system_administrators_only
remote_private_file_modes=0600
remote_gate_script_mode=0700
```

## Config Shape Check

```text
has_interface_section=true
has_peer_section=true
has_private_key=true
has_preshared_key=true
has_awg_jc=true
has_awg_jmin=true
has_awg_jmax=true
has_awg_h1=true
has_endpoint=true
has_allowed_ips_full_tunnel=true
config_bytes=439
```

The config is an AmneziaWG v2 shaped `.conf` with AWG-specific parameters. It is
not treated as a plain WireGuard-only export by AMN2 metadata.

This proves config shape and server-side peer presence. It does not yet prove a
working client connection: the 2026-07-10 read-only audit found no handshake and
zero RX/TX for device `8`.

## Post-Gate Audit 2026-07-10

```text
live_peer_present=true
handshake_seen=false
rx_bytes=0
tx_bytes=0
owner_selection=existing_active_user
owner_status=active
owner_is_admin=false
linked_order_count=0
target_device_admin_action_count=0
supported_access_service_path_used=false
global_VPS_APPLY_ENABLED_after_gate=false
```

The gate script selected the first active user because no owner was supplied.
That owner relationship is not proven to match the intended operator/device
owner. It must not be changed automatically: a correct target user must be
selected explicitly before any ownership correction.

Operator follow-up decision 2026-07-10: leave device `8` with the current active
user provisionally and perform no ownership mutation before the Android TV is
available for import/connect acceptance. Recheck ownership during that
acceptance; correct it only if the current owner is proven wrong.

The one-off script also used private implementation helpers and direct
repository connection access. It bypassed the normal `AccessService` order,
device-limit and audit path. A productized replacement must require an explicit
owner, use a public service API, render the config before remote mutation, and
cover rollback for every local failure after the remote peer write.

## Android Display Name Note

Android import display name remains a client-side limitation. AMN2 generated the
device name and filename as `Neobyatnaya-AMNZ-N-android-tv-01`, but Android may
still display a localized generated name such as `Сервер 1`. Manual rename to
`NeobyatnayaNET` or `Neobyatnaya-AMNZ-N` remains the accepted fallback.

## Boundary

Performed:

- one live peer add to the existing AmneziaWG Docker config;
- Docker container restart for that peer add;
- one AMN2 DB device record with `config_material_status=available`;
- one private local `.conf` copy under `private-artifacts/`;
- safe metadata/evidence only.

Not performed:

- public API or web/admin exposure;
- Telegram delivery or live bot send;
- QR generation/publication;
- `vpn://` generation/publication;
- bulk peer creation;
- peer revoke;
- backup/import/reboot route execution;
- firewall, domain, HTTPS or reverse proxy changes;
- raw config, keys, PSK, tokens, `.env`, `servers.yml` or full logs publication.

## Next Operator Step

When the Android TV is available, import the private file into AmneziaWG. If the
app shows `Сервер 1`, manually rename the profile after import. After connection,
confirm handshake and traffic server-side, review the provisional ownership, and
only then change the status to `working-config-pass`.
