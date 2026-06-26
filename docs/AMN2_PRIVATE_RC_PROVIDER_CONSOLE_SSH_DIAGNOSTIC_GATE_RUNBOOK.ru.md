# PRIVATE_RC_PROVIDER_CONSOLE_SSH_DIAGNOSTIC_GATE_RUNBOOK

Дата: 2026-06-26.

Статус: `prepared-operator-side-runbook`.

Назначение: выполнить read-only diagnostic через provider console/VNC/serial,
если SSH transport закрывается до remote execution.

Этот runbook сам по себе не открывает VPS/provider действие. Использовать его
только после explicit gate:

```text
PRIVATE_RC_PROVIDER_CONSOLE_SSH_DIAGNOSTIC_GATE
```

## Operator boundary

Разрешено:

- войти в provider console/VNC/serial;
- вставить один read-only command block ниже;
- вернуть только safe summary.

Запрещено:

- reboot/reset/rebuild/restore/import;
- менять firewall/sshd/auth/users/keys;
- стартовать/останавливать/перезапускать сервисы;
- открывать public exposure;
- запускать Telegram polling;
- генерировать/deliver config;
- выводить raw auth logs, IP/ports, env, DB rows, tokens, keys, `.conf`, QR,
  `vpn://`, PSK/password.

## Console command block

Вставлять в provider console только если это обычная root shell на целевом VPS.
Блок печатает aggregate counters и safe statuses, без raw log output.

```bash
echo "PRIVATE_RC_PROVIDER_CONSOLE_SSH_DIAGNOSTIC_GATE"
echo "target=89.185.80.166"
echo "utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "opened_gate=PRIVATE_RC_PROVIDER_CONSOLE_SSH_DIAGNOSTIC_GATE"
echo "scope=provider-console-read-only-ssh-diagnostic"
echo "provider_mutation_performed=false"
echo "reboot_restore_import_rebuild_performed=false"
echo "service_start_restart_stop_performed=false"
echo "sshd_config_change_performed=false"
echo "firewall_auth_user_key_change_performed=false"
echo "public_exposure_performed=false"
echo "telegram_polling_started=false"
echo "config_generation_delivery_performed=false"
echo "peer_creation_performed=false"
echo "secret_values_printed=false"

echo ""
echo "[console] host health"
echo "remote_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uptime -p 2>/dev/null | sed 's/^/remote_uptime_pretty=/' || true
if [ -r /proc/loadavg ]; then echo "remote_loadavg=$(cut -d ' ' -f 1-3 /proc/loadavg)"; fi
df -h / /opt 2>/dev/null | awk 'NR==1{next} {gsub(/%/,"",$5); print "disk_" NR "_mount=" $6 " used_percent=" $5}' || true
free -m 2>/dev/null | awk '/Mem:/ {print "memory_total_mb="$2; print "memory_used_mb="$3; print "memory_available_mb="$7}' || true
echo "remote_uname=$(uname -srm)"
echo "remote_uid=$(id -u)"

echo ""
echo "[console] sshd status"
if command -v systemctl >/dev/null 2>&1; then
  systemctl is-active ssh 2>/dev/null | sed 's/^/systemctl_ssh_active=/' || true
  systemctl is-active sshd 2>/dev/null | sed 's/^/systemctl_sshd_active=/' || true
fi
if command -v ss >/dev/null 2>&1; then
  echo "sshd_listen_22_count=$(ss -ltn 2>/dev/null | awk '{print $4}' | grep -Ec '(^0\.0\.0\.0:22$)|(^\[::\]:22$)|(:22$)' || true)"
fi
echo "sshd_process_count=$(pgrep -x sshd 2>/dev/null | wc -l | tr -d ' ')"
echo "raw_process_list_output_performed=false"

echo ""
echo "[console] auth noise counters"
AUTH_DATA=""
if command -v journalctl >/dev/null 2>&1; then
  AUTH_DATA="$(journalctl --no-pager -u ssh -u sshd --since '2026-06-26 12:00:00 UTC' -n 1000 2>/dev/null || true)"
fi
if [ -z "$AUTH_DATA" ] && [ -r /var/log/auth.log ]; then
  AUTH_DATA="$(tail -n 1000 /var/log/auth.log 2>/dev/null || true)"
fi
count_pattern() {
  pattern="$1"
  if [ -z "$AUTH_DATA" ]; then printf '0\n'; else printf '%s\n' "$AUTH_DATA" | grep -Eci "$pattern" 2>/dev/null || true; fi
}
if [ -z "$AUTH_DATA" ]; then echo "auth_data_present=false"; else echo "auth_data_present=true"; fi
echo "auth_recent_line_count=$(printf '%s\n' "$AUTH_DATA" | sed '/^$/d' | wc -l | tr -d ' ')"
echo "auth_connection_closed_count=$(count_pattern 'Connection closed')"
echo "auth_disconnected_from_count=$(count_pattern 'Disconnected from')"
echo "auth_failed_password_count=$(count_pattern 'Failed password')"
echo "auth_accepted_password_count=$(count_pattern 'Accepted password')"
echo "auth_maxstartups_count=$(count_pattern 'MaxStartups|beginning MaxStartups throttling')"
echo "auth_too_many_auth_failures_count=$(count_pattern 'Too many authentication failures')"
echo "auth_kex_exchange_identification_count=$(count_pattern 'kex_exchange_identification')"
echo "auth_pam_count=$(count_pattern 'pam_unix')"
echo "raw_auth_log_output_performed=false"
echo "ip_port_log_values_printed=false"

echo ""
echo "[console] kernel pressure counters"
KERNEL_DATA="$(dmesg -T 2>/dev/null | tail -n 300 || true)"
count_kernel() {
  pattern="$1"
  if [ -z "$KERNEL_DATA" ]; then printf '0\n'; else printf '%s\n' "$KERNEL_DATA" | grep -Eci "$pattern" 2>/dev/null || true; fi
}
echo "kernel_recent_line_count=$(printf '%s\n' "$KERNEL_DATA" | sed '/^$/d' | wc -l | tr -d ' ')"
echo "kernel_oom_count=$(count_kernel 'Out of memory|Killed process')"
echo "kernel_segfault_count=$(count_kernel 'segfault')"
echo "kernel_conntrack_count=$(count_kernel 'conntrack|nf_conntrack')"
echo "kernel_tcp_count=$(count_kernel 'TCP|tcp')"
echo "raw_kernel_log_output_performed=false"

echo ""
echo "[console] AMN2 marker"
if [ -d /opt/amn2 ]; then echo "opt_amn2_present=true"; else echo "opt_amn2_present=false"; fi
if [ -f /opt/amn2/.amn2_source_overlay_commit ]; then
  SRC="$(tr -d '[:space:]' < /opt/amn2/.amn2_source_overlay_commit)"
  echo "source_overlay_commit=$SRC"
  if [ "$SRC" = "187949bffb927a0a6d6c1f260fc0bb9ebb972447" ] || [ "$SRC" = "187949b" ]; then
    echo "source_overlay_match=yes"
  else
    echo "source_overlay_match=no"
  fi
else
  echo "source_overlay_commit=missing"
  echo "source_overlay_match=no_marker"
fi
echo "source_marker_secret_values_printed=false"

echo ""
echo "[console] Telegram polling guard"
POLLING_COUNT=0
for pid in $(pgrep -f 'app.main' 2>/dev/null || true); do
  [ -d "/proc/$pid" ] || continue
  CMD="$(tr '\0' ' ' < "/proc/$pid/cmdline" 2>/dev/null || true)"
  CWD="$(readlink -f "/proc/$pid/cwd" 2>/dev/null || true)"
  case "$CMD" in
    *"-m app.main"*) if [ "$CWD" = "/opt/amn2" ]; then POLLING_COUNT=$((POLLING_COUNT+1)); fi ;;
  esac
done
echo "telegram_app_main_polling_process_count=$POLLING_COUNT"
if [ "$POLLING_COUNT" -eq 0 ]; then echo "no_telegram_polling_process=true"; else echo "no_telegram_polling_process=false"; fi
echo "raw_process_list_output_performed=false"

echo ""
echo "[console] final guard"
echo "provider_console_read_only_diagnostic_status=completed_operator_side"
echo "provider_mutation_performed=false"
echo "reboot_restore_import_rebuild_performed=false"
echo "service_start_restart_stop_performed=false"
echo "sshd_config_change_performed=false"
echo "firewall_auth_user_key_change_performed=false"
echo "public_exposure_performed=false"
echo "telegram_polling_started=false"
echo "config_generation_delivery_performed=false"
echo "peer_creation_performed=false"
echo "secret_values_printed=false"
```

## Safe summary to paste back

Потом вернуть в чат только safe output блока выше или короткую сводку:

```text
provider_console_access_available=true|false
provider_console_read_only_diagnostic_status=completed_operator_side|blocked
source_overlay_match=yes|no|not_observed
no_telegram_polling_process=true|false|not_observed
auth_failed_password_count=<number>
auth_connection_closed_count=<number>
auth_maxstartups_count=<number>
kernel_oom_count=<number>
kernel_conntrack_count=<number>
provider_mutation_performed=false
secret_values_printed=false
exact_blocker=<none|safe_text>
```
