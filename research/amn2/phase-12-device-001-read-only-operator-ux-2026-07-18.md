# Post-release `DEVICE-001` read-only operator UX evidence

Date: `2026-07-18`

## Result

`DEVICE-001` is implemented and verified locally in AMN2 at
`e564b95e799fefa71599438a731e3f172a50c224`. It adds authenticated read-only
operator pages for existing Device Passports. This work is not deployed and
does not reopen the completed Phase 11 controlled private release.

```text
design_commit=57efe86
implementation_plan_commit=4c5b597
source_head=e564b95e799fefa71599438a731e3f172a50c224
source_branch=codex-vps-test-prep
production_source=0b858c5cdbc5b565cc265966a2edfe2d339d65e0
deployment=false
db_mutation=false
remote_observation=false
telegram=false
vps=false
config_peer_delivery=false
awg=untouched
```

## Closed scope

The slice adds two session-authenticated GET surfaces:

- `/device-passports` — bounded list of existing passports;
- `/device-passports/{device_id}` — safe detail projection with fixed `404`
  for an unknown device.

The runtime policy IDs are:

- `web.device_passports.index`;
- `web.device_passports.detail`.

Only safe passport metadata and lifecycle summaries are projected. Raw VPN
configuration, private keys, preshared keys and enrollment tokens are neither
loaded into the web view contract nor rendered by its templates. No POST,
write, enrollment, configuration or peer-delivery surface was admitted.

## Verification

Strict TDD evidence:

```text
focused_tests=74 passed, 1 warning in 16.12s
full_tests=928 passed, 1 skipped, 1 warning in 112.26s
compileall=pass
git_diff_check=pass
template_mutation_control_scan=0_matches
added_line_live_operation_scan=0_matches
added_line_high_confidence_secret_scan=0_matches
```

The remaining warning is the pre-existing Starlette/httpx deprecation emitted
through `fastapi/testclient.py`.

The bounded Codex Security diff scan covered every changed production
source-like file in `4c5b597..e564b95`:

```text
security_diff_coverage=complete|9_of_9
security_findings=0
security_deferred_candidates=0
snapshot=codex-security-snapshot/v1:sha256:ebc2f3f36453e97a57975c0f9decc1f32de22c4922048d3a3f6947c8d0cedd2a
report=C:\Users\SooL\AppData\Local\Temp\codex-security-scans\amn2-p7-c005-write-install\e564b95e799fefa71599438a731e3f172a50c224_20260718T085654Z\report.md
```

The only non-reportable hardening note is a bounded N+1 lifecycle read pattern:
the parent list is capped at 100 and current writers cannot create unbounded
failed lifecycle events, so it is not a plausible security finding for this
closed scope.

## Release boundary

Phase 11 remains `completed-controlled-private-release`. `DEVICE-001` is a
local post-release slice only. Public access, web API, write operations,
self-service, enrollment, config/peer delivery and live Telegram mutations
remain closed. The production bot, web service, database and AWG were not
contacted or changed during this implementation.

`TELEGRAM-GROUP-ICON-001` remains a separate fail-closed gate. Its live action
must not reuse any Phase 11 approval and requires its own checksum-bound
executor, tests, security review, commit/push and exact live approval.
