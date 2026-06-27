# AMN2 Telegram operation runbook polish (Phase 9 hardening lane)

Дата: 2026-06-27.
Модель: `Codex-Spark`.
Статус: `completed-docs-only`.

Использованы существующие Phase 8 evidence и `PHASE 9 hardening` решения.
Live/VPS/SSH/Telegram/public gates этим документом не открывались.

## Цель

Привести operational runbook Telegram operation под no-long-SSH паттерн:

- key-based SSH only;
- короткие SSH precheck/start/final guard шаги;
- remote watchdog с TTL (<= 180s);
- local manual Telegram window без открытого SSH.

## Исправленная модель окна

```text
local public probes -> short SSH precheck -> short SSH polling start -> local manual window (no SSH) -> short SSH final stop/guard -> local public probes
```

## Ключевые acceptance criteria

```text
ssh_key_login_only=true
password_fallback_used=false
remote_polling_ttl_seconds<=180
ssh_session_open_during_manual_window=false
bot_polling_started=true
bot_polling_stopped_in_final_guard=true
final_no_polling_guard_status=passed
config_delivery_attempted=false
peer_creation_performed=false
public_closed_probes_before_status=passed
public_closed_probes_after_status=passed
secret_values_printed=false
raw_output_for_sensitive_sources=false
```

## Точно требуемые проверки перед запуском

```text
1) parse check и dry URL inspect helper-а;
2) probe_url shape must be `${TargetIp}:PORT` (не `$TargetIp:PORT`);
3) SSH precheck: source overlay, settings/env presence, public listener guard, polling guard;
4) Telegram getMe precheck;
5) final guard только no-polling stop;
6) public probes до и после must be 000.
```

## Обновленный copy/paste gate

```text
PRIVATE_RC_TELEGRAM_OPERATION_NO_LONG_SSH_RETRY_GATE

Открыть exact gate для controlled private/operator Telegram bot operation
retry без удержания SSH во время manual Telegram window.

Target VPS: 89.185.80.166.
Expected AMN2 runtime/source head: 187949bffb927a0a6d6c1f260fc0bb9ebb972447.

Allowed:
- local public closed probes before/after;
- key-based SSH only;
- short SSH precheck;
- short SSH controlled polling start with remote self-stop watchdog;
- local manual Telegram window while no SSH session is open;
- short SSH final no-polling guard;
- Telegram getMe;
- live Telegram replies only to approved admin/operator chats;
- minimal admin/operator DB state mutation only;
- safe evidence without secret payload.

Forbidden:
- destructive VPS/provider action;
- package apply/upload;
- password fallback;
- SCP/helper upload;
- remote temp helper files;
- broad service restart;
- public exposure or firewall/auth changes;
- config generation/delivery;
- peer creation;
- .conf, QR, vpn://, private key, PSK, token/password output;
- restore/import/reboot;
- Telegram profile/media mutation;
- production rollout.

Manual window:
- open Telegram before local SSH start;
- when `local_manual_window_status=started`, send `/start` immediately;
- stop-polling and final guard must run after manual window.
```

## Stop-lines для этого runbook

Невыполнение любых ниже перечисленных пунктов требует отдельного exact named gate:

```text
public_exposure
config_delivery
peer_creation
package_upload_apply
service_restart_outside_guard
firewall_sshd_auth_keys_users_changes
telegram_profile_media_mutation
restore_import_reboot
provider_rebuild
production_scale_rollout
```

## Полезно знать после hardening

После прохода `PRIVATE_RC_TELEGRAM_OPERATION_NO_LONG_SSH_RETRY_GATE`:

```text
telegram_private_operator_status=passed_private_operator_no_config_delivery
telegram_no_polling_status=restored_and_proven
remaining_amn2_app_main_polling_process_count=0
```

Это не снимает hard limitations на launch/config/peer/public rollout.
