# Manager Config Export Contract

Дата: 2026-06-01.

Назначение: зафиксировать safety boundary для будущего `ConfigExportResult`/manager export layer в `amn2`, чтобы `.conf`, QR, `vpn://` и protocol-specific artifacts выдавались через единый typed contract, а не через несовместимые helper signatures.

Этот документ не является implementation plan. Он не меняет `amn2`, не добавляет API routes, не меняет bot/web delivery behavior, не читает `.env`, не требует live VPS и не переносит код из PRVTPRO/Amnezia-Web-Panel. Он описывает, какой контракт нужен перед расширением config delivery, public/self-service links, Local Agent `/configs` или hybrid protocol managers.

## Current production baseline

В `amn2` уже есть работающий config delivery pipeline:

```text
app/services/config_delivery.py::build_device_config_delivery()
app/bot/delivery.py::ConfigDeliveryPackage
app/bot/delivery.py::build_config_delivery()
app/vpn/config_versions.py::render_client_config_for_version()
app/vpn/config_templates.py::build_vpn_import_link()
tests/services/test_config_delivery.py
tests/bot/test_delivery.py
```

Текущий behavior:

- device secrets хранятся encrypted в DB и decrypt-ятся только для runtime delivery;
- `render_client_config_for_version()` выбирает supported config version;
- `build_config_delivery()` собирает message, `.conf` bytes, QR PNG, `vpn://` import link и artifact metadata;
- `.conf`, QR payload/PNG и `vpn://` уже классифицированы как `client-config-secret`;
- tests покрывают UTF-8 bytes, non-ASCII profile data, `vpn://` decode round-trip и redaction of rendered secret artifacts.

Этот baseline полезен и не должен переписываться первым срезом. Новый contract нужен не потому, что текущая доставка сломана, а потому что future protocol managers/API/UI/bot/self-service не должны напрямую зависеть от разных `get_client_config(...)` signatures или от raw config string as implicit API.

## Problem

Config export кажется "простым чтением", но фактически это `secret-read`:

- raw `.conf` содержит peer private key and preshared key;
- QR may encode the same full config or a protocol-specific import payload;
- `vpn://` reversibly encodes config text even when it hides literal `PrivateKey`;
- email, bot, web, public share, Local Agent and future API all become delivery channels;
- protocol managers may support different artifacts and targets.

PRVTPRO issue #49 is the warning class: caller and manager disagree on `get_client_config` arguments, so a runtime error reaches config display. For `amn2`, the lesson is not "copy the helper"; it is "never let UI/API call protocol managers through informal signatures".

## Decision status

Status: `implemented-pushed-local-gate-complete`.

Decision: manager-driven config export must return a typed result with explicit artifacts, capabilities, safe metadata and safe error categories. The first implementation slice is complete as a local-only contract/tests adapter and does not expose a new config route.

Implementation evidence:

```text
branch: codex/manager-config-export-contract
base: codex/api-token-lifecycle-gate-stacked
commit: 4d4e7a4 Add manager config export contract
focused local gate: 40 passed
full local suite: 560 passed, 1 StarletteDeprecationWarning
```

## Contract goals

The contract must:

- keep current `build_device_config_delivery()` behavior working;
- make every exported artifact typed and risk-classed;
- allow protocols to support different artifact sets;
- make QR payload target explicit;
- keep raw secret payload out of audit/log/error metadata;
- make unsupported export a safe category, not an exception string;
- give web/API/bot/self-service one normalized shape to consume.

The contract must not:

- force every protocol to produce `.conf`, QR and `vpn://`;
- store raw configs in DB as the normal model;
- add public/self-service endpoints by itself;
- grant `config:read` API tokens;
- call live VPS, Docker or SSH;
- copy PRVTPRO manager code.

## Proposed model

Minimum conceptual shape:

```text
ConfigExportRequest
  actor_type
  actor_id
  device_id
  user_id
  server_id
  protocol_id
  config_version
  target_client
  requested_artifacts
  delivery_channel

ConfigExportResult
  status
  protocol_id
  device_id
  config_version
  secret_class
  artifacts
  warnings
  safe_metadata

ConfigExportArtifact
  kind
  target_client
  filename
  media_type
  content_encoding
  secret_class
  payload
  safe_metadata
```

This is a design shape, not a promise to add these exact class names. The important contract is the boundary:

- `payload` is secret-bearing and must never enter audit/log/error text;
- `safe_metadata` is the only part allowed in audit and diagnostics;
- `status` and `warnings` are categories, not raw exception text;
- `target_client` says what client/import flow this artifact is intended for.

## Artifact kinds

| Kind | Payload | Secret class | Notes |
| --- | --- | --- | --- |
| `wireguard_conf` | UTF-8 `.conf` bytes/text | `client-config-secret` | Current raw config artifact. |
| `qr_payload` | Text encoded into QR | `client-config-secret` | Must state whether this is raw `.conf`, `vpn://`, or protocol-specific URI. |
| `qr_png` | PNG bytes | `client-config-secret` | Binary artifact; do not log/base64 in diagnostics. |
| `amnezia_import_uri` | `vpn://...` or future URI | `client-config-secret` | Reversible import payload, never metadata. |
| `delivery_message` | User-facing instructions | `secret-adjacent` or `client-config-secret` | Becomes secret-bearing if it embeds import URI. |
| `download_file` | Attachment wrapper | `client-config-secret` | Filename/media type/size may be metadata; body is not. |

## Capability model

Each protocol manager should declare capabilities instead of pretending all protocols export the same shape:

| Capability | Meaning | First-slice behavior |
| --- | --- | --- |
| `export.conf` | Can produce raw config file | Existing AmneziaWG path supports it. |
| `export.import_uri` | Can produce app import URI | Existing `vpn://` helper supports one format. |
| `export.qr` | Can produce QR payload/PNG | Existing package can generate QR from config text. |
| `export.target_client` | Can vary output per target client | Future only; first slice can default to `amnezia_generic`. |
| `export.redacted_preview` | Can show safe preview | Only synthetic/sample previews, never real secrets. |

Unsupported capability must return `unsupported_artifact` or `unsupported_target_client`, not a raw traceback.

## Request policy

Config export cannot decide authorization alone. It must be called only after an outer gate has already checked actor/resource access:

| Caller | Required gate before export | Notes |
| --- | --- | --- |
| Telegram user resend | user owns device | Existing ownership pattern stays. |
| Telegram admin resend | admin actor + device lookup | Existing admin pattern stays. |
| Web admin email send | session + CSRF + email policy | Audit must exclude payload. |
| Public recovery token | hashed token + TTL + one-time + ownership | Existing token discipline stays. |
| Future API token | `config:read` scope + resource policy | Not allowed in first route expansion. |
| Future Local Agent `/configs` | agent token + route policy + secret-read gate | Blocked until separate design. |

The export contract is not an auth bypass. It is the safe object returned after policy succeeds.

## Safe metadata

Allowed metadata:

- artifact kinds requested and produced;
- protocol id;
- config version;
- target client;
- filenames without secret values;
- payload byte length;
- content encoding;
- result status;
- safe warning codes;
- user/device/server numeric ids when the caller is already authorized.

Forbidden metadata:

- raw `.conf`;
- QR payload text;
- QR PNG/base64;
- `vpn://` or other import URI;
- private key;
- preshared key;
- public share raw token;
- SMTP/token/agent/API secrets;
- template text after real secret substitution.

## Error model

Config export errors must be stable categories:

| Error code | External message | Internal note |
| --- | --- | --- |
| `unsupported_config_version` | Config version is not supported. | Include safe version id only. |
| `unsupported_artifact` | Requested artifact is not available. | Include kind and protocol. |
| `unsupported_target_client` | Target client is not supported. | Include safe target id. |
| `missing_device_secret` | Config cannot be restored for this device. | Do not reveal which secret value. |
| `secret_decrypt_failed` | Config cannot be restored for this device. | Audit category only; no ciphertext/detail. |
| `template_invalid` | Config template is invalid. | Safe placeholder names only. |
| `export_failed` | Config export failed. | Redacted internal detail only. |

Raw exception messages must not be returned to users if they can include function signatures, file paths, config text or secret values.

## Relation to current `ConfigDeliveryPackage`

`ConfigDeliveryPackage` already contains useful fields:

- `config_filename`;
- `config_bytes`;
- `qr_filename`;
- `qr_png_bytes`;
- `vpn_import_link`;
- `qr_payload_text`;
- `config_secret_class`;
- `config_content_encoding`;
- `vpn_import_link_encoding`.

The future manager contract should not discard this. The safe path is to wrap or adapt the existing package into typed artifacts, then move callers gradually.

Good first adapter boundary:

```text
DeviceConfigDelivery -> ConfigExportResult -> channel-specific delivery
```

Where channel-specific delivery is still bot/email/web and not a new public API.

## QR target rule

QR must say what it encodes:

- `qr_payload_kind=wireguard_conf`
- `qr_payload_kind=amnezia_import_uri`
- `qr_payload_kind=protocol_specific_uri`

Current `amn2` QR uses raw config text. That is acceptable only while documented and tested. If a future client target needs QR from `vpn://`, it must be a separate artifact/target, not a silent behavior change.

## Audit events

Allowed audit shape:

```json
{
  "event": "config_export",
  "actor_type": "web-admin",
  "user_id": 42,
  "device_id": 7,
  "protocol_id": "amneziawg",
  "config_version": "amneziawg_v2",
  "target_client": "amnezia_generic",
  "artifact_kinds": ["wireguard_conf", "qr_png", "amnezia_import_uri"],
  "secret_class": "client-config-secret",
  "status": "success"
}
```

Forbidden audit values:

- `payload`;
- `config_text`;
- `vpn_import_link`;
- `qr_payload_text`;
- raw token;
- private/preshared key;
- rendered message text if it embeds `vpn://`.

## Tests required before implementation

Contract tests:

- every manager/exporter returns a typed `ConfigExportResult`;
- unsupported artifact returns a safe category;
- unsupported target client returns a safe category;
- no raw exception message reaches public result;
- result safe metadata excludes `.conf`, QR payload and `vpn://`;
- artifact payloads are present only in secret-bearing artifact fields.

Artifact tests:

- `.conf` bytes equal UTF-8 config text;
- non-ASCII profile/user/server names round-trip;
- `vpn://` decodes back to original config;
- QR payload decode equals expected payload when a QR decoder is available;
- QR payload kind is explicit.

Policy tests:

- user cannot export another user's device config;
- admin can export only through admin-gated surfaces;
- API token cannot use `config:read` until route policy exists;
- public token export requires hash lookup, TTL and one-time consume;
- audit has ids/status/artifact kinds but no secret payload.

Regression test for the PRVTPRO #49 class:

- callers use a single export interface;
- adding a manager with a different internal implementation does not change caller signature;
- manager mismatch becomes `export_failed` or `unsupported_artifact`, not a raw `TypeError` in UI/API.

## First safe implementation boundary

The first safe code slice, already moved from AMN3 docs to `amn2`, is:

```text
manager config export contract and no-route adapter
```

It includes:

- typed request/result/artifact objects;
- adapter from current `DeviceConfigDelivery`/`ConfigDeliveryPackage`;
- capability declarations for current AmneziaWG config versions;
- no-side-effect contract tests;
- safe metadata tests;
- one regression test for signature mismatch class.

It must not include:

- public/self-service config endpoint;
- API `config:read` scope;
- Local Agent `/configs`;
- new QR/import behavior for users;
- live VPS calls;
- DB storage of raw config bodies;
- copying PRVTPRO manager code.

## Next product decision

Before any public/self-service or API config route, choose whether the product wants:

1. channel-only export: bot/email/web internal delivery can use the contract, but no new route;
2. authenticated admin/user route: session/API route with `secret-read`, ownership and audit gates;
3. public token delivery: one-time hash-token flow with expiry, revoke, rate limit and audit.

Default recommendation: start with option 1. It gives the architecture benefit without expanding the exposed secret-delivery surface.
