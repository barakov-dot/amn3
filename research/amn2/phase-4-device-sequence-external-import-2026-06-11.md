# Phase 4 device sequence and external import visibility

Date: 2026-06-11.

Scope: AMN2 local-only implementation slice after bot config delivery localization.

## Result

AMN2 branch `codex/device-sequence-existing-peers`, commit `59bc266 Add device sequence and external import visibility`, was pushed and fast-forwarded into `amn2/codex-vps-test-prep`.

The slice closes the immediate bot/admin UX gap reported during Telegram config delivery testing:

- new bot-approved devices use the shared prefix `Neobyatnaya-AMNZ`;
- default sequence seed is `4`, so a fresh local DB starts new approvals at `Neobyatnaya-AMNZ-5`;
- if the DB already contains a higher `Neobyatnaya-AMNZ-N`, the next approval continues from the highest saved number;
- previously issued live/test peers can be imported into the local AMN2 DB as `config_material_status=external_only`;
- imported external-only devices are visible in the bot device list and web user detail view;
- external-only devices do not expose `Show secrets`, `Email config` or bot resend config actions;
- direct resend attempts for external-only devices return a safe unavailable message instead of generating a fake config;
- a local CLI command was added for backfill: `python -m app.cli device import-external ...`.

## Safety Boundary

This slice does not reconstruct old client configs. For peers created outside AMN2, the server-side peer public key is not enough to rebuild a valid client config because AMN2 does not have the original client private key. Such devices are tracked as visible records only until the original `.conf` is supplied by the operator or the device is reissued.

No live VPS command, SSH command, service restart, real Telegram delivery by Codex, production peer/user mutation, public exposure, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot or upstream code copy was performed.

`VPS_APPLY_ENABLED=false` remains the boundary for live peer apply/revoke.

## Verification

Focused local suite:

```text
171 passed, 1 warning
```

Full AMN2 local suite:

```text
644 passed, 1 warning
```

Additional hygiene:

```text
git diff --check: passed
git diff --cached --check: passed
```

The warning is the existing Starlette TestClient deprecation warning from the local test runtime.

## Operator Notes

For the existing test sequence:

- `Neobyatnaya-AMNZ-1` and `Neobyatnaya-AMNZ-2` remain the approved active test peers by Phase 3 evidence;
- `Neobyatnaya-AMNZ-3` and `Neobyatnaya-AMNZ-4` remain revoked by Phase 3 evidence;
- backfill must use safe local/operator-known peer metadata and must not publish private keys, PSKs, raw configs, QR payloads or endpoints to GitHub/chat.

After this slice, the earlier recommendation still stands: the next safe local-only step is `P4-AMNEZIA-REFRESH-002`, the client import compatibility matrix for `.conf`, `vpn://`, QR and future native `.vpn`/Amnezia JSON behavior.
