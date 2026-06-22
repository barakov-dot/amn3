# AMN2 private RC operator run gate review

Дата: 2026-06-22.

Статус:

```text
operator_run_gate_review_status=completed-docs-only
gate_name=PRIVATE_RC_OPERATOR_RUN_GATE
operator_run_gate_proposal_status=prepared-not-opened
operator_run_gate_opened=false
phase8_final_status=launch-ready-with-explicit-limitations
private_operator_rc_launch_ready=true
public_launch_status=not-approved
```

Этот review использует только существующие Phase 8 evidence. Он не открывает
live/VPS/config/Telegram/public gates и не выполняет никаких live-действий.

## 1. Reviewed proposal

Reviewed document:

```text
docs/AMN2_PRIVATE_RC_OPERATOR_RUN_GATE_PROPOSAL.ru.md
```

Related plan:

```text
docs/AMN2_PRIVATE_RC_SESSION_0_PLAN.ru.md
```

Evidence at review time:

```text
amn3_evidence_head_at_review_time=3286e6c Prepare private RC session zero gate
```

## 2. Target VPS review

```text
target_vps_expected=89.185.80.166
target_vps_review=passed
```

Review result:

- proposal names only `89.185.80.166`;
- proposal stop-line requires stopping if target is not `89.185.80.166`;
- no provider rebuild or destructive provider action is allowed.

## 3. Expected AMN2 head review

```text
expected_amn2_runtime_package_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
expected_amn2_head_review=passed
```

Review result:

- proposal requires AMN2 `187949bffb927a0a6d6c1f260fc0bb9ebb972447`;
- proposal stop-line requires stopping if runtime head does not match;
- package upload/apply is not allowed inside this gate.

## 4. Allowed actions review

Allowed actions are intentionally narrow:

```text
read_only_vps_observation_allowed=true
loopback_web_api_health_allowed=true
telegram_getme_allowed=true
telegram_live_send_allowed=false
bot_polling_allowed=false
public_exposure_allowed=false
config_delivery_allowed=false
package_apply_allowed=false
service_restart_allowed=false
restore_import_allowed=false
provider_rebuild_allowed=false
secret_payload_output_allowed=false
```

Review result:

```text
allowed_actions_review=passed
```

The proposal is a read-only/private operator session gate. It is not a config
delivery gate, not a Telegram live delivery gate and not a public exposure
gate.

## 5. Stop-lines review

Stop-lines cover the required boundaries:

- wrong target VPS;
- wrong AMN2 runtime head;
- public exposure;
- service restart/package apply;
- config delivery;
- Telegram live send;
- bot polling;
- `.conf`, QR, `vpn://`, private key, PSK, token or password output;
- restore/import/reboot;
- provider rebuild;
- failed smoke or ambiguous evidence.

Review result:

```text
stop_lines_review=passed
```

## 6. Private inputs readiness review

Private inputs must be confirmed at run time and must not be pasted into chat
or evidence.

Required for opening the gate:

```text
vps_ssh_access_available_privately=operator_must_confirm_at_gate_open
telegram_bot_token_available_privately=operator_must_confirm_if_getme_runs
web_admin_credentials_available_privately=operator_must_confirm_if_login_check_runs
secret_values_to_chat_or_evidence_allowed=false
```

Review result:

```text
private_inputs_readiness_review=conditional-passed
condition=operator_confirms_private_inputs_at_gate_open
```

If SSH access, Telegram token or web/admin credentials are not privately
available at gate open, stop and do not run that part.

## 7. Pass/fail criteria review

Pass criteria are clear:

- target VPS confirmed as `89.185.80.166`;
- runtime/package line matches AMN2 `187949b`;
- web/admin/API stay private/loopback-only;
- external probes to `3030`, `3040`, `80`, `443` remain closed;
- Telegram `getMe` passes if token is privately available;
- bot polling does not start;
- Telegram live send does not happen;
- config delivery does not happen;
- no secret-bearing payload is printed;
- evidence contains only safe metadata.

Review result:

```text
pass_fail_criteria_review=passed
```

## 8. Go/no-go

```text
review_go=true
gate_open_go=conditional-go
operator_run_gate_opened=false
```

Meaning:

- `GO` for operator review;
- `GO` to open `PRIVATE_RC_OPERATOR_RUN_GATE` only if the operator explicitly
  opens it and confirms private inputs at run time;
- `NO-GO` for automatic execution from this review;
- `NO-GO` for config delivery, Telegram live delivery, public exposure,
  package apply, restore/import, provider rebuild or broader rollout.

## 9. Copy/paste команда открытия gate

```text
PRIVATE_RC_OPERATOR_RUN_GATE

Открыть exact gate для первой private/operator RC-сессии.

Использовать существующие Phase 8 evidence.
Target VPS: 89.185.80.166.
Expected AMN2 runtime/package head:
187949bffb927a0a6d6c1f260fc0bb9ebb972447.
AMN3 evidence head at review time:
3286e6c Prepare private RC session zero gate.

Private inputs readiness:
- VPS SSH access/password available privately.
- Telegram bot token available privately for getMe only.
- Web/admin credentials available privately only if loopback login check is included.
- Do not paste secrets into chat or evidence.

Разрешено только:
- read-only VPS observation;
- current runtime/source head check without package apply;
- loopback web/API health check;
- Telegram getMe without live send, polling or profile/media mutation;
- external closed probes for 3030, 3040, 80, 443;
- safe evidence without secret-bearing payload.

Запрещено:
- destructive VPS/provider action;
- package upload/apply;
- service restart;
- public exposure;
- firewall/listener/TLS/reverse proxy/Cloudflare/ngrok changes;
- config generation or config delivery;
- .conf/QR/vpn:// output;
- private key/PSK/token/password output;
- Telegram live send;
- bot polling;
- Telegram profile/media mutation;
- restore/import/reboot;
- provider rebuild;
- production peer/user mutation;
- broader rollout.

Stop at first failed gate and report the exact blocker.
```
