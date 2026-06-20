# Phase 7 P7-I004 public/config/write prerequisite split

Дата: 2026-06-14.

Статус: `completed`.

Importance: very important.

Gate: `local-only/docs/tests`.

## Purpose

`P7-C002 + P7-C003 + P7-C005` был открыт как combined public/config/write gate
для `b121865`, но read-only preflight закрыл его как
`blocked-by-preconditions`. Этот slice превращает этот результат в явную
local-only readiness структуру, чтобы не повторять широкий live gate без
подготовленных prerequisite.

Source preflight evidence:

```text
research/amn2/phase-7-public-config-write-preflight-b121865-2026-06-14.md
```

## AMN2 Changes

AMN2 fresh installer manifest now exposes:

```text
public_config_write_prerequisite_split
schema_version=public-config-write-prerequisite-split.v1
status=blocked_by_preconditions
mode=local_only_docs_tests
combined_gate_retry_allowed=false
live_changes_allowed=false
```

Readiness tracks:

- `public-exposure-readiness`, gate `P7-C002`: admin credential contract,
  domain/TLS/reverse proxy plan, firewall/listener plan, public probe matrix and
  rollback to loopback.
- `config-delivery-channel-readiness`, gate `P7-C003`: SMTP or operator-local
  channel, secret-safe evidence protocol, client import matrix, one-time
  delivery policy and delivery revocation story.
- `write-api-scope-decision`, gate `P7-C005`: keep public API read-only for RC,
  add a separate write API implementation slice, or use an operator-only web
  write window.

Observed blockers from live preflight are represented as safe metadata:

```text
web_loopback_only
external_public_probes_closed
web_admin_username_missing
smtp_config_missing
vps_apply_enabled_false
local_agent_disabled
write_api_route_count_zero
```

Blocked actions remain:

```text
public_listener_change
domain_tls_reverse_proxy_apply
config_artifact_output
write_api_route_enablement
vps_apply_enabled_true
local_agent_mutation
live_peer_user_mutation
```

The rendered fresh-install plan now includes phase
`public-config-write-prerequisite-split`.

`/api/integration/status` now exposes the same split through
`public_config_write_prerequisite_split`.

AMN2 operator docs were updated:

- `docs/FRESH_INSTALL_WIZARD.ru.md`;
- `docs/FRESH_INSTALLER_OPERATOR_INDEX.ru.md`.

## Verification

RED focused:

```text
3 failed, 19 passed, 1 StarletteDeprecationWarning
```

Expected failures:

- missing `public_config_write_prerequisite_split` in manifest;
- missing rendered plan phase `public-config-write-prerequisite-split`;
- missing integration status key.

GREEN focused:

```text
22 passed, 1 StarletteDeprecationWarning
```

Expanded:

```text
28 passed, 1 StarletteDeprecationWarning
```

Expanded command covered:

```text
tests/services/test_fresh_install_wizard.py
tests/services/test_integration_status_service.py
tests/api/test_api_integration_status.py
tests/web/test_web_integration_status.py
```

## Not Performed

- live VPS command;
- SSH command;
- package upload/apply/rebuild on VPS;
- service restart/deploy;
- public listener, domain, TLS, reverse proxy or firewall change;
- public OpenAPI publication;
- config delivery, `.conf`, QR or `vpn://` output;
- write API route enablement;
- `/api/clients` CRUD;
- Local Agent mutation;
- `VPS_APPLY_ENABLED=true`;
- live peer/user mutation;
- backup/import/reboot;
- destructive cleanup/reinstall;
- Telegram token use, live bot send or identity/profile mutation;
- secret-bearing evidence publication;
- upstream/GPL code copy.

## Outcome

`P7-I004` is complete and should be removed from the active plan.

The combined `P7-C002 + P7-C003 + P7-C005` live path should not be retried as a
single enablement step until the three readiness tracks are handled separately.
