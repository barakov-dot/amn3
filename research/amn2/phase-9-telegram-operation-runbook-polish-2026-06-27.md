# AMN2 Telegram operation runbook polish (Phase 9)

Дата: 2026-06-27.
Модель: `Codex-Spark`.
Type: docs-only refresh.

## Input evidence

- `docs/AMN2_HELPER_TELEGRAM_OPERATION_NO_LONG_SSH_HARDENING.ru.md`
- `docs/AMN2_HELPER_SSH_TRANSPORT_HARDENING.ru.md`
- `docs/AMN2_PRIVATE_RC_TELEGRAM_OPERATION_NO_LONG_SSH_RETRY_RESULT.ru.md`
- `docs/AMN2_PRIVATE_RC_TELEGRAM_OPERATION_KEY_PATH_CLEANUP_GUARD_RESULT.ru.md`
- `docs/AMN2_PHASE_9_HARDENING_ENTRY_REVIEW.ru.md`

## Result

`AMN2_TELEGRAM_OPERATION_RUNBOOK_POLISH` prepared as docs-only.

```text
runbook_polish_status=completed
resulting_gateway_model=no-long-ssh_retry_gate
manual_window_without_open_ssh=true
remote_polling_ttl_max=180
stop_lines_reinforced=true
secret_payload_guard=true
exact_gate_copy_paste_updated=true
```

## Design alignment

Runbook now matches:

1. key-based SSH only;
2. short SSH precheck and short final guard;
3. remote watchdog on polling start;
4. no SSH during local manual Telegram window;
5. final no-polling verification + public probe symmetry before/after.

## Stop-line matrix

No live action allowed for this polish artifact itself:

```text
public_exposure=false
config_delivery=false
peer_creation=false
package_upload_apply=false
service_restart=false
firewall_sshd_auth_users_keys=false
restore_import_reboot=false
provider_rebuild=false
telegram_profile_media_mutation=false
secret_output=false
```

## Next exact gate

Recommended immediate execution gate:

```text
PRIVATE_RC_TELEGRAM_OPERATION_NO_LONG_SSH_RETRY_GATE
```

## Next-doc follow-up

After this polish, next-step handoff doc should remain on hold until exact gate
operator confirmation:

```text
hold_gate=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
```
