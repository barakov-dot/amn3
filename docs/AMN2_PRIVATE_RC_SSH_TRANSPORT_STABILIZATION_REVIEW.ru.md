# PRIVATE_RC_SSH_TRANSPORT_STABILIZATION_REVIEW

Дата: 2026-06-26.

Статус: `completed-docs-only`.

Использованы существующие Phase 8 evidence, SSH transport diagnostic result,
SSH server log diagnostic result и Telegram operation blocker record.

Live/VPS/SSH/config/Telegram/public gates этим review не открывались.

## Review verdict

```text
review_go=true
execution_gate_go=conditional-go-with-explicit-operator-approval
target_vps=89.185.80.166
current_blocker=intermittent-ssh-scp-transport-close-during-repeated-sessions
telegram_operation_retry_go=false
recommended_next_execution_gate=PRIVATE_RC_SSH_SINGLE_SESSION_DIAGNOSTIC_GATE
public_exposure_status=closed
config_delivery_status=not-approved
telegram_polling_status=blocked-until-ssh-transport-stabilized
```

Основная рекомендация: не пытаться снова запускать Telegram operation и не
делать серию коротких SSH/SCP-сессий. Следующий execution gate должен быть
одним SSH-сеансом, который выполняет read-only диагностику внутри одного
подключения и печатает только safe evidence.

## 1. Current facts

Зафиксировано:

```text
private_rc_telegram_operation_gate_status=blocked-by-intermittent-ssh-transport
ssh_trivial_commands_can_pass=true
ssh_repeated_sessions_unstable=true
scp_upload_can_fail_with_exit_255=true
server_auth_noise=heavy
maxstartups_evidence=false
oom_evidence=false
conntrack_evidence=false
kernel_kill_evidence=false
public_exposure_status=closed
known_temp_helper_cleanup_status=passed
no_polling_guard_previous_status=passed
```

Server-side log diagnostic показал:

```text
journal_sshd_recent_connection_closed_count=34
journal_sshd_recent_failed_password_count=41
journal_sshd_recent_accepted_password_count=3
journal_sshd_recent_maxstartups_count=0
journal_sshd_recent_timeout_count=0
journal_sshd_recent_oom_count=0
journal_sshd_recent_conntrack_count=0
auth_log_recent_failed_password_count=40
auth_log_recent_pam_count=61
kernel_relevant_recent_status=blocked_connection_closed
```

## 2. What this review does not approve

Этот review не разрешает:

- запускать Telegram polling;
- повторять `PRIVATE_RC_TELEGRAM_OPERATION_GATE`;
- выполнять package upload/apply;
- выполнять service start/restart/stop;
- менять `sshd_config`, firewall, users, keys или auth policy;
- открывать public exposure;
- менять listener/TLS/reverse proxy/Cloudflare/ngrok;
- генерировать или доставлять config;
- создавать peer/config;
- выводить `.conf`, QR, `vpn://`, private key, PSK, token/password;
- выполнять restore/import/reboot/provider action.

## 3. Stabilization options

### Option A: single-session read-only diagnostic

Рекомендуемый первый execution gate.

Идея: вместо 4-8 отдельных SSH-сессий открыть один SSH-сеанс и выполнить внутри
него read-only checks последовательно.

Разрешить:

- one SSH login;
- read-only uptime/load/process summary;
- read-only sshd/auth log counters;
- read-only AMN2 source marker check;
- read-only no-polling check;
- public closed probes только локально до и после SSH-сеанса;
- safe evidence only.

Запретить:

- upload helper через SCP;
- package apply;
- service start/restart/stop;
- sshd/firewall/auth mutation;
- Telegram polling/live send;
- config generation/delivery.

Pass criteria:

```text
single_ssh_session_opened=true
all_read_only_checks_completed_in_one_session=true
source_overlay_match=yes
no_telegram_polling_process=true
auth_noise_observed_or_noted=true
public_closed_probes_before_status=passed
public_closed_probes_after_status=passed
secret_values_printed=false
```

Fail criteria:

```text
single_session_connection_closed=true
auth_denied=true
public_probe_not_closed=true
unexpected_mutation_required=true
secret_bearing_output_risk=true
```

Recommended gate:

```text
PRIVATE_RC_SSH_SINGLE_SESSION_DIAGNOSTIC_GATE
```

### Option B: provider console / out-of-band inspection

Использовать, если single-session diagnostic тоже получает `Connection closed`.

Цель: через панель/VNC/serial/provider console посмотреть, что происходит без
зависимости от SSH-транспорта.

Разрешить только review или ручную operator-side инспекцию без изменений:

- uptime/load;
- auth log tail;
- sshd status;
- disk space;
- process summary.

Любые reboot/provider rebuild/firewall/sshd changes требуют отдельного
destructive/provider/config gate.

Recommended review:

```text
PRIVATE_RC_PROVIDER_CONSOLE_SSH_DIAGNOSTIC_REVIEW
```

### Option C: auth-noise mitigation proposal

Использовать только после docs-only review, не как немедленное действие.

Возможные идеи для отдельного future gate:

- move SSH off default port;
- key-only SSH;
- disable password auth;
- allowlist operator IP;
- install/configure rate limiting;
- fail2ban-like policy.

Все это меняет auth/network boundary, поэтому сейчас не разрешено.

Recommended review:

```text
PRIVATE_RC_SSH_AUTH_NOISE_MITIGATION_REVIEW
```

### Option D: backoff policy only

Самый консервативный вариант, если не хотим трогать VPS auth/network.

Правило:

```text
ssh_exit_255_backoff_minutes=15
max_retries_per_gate=1
if_second_exit_255_then_gate_status=blocked-by-ssh-transport
no_live_retry_same_gate=true
```

Этот вариант не чинит причину, но снижает риск поломать live gate серией
повторов.

## 4. Recommended decision

Рекомендация:

```text
recommended_path=Option_A_single_session_read_only_diagnostic
recommended_next_gate=PRIVATE_RC_SSH_SINGLE_SESSION_DIAGNOSTIC_GATE
telegram_operation_retry_go=false
```

Причина:

- текущая проблема проявляется на серии SSH/SCP-сессий;
- single-session gate уменьшает количество handshakes;
- не требует изменения SSH/firewall/provider;
- сохраняет private/operator RC safety boundary;
- дает шанс собрать все нужные no-polling/source/public evidence одним заходом.

## 5. Exact copy/paste command for next gate

```text
PRIVATE_RC_SSH_SINGLE_SESSION_DIAGNOSTIC_GATE

Открыть exact gate для single-session read-only SSH transport diagnostic.

Использовать существующие Phase 8 evidence, SSH server log diagnostic result
и Telegram operation blocker record.
Target VPS: 89.185.80.166.
Expected AMN2 runtime/source head:
187949bffb927a0a6d6c1f260fc0bb9ebb972447.

Allowed:
- local public closed probes for 3030, 3040, 80, 443 before and after;
- exactly one SSH login/session for remote checks;
- read-only uptime/load/kernel/user summary;
- read-only sshd/auth log counters with IP/port redaction;
- read-only AMN2 source marker check;
- read-only no Telegram polling process guard;
- safe evidence only.

Forbidden:
- package upload/apply;
- SCP/helper upload;
- service start/restart/stop;
- sshd_config/firewall/user/key/auth changes;
- public exposure;
- config generation or config delivery;
- peer creation;
- .conf/QR/vpn:// output;
- private key/PSK/token/password output;
- DB row dump or DB download/copy;
- Telegram polling or live send;
- Telegram profile/media mutation;
- restore/import/reboot;
- provider action.

Stop at first failed gate and report exact blocker.
```

## 6. Updated task menu

Одиночный:

```text
PRIVATE_RC_SSH_SINGLE_SESSION_DIAGNOSTIC_GATE
```

Парный:

```text
PRIVATE_RC_SSH_SINGLE_SESSION_DIAGNOSTIC_GATE
+
HELPER_SSH_TRANSPORT_HARDENING
```

Тройной:

```text
PRIVATE_RC_SSH_SINGLE_SESSION_DIAGNOSTIC_GATE
+
HELPER_SSH_TRANSPORT_HARDENING
+
PRIVATE_RC_FINAL_STATUS_REFRESH
```

Более широкий пакет:

```text
PRIVATE_RC_SSH_SINGLE_SESSION_DIAGNOSTIC_GATE
+
PRIVATE_RC_SSH_AUTH_NOISE_MITIGATION_REVIEW
+
HELPER_SSH_TRANSPORT_HARDENING
+
PRIVATE_RC_FINAL_STATUS_REFRESH
+
NEXT_CHAT_SYNC_AND_PUSH
```
