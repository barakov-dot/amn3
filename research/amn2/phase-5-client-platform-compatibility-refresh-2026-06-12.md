# Phase 5 P5-N003 client/platform compatibility refresh

Дата: 2026-06-12.

Scope: read-only upstream refresh plus AMN2 local-only compatibility wording/tests/docs.

## Result

Status: `closed`.

Upstream note: `research/upstreams/amnezia-vpn-client-defaultvpn-refresh-2026-06-12.md`.

AMN2 branch `codex-vps-test-prep` advanced from `de25576` to `dd0dd44 Refresh client platform guidance` and was pushed to `barakov-dot/amn2`.

The slice updates the AmneziaVPN platform guidance after checking current public GitHub metadata. The previous matrix already covered `.conf`, `vpn://`, QR, DefaultVPN and AmneziaWG import boundaries. The new change only refines Linux availability wording: current upstream release assets include a generic Linux x64 tar, but AMN2 still must not promise distro-specific Linux packages or universal Linux install support.

## AMN2 Changes

- `app/vpn/client_compatibility.py`: replaces stale Debian/Ubuntu-unavailable wording with `Linux x64 tar available; distro-specific packages not promised`.
- `tests/vpn/test_client_compatibility.py`: makes that wording machine-checkable and prevents the old text from returning to user guidance.
- `docs/WEB_PANEL_AND_BOT_SETUP.ru.md`: syncs operator-facing setup guidance with the matrix.

## Verification

RED:

```text
$env:PYTHONPATH='.codex_deps'; py -3.14 -m pytest tests/vpn/test_client_compatibility.py -q
result: 2 failed, 3 passed
expected failure: tests still expected the new Linux tar wording before implementation changed
```

GREEN focused:

```text
C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe --version
result: Python 3.12.13

$env:PYTHONPATH='.codex_deps'; C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest tests/vpn/test_client_compatibility.py tests/bot/test_delivery.py -q
result: 13 passed
```

AMN2 git hygiene:

```text
git diff --check: passed
git diff --cached --check: passed
git push amn2 codex-vps-test-prep: passed
remote head: dd0dd442f0f25c1113accdc625dd16a96059eba4
```

Full AMN2 suite was not run in this slice because the change is narrow and covered by focused compatibility/bot-delivery tests.

## Safety Boundary

Performed:

- public GitHub metadata/release asset read;
- AMN2 local-only code/test/docs wording change;
- AMN3 documentation/evidence/status updates.

Not performed:

- upstream code copy;
- live VPS command;
- SSH command;
- package apply/rebuild on VPS;
- service restart/deploy;
- public exposure;
- config delivery;
- write API;
- Local Agent mutation;
- backup/import/reboot;
- production peer/user mutation;
- destructive provider/VPS action;
- Telegram token use or live Telegram send;
- secret-bearing evidence publication.

`VPS_APPLY_ENABLED=false` remains the Phase 5 default.

## Remaining Active Plan

### Critical

No active default critical tasks. Carried/gated directions remain: `VPS-REBUILD-001`, write API, config delivery, public exposure and any future live/write/destructive named gates.

### Very Important

No active tasks.

### Important

No active tasks.

### Normal

- `P4-PRVTPRO-REFRESH-003` Read-only server status/latency UX boundary, carried from Phase 4, design-boundary-only.

### Simple

No active tasks.

### Cosmetic

No active tasks.

## Next Recommendation

`P4-PRVTPRO-REFRESH-003` read-only server status/latency UX boundary as a docs/design-only slice first. Do not implement PRVTPRO-derived UI/code directly and do not open live/write/config/public behavior without a separate named gate.
