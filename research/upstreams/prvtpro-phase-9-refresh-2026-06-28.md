# PRVTPRO Phase 9 upstream refresh 2026-06-28

Дата: 2026-06-28.

Источник: Phase 9 automation aggregation input for
`prvtpro-weekly-upstream-refresh`.

Scope: read-only upstream refresh note. This note does not open live VPS, SSH,
public exposure, config delivery, write API, package apply, Telegram actions,
peer creation or secret-bearing output.

## Observed upstream state

No fresh changes after the already-known `a62f958` baseline from 2026-06-19
were found in the provided aggregation.

Latest visible commit remains:

```text
commit=a62f958
message=Add public tunnels and fix protocol connection bugs
date=2026-06-19
```

Latest release remains `v1.4.4` from 2026-06-19 on the same commit.

Open PR count was observed as `0`. GitHub UI showed roughly `21-22` open issues;
visible latest open issues were not newer than the current Phase 9 baseline.

## Carry-forward signals from PRVTPRO v1.4.4

- Public tunnels through Cloudflare Quick Tunnel / ngrok are `hybrid-only` and
  gated. They are useful as UX/reference input, but do not approve AMN2 public
  exposure.
- AWG Legacy actual config path detection is `candidate-now-docs-only`: manager
  or config retrieval must resolve the actual runtime config path, not assume a
  static path.
- Xray runtime API without container restart is `candidate-now-docs-only`:
  config/client mutation paths must define restart/no-restart expectations
  before live write gates.
- WireGuard show config through unified manager adapter reinforces the existing
  AMN2 manager export contract direction: config export should go through one
  redacted adapter contract with client-compatibility tests.
- API token/security ideas are `already-covered` by AMN2 scoped token, audit and
  write-guard work.
- GPL code/templates/managers/workflows remain `rejected-by-negative-control`.

## Chain guidance

Treat PRVTPRO `v1.4.4` as already-known Phase 9 input, not as a new launch
blocker. Do not convert PRVTPRO public tunnels into AMN2 public exposure
without an exact named public/hybrid gate.

Compare KYORESUAS API signals against Phase 9 time/config/auth contract audit.
Compare Amnezia client signals against current Android/self-config naming
limitations.

Default hold remains `ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА`.
