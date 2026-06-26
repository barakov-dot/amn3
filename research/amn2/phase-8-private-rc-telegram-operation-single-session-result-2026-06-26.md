# Phase 8 evidence: private RC Telegram operation single-session result

Date: 2026-06-26.

Status: `blocked-by-ssh-transport-before-remote-execution`.

No secrets, config payloads, keys, PSK, tokens, passwords, QR, `vpn://`, raw
process lists or DB rows are recorded here.

## Gate

```text
gate_name=PRIVATE_RC_TELEGRAM_OPERATION_SINGLE_SESSION_GATE
target_vps=89.185.80.166
expected_amn2_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
run_id=20260626T183902Z
manual_window_seconds=1800
helper=tmp/private_rc_telegram_operation_single_session_gate.ps1
```

## Observed safe output

```text
probe_url=http://89.185.80.166:3030/login
probe_url=http://89.185.80.166:3040/api/servers
probe_url=http://89.185.80.166:80/
probe_url=https://89.185.80.166:443/
probe_url_shape_status=passed
http://89.185.80.166:3030/login 000
http://89.185.80.166:3040/api/servers 000
http://89.185.80.166:80/ 000
https://89.185.80.166:443/ 000
public_closed_probes_before_status=passed
Connection closed by 89.185.80.166 port 22
ssh_single_session_telegram_operation_exit_code=255
```

## Classification

```text
remote_script_output_observed=false
remote_boundary_marker_observed=false
remote_precheck_started=false
telegram_getme_reached=false
bot_polling_started=false
manual_window_started=false
bot_polling_stop_required=false_not_started
public_exposure_performed=false
config_delivery_performed=false
peer_creation_performed=false
secret_values_printed=false
classification=ssh_transport_closed_before_remote_execution
telegram_application_failure=false
```

## Impact

The gate does not prove a Telegram bot runtime/application defect. It proves
that the current SSH transport path can close before remote script execution,
even when the helper is redesigned as single-session/no-SCP/LF-normalized.

Private/operator RC remains `launch-ready-with-explicit-limitations`; the
explicit limitation is that real Telegram operation is not currently proven
beyond the earlier live preview and should not be retried until an SSH
auth-noise/transport mitigation path is selected.
