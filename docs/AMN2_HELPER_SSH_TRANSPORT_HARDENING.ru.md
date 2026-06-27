# HELPER_SSH_TRANSPORT_HARDENING

Дата: 2026-06-27.
Модель: `Codex-Spark`.
Статус: `completed-docs-only`.

Live/VPS/SSH/Telegram/public gates этим hardening не открывались.

## Problem

Во время Phase 8/9 hardening накопились повторяющиеся SSH-транспортные проблемы:

- нестабильные `ssh` сессии при длинных командах;
- закрытие соединения на `Connection closed ...` во время remote phase;
- `CRLF` в stdin-скриптах, которые ломали финальную обработку `exit 0` на стороне wrapper.

Чтобы снизить риск повторения, для дальнейших helper-пайпов нужен отдельный транспортный hardening.

## Target design

Для live/controlled gates после этого hardening:

- использовать короткие, узкие SSH-команды;
- предпочитать single-session где это возможно по задаче;
- где задача требует ручного окна (`manual window`), не держать SSH-сессию открытой;
- при длинном/длительном remote процессе запускать remote watchdog с ограничением TTL;
- избегать `scp` и `remote temp helper`;
- нормализовывать bash-тело в LF перед передачей в `ssh ... bash -s`;
- не печатать secret/raw output.

## Required hardening rules

```text
helper_ssh_transport_hardening_status=completed-docs-only
single_session_preference=true
short_ssh_precheck_required=true
short_ssh_start_required=true
short_ssh_final_guard_required=true
manual_window_without_open_ssh_preferred=true
remote_watchdog_required_on_long_polling=true
remote_script_lf_normalization_required=true
remote_polling_ttl_default=120
remote_polling_ttl_max=180
scp_upload_required=false
remote_temp_helper_file_created=false
raw_process_list_output_allowed=false
raw_log_output_allowed=false
secret_values_printed=false
```

## Operational checklist

1. Перед выпуском helper-а всегда выполнить `parse_check` и dry-inspect URL шаблонов.
2. Перед live-коротким gate сделать local `public closed probes` для `3030/3040/80/443`.
3. Выполнить короткий remote precheck по source/env/safety.
4. Для polling/manual окна не держать open SSH.
5. Запустить только targeted короткий final guard и затем short cleanup/no-polling verification.
6. После завершения выполнить local `public closed probes` снова.

## Stop-lines

После hardening нельзя открывать:

- public exposure;
- config generation/delivery (в том числе `.conf`, QR, `vpn://`, key/PSK/token/password output);
- peer creation;
- package upload/apply;
- service restart/start/stop (кроме строго целевого named gate с этим разрешением);
- firewall/sshd/auth/users/keys mutation;
- Telegram profile/media mutation;
- `restore/import/reboot/provider rebuild/production rollout`;
- raw DB row dump/download/copy.

## Stop-line для wrapper serialization

Если remote output уже дал все `*_status=passed`, но wrapper падает на `exit` из-за shell-сериализации,
классифицировать как `helper serialization issue` и не перезапускать remote action автоматически:

```text
issue=remote_output_passing_with_local_exit_masking
response=stop_and_prepare_cleanup_or_retry_plan
```

## Next exact helper step

Этот hardening применяется как prerequisite для:

- `PRIVATE_RC_TELEGRAM_OPERATION_NO_LONG_SSH_RETRY_GATE`;
- всех следующих controlled helper-интеграций в hardening lane;
- любых новых helper-скриптов с ручными flow.

Не открывать live gates этим документом.
