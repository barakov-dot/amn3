# AMN2 Web/Admin Header Asset Boundary

Дата: 2026-06-11.

Статус: `P5-M004` closed as AMN3 docs-only/local-only design boundary.

Русское название задачи: `P5-M004` Граница ассета шапки веб-панели.

Этот документ фиксирует, куда относится planning asset
`NEOBYATNAYA-AMNZ-ADMIN-PANEL.png`. Он не добавляет файл в AMN2, не меняет
web/admin runtime, не открывает публичный доступ и не создает новый UI.

## Naming Rule

Для русскоязычных планов используем правило:

- technical ID remains stable: `P5-M004`;
- human-readable task title is Russian-first;
- English alias may remain only where it helps historical search.

Preferred label:

```text
P5-M004 Граница ассета шапки веб-панели
```

Not preferred for active Russian plans:

```text
P5-M004 Admin panel header asset boundary
```

Rationale: the ID already gives stable tracking. The title should tell the
operator what and where we are touching without forcing English project jargon.

## Scope

`NEOBYATNAYA-AMNZ-ADMIN-PANEL.png` belongs to the web/admin product surface.

Possible future local surfaces:

- login page brand/header area;
- authenticated admin top navigation brand mark;
- dashboard header or service-mode status area;
- read-only brand/media registry preview.

Out of scope:

- current access bot `/start` header;
- future support/news bot header;
- Telegram bot profile icon/avatar;
- public marketing landing page;
- public self-service user portal;
- config delivery, QR, `.conf` or `vpn://` surfaces.

## Current Boundary

Current Phase 5 web/admin mode is operator-only:

```text
web/admin bind: 127.0.0.1:3030
operator access: SSH local port forward
direct public web/admin 3030: no
public API 3040: no
domain/Caddy/HTTPS public cutover: no
VPS_APPLY_ENABLED: false
```

Therefore a web/admin header asset must not imply public launch, public domain,
self-service access or marketing-site behavior.

## Asset Status

Current evidence from `P5-M001`:

- AMN2 current remote head tracks `app/bot/assets/NEOBYATNAYA-AMNZ-BOT.png`.
- No current-head tracked file was found for
  `NEOBYATNAYA-AMNZ-ADMIN-PANEL.png`.
- The admin-panel filename is a planning input, not a current runtime asset.

Future implementation must start by confirming the actual source file, license
and operator intent before copying anything into AMN2.

## Recommended Future Approach

Use a local-only implementation path if this asset is accepted later.

1. Asset intake.
   Operator supplies the image through a local path or repo-provided private
   asset handoff. The file source/license and SHA-256 are recorded.

2. Local validation.
   Validate MIME type, byte size, dimensions, transparency/background behavior
   and safe filename. Reject files that contain secrets, QR codes, config
   fragments, private server data or user identifiers.

3. Web/admin placement decision.
   Choose exactly one first placement: login header, admin nav brand, or
   dashboard header. Do not introduce a broad redesign in the same slice.

4. Local tests.
   Test that the selected page references the packaged static asset, renders
   safe alt text if needed and does not expose secret-bearing metadata.

5. Operator preview.
   Preview remains local/private. Public exposure stays blocked unless a
   separate named public-exposure gate exists.

## UI Boundary

The web/admin panel is an operator tool. Keep the future visual treatment:

- restrained;
- readable on small laptop screens;
- compatible with existing admin navigation;
- clear about service-mode/operator-only status;
- not a marketing hero;
- not a public product landing page.

The login page can show a public-safe brand image because unauthenticated users
may see it through the operator tunnel, but it must not leak endpoints, server
details, QR codes, config data or operational state.

## Suggested Future Metadata

```text
asset_id: stable local id
surface: web_admin_header
placement: login_header | admin_nav_brand | dashboard_header
source_filename: sanitized basename
content_sha256: hash of local file bytes
mime_type: image/png | image/jpeg | image/webp
byte_size: integer
width_px: integer
height_px: integer
public_safe: true | false
selected_for_runtime: true | false
operator_note: optional safe text
```

Fields that must not be stored:

- web admin password/session secret;
- Telegram token or API token;
- server config values;
- raw `.conf`, QR, `vpn://`, private key or PSK;
- private support/user identifiers in filenames or metadata.

## Stop Conditions

Stop before implementation if any of these are true:

- asset source/license is unclear;
- image contains secret-bearing material or private operational data;
- implementation requires public web/admin exposure;
- static path would publish private files broadly;
- task grows into a redesign of multiple web/admin screens;
- task touches write/config/public/backup/import/reboot behavior;
- live VPS deploy/restart/package apply is requested without a named gate.

## Active Plan Update

Remove from active Phase 5 plan:

```text
P5-M004 Граница ассета шапки веб-панели
```

Historical next safe local-only recommendation at the time:

```text
P5-M006 Одно нажатие для копирования import-ссылки в Telegram
```

Status: completed later in Phase 5.

Current Phase 5 handoff after `P5-S003` keeps no default local-only active work.
The next recommendation is `P5-C007` named live update/smoke gate for AMN2
`9bff807` on the disposable test VPS, if the operator chooses the VPS path.
