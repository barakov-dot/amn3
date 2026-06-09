# Target Server Service-Mode B0.1 Prep And B0 Repeat Evidence - 2026-06-09

Status: `phase3_service_mode_B0_ready_for_B1_loopback_systemd`.

Scope: controlled B0.1 service-mode preparation after the first B0 preflight found blockers. This gate created and prepared the service account and effective settings required for loopback-only `systemd`, then repeated B0 read-only preflight. It did not install, enable or start any systemd unit. It did not create or change any reverse proxy route. It did not open public API, direct public web/admin, config delivery, Local Agent mutation, backup/import/reboot or peer mutation.

## First B0.1 Attempt

The first B0.1 prep attempt was blocked before changes because the private admin Telegram ID value was missing or invalid.

```text
b0_1_prep_status: blocked
block_reason: admin_telegram_ids_value_missing_or_invalid
```

## B0.1 Prep Summary

After the operator supplied the private numeric admin Telegram ID locally on the VPS, B0.1 created the service account and updated effective service-mode settings.

```text
phase3_B0_1_service_mode_prep: done
env_file_present_before: yes
amneziya_user_action: created
settings_as_amneziya_check: no
amneziya_user_exists: yes
env_group_amneziya: yes
env_mode_640: yes
web_admin_enabled_set: yes
web_admin_host_loopback_set: yes
web_admin_port_3030_set: yes
admin_telegram_ids_present: yes
VPS_APPLY_ENABLED_file_set_false: yes
systemd_units_installed_or_started: no
reverse_proxy_changed: no
b0_1_prep_status: needs-investigation
```

Investigation showed the service user existed but could not traverse `/opt/amn2` or execute the venv Python.

```text
id_amneziya: yes
root_dir_access_as_amneziya: no
env_read_as_amneziya: no
venv_python_exec_as_amneziya: no
data_write_as_amneziya: no
logs_write_as_amneziya: no
settings_probe_rc: 1
settings_probe_error_last_line: sudo: unable to execute /opt/amn2/venv/bin/python: Permission denied
```

## B0.1 Permissions Fix

The permission fix granted the service group the minimum access required to read the app/venv/env and write runtime data/logs.

```text
b0_1_permissions_fix: done
app_group_access: set
deploy_group_access: set
venv_group_access: set
data_group_rw_access: set
logs_group_rw_access: set
root_dir_access_as_amneziya: yes
env_read_as_amneziya: yes
venv_python_exec_as_amneziya: yes
data_write_as_amneziya: yes
logs_write_as_amneziya: yes
settings_probe_rc: 0
settings_as_amneziya_check: yes
systemd_units_installed_or_started: no
reverse_proxy_changed: no
b0_1_permissions_fix_status: ok
```

## B0 Repeat Summary

The repeated B0 preflight is now ready for a separate B1 loopback-only systemd gate.

```text
phase3_B0_service_mode_preflight_repeat: done
source_overlay_commit: f7f6131
runtime_type: docker
container_running: true
live_peer_count: 3
tcp_3030_before: absent
tcp_3040_before: absent
VPS_APPLY_ENABLED_process: false
web_unit_template_present: yes
web_unit_loopback_execstart: yes
web_unit_no_wildcard_host: yes
bot_unit_template_present: yes
bot_unit_python_entry: yes
amneziya-web_unit_file_present: no
amneziya-web_enabled: not-found
amneziya-web_active: inactive
amneziya-bot_unit_file_present: no
amneziya-bot_enabled: not-found
amneziya-bot_active: inactive
telegram_bot_token_present: yes
app_secret_key_present: yes
admin_telegram_ids_present: yes
web_admin_enabled_present: yes
web_admin_password_hash_present: yes
web_admin_session_secret_present: yes
web_admin_host_present: yes
web_admin_port_present: yes
vps_apply_enabled_present: yes
settings_web_admin_enabled: True
settings_web_admin_host: 127.0.0.1
settings_web_admin_port: 3030
settings_api_host: 127.0.0.1
settings_api_port: 3040
settings_vps_apply_enabled: False
amn2_user_exists: yes
settings_as_amneziya_check: yes
env_group_amneziya: yes
env_mode_640: yes
web_import_check: yes
bot_import_check: yes
rollback_plan_available: yes
reverse_proxy_choice: undecided
B0_writes_performed: no
B0_repeat_status: ready-for-B1-loopback-systemd
```

## Current Decision Point

B1 can now be considered as a separate explicit gate:

- install/copy `amneziya-web` and `amneziya-bot` systemd units;
- start/enable them;
- verify web/admin listens only on loopback `127.0.0.1:3030`;
- verify bot service is active without publishing logs;
- verify TCP `3040` remains absent/public-closed;
- keep `VPS_APPLY_ENABLED=false`.

Reverse proxy / HTTPS public cutover remains out of scope until a separate proxy choice and gate.

## Secret Handling

No public IP, SSH credentials, host key material, `.env`, raw `servers.yml`, raw tokens, Authorization headers, token hashes, web password hash, session secret, private keys, PSK, peer public keys, client `.conf`, QR payloads, VPN URLs, endpoint values, backup contents or full logs were copied into this evidence.
