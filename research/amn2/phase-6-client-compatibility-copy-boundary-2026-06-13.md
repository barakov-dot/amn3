# Phase 6 Client Compatibility And Copy Boundary

Date: 2026-06-13.

Tasks closed:

- `P6-M004` iOS AmneziaWG import/connectivity diagnostic boundary.
- `P6-X001` Public product copy polish.
- `P6-X002` Brand/media consistency across bots, panel and docs.

AMN2 branch: `codex-vps-test-prep`.

AMN2 commit: `b3102db Add client compatibility delivery boundary`.

Latest VPS-smoked/package head remains `2215761 Polish operator web admin UX`.
`b3102db` is not package-rebuilt and not VPS-smoked.

## What Changed

- Added explicit client roles to the AMN2 compatibility matrix:
  - iOS DefaultVPN: primary RF-available iOS path.
  - iOS AmneziaWG/Apple: installed/legacy path for users who already have it.
  - Android AmneziaWG: separate supported Android path.
- Updated Telegram delivery copy so the first visible instructions match the
  matrix and keep `.conf` as the first fallback.
- Updated web `Config templates` copy with the same matrix.
- Added a safe `client_compatibility_boundary` summary to API and web
  `/integration-status`.
- Kept full `.conf`, QR payloads and import links secret-bearing.
- Recorded that always-copyable one-tap links require short tokenized config
  delivery and therefore remain inside `P6-C002` Config delivery gate.

## Verification

RED:

- `pytest tests/vpn/test_client_compatibility.py tests/bot/test_delivery.py`
  initially failed on missing client-role constants.
- `pytest tests/api/test_api_integration_status.py tests/web/test_web_integration_status.py`
  initially failed on missing `client_compatibility_boundary`.

GREEN:

- Focused client/delivery/panel/status:
  `26 passed, 1 warning`.
- Expanded API/web/bot/vpn:
  `290 passed, 1 warning`.
- `git diff --check`: passed.
- `git diff --cached --check`: passed before commit.

Warning: existing `StarletteDeprecationWarning` from the local FastAPI
TestClient shim.

## Safety Boundary

No live VPS command, SSH command, package apply/rebuild, service restart/deploy,
public exposure, config delivery, write API, Local Agent mutation,
backup/import/reboot, production peer/user mutation, destructive provider
action, Telegram token use, live bot send, Telegram profile mutation,
secret-bearing evidence publication or upstream/GPL code copy was performed.

## Follow-Up

`P6-C002` now explicitly includes short one-tap config delivery links if the
product needs the exact Telegram `CopyTextButton` UX shown by the operator:
the current full `vpn://` import link can exceed Telegram's copy-text length
limit, while a short always-copyable link requires tokenized secret delivery,
TTL/revoke/audit/redaction and a separate named gate.
