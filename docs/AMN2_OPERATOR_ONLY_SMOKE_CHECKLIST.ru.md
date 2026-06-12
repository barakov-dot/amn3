# AMN2 Operator-Only Smoke Checklist

Дата: 2026-06-11.

Назначение: подготовить безопасный чеклист для Phase 5 operator-only pilot. Чеклист покрывает web/admin loopback, bot dry/local behavior, private read-only API routes and no-public-exposure checks without opening live/write/config/public/destructive gates.

Этот документ сам по себе не разрешает live VPS commands, SSH commands against target VPS, deploy/restart/package apply, public exposure, config delivery, `/api/clients` write CRUD, Local Agent mutations, backup/import/reboot or production peer/user mutation. Если проверка требует touch real VPS, SSH session, service state or network listener sampling, сначала нужен отдельный named gate.

## Current Boundary

```text
phase: Phase 5 Operator-Only Pilot
default_mode: local-only/docs/tests/checklists
AMN2 current head: de25576 Polish Russian-first microcopy
latest VPS-smoked source-overlay/package head: de25576 Polish Russian-first microcopy
web/admin target bind: 127.0.0.1:3030
operator access: SSH local port forward only, external browser only
public/direct 3030: closed by loopback bind
public API 3040: absent/closed
TCP 80/443: absent
domain/Caddy/HTTPS public cutover: deferred
VPS_APPLY_ENABLED: false
config delivery: blocked without separate named gate
write API: blocked without separate named gate
```

## Stop Lines

Stop the smoke and record `decision: no-go` if any step would require:

- setting `VPS_APPLY_ENABLED=true`;
- package apply, rebuild on VPS, deploy, service restart/enable/disable;
- firewall, Caddy, nginx, HTTPS, domain or public listener changes;
- public API `3040` or direct public web/admin `3030`;
- POST/submit/save/reset actions in web/admin;
- create/update/delete user, device, peer, server, token or setting;
- peer apply/revoke/sync, add missing local device or remove unknown remote peer;
- config delivery, `.conf`, QR, `vpn://`, import/export/download;
- API `config:read` or `/api/clients` write CRUD;
- Local Agent write/config routes;
- backup/import/reboot;
- raw `.env`, `servers.yml`, tokens, Authorization headers, token hashes, keys, PSK, peer public keys, configs, QR, `vpn://`, endpoint values, session cookies or full logs in evidence.

If a button or route looks read-only but its side effect is unclear, do not click it. Record `risk_class: needs-design`.

## Preconditions To Record

Use safe summaries only. If the value is from the last accepted evidence rather than a fresh operator run, mark it as `from_existing_evidence`.

```text
source_evidence:
operator:
AMN2 head selected:
latest package/source status:
web/admin access path:
web/admin bind expected:
api listener policy:
public exposure decision:
VPS_APPLY_ENABLED default:
secret publication policy reviewed:
named gate opened for live checks: yes/no
```

Expected values for a Phase 5 default check:

```text
web/admin access path: external browser over SSH local port forward
web/admin bind expected: 127.0.0.1:3030
api listener policy: loopback-only if checked, not public
public exposure decision: no public 3030, no public 3040, no 80/443/domain cutover
VPS_APPLY_ENABLED default: false
secret publication policy reviewed: yes
named gate opened for live checks: no
```

## Web/Admin Loopback Smoke

Allowed default scope: review existing docs/evidence and prepare an operator checklist. Fresh real target checks require a named gate because they involve SSH/tunnel or live listener sampling.

If an approved operator-only gate is open, use only an external browser through the operator SSH tunnel. Codex browser preview is not the access path.

Allowed observations are GET navigation and visual/status review:

```text
/login
/
/users
/servers
/orders
/logs
/settings
/config-templates
/api-readiness
/integration-status
/api-tokens
/devices/disabled
```

For each route record:

```text
route:
loaded: yes/no/not_checked
auth_state: unauth_redirect | authenticated_200 | not_checked
primary_purpose_clear: yes/no/unclear/not_applicable
service_mode_or_loopback_boundary_visible: yes/no/not_applicable
write_config_public_actions_visible: no | gated_or_explained | unclear | yes-stop
external_only_devices_explained: yes/no/not_applicable
secret_artifacts_visible: no | unclear-stop | yes-stop
candidate_issue:
risk_class: read-only-ux | needs-design | blocked-write-config-public-gate
```

Pass criteria:

- `/login` and overview/status pages load through the operator-only path.
- Web/admin wording keeps loopback/service-mode boundary visible.
- Users/devices pages distinguish local AMN2 records from live/external-only inventory.
- Any dangerous action is gated, disabled or clearly explained.
- No config payload, QR, `vpn://`, private key, PSK, raw token or endpoint value is exposed in evidence.
- No POST/action button is clicked.

## Bot Dry/Local Smoke

Default scope: local/dry behavior, tests or operator observation only. Do not deploy, restart or mutate the live bot from this checklist.

Safe bot observations:

```text
/start sends access-bot header image: yes/no/not_checked
language selector shown: ru_en | not_checked
Russian default path works: yes/no/not_checked
English fallback works: yes/no/not_checked
main menu renders selected locale: yes/no/not_checked
approved device naming remains Neobyatnaya-AMNZ-N: yes/no/not_checked
external_only device is visible without resend/secrets promise: yes/no/not_checked
config resend blocked for external_only: yes/no/not_checked
real config delivery performed: no
live bot deploy/restart performed: no
```

Pass criteria:

- `/start` UX matches the access-bot boundary from `P4-BOT-ONBOARDING-001`.
- Language choice and Russian-first copy remain clear.
- External-only devices are shown as visible state, not recoverable config material.
- No `.conf`, QR, `vpn://`, private key, PSK, token or raw endpoint value is sent or published by Codex.
- No live bot restart/deploy is performed.

## Read-Only API Smoke

Default scope: check the route contract from docs/evidence. Fresh API loopback smoke on a target VPS requires a named gate, even if the script is read-only.

The private/local read-only route set remains six:

```text
GET /api/servers
GET /api/servers/{server_name}/summary
GET /api/integration/status
GET /api/local-agent/runtime/summary
GET /api/metrics/summary
GET /api/users/summary
```

Safe summary fields:

```text
checked_routes:
route_status_codes:
forbidden_markers:
auth_missing_bearer:
auth_wrong_scope:
auth_revoked_token:
listener_policy:
audit_status:
public_api_3040:
api_config_read_present:
api_clients_write_present:
secret_publication:
```

Expected Phase 5 default result:

```text
checked_routes: 6
forbidden_markers: none
auth_missing_bearer: 401 if checked
auth_wrong_scope: 403 if checked
auth_revoked_token: 401 if checked
listener_policy: loopback-only if checked
public_api_3040: absent/closed/not_public
api_config_read_present: no
api_clients_write_present: no
secret_publication: no
```

Pass criteria:

- Route count remains six.
- Responses contain only safe aggregate/status metadata.
- No `config:read`, `/api/clients` write CRUD, token issue/revoke/rotate API route, Local Agent mutation, backup/import/reboot or public docs exposure is introduced.
- Any live API sampling is backed by a named gate and safe evidence only.

## No-Public-Exposure Check

Record the source of evidence:

```text
evidence_source: existing_evidence | named_gate_operator_check | not_checked
direct_public_3030: no/not_checked
public_api_3040: no/not_checked
tcp_80_443: absent/not_checked
domain_https_cutover: deferred/not_checked
reverse_proxy_changed: no/not_checked
firewall_changed: no/not_checked
```

Pass criteria:

- Public `3030`, public `3040`, TCP `80/443`, domain/HTTPS and reverse proxy remain unchanged from the accepted loopback-only boundary.
- If the check cannot be done without live commands, mark `not_checked` and do not infer a fresh result.
- Do not publish public endpoint values, full port scan output or secret-bearing logs.

## Evidence Template

```text
check_id: P5-I004
date/time:
operator:
scope: docs-only | local-only | named-gate-operator-smoke
AMN2 selected head:
latest VPS-smoked source:
web_admin_loopback_status:
bot_dry_local_status:
read_only_api_status:
no_public_exposure_status:
VPS_APPLY_ENABLED_false:
write_actions_called:
config_delivery_performed:
live_vps_commands_by_codex:
ssh_commands_by_codex:
package_apply_or_rebuild:
service_restart_or_deploy:
public_exposure_changed:
secrets_published:
blocked_or_unclear_items:
decision: pass | needs-fix | defer | no-go
next_recommended_slice:
```

## Decision Rules

Use `pass` only when:

- all in-scope checks passed;
- no stop line was crossed;
- no blocked action was performed;
- no secret-bearing evidence was published;
- every live-target value has either a named-gate source or is marked `not_checked`.

Use `needs-fix` when a local/docs/UI/API/bot wording or checklist issue is found and can be fixed without live/write/config/public work.

Use `defer` when a useful check needs a separate named gate.

Use `no-go` when a stop line would be needed, a blocked action was performed, or evidence cannot be made secret-safe.

## Handoff After Smoke

After any checklist run:

- attach or create one safe evidence file in `research/amn2/`;
- update `docs/PROJECT_STATUS_CURRENT.ru.md`;
- update `research/amn2/transfer-backlog.md`;
- remove completed items from the active Phase 5 plan;
- keep closed gate slices in history/evidence, not in the active plan;
- keep `VPS-REBUILD-001`, write API, config delivery, public exposure and other future live/write/destructive directions gated unless the operator opens a separate named gate;
- give the next recommendation explicitly.
