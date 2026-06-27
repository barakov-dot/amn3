# AMN2 SSH auth-noise mitigation review

Дата: 2026-06-27.
Модель решения: `GPT-5.5`.
Статус: `completed-docs-only-review`.

Этот review использует существующие Phase 8/9 evidence. Live/VPS/SSH/config/
Telegram/public gates этим документом не открывались.

## Decision

```text
gate_name=AMN2_SSH_AUTH_NOISE_MITIGATION_REVIEW
selected_phase9_lane=HARDENING_PRODUCTIZATION
review_status=passed
ssh_auth_noise_observed=true
ssh_auth_noise_execution_required_for_current_lane=false
ssh_auth_hardening_execution_approved=false
ssh_auth_hardening_future_exact_gate_required=true
current_safe_policy=no-mutation-short-ssh-key-based-operations
default_hold=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
```

Итог: SSH auth-noise mitigation не является blocker для текущего Phase 9
`HARDENING_PRODUCTIZATION` lane. Исполнительные изменения `sshd`, firewall,
users, keys, password auth, root login, SSH port или rate limiting не
разрешены этим review.

## Evidence base

Использованные документы:

- `docs/AMN2_PRIVATE_RC_SSH_AUTH_NOISE_MITIGATION_REVIEW.ru.md`;
- `docs/AMN2_PRIVATE_RC_SSH_SERVER_LOG_DIAGNOSTIC_RESULT.ru.md`;
- `docs/AMN2_PRIVATE_RC_SSH_SINGLE_SESSION_DIAGNOSTIC_RESULT.ru.md`;
- `docs/AMN2_PRIVATE_RC_SSH_KEY_BASED_ACCESS_PREP_GATE_RESULT.ru.md`;
- `docs/AMN2_HELPER_SSH_TRANSPORT_HARDENING.ru.md`;
- `docs/AMN2_PHASE_9_HARDENING_ENTRY_REVIEW.ru.md`.

Ключевые факты:

```text
server_auth_noise=heavy
journal_sshd_recent_failed_password_count=125
auth_log_recent_failed_password_count=121
journal_sshd_recent_maxstartups_count=0
auth_log_recent_maxstartups_count=0
kernel_recent_oom_count=0
kernel_recent_conntrack_count=0
ssh_key_based_access_prep_gate_status=passed
operator_public_key_installed=true
public_exposure_status=closed-by-default
```

## Interpretation

Логи доказали тяжелый внешний SSH auth-noise фон, но не доказали:

- `MaxStartups` throttling;
- OOM / killed process;
- conntrack exhaustion;
- fatal sshd error;
- AMN2 runtime failure;
- Telegram bot failure.

Практическая проблема уже была частично обойдена более безопасным способом:

```text
key_based_access_path_status=passed
no_long_ssh_telegram_operation_status=passed
manual_window_without_open_ssh=true
remote_watchdog_ttl_used=true
final_no_polling_guard_status=passed
```

Поэтому current lane не требует срочного изменения SSH/auth policy. Менять
SSH/firewall/auth слишком рискованно без отдельного rollback/provider-console
плана.

## Current safe policy

Для текущего hardening lane принять как standard operating policy:

- использовать key-based SSH где возможно;
- не держать длинные SSH-сессии во время manual windows;
- делать short SSH precheck/start/final-guard commands;
- не повторять один и тот же failed SSH helper много раз;
- при `exit 255` до remote marker фиксировать blocker и останавливаться;
- не менять auth/firewall/sshd без отдельного exact gate;
- сохранять provider-console/rollback boundary как precondition для будущих
  auth changes.

## Future mitigation path

Если operator решит реально снижать SSH auth-noise, нужен отдельный review:

```text
AMN2_SSH_AUTH_HARDENING_GATE_REVIEW
```

Минимальные preconditions:

```text
provider_console_or_recovery_access_confirmed=true
key_based_root_login_confirmed=true
current_authorized_keys_preserved=true
rollback_plan_written=true
public_ports_3030_3040_80_443_remain_closed=true
operator_lockout_risk_accepted=true
```

Возможные будущие actions только внутри отдельного exact gate:

- disable password auth after key path is proven;
- restrict root password login without disabling proven key login;
- move SSH port only with provider/firewall rollback plan;
- add rate limiting/fail2ban-like policy;
- provider-side firewall allowlist only after recovery path is proven.

## Stop-lines

Без нового exact named gate нельзя:

- менять `sshd_config`;
- отключать password auth;
- отключать root login;
- менять SSH port;
- менять firewall/provider security rules;
- удалять или перезаписывать `authorized_keys`;
- устанавливать или настраивать rate limiting/fail2ban;
- restart/stop/start `sshd` или другие сервисы;
- выполнять reboot/restore/import/provider rebuild;
- открывать public exposure;
- запускать Telegram polling/live send;
- создавать или доставлять config;
- создавать peer/config;
- выводить secrets/payloads.

## Phase 9 status

```text
phase9_ssh_auth_noise_mitigation_review_status=passed
phase9_ssh_auth_noise_blocker=false
phase9_ssh_auth_hardening_future_gate_required=true
recommended_next_docs_only=AMN2_DB_AGGREGATE_COUNTS_REVIEW
```
