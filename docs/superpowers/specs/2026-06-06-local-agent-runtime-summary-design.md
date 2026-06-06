# Local Agent Runtime Summary Design

Date: 2026-06-06.

Status: design-only, local AMN3 coordination. This document does not change AMN2 code, does not run VPS commands, does not enable write operations, and does not approve public exposure.

## Context

Current AMN2 production baseline is `32d01fd Update integration status for controlled prod` on `codex-vps-test-prep`.

The `32d01fd` update package passed real VPS read-only loopback smoke:

```text
run_id: 20260606T185114Z
checked_routes: 5
routes: servers, integration_status, server_summary, metrics_summary, users_summary
auth checks: missing bearer 401, wrong scope 403, revoked token 401
listener_status: passed
audit_status: passed
```

Controlled-prod readiness is still pending operator-only confirmations. The next safe local implementation direction after that gate is a controller-safe Local Agent runtime summary.

Existing Local Agent read-only first slice already has:

```text
GET /agent/health
GET /agent/version
GET /agent/runtime
GET /agent/protocols
```

Those routes are Local Agent routes, not a public controller surface. The future controller/web layer must not forward raw Local Agent responses directly.

## Goal

Add a small, testable, read-only contract for summarizing Local Agent runtime state for an operator/controller view.

The summary should answer only:

- is the Local Agent reachable;
- what runtime contract/version is present;
- whether writes are disabled;
- what read-only protocol statuses/capabilities are visible;
- aggregate protocol client counts when privacy policy allows them.

The summary must not expose topology, peer identity, config delivery, command output, tokens, private material, or mutation routes.

## Non-Goals

This slice does not include:

- public web/API exposure;
- `config:read`;
- `/api/clients` write CRUD;
- Local Agent clients/configs routes;
- peer config delivery;
- backup/import/reboot;
- apply/revoke/write lifecycle;
- broad controller-to-agent mutation;
- publishing `.env`, `servers.yml`, raw tokens, Authorization headers, token hashes, private keys, PSK, `.conf`, QR payloads, VPN URI payloads, or full logs.

## Approaches Considered

### Recommended: safe mapper/service first

Create a pure internal mapper/service in AMN2 that normalizes Local Agent read-only metadata into a smaller `LocalAgentRuntimeSummary` object.

Trade-offs:

- best fit for TDD because it can be tested without VPS or live agent calls;
- keeps route exposure separate from data classification;
- lets web/admin and API code reuse one safety contract later;
- does not require a public route in the first implementation slice.

This is the chosen approach.

### Alternative: add an external API route immediately

Add a controller API route that returns the safe summary.

Trade-offs:

- useful for web/admin integration sooner;
- increases route-policy and auth surface immediately;
- requires stronger review because it turns internal Local Agent facts into API output.

This can follow only after the mapper tests are green and the route policy is explicit.

### Rejected: raw proxy of `/agent/*`

Expose or forward raw Local Agent responses to the controller/API.

Trade-offs:

- fastest to wire;
- couples external behavior to Local Agent internals;
- risks leaking topology-sensitive fields such as server aliases, container names, interface names, paths, or future sensitive fields.

This is rejected.

## Summary Contract

The mapper should return a compact shape like:

```text
agent_status
agent_version
runtime_contract_version
write_enabled
runtime_type
runtime_status
protocols[].name
protocols[].status
protocols[].runtime_type
protocols[].capabilities
protocols[].client_count
```

The mapper should omit by default:

```text
server_name
container_name
interface
config_path
service_name
command strings
stdout/stderr
peer public keys
VPN IPs
endpoints
latest handshakes
per-peer traffic
client names
configs
```

`write_enabled` must remain `false` for this slice. Any `true` value should be treated as a stop condition for the controller-safe summary until a separate write gate exists.

`client_count` is allowed only as an aggregate count. It must not create a path to client names, public keys, VPN addresses, config payloads, latest handshakes, or per-peer traffic.

## Route and Scope Boundary

The first implementation should prefer a service/mapper with unit tests and no new route.

If a route is added later, the route should:

- use an existing read scope such as `server:read` for runtime summary;
- avoid exposing Local Agent `agent:*` scopes through public controller tokens;
- avoid `config:read`;
- reject missing or insufficient scope;
- be covered by route-policy binding tests;
- return only the mapper output, never raw Local Agent data.

The route must not mount Local Agent clients/configs/write lifecycle surfaces.

## Audit and Logging

The implementation must not log:

- raw bearer tokens;
- token hashes;
- Authorization headers;
- Local Agent tokens;
- private keys;
- PSK values;
- config payloads;
- full command output.

Audit records may contain route name, safe operation id, status, and high-level decision, but not secret-bearing input or output.

## Error Handling

The mapper should handle missing Local Agent data conservatively:

- missing health/version/runtime/protocol data should become `unknown` or absent safe fields, not an exception that leaks raw response content;
- malformed protocol entries should be skipped or marked `unknown` without including original raw payload;
- if `write_enabled` is not explicitly `false`, the summary should mark the agent as unsafe for controller display.

API/web code that consumes the mapper should display a degraded/unknown status rather than attempting config, clients, or write fallbacks.

## Test Plan

AMN2 implementation must use TDD.

Required RED tests before production code:

- summary includes `runtime_contract_version` and `write_enabled=false`;
- summary includes protocol name, status, runtime type, capabilities, and aggregate `client_count`;
- summary omits `server_name`, `container_name`, `interface`, `config_path`, command strings, stdout/stderr, peer keys, VPN addresses, endpoints, per-peer traffic, client names, and configs;
- summary treats missing or non-false `write_enabled` as unsafe/degraded;
- if an API route is added, missing read scope is rejected and route-policy binding is covered;
- Local Agent raw token and controller Authorization header are not logged or audited;
- `/agent/clients`, `/agent/configs`, backup/import/reboot/write lifecycle remain unavailable.

Suggested verification after implementation:

```text
focused mapper tests
focused API route-policy tests, only if a route is added
existing agent tests
existing API auth/scope tests
secret marker scan on changed files
```

No VPS smoke is required for a mapper-only implementation. A VPS read-only smoke is required if the implementation changes API routes, web/admin runtime status, auth policy, packaging, or smoke behavior.

## Decision

Proceed with the recommended safe mapper/service first.

Do not implement public API exposure, config delivery, Local Agent mutation, or live VPS write behavior in this slice.

The next step after this spec is an implementation plan for AMN2 TDD work, then tests-first implementation in `C:\Users\SooL\Documents\Amneziya`.
