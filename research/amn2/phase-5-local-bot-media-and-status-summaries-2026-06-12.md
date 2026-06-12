# Phase 5 P5-L002/P5-L001 local bot media and status summaries

Date: 2026-06-12.

Scope: AMN2 local-only product improvements before any VPS update.

AMN2 commit:

```text
9bff807 Add local bot media and status summaries
branch: codex-vps-test-prep
remote: amn2/codex-vps-test-prep
```

## P5-L002 Bot Media Local Registry

Implemented:

- `app.services.bot_media.BotMediaRegistry`;
- `python -m app.cli bot-media validate`;
- `python -m app.cli bot-media stage`;
- `python -m app.cli bot-media select`;
- `python -m app.cli bot-media manifest`;
- local safe JSON registry defaults:
  - `data/bot-media-registry.json`;
  - `data/bot-media/<asset_id>/...`;
- support for `access`, `support`, `news`;
- support for `start_header` and `profile_icon`;
- PNG/JPEG/WebP header-based validation without adding external image dependencies;
- safe manifest fields only: hash, sanitized filename, dimensions, MIME type, byte size, local-only safety flags and selected runtime mapping.

Boundary:

- `start_header` can be validated/staged/selected locally;
- `profile_icon` can be staged locally only as `staged-for-operator`;
- no Telegram API call;
- no Telegram token storage;
- no BotFather/profile mutation;
- no live bot send;
- no web/public upload route;
- no config delivery.

## P5-L001 Read-Only Status/Latency Summary

Implemented:

- existing web/admin server detail page now shows a `Read-only server summary` block;
- the block uses only existing local DB `server_health_checks` cached data;
- fields include:
  - `server_label`;
  - `runtime_kind`;
  - `service_mode=loopback-only`;
  - `latest_health_status`;
  - `latest_latency_ms`;
  - `last_checked_at`;
  - `data_source=cached_db`;
  - `freshness`;
  - action hint: read-only status, does not change VPS or peers, live check requires named gate.

Boundary:

- no new route;
- no live probe;
- no SSH;
- no health/sync action triggered by viewing the block;
- no raw logs;
- no user/device/peer/config/secret fields;
- no `.conf`, QR, `vpn://`, private key or PSK material.

## Verification

TDD RED checks:

```text
P5-L002 RED:
tests/services/test_bot_media.py tests/cli/test_bot_media.py
result: collection failed because app.services.bot_media and bot-media CLI entrypoints did not exist

P5-L001 RED:
tests/web/test_servers.py::test_server_detail_shows_phase5_read_only_status_latency_summary
result: failed because Read-only server summary block did not exist
```

Focused final:

```text
PYTHONPATH=.codex_deps python -m pytest tests/services/test_bot_media.py tests/cli/test_bot_media_cli.py tests/web/test_servers.py tests/bot/test_bot_handlers.py tests/bot/test_delivery.py -q
result: 71 passed, 1 warning
warning: known StarletteDeprecationWarning
```

Full final:

```text
PYTHONPATH=.codex_deps python -m pytest -q
result: 671 passed, 1 warning
warning: known StarletteDeprecationWarning
```

Git hygiene:

```text
git diff --check: passed
git diff --cached --check: passed
```

## Package Status After This Slice

Before this slice, `P5-C006` built `dist/amn2-vps-update-and-smoke-kit-dd0dd44.zip` as `package-ready-not-vps-smoked`.

After this slice, AMN2 current head is `9bff807`, so the `dd0dd44` package is now superseded for future VPS update work. It remains valid evidence for `P5-C006`, but it is not the current-head package anymore.

Before any live update/smoke gate, rebuild a new package from AMN2 `9bff807`.

## Boundary

Performed:

- AMN2 local-only code/tests/docs;
- AMN2 local CLI implementation;
- AMN2 private web/admin template/view-model update;
- local pytest verification;
- local git commit/push.

Not performed:

- live VPS command;
- SSH command;
- package apply/rebuild on VPS;
- source overlay;
- service restart/deploy;
- public exposure;
- config delivery;
- write API;
- Local Agent mutation;
- backup/import/reboot;
- production peer/user mutation;
- destructive VPS/provider action;
- Telegram token use;
- Telegram API call;
- live bot send;
- Telegram profile icon/avatar mutation;
- secret-bearing evidence publication;
- upstream/GPL code copy.

`VPS_APPLY_ENABLED=false` remains the expected target boundary.

## Active Plan Update

Remove from active Phase 5 plan:

```text
P5-L002 Bot media local registry/upload for start/header assets
P5-L001 Read-only status/latency display
```

Remaining active default Phase 5 plan:

```text
critical: none
very_important: none
important: none
normal: none
simple: none
cosmetic: none
```

Carried/gated directions remain:

```text
VPS-REBUILD-001: critical destructive gate, defer.
write API/config delivery/public exposure: critical gated.
P4-PRVTPRO-REFRESH-003 status/latency: carried from Phase 4, normal, design boundary closed and local display slice now implemented without live probes.
```

## Next Recommendation

Recommended next step:

```text
P5-C008 Current-head package rebuild for AMN2 9bff807
```

Do `P5-C008` before reopening the live update/smoke path. After that, `P5-C007` can be the named live update/smoke gate for the disposable test VPS if the operator chooses it.
