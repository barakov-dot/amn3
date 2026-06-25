# AMN2 private RC DB/runtime observation retry plan

Дата: 2026-06-25.

Статус:

```text
private_rc_db_runtime_observation_retry_plan_status=completed-docs-only
retry_gate_name=PRIVATE_RC_DB_RUNTIME_OBSERVATION_GATE_RETRY
retry_gate_opened=false
live_vps_ssh_performed=false
package_upload_apply_performed=false
service_restart_performed=false
telegram_polling_started=false
config_delivery_performed=false
public_exposure_performed=false
secret_values_printed=false
```

Этот retry plan использует существующие Phase 8 evidence и DB/runtime
observation blocker result. Он не открывает live/VPS/config/Telegram/public
gates.

## 1. Почему retry нельзя делать сразу

Первичный `PRIVATE_RC_DB_RUNTIME_OBSERVATION_GATE` не дошел до remote
observation:

```text
exact_blocker=ssh_transport_closed_before_remote_precheck
db_root_cause_classification=not_observed
```

Поэтому повтор DB/runtime observation допустим только после одного из условий:

```text
ssh_transport_diagnostic_passed=true
operator_explicitly_accepts_adjusted_ssh_method=true
```

Без этого retry рискует снова упереться в тот же transport blocker и не
добавить DB evidence.

## 2. Цель retry

ЦЕЛЬ:
повторить read-only DB/runtime observation после подтверждения, что SSH command
execution работает выбранным методом.

Что доказывает:

- `Settings().database_path` и resolved path;
- DB path candidates under `/opt/amn2`;
- web process cwd and env key presence without values;
- safe DB aggregate inventory if DB exists;
- loopback web health if already running;
- whether `db_present=false` in Telegram preview was path mismatch, missing DB,
  helper issue, or expected runtime behavior.

Что не доказывает:

- restore/import DR;
- DB migration safety;
- config delivery;
- public launch;
- Telegram production operation;
- production-scale rollout.

## 3. Retry method

Recommended retry method after SSH diagnostic:

```text
retry_method=small_read_only_ssh_commands
large_stdin_script=false
remote_script_upload=false
package_upload_apply=false
service_restart=false
```

Allowed command strategy:

- split diagnostics into small commands;
- no large heredoc over SSH stdin;
- no remote helper upload unless a new gate explicitly allows helper upload;
- each command must print only safe markers;
- stop at first failed command.

## 4. Allowed actions

Allowed only inside future `PRIVATE_RC_DB_RUNTIME_OBSERVATION_GATE_RETRY`:

- read-only VPS observation;
- current runtime/source head check without package apply;
- safe env key presence checks without values;
- settings-derived DB path observation;
- DB candidate path/size/mode/mtime observation;
- web process cwd and env key presence markers only;
- DB aggregate counts if DB exists;
- loopback web health if already running, without service start/restart;
- public closed probes for `3030`, `3040`, `80`, `443`;
- final no-mutation guard.

Forbidden:

- package upload/apply;
- service start/restart/stop;
- DB migration/write;
- DB row dump;
- DB download/copy;
- public exposure;
- config generation/delivery;
- peer creation;
- Telegram polling/live send;
- restore/import/reboot;
- provider rebuild;
- secret output.

## 5. Stop-lines

Stop if:

```text
ssh_transport_diagnostic_not_passed=true
source_overlay_mismatch=true
settings_load_failed=true
secret_value_would_be_printed=true
db_row_dump_needed=true
public_probe_not_closed=true
```

Do not compensate with:

```text
service_restart=false
package_apply=false
db_migration=false
restore_import=false
provider_action=false
public_exposure=false
telegram_polling=false
config_delivery=false
```

## 6. Pass/fail criteria

Pass if all true:

```text
ssh_transport_diagnostic_passed=true
target_vps_match=yes
source_overlay_match=yes
settings_database_path_observed=true
settings_database_resolved_path_observed=true
db_path_observation_completed=true
db_root_cause_classification=classified
db_rows_printed=false
secret_values_printed=false
package_upload_apply_performed=false
service_start_restart_stop_performed=false
public_closed_probes_after_status=passed
```

Fail if any true:

```text
ssh_transport_closed_before_remote_precheck=true
source_overlay_mismatch=true
db_path_observation_inconclusive=true
secret_value_printed=true
db_row_dump_performed=true
forbidden_mutation_performed=true
public_probe_not_closed=true
```

## 7. Copy/paste command

```text
PRIVATE_RC_DB_RUNTIME_OBSERVATION_GATE_RETRY

Открыть exact gate для retry private/operator DB/runtime read-only observation.

Prerequisite:
- PRIVATE_RC_SSH_TRANSPORT_DIAGNOSTIC_GATE passed, or operator explicitly accepts adjusted SSH method.

Использовать существующие Phase 8 evidence, DB runtime observation blocker result,
and SSH transport diagnostic result.
Target VPS: 89.185.80.166.
Expected AMN2 runtime/source head:
187949bffb927a0a6d6c1f260fc0bb9ebb972447.

Allowed:
- read-only VPS observation;
- current runtime/source head check without package apply;
- safe env presence checks without printing token/password values;
- settings-derived DB path observation with secret redaction;
- DB path/cwd/process observation without DB row dump;
- DB aggregate inventory if DB exists;
- loopback web health only if already running, without service start/restart;
- public closed probes for 3030, 3040, 80, 443;
- safe evidence without secret-bearing payload.

Forbidden:
- destructive VPS/provider action;
- package upload/apply;
- service start/restart/stop;
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

Stop at first failed gate and report the exact blocker.
```
