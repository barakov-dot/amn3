# Phase 10 Android TV single peer/config gate

Date: 2026-07-07.

Status: `completed-private-operator-only`.

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

Import the private file from the local artifact path into Android TV / AmneziaWG.
If the app shows `Сервер 1`, manually rename the profile after import. The server
side is already configured for this peer.
