# Phase 14 dual-protocol application readiness receipt

Date: 2026-08-11

Status: `APPLICATION_STAGE_VERIFIED_LOCAL`

This is a secret-free local application-stage receipt. It records source
verification only. It is not a package, preflight, SSH, deployment, live
mutation, production issuance, or live-approval artifact.

## Source identity

- Approved source base: `4547af1b23e4774822119f98004568c6eb039303`
- Verified application HEAD: `36981d7afc1fcd9eb17386c62f70adf175d76263`
- Source branch: `codex/phase14-dual-protocol-application-local`
- Final whole-branch and scoped re-reviews: `ALL ADDRESSED`; no open findings

## Application commit ledger

### Task 1

- `af73aa9c580c2b47eea69471162a3716ee944e0b` — `feat: add Phase 14 dual protocol state`

### Task 2

- `ce5917775984c8d0d57f34d11883904a98ad2bef` — `feat: gate AWG3 issuance globally`
- `f29690f908f2d6a67d0db1d7d28784dee541b5d3` — `fix: enforce atomic AWG3 control gates`
- `a1c66cf0a8536f4dfe155d0fdac110705849a9be` — `fix: make repository transactions nested safe`

### Task 3

- `97093485755d3b4595337e5a2948d44f631f9717` — `feat: add per-device protocol profiles`
- `9a4597616c996c567599c532908e28033a2731dd` — `fix: make protocol profiles durable and restart safe`
- `22c2594ce71e490d39eae6a22be3c255a6c6f2f1` — `fix: bind compromise completion to revoked snapshot`

### Task 4

- `2473233246ba6c4b3fb109b0914b362429e1c8cb` — `feat: add fail closed self service issuance`
- `4429f65942782a2b83c9c0361730de8e073e1016` — `fix: make self service issuance durable`

### Task 5

- `662ddd9118a6f6b54afcec0e8a6e0f8ea4d13ea9` — `feat: expose dual protocol bot and admin flows`
- `946ff46f21c5e35b782a426bd780c364c32bab16` — `fix: harden dual protocol presentation flows`

### Task 6

- `ce56537a4353a62e53e2785e89066375100c536a` — `feat: enforce dual protocol lifecycle cascades`
- `0d67022c209c5a3b4e65138e5a66b5bafdbb636f` — `fix: paginate protocol lifecycle projections`

### Task 7 source-fixture correction

- `1cb3b058b535391ef8eed195d4c481055cdca58b` — `test: remove raw-shaped dual protocol fixtures`

### Task 8 consolidated issuance/revocation safety

- `171904889630b2ec8d459ad067202d442aaa7b38` — `fix: serialize dual protocol issuance and revocation`
- `348a026b0fd6529847877f4643f4f1a39bf7a5aa` — `fix: harden issuance migration and recovery`
- `324c8190132aa8c71c5e03e0b4c4b50c65a36a72` — `fix: close phase14 whole branch findings`
- `ab1245e2180f40acdc90f1e149e795426be57aa8` — `fix: persist issuance recovery before remote effects`
- `36981d7afc1fcd9eb17386c62f70adf175d76263` — `fix: make admin issuance finalization atomic`

## Final verification evidence

Fresh post-review Phase 14 integrated focused suite:

```text
345 passed, 1 warning in 84.46s
```

Fresh post-review full source suite:

```text
1321 passed, 1 skipped, 1 warning in 197.64s
```

The known warning is the existing Starlette `httpx` test-client deprecation.

The fresh post-review checks ran at exact source HEAD
`36981d7afc1fcd9eb17386c62f70adf175d76263`. Source status, index and range
diff checks were clean. The complete Phase 14 range from the approved base
contains 39 files, 9,936 additions and 57 deletions. Final whole-branch and
scoped reviews found no remaining Critical, Important or Minor findings.

Manual secret/scope review found no PEM/private-key material, WireGuard key
assignment or production-shaped import URI in added lines. Two generic token
matches were short synthetic `token-N` values in bot tests. No raw
configuration, private key, PSK, QR payload or secret-bearing import material
is recorded in this receipt. No AWG2 golden or runtime artifact, monitoring
code, package/preflight/live script, Phase 13 tree or production bootstrap was
changed by the final scoped fixes.

## Task 5 production bootstrap deferral

Production Telegram activation remains explicitly deferred. The AWG3
Telegram adapter is fail-closed and dependency-injected; no production
router/factory bootstrap or production issuer was added. Activation requires
a separate package/bootstrap gate with a checksum-bound runtime,
evidence/build provider, and production issuer. This receipt does not approve
that work.

## Control and execution state

```text
AWG2_DEFAULT_PRESERVED=true
AWG3_GLOBAL_ACCEPTANCE_REQUIRED=true
AWG3_PER_USER_ADMIN_APPROVAL_REQUIRED=false
AWG3_ISSUANCE_ENABLED=false
PACKAGE_MATERIALIZED=false
PREFLIGHT_RUN=false
SSH_USED=false
LIVE_MUTATION=false
```

## Boundary

The application stage is locally verified at the exact HEAD above. Package
materialization, preflight, SSH use, production bootstrap, real issuance, and
any live mutation remain outside this receipt and require separate explicit
approval.
