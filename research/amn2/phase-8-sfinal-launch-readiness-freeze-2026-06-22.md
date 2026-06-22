# Phase 8 P8-SFINAL launch readiness freeze

Date: 2026-06-22.

Status: `launch-ready-with-explicit-limitations`.

Scope: docs-only final Phase 8 launch readiness freeze using existing evidence
only. No live VPS/SSH command, destructive action, package upload/apply,
service restart, public exposure, config delivery, Telegram live send, bot
polling, Telegram profile/media mutation, backup restore/import/reboot,
provider mutation, production peer/user mutation or secret-bearing output was
performed in this freeze.

## Final Verdict

Chosen status:

```text
phase8_final_status=launch-ready-with-explicit-limitations
private_operator_rc_launch_ready=true
public_launch_ready=false
remaining_blockers_for_private_operator_rc=none-with-listed-limitations
blocked_with_exact_remaining_blockers=false
recommended_next_step=private_operator_rc_handoff_docs_or_exact_operator_launch_gate
```

This is not a public launch approval. It is a private/operator RC readiness
freeze for the Telegram-first, private-admin, `.conf`-first lane.

## Evidence Basis

### P8-C001 Fresh Android Phone Acceptance

Evidence:
`research/amn2/phase-8-p8-c001-fresh-android-config-acceptance-2026-06-21.md`.

Key result:

```text
fresh_peer_public_key_fp=594ba96e4f90
android_import_status=passed
android_connect_status=passed
android_traffic_status=passed
endpoint_observed=yes
latest_handshake_age_s=45
reconnect_sanity_status=passed
reconnect_latest_handshake_age_s=18
payload_output_status=not_performed
public_exposure_status=not_performed
telegram_live_send_status=not_performed
```

Conclusion: fresh per-device Android AmneziaWG acceptance exists for a real
Android phone in a separate P8 gate. Old shared configs remain diagnostic proof
only and are not release delivery artifacts.

### P8-C002 Current-Head Package Smoke

Evidence:
`research/amn2/phase-8-p8-c002-187949b-package-apply-smoke-2026-06-21.md`.

Key result:

```text
amn2_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
package_sha256=7FA073E4C66C0981673061D167D525BB9BCD6DFDDAA075E15701F0C2608E2E82
source_overlay_match=yes
settings_client_awg_compatible=yes
loopback_web_runtime_status=passed
api_smoke_status=passed
telegram_get_me_status=passed
telegram_live_send_performed=false
backup_create_status=passed
backup_verify_status=passed
backup_artifact_mode=600
public_3030_probe=000
public_3040_probe=000
public_80_probe=000
public_443_probe=000
secret_values_printed=false
```

Conclusion: the selected AMN2 head `187949b` is the current package/runtime line
for this private/operator RC, and Android-compatible AWG defaults are persisted
in the normal package/runtime path.

### P8-C003 Fresh-From-Zero Rehearsal

Evidence:
`research/amn2/phase-8-p8-c003-fresh-zero-rehearsal-2026-06-22.md`.

Key result:

```text
target_vps=89.185.80.166
fresh_install_status=passed
source_overlay_match=yes
fresh_env_db_init_status=passed
admin_telegram_ids_count_actual=2
operator_admin_pair_present=yes
loopback_web_status=passed
loopback_api_smoke_status=passed
telegram_get_me_status=passed
telegram_polling_started=false
telegram_live_send_performed=false
backup_create_status=passed
backup_verify_status=passed
backup_artifact_mode_600_verified=true
fresh_peer_public_key_fp=d0ab128d6801
fresh_android_acceptance_device=android_projector
fresh_android_phone_available=false
fresh_android_traffic_source=browser_or_app
endpoint_observed_after=yes
transfer_rx_delta_bytes=622084
transfer_tx_delta_bytes=9004751
public_3030_probe=000
public_3040_probe=000
public_80_probe=000
public_443_probe=000
secret_values_printed=false
```

Conclusion: fresh-from-zero private/operator RC reproducibility is proven for
AMN2 `187949b` on the disposable VPS, including backup evidence, closed public
exposure, two Telegram bot admins and Android projector browser/app traffic.

## Explicit Limitations

1. `P8-C003` Android acceptance used an Android projector, not an Android phone.
   Android phone acceptance is covered by separate `P8-C001` evidence, not by
   the fresh-from-zero rehearsal itself.
2. Public web/admin/API exposure is not approved. Public probes to `3030`,
   `3040`, `80` and `443` stayed closed; operator web/admin remains private by
   loopback/SSH tunnel or equivalent operator-only access.
3. Telegram server-side readiness was smoked through `getMe` and non-polling
   dispatcher/user-flow construction. This freeze did not start bot polling and
   did not perform Telegram live send/profile/media mutation.
4. `.conf` is the release-primary mobile handoff artifact. QR and full
   `vpn://` are not release-primary.
5. No config payload, private key, PSK, token, password, QR payload or
   `vpn://` payload may be pasted into chat/evidence.
6. iOS DefaultVPN remains experimental/unreliable. Windows desktop remains
   accepted by operator observation, not by a fresh automated device gate.
7. Backup create+verify is proven; restore/import DR is not proven and remains
   behind a separate exact gate.
8. Provider rebuild, reboot, public exposure, firewall/listener changes,
   Cloudflare/ngrok/reverse proxy/TLS publication and production-scale user/peer
   rollout are not approved by this freeze.

## Launch Readiness Decision

The correct final Phase 8 status is:

```text
private_operator_rc_launch_ready=true
phase8_final_status=launch-ready-with-explicit-limitations
phase8_launch_gate_status=closed-for-private-operator-rc-with-limitations
public_launch_status=not-approved
fresh_android_phone_acceptance_source=P8-C001
fresh_zero_android_acceptance_device=P8-C003_android_projector
telegram_first_runtime_status=server-side-getme-and-non-polling-smoke-passed
telegram_live_send_status=not-performed
public_exposure_status=closed-by-default
backup_evidence_status=create-and-verify-passed
restore_import_status=not-proven
secret_payload_output_status=not-performed
```

## Next Recommended Work

Critical:

- Одиночные: private/operator RC handoff package, docs-only.
- Парные: RC handoff + operator run checklist.
- Тройные: RC handoff + operator run checklist + limitations acknowledgement.
- 4+: RC handoff + checklist + rollback/backup note + exact future gate menu.

Very important:

- keep public exposure closed by default;
- keep Telegram live send/profile/media mutation behind exact gates;
- keep restore/import behind exact gates;
- keep config payloads out of chat/evidence.

Important:

- if a future production rollout is requested, open a new exact named operator
  launch gate with target users/devices and delivery channel.

Simple:

- update next-chat/current-status handoffs to start from this final verdict.

Cosmetic:

- polish release wording only after the freeze is committed.

## Stop Lines After Freeze

Without a fresh exact named gate, do not perform:

- destructive VPS/provider action;
- public exposure, Cloudflare, ngrok, reverse proxy, TLS, firewall/listener
  changes;
- `.conf`, QR, `vpn://`, private key, PSK, token or password output;
- Telegram live send/profile/media mutation or bot polling;
- write/install execution;
- backup restore/import/reboot;
- production peer/user mutation.
