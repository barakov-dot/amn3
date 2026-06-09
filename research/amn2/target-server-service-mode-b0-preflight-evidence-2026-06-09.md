# Target Server Service-Mode B0 Preflight Evidence - 2026-06-09

Status: `phase3_service_mode_B0_preflight_needs_fix_before_B1`.

Scope: read-only service-mode B0 preflight for web/bot `systemd` readiness after manual-runtime field testing and the `Neobyatnaya-AMNZ-3` revoke-by-number gate. No `systemd` unit was installed, copied, enabled or started. No reverse proxy route was created or changed. No public API, config delivery, Local Agent mutation, backup/import/reboot or peer mutation was unlocked.

## Safe Summary

```text
source_overlay_commit: f7f6131
runtime_type: docker
runtime_container_name_present: yes
runtime_config_path_present: yes
container_running: true
live_peer_count: 3
tcp_3030_before: absent
tcp_3040_before: absent
VPS_APPLY_ENABLED_process: false
```

## Systemd Template Readiness

```text
web_unit_template_present: yes
web_unit_loopback_execstart: yes
web_unit_no_wildcard_host: yes
web_unit_workdir_opt_amn2: yes
web_unit_envfile_opt_amn2: yes
web_unit_user_amneziya: yes
bot_unit_template_present: yes
bot_unit_python_entry: yes
bot_unit_workdir_opt_amn2: yes
bot_unit_envfile_opt_amn2: yes
bot_unit_user_amneziya: yes
amneziya-web_unit_file_present: no
amneziya-web_enabled: not-found
amneziya-web_active: inactive
amneziya-bot_unit_file_present: no
amneziya-bot_enabled: not-found
amneziya-bot_active: inactive
```

Interpretation: the checked templates are suitable for loopback-only service-mode, but no service has been installed yet.

## Environment And Import Readiness

```text
env_file_present: yes
telegram_bot_token_present: yes
app_secret_key_present: yes
admin_telegram_ids_present: no
web_admin_enabled_present: yes
web_admin_password_hash_present: yes
web_admin_session_secret_present: yes
web_admin_host_present: yes
web_admin_port_present: yes
vps_apply_enabled_present: yes
settings_loaded: yes
settings_web_admin_enabled: False
settings_web_admin_host: 127.0.0.1
settings_web_admin_port: 3030
settings_api_host: 127.0.0.1
settings_api_port: 3040
settings_vps_apply_enabled: False
amn2_user_exists: no
working_dir_owned_or_accessible_marker: yes
venv_python_present: yes
web_import_check: yes
bot_import_check: yes
```

## B1 Blockers

Do not proceed to `systemctl enable --now` yet.

Required fixes or explicit decisions before B1:

- `amneziya` system user/group is absent while both unit templates use `User=amneziya` and `Group=amneziya`; starting the units as-is is expected to fail.
- `settings_web_admin_enabled` is `False`; if B1 includes web/admin, the effective `.env` must intentionally enable web admin before starting `amneziya-web`.
- `admin_telegram_ids_present` is `no`; if B1 includes the bot as an operator/admin bot, the admin identity boundary must be intentionally configured or explicitly deferred.
- `reverse_proxy_choice` remains `undecided`; this is not a blocker for loopback-only systemd B1, but it blocks any HTTPS public cutover.

## Rollback Markers

```text
rollback_plan_available: yes
rollback_stop_disable_units: sudo systemctl disable --now amneziya-web amneziya-bot
rollback_remove_units: sudo rm /etc/systemd/system/amneziya-web.service /etc/systemd/system/amneziya-bot.service
rollback_daemon_reload: sudo systemctl daemon-reload
reverse_proxy_choice: undecided
B0_writes_performed: no
```

## Recommendation

Original recommendation was to run a separate B0.1 prep gate before B1:

1. create or otherwise decide the service account for `User=amneziya` / `Group=amneziya`;
2. intentionally set the effective web/admin enablement for loopback service-mode;
3. intentionally set or defer admin Telegram IDs;
4. rerun B0 preflight and require `amn2_user_exists=yes`, `settings_web_admin_enabled=True` if web/admin is in scope, and `admin_telegram_ids_present=yes` if bot admin operations are in scope.

Follow-up completed in `research/amn2/target-server-service-mode-b0-1-prep-and-repeat-evidence-2026-06-09.md`: B0.1 prep and permissions fix passed, repeated B0 is now `ready-for-B1-loopback-systemd`.

## Secret Handling

No public IP, SSH credentials, host key material, `.env`, raw `servers.yml`, raw tokens, Authorization headers, token hashes, web password hash, session secret, private keys, PSK, peer public keys, client `.conf`, QR payloads, VPN URLs, endpoint values, backup contents or full logs were copied into this evidence.
