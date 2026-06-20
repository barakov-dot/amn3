# Phase 7 P7-I005 public exposure readiness design

Дата: 2026-06-14.

Статус: `completed`.

Importance: very important.

Gate: `local-only/docs/tests`.

## Purpose

`P7-I005` separates public exposure readiness from the blocked combined
`P7-C002 + P7-C003 + P7-C005` gate. It prepares the `P7-C002` checklist without
opening public access, changing firewall rules, applying reverse proxy, issuing
TLS certificates or publishing OpenAPI.

Source preflight evidence:

```text
research/amn2/phase-7-public-config-write-preflight-b121865-2026-06-14.md
```

## AMN2 Changes

AMN2 fresh installer manifest now exposes:

```text
public_exposure_readiness_design
schema_version=public-exposure-readiness-design.v1
status=readiness_design_ready
mode=local_only_docs_tests
gate=P7-I005
target_gate=P7-C002
live_exposure_allowed=false
requires_named_gate_for_apply=P7-C002 public exposure gate
```

`/api/integration/status` exposes the same safe metadata through
`public_exposure_readiness_design`.

The rendered fresh-install plan now includes phase:

```text
public-exposure-readiness-design
```

Readiness checklists:

- `admin-credential-contract`: require `WEB_ADMIN_USERNAME`,
  `WEB_ADMIN_PASSWORD_HASH` and `APP_SECRET_KEY` presence, while evidence stays
  presence-only and never prints raw credential or hash values.
- `domain-tls-reverse-proxy-plan`: require operator decisions for `domain_name`,
  `tls_mode` and `reverse_proxy_kind`; allowed backend target is
  `127.0.0.1:3030`; public API `3040` is blocked as a proxy target.
- `firewall-listener-plan`: backend remains loopback `127.0.0.1:3030`; direct
  public `0.0.0.0:3030` and `0.0.0.0:3040` are blocked.
- `external-probe-matrix`: before apply, external `3030` and `3040` stay
  closed; after apply, `3030` and `3040` still stay closed, while `80` and
  `443` can be verified as proxy redirect/challenge/auth surfaces.
- `rollback-to-loopback`: rollback goal is `web_loopback_only`.

Blocked actions remain:

```text
public_listener_change
firewall_apply
reverse_proxy_apply
tls_certificate_issue
public_openapi_publication
direct_public_api_3040
```

AMN2 operator docs updated:

- `docs/FRESH_INSTALL_WIZARD.ru.md`;
- `docs/FRESH_INSTALLER_OPERATOR_INDEX.ru.md`.

## Verification

RED focused:

```text
3 failed, 21 passed, 1 StarletteDeprecationWarning
```

Expected failures:

- missing `public_exposure_readiness_design` in manifest;
- missing rendered plan phase `public-exposure-readiness-design`;
- missing integration status key.

GREEN focused:

```text
24 passed, 1 StarletteDeprecationWarning
```

Expanded:

```text
30 passed, 1 StarletteDeprecationWarning
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

`P7-I005` is complete and should be removed from the active plan.

`P7-C002` remains critical gated/deferred. A future public exposure live gate
should start from this checklist and still require an exact named gate.
