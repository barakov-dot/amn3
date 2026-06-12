# AMN2 read-only server status/latency UX boundary

Дата: 2026-06-12.

Назначение: закрыть design boundary для `P4-PRVTPRO-REFRESH-003` и отделить безопасную идею "operator can see server status/latency" от PRVTPRO GPL implementation, public panel assumptions, live probes and write actions.

Этот документ не является implementation plan и не меняет AMN2 runtime. Он определяет, какие status/latency поля можно проектировать для будущего local-only AMN2 slice, какие поля запрещены, какие gates нужны перед runtime probe, and when to stop.

## Source Boundary

Inputs:

- `research/upstreams/prvtpro-amnezia-web-panel-upstream-refresh-2026-06-10.md`;
- `research/upstreams/prvtpro-amnezia-web-panel-github-watch.md`;
- `research/amn2/read-only-metrics-privacy-classification.md`;
- `docs/AMN2_WEB_PANEL_READ_ONLY_UX_REVIEW_CHECKLIST.ru.md`;
- `research/amn2/phase-4-prvtpro-api-taxonomy-openapi-grouping-2026-06-10.md`.

PRVTPRO/Amnezia-Web-Panel is GPL-3.0 and remains `research-only`. AMN2 may use the product need as an idea, but must not copy upstream code, UI, templates, route layout, CSS/JS, manager implementation, command strings, workflows or text.

## Current AMN2 Boundary

Allowed by default:

- private operator web/admin over loopback/SSH tunnel;
- local-only docs/tests/templates;
- already safe aggregate server metadata;
- GET/navigation review;
- safe summaries without raw logs/secrets.

Not allowed without a separate named gate:

- live VPS command or SSH probe launched by Codex;
- public API `3040` or direct public web/admin `3030`;
- Caddy/nginx/domain/HTTPS public exposure;
- service restart/deploy/package apply;
- `Run health`, `Run sync`, peer apply/revoke or any remote mutation;
- config delivery, `.conf`, QR, `vpn://`;
- write API, Local Agent mutation, backup/import/reboot;
- production peer/user mutation;
- destructive provider/VPS action.

`VPS_APPLY_ENABLED=false` remains the default.

## Allowed Future UX Shape

A future local-only implementation may design a compact read-only status/latency block if it uses already available safe data or local/fake fixtures:

```text
server_label: safe internal alias only
runtime_kind: docker | systemd | unknown
service_mode: loopback-only | unknown
latest_health_status: ok | warning | error | not_checked
latest_latency_ms: aggregate server probe only, no per-peer labels
last_checked_at: timestamp of safe check source
data_source: cached_db | local_fake | operator_safe_summary
freshness: fresh | stale | not_checked
action_hint: read-only status; no automatic fix/sync/apply
```

The UI should visually separate:

- passive status display;
- stale/not checked state;
- blocked actions that need gates;
- links to runbooks/checklists, not buttons that run remote work.

## Forbidden Fields

Do not show by default in this surface:

- user names, Telegram IDs, emails or device names;
- peer public keys or peer hash identifiers;
- VPN IPs, endpoint IP/port or interface config paths;
- latest handshake per peer;
- per-peer rx/tx traffic;
- raw stdout/stderr/log snippets;
- `.conf`, QR payload, QR PNG/base64, `vpn://`, private key, PSK;
- API token hashes or raw tokens;
- backup names/paths if they reveal private context.

## UX Copy Requirements

Required copy concepts:

- "read-only";
- "last safe summary" or "not checked";
- "does not change VPS or peers";
- "live check requires named gate" when a button/action would be tempting;
- "loopback/private operator panel" if the status is shown in web/admin context.

Avoid:

- "online" if the value is cached or not actively probed;
- "fix", "sync", "repair", "apply" or "restart" labels in this block;
- public/self-service wording;
- promises that latency means user connectivity is good.

## Implementation Gate Rules

Future implementation is still separate from this boundary.

Local-only implementation may proceed only if:

- it uses cached DB/local fake/operator-safe-summary data;
- no live probe is run by Codex;
- route policy classifies the surface as read-only;
- tests assert forbidden fields are absent;
- templates make blocked live actions visibly separate from read-only status.

Separate named gate required if implementation would:

- run an SSH command or network probe against the VPS;
- call a Local Agent route not already approved as read-only;
- add API route exposure beyond current policy;
- change service health/sync behavior;
- collect or display raw logs;
- publish metrics outside the private operator boundary.

## Minimum Tests For Future Local Slice

Future AMN2 implementation plan should include:

- unit/service tests for status view model classification;
- template tests for `read-only`, `not_checked/stale`, and blocked action copy;
- forbidden-marker tests for user/device/peer/config/secret fields;
- route policy tests if an API route is added;
- audit classification tests if a status refresh action is introduced;
- no public exposure assumptions.

## Decision

`P4-PRVTPRO-REFRESH-003` is closed as a design-boundary slice.

The allowed future implementation is a separate optional local-only AMN2 slice: read-only server status/latency display from safe cached/local/fake sources. It is not authorized to run live probes, add public exposure, perform health/sync actions, deliver configs, mutate peers/users, or copy PRVTPRO GPL code/UI/templates.
