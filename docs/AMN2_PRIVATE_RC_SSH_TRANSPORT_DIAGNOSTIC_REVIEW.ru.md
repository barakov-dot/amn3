# AMN2 private RC SSH transport diagnostic review

Дата: 2026-06-25.

Статус:

```text
private_rc_ssh_transport_diagnostic_review_status=completed-docs-only
gate_name=PRIVATE_RC_SSH_TRANSPORT_DIAGNOSTIC_GATE
gate_opened=false
live_vps_ssh_performed=false
package_upload_apply_performed=false
service_restart_performed=false
telegram_polling_started=false
telegram_live_send_performed=false
config_generation_performed=false
config_delivery_performed=false
public_exposure_performed=false
secret_values_printed=false
```

Этот review использует только существующие Phase 8 evidence, private RC live
preview result и DB/runtime observation blocker result. Он не открывает
live/VPS/config/Telegram/public gates.

## 1. Почему нужен этот gate

`PRIVATE_RC_DB_RUNTIME_OBSERVATION_GATE` был открыт как read-only gate, но два
независимых helper-а не дошли до remote precheck:

```text
main_run_id=20260624T190511Z
resume_run_id=20260624T190840Z
ssh_error=Connection closed by 89.185.80.166 port 22
remote_observation_started=false
db_runtime_observation_completed=false
```

Важная граница:

```text
db_root_cause_classification=not_observed
db_discrepancy_status=unresolved_due_to_ssh_transport_blocker
```

Это не доказывает, что DB отсутствует. Это доказывает только, что выбранный SSH
transport/method не дал выполнить read-only command.

## 2. Цель gate

ЦЕЛЬ:
отделить SSH transport/session problem от AMN2 runtime/DB problem, не меняя VPS
и не выполняя service/package/config/Telegram действия.

Что доказывает:

- SSH password/session can execute trivial read-only command;
- remote shell can run non-interactive command without stdin body;
- remote shell can run small inline script without mutation;
- `ssh` exit code and stderr are captured safely;
- public exposure remains closed before/after diagnostics;
- next DB/runtime observation retry method can be selected safely.

Что не доказывает:

- DB/runtime path root cause;
- AMN2 application health;
- Telegram live operation;
- config delivery;
- restore/import readiness;
- production rollout.

## 3. Target VPS

```text
target_vps=89.185.80.166
target_review=passed
```

Основание:

- previous private RC gates targeted `89.185.80.166`;
- DB/runtime observation blocker occurred on `89.185.80.166`;
- public probes stayed closed as `000`.

## 4. Expected AMN2 head

```text
expected_amn2_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
expected_amn2_head_review=reference-only
```

SSH diagnostic does not need to inspect AMN2 head unless SSH reaches remote
command execution. If it does, head check may be read-only:

```text
source_overlay_marker_read_allowed=true
source_overlay_marker_write_allowed=false
```

## 5. Allowed read-only SSH diagnostics

Allowed only inside future `PRIVATE_RC_SSH_TRANSPORT_DIAGNOSTIC_GATE`:

- local dry probe URL inspection;
- external closed probes for `3030`, `3040`, `80`, `443`;
- `ssh root@target "true"` or equivalent trivial command;
- `ssh root@target "echo ssh_command_execution=passed"`;
- remote `pwd`, `id -u`, `uname -a` safe summary;
- remote shell detection without changing shell config;
- read-only `/opt/amn2` existence marker;
- read-only source overlay marker if reachable;
- SSH verbose client diagnostics with secrets redacted;
- final no-mutation guard.

Forbidden:

- package upload/apply;
- service start/restart/stop;
- changing `sshd_config`, firewall, users, keys or auth settings;
- reboot;
- provider action;
- public exposure changes;
- DB read beyond path/existence marker;
- DB dump/download/copy;
- Telegram polling/live send;
- config generation/delivery;
- secret output.

## 6. Stop-lines

Stop immediately if:

```text
ssh_trivial_command_fails=true
ssh_disconnects_before_command_output=true
ssh_auth_failure=true
public_probe_not_closed=true
secret_value_would_be_printed=true
operator_password_prompt_repeats_unexpectedly=true
```

Do not compensate by:

```text
service_restart=false
sshd_config_change=false
firewall_change=false
provider_rebuild=false
reboot=false
package_apply=false
telegram_polling=false
config_delivery=false
```

## 7. Pass/fail criteria

Pass if all true:

```text
public_closed_probes_before_status=passed
ssh_trivial_command_status=passed
ssh_echo_command_status=passed
ssh_remote_shell_summary_status=passed
ssh_disconnect_before_command_output=false
package_upload_apply_performed=false
service_start_restart_stop_performed=false
public_exposure_performed=false
telegram_polling_started=false
config_delivery_performed=false
secret_values_printed=false
public_closed_probes_after_status=passed
```

Fail if any true:

```text
ssh_transport_closed_before_remote_precheck=true
ssh_auth_failed=true
ssh_command_execution_not_confirmed=true
public_probe_not_closed=true
forbidden_mutation_performed=true
secret_values_printed=true
```

## 8. GO / NO-GO

```text
review_go=true
gate_open_go=conditional-go-with-explicit-operator-approval
operator_can_open_gate_now=true
```

Причина:
gate является SSH/VPS interaction, поэтому требует явного operator approval.
Android phone и Telegram live preview для него не нужны.

## 9. Copy/paste command

```text
PRIVATE_RC_SSH_TRANSPORT_DIAGNOSTIC_GATE

Открыть exact gate для private/operator SSH transport diagnostic.

Использовать существующие Phase 8 evidence и DB runtime observation blocker result.
Target VPS: 89.185.80.166.
Expected AMN2 runtime/source head, if remote command execution reaches AMN2 check:
187949bffb927a0a6d6c1f260fc0bb9ebb972447.

Allowed:
- local dry probe URL inspection;
- public closed probes for 3030, 3040, 80, 443;
- trivial read-only SSH command execution check;
- safe remote shell/cwd/user/kernel summary;
- read-only /opt/amn2 existence and source marker check if SSH works;
- SSH client diagnostic metadata without secrets;
- final no-mutation/no-public-exposure guard.

Forbidden:
- destructive VPS/provider action;
- package upload/apply;
- service start/restart/stop;
- sshd_config/firewall/user/key/auth changes;
- public exposure;
- firewall/listener/TLS/reverse proxy/Cloudflare/ngrok changes;
- config generation or config delivery;
- peer creation;
- .conf/QR/vpn:// output;
- private key/PSK/token/password output;
- DB row dump or DB download/copy;
- Telegram polling or live send;
- Telegram profile/media mutation;
- restore/import/reboot;
- provider rebuild;
- production rollout.

Stop at first failed diagnostic and report the exact blocker.
```
